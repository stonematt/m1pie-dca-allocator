"""
st_aggrid_view.py: AgGrid-based visualization for nested portfolio structure.

Implements a master-detail interactive table using streamlit-aggrid,
allowing users to explore pie and ticker allocations in a collapsible view.

Key Features:
- Expandable rows for nested pies
- Leaf rows for tickers with value and weight
- Sorting, alignment, and structured formatting
- Logs UI render events for session tracking

Requires:
- portfolio.get_aggrid_portfolio_rows()
- streamlit-aggrid with enterprise modules enabled
"""

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import JsCode

from scripts.log_util import app_logger
from scripts.portfolio import get_aggrid_portfolio_rows

logger = app_logger(__name__)


def render_portfolio_aggrid():
    """
    Display the portfolio as a collapsible tree table using AgGrid.
    Uses icon class with JS cellRenderer to inject real DOM for background icons.
    """
    logger.info("Rendering portfolio AgGrid view")
    portfolio = st.session_state["portfolio"]
    rows = get_aggrid_portfolio_rows(portfolio)
    df_schema = pd.json_normalize(rows)

    gb = GridOptionsBuilder.from_dataframe(df_schema)
    gb.configure_grid_options(
        treeData=True,
        getDataPath=JsCode("function(data) { return data.path; }"),
        groupDefaultExpanded=0,
        suppressRowGroupPanel=True,
        autoGroupColumnDef={
            "headerName": "Asset",
            "field": "name",
            "cellRendererParams": {"suppressCount": True},
            "cellStyle": {"paddingLeft": "8px"},
        },
    )
    gb.configure_column("name", hide=True)
    gb.configure_column("path", hide=True)

    gb.configure_column(
        "icon",
        header_name="",
        width=40,
        cellRenderer=JsCode(
            """
            class IconRenderer {
                init(params) {
                    const span = document.createElement('span');
                    span.className = params.value;
                    this.eGui = span;
                }
                getGui() {
                    return this.eGui;
                }
            }
        """
        ),
        cellStyle={"textAlign": "center"},
    )

    gb.configure_column(
        "value",
        header_name="Value ($)",
        type=["numericColumn", "rightAligned"],
        valueFormatter=JsCode(
            "function(params) { return params.value != null ? '$' + params.value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) : ''; }"
        ),
    )
    gb.configure_column(
        "weight",
        header_name="Weight (%)",
        type=["numericColumn", "rightAligned"],
        valueFormatter=JsCode(
            "function(params) { return params.value != null ? params.value.toFixed(2) + '%' : ''; }"
        ),
    )
    gb.configure_column("type", header_name="Type", cellStyle={"textAlign": "center"})
    gridOptions = gb.build()

    AgGrid(
        pd.DataFrame(rows),
        gridOptions=gridOptions,
        enable_enterprise_modules=True,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        custom_css={
            ".icon-pie": {
                "display": "inline-block",
                "background-image": "url(assets/pie_icon_32.png)",
                "background-size": "contain",
                "height": "20px",
                "width": "20px",
            },
            ".icon-ticker": {
                "display": "inline-block",
                "background-image": "url(assets/ticker_icon_32.png)",
                "background-size": "contain",
                "height": "20px",
                "width": "20px",
            },
            ".ag-cell": {
                "line-height": "24px",
                "padding": "2px",
            },
        },
    )
