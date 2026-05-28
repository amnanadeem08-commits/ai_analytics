"""tabs/category.py — Category Analytics tab (V3)."""

import streamlit as st
from components.category_charts import render_category_analytics
from tabs.dashboard import render_chart   # shared chart renderer


def render(category_analytics) -> None:
    st.markdown("### 📊 Category Analytics")
    st.caption(
        "Complete category-wise breakdowns: totals, share, distribution, "
        "treemap, and trends over time."
    )
    if category_analytics and category_analytics.charts:
        render_category_analytics(category_analytics, render_chart)
    else:
        st.info("Upload data with categorical and numeric columns to generate category charts.")
