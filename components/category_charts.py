"""
category_charts.py — V3 category-wise Plotly chart gallery UI.
"""

import streamlit as st
from services.category_analytics_service import CategoryAnalyticsResult


def render_category_analytics(
    result: CategoryAnalyticsResult,
    render_chart_fn,
) -> None:
    """
    Render the full category analytics gallery.

    Args:
        result: Output from CategoryAnalyticsService.generate().
        render_chart_fn: Callable(fig, key) — app-level Plotly renderer with fixed height.
    """
    st.markdown(result.summary)

    if not result.category_sets:
        st.info(
            "No category breakdowns available. Ensure your file has categorical columns "
            "(e.g. plan, region, product) and at least one numeric metric (e.g. amount, revenue)."
        )
        return

    for i, cat_set in enumerate(result.category_sets):
        st.markdown(
            f"### 🏷 {cat_set.category_column.replace('_', ' ').title()} "
            f"({cat_set.cardinality:,} categories · metric: "
            f"{cat_set.metric_column.replace('_', ' ').title()})"
        )

        titles_in_set = {t for t, _ in cat_set.charts}
        section_charts = [(t, f) for t, f in result.charts if t in titles_in_set]

        if not section_charts:
            st.caption("No charts rendered for this column.")
            continue

        cols = st.columns(2)
        for j, (title, fig) in enumerate(section_charts):
            with cols[j % 2]:
                st.markdown(f"**{title}**")
                render_chart_fn(fig, key=f"cat_{i}_{j}")

        st.markdown("---")
