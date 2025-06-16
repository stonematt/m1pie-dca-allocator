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
    """
    logger.info("Rendering portfolio AgGrid view")
    portfolio = st.session_state["portfolio"]
    rows = get_aggrid_portfolio_rows(portfolio)
    df = pd.DataFrame(rows)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_grid_options(
        treeData=True,
        getDataPath=JsCode("function(data) { return data.path; }"),
        groupDefaultExpanded=0,
        suppressRowGroupPanel=True,
        autoGroupColumnDef={
            "headerName": "Asset",
            "field": "name",
            "cellRendererParams": {"suppressCount": True, "padding": 10},
            "cellStyle": {"paddingLeft": "8px"},
        },
    )
    gb.configure_column("name", hide=True)
    gb.configure_column("path", hide=True)
    gb.configure_column(
        "value",
        header_name="Value ($)",
        type=["numericColumn", "rightAligned"],
        valueFormatter=JsCode(
            """
            function(params) {
                return params.value != null
                    ? '$' + params.value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})
                    : '';
            }
            """
        ),
    )
    gb.configure_column(
        "weight",
        header_name="Weight (%)",
        type=["numericColumn", "rightAligned"],
        valueFormatter=JsCode(
            """
            function(params) {
                return params.value != null
                    ? params.value.toFixed(2) + '%'
                    : '';
            }
            """
        ),
    )
    gb.configure_column("type", header_name="Type", cellStyle={"textAlign": "center"})
    gridOptions = gb.build()

    AgGrid(
        df,
        gridOptions=gridOptions,
        enable_enterprise_modules=True,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
    )
