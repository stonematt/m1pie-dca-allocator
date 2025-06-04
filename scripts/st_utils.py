"""
st_utils.py: Streamlit UI helpers for the M1 Pie DCA Allocator.

Contains reusable components for visualizing portfolio adjustments,
such as allocation review tables comparing current and target states.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


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
        current_val = original_children.get(k, {}).get("value", 0.0)
        target_val = adjusted_children[k]["value"]
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
