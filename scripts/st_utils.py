"""
st_utils.py: Streamlit UI helpers for the M1 Pie DCA Allocator.

Contains reusable components for visualizing portfolio adjustments,
such as allocation review tables comparing current and target states.
"""

from decimal import Decimal, InvalidOperation
import random

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.colors import qualitative

from scripts.log_util import app_logger

logger = app_logger(__name__)


def render_allocation_review_table(original: dict, adjusted: dict) -> None:
    """
    Render a comparison table showing the effect of DCA allocation.

    :param original: Original pie structure
    :param adjusted: Adjusted pie structure after DCA allocation
    :return: None
    """
    original_children = original.get("children", {})
    adjusted_children = adjusted.get("children", {})

    data = []
    total_original = sum(v["value"] for v in original_children.values())

    # Build row data comparing current and target state per asset
    for k in adjusted_children:
        try:
            current_val = Decimal(str(original_children.get(k, {}).get("value", 0.0)))
        except (TypeError, InvalidOperation):
            current_val = Decimal("0.0")

        try:
            target_val = Decimal(str(adjusted_children[k].get("value", 0.0)))
        except (TypeError, InvalidOperation):
            target_val = Decimal("0.0")

        capital_allocated = target_val - current_val

        # Compute weights as whole-number percentages
        current_weight = (current_val / total_original * 100) if total_original else 0
        target_weight = adjusted_children[k].get("target_weight", 0)

        data.append(
            {
                "Ticker/Pie": k,
                "Current Value": f"${current_val:,.2f}",
                "Current Weight": f"{int(round(current_weight))}%",
                "Capital Allocated": f"${capital_allocated:,.2f}",
                "Target Value": f"${target_val:,.2f}",
                "Target Weight": f"{target_weight}%",
            }
        )

    # Display as an interactive Streamlit table with aligned currency columns
    df = pd.DataFrame(data)
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Current Value": st.column_config.Column("Current Value", width="small"),
            "Capital Allocated": st.column_config.Column(
                "Capital Allocated", width="small"
            ),
            "Target Value": st.column_config.Column("Target Value", width="small"),
        },
    )


def render_allocation_comparison_charts(original: dict, adjusted: dict) -> None:
    """
    Render vertically stacked pie charts comparing original and adjusted portfolio weights using Plotly.
    """

    def extract_pie_data(pie):
        children = pie.get("children", {})
        labels = list(children.keys())
        values = [v["value"] for v in children.values()]
        return labels, values

    orig_labels, orig_values = extract_pie_data(original)
    adj_labels, adj_values = extract_pie_data(adjusted)

    fig = go.Figure()

    fig.add_trace(
        go.Pie(
            labels=orig_labels,
            values=orig_values,
            name="Current",
            domain=dict(y=[0.55, 1]),
            hole=0.3,
            title="Current Allocation",
            textinfo="label+percent",
        )
    )

    fig.add_trace(
        go.Pie(
            labels=adj_labels,
            values=adj_values,
            name="Adjusted",
            domain=dict(y=[0, 0.45]),
            hole=0.3,
            title="Adjusted Allocation",
            textinfo="label+percent",
        )
    )

    fig.update_layout(height=600, margin=dict(t=40, b=0, l=0, r=0), showlegend=False)

    st.plotly_chart(fig, use_container_width=True)


def render_sankey_diagram(portfolio: dict) -> None:
    """
    Render a Sankey diagram showing the structure of the portfolio.
    :param portfolio: Portfolio dictionary with nested pies and tickers
    """
    if not portfolio.get("children"):
        st.info("This portfolio has no children to visualize.")
        return
    node_map = {}
    links = []
    positions = {}

    def get_node_id(name):
        if name not in node_map:
            node_map[name] = len(node_map)
        return node_map[name]

    def visit(node, parent_name, depth=0):
        parent_id = get_node_id(parent_name)
        if parent_name not in positions:
            positions[parent_name] = depth
        if node["type"] == "pie":
            for name, child in node["children"].items():
                child_id = get_node_id(name)
                links.append((parent_id, child_id, float(child["value"])))
                positions[name] = depth + 1
                if child["type"] == "pie":
                    visit(child, name, depth + 1)

    root_name = portfolio["name"]
    visit(portfolio, root_name)

    label = list(node_map.keys())
    source, target, value = zip(*links) if links else ([], [], [])

    max_depth = max(1, max(positions.values(), default=0))
    x_pos = [positions.get(name, 0) / max_depth for name in label]
    y_pos = [i / len(label) for i in range(len(label))]

    height = max(400, len(label) * 35)

    palette = qualitative.Set2
    color_map = {name: palette[i % len(palette)] for i, name in enumerate(label)}
    node_colors = [color_map[name] for name in label]

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                orientation="h",
                node=dict(
                    pad=20,
                    thickness=30,
                    line=dict(
                        color="rgba(0,0,0,0.1)", width=1
                    ),  # Subtle border for better definition
                    label=label,
                    x=x_pos,
                    y=y_pos,
                    color=node_colors,
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value,
                    hovertemplate="Value: %{value}<extra></extra>",
                ),
            )
        ]
    )

    # Improved font settings for better readability
    fig.update_layout(
        font=dict(
            family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
            size=12,  # Increased from 10
            color="#2c3e50",  # Darker color for better contrast
        ),
        height=height,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=20, b=20),  # Better margins
    )

    # Additional font customization specifically for the Sankey node labels
    fig.update_traces(
        textfont=dict(
            family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
            size=12,
            color="#2c3e50",
        ),
        selector=dict(type="sankey"),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_support_link():
    """Render a support button linking to Ko-fi or similar.

    Set the donation URL via .streamlit/secrets.toml:
    [support]
    kofi_url = "https://ko-fi.com/yourhandle"
    """
    kofi_url = st.secrets.get("support", {}).get("kofi_url")
    if kofi_url:
        labels = [
            "\u2615 Support on Ko-fi",
            "\ud83d\udc96 Buy me a coffee",
            "\ud83d\ude4f Tip the dev",
            "\ud83c\udf69 Donate via Ko-fi",
            "\u2764\ufe0f Send a thank-you",
        ]
        st.sidebar.link_button(random.choice(labels), kofi_url)
    else:
        logger.warning(
            "No support.kofi_url found in st.secrets; support button not shown."
        )
