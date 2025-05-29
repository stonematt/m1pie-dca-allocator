import streamlit as st
from decimal import Decimal
from scripts.portfolio import load_portfolio, normalize_portfolio
from scripts.dca_allocator import allocate_dca
from scripts.utils import to_decimal

st.title("📊 M1 Pie DCA Allocator")

portfolio_file = st.file_uploader("Upload portfolio JSON", type="json")
amount_input = st.number_input("DCA Amount ($)", min_value=0.01, format="%.2f")

if portfolio_file and amount_input:
    portfolio_data = load_portfolio(portfolio_file)
    normalized = normalize_portfolio(portfolio_data)
    allocations = allocate_dca(normalized, to_decimal(amount_input))

    st.subheader("📈 Allocations")
    for ticker, amt in allocations.items():
        st.write(f"{ticker}: ${amt:.2f}")
