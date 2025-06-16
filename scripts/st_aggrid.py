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
    Uses base64 HTML <img> tags for inline icons.
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
                        if (params.value && params.value.startsWith('data:image')) {
                            // Handle base64 data URLs
                            const img = document.createElement('img');
                            img.src = params.value;
                            img.width = 20;
                            img.height = 20;
                            img.style.display = 'block';
                            img.style.margin = 'auto';
                            this.eGui = img;
                        } else {
                            // Fallback to text
                            this.eGui = document.createTextNode(params.value || '?');
                        }
                    }
                    getGui() {
                        return this.eGui;
                    }
                }
                """
        ),
        cellStyle={"textAlign": "center", "padding": "2px"},
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
    )
