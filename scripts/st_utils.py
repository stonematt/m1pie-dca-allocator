"""
st_utils.py: Streamlit UI helpers for the M1 Pie DCA Allocator.

Contains reusable components for visualizing portfolio adjustments,
such as allocation review tables comparing current and target states.
"""
import pandas as pd
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
