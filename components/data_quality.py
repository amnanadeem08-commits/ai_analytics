"""
data_quality.py — Premium data quality score visualization.

Displays overall quality score with grade, dimensional breakdown,
and column-level quality details in a modern card-based layout.
"""

import streamlit as st
from services.data_quality_service import DataQualityReport


# ─── CSS Styling ───────────────────────────────────────────────────────────────

DATA_QUALITY_CSS = """
<style>
    /* Main Quality Score Card */
    .quality-score-card {
        background: rgba(255,255,255,0.04);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 8px 30px rgba(0,0,0,0.35);
        backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        gap: 1.5rem;
        transition: all 0.2s ease-in-out;
    }
    
    .quality-score-card:hover {
        box-shadow: 0 12px 40px rgba(0,0,0,0.45);
    }
    
    /* Grade Badge */
    .quality-grade-badge {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.2rem;
        font-weight: 800;
        flex-shrink: 0;
        position: relative;
    }
    
    .quality-grade-badge.grade-A {
        background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
        color: #065F46;
        box-shadow: 0 4px 12px rgba(14, 159, 110, 0.3);
    }
    
    .quality-grade-badge.grade-B {
        background: linear-gradient(135deg, #D1FAE5 0%, #6EE7B7 100%);
        color: #047857;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.2);
    }
    
    .quality-grade-badge.grade-C {
        background: linear-gradient(135deg, #FEF9C3 0%, #FDE68A 100%);
        color: #92400E;
        box-shadow: 0 4px 12px rgba(227, 160, 8, 0.3);
    }
    
    .quality-grade-badge.grade-D {
        background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
        color: #B91C1C;
        box-shadow: 0 4px 12px rgba(249, 128, 128, 0.3);
    }
    
    .quality-grade-badge.grade-F {
        background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
        color: #991B1B;
        box-shadow: 0 4px 12px rgba(231, 70, 148, 0.3);
    }
    
    /* Score Details */
    .quality-score-details {
        flex: 1;
    }
    
    .quality-score-value {
        font-family: 'JetBrains Mono', ui-monospace, monospace;
        font-size: 2rem;
        font-weight: 700;
        color: #F3F4F6;
        line-height: 1.1;
        letter-spacing: -0.02em;
    }
    
    .quality-score-label {
        font-size: 0.875rem;
        color: #9CA3AF;
        font-weight: 500;
        margin-top: 0.25rem;
    }
    
    .quality-score-meta {
        display: flex;
        gap: 1.5rem;
        margin-top: 0.75rem;
    }
    
    .quality-meta-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .quality-meta-label {
        font-size: 0.75rem;
        color: #9CA3AF;
        font-weight: 500;
    }
    
    .quality-meta-value {
        font-size: 0.875rem;
        font-weight: 700;
        color: #E5E7EB;
    }
    
    /* Dimension Bars */
    .quality-dimensions {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        margin-top: 1rem;
        width: 100%;
    }
    
    .quality-dimension {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .quality-dim-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #9CA3AF;
        width: 90px;
        flex-shrink: 0;
    }
    
    .quality-dim-bar-track {
        flex: 1;
        height: 8px;
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
        overflow: hidden;
    }
    
    .quality-dim-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease-out;
    }
    
    .quality-dim-bar-fill.good {
        background: linear-gradient(90deg, #0E9F6E 0%, #059669 100%);
    }
    
    .quality-dim-bar-fill.fair {
        background: linear-gradient(90deg, #E3A008 0%, #B45309 100%);
    }
    
    .quality-dim-bar-fill.poor {
        background: linear-gradient(90deg, #DC2626 0%, #B91C1C 100%);
    }
    
    .quality-dim-value {
        font-size: 0.8rem;
        font-weight: 700;
        color: #E5E7EB;
        width: 40px;
        text-align: right;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Column Details Table */
    .quality-column-details {
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
        overflow: hidden;
    }
    
    .quality-column-header {
        display: flex;
        align-items: center;
        padding: 1rem 1.25rem;
        background: rgba(255,255,255,0.03);
        border-bottom: 1px solid rgba(255,255,255,0.08);
        font-size: 0.9rem;
        font-weight: 600;
        color: #E5E7EB;
        gap: 0.5rem;
    }
    
    .quality-column-row {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 2fr;
        padding: 0.75rem 1.25rem;
        border-bottom: 1px solid rgba(255,255,255,0.07);
        align-items: center;
        font-size: 0.825rem;
        transition: background 0.15s;
    }
    
    .quality-column-row:hover {
        background: rgba(255,255,255,0.05);
    }
    
    .quality-column-row:last-child {
        border-bottom: none;
    }
    
    .quality-col-name {
        font-weight: 600;
        color: #F3F4F6;
    }
    
    .quality-col-score {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .quality-col-score-bar {
        width: 60px;
        height: 6px;
        background: #E5E7EB;
        border-radius: 3px;
        overflow: hidden;
    }
    
    .quality-col-score-fill {
        height: 100%;
        border-radius: 3px;
    }
    
    .quality-col-issues {
        color: #6B7280;
        font-size: 0.775rem;
    }
    
    .quality-issue-badge {
        display: inline-block;
        padding: 2px 8px;
        background: #FEF3C7;
        color: #92400E;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 500;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .quality-score-card {
            flex-direction: column;
            text-align: center;
        }
        
        .quality-score-meta {
            justify-content: center;
        }
        
        .quality-column-row {
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
        }
    }
</style>
"""


def _get_grade_class(grade: str) -> str:
    """Get CSS class for grade badge."""
    return f"grade-{grade}"


def _get_bar_class(score: float) -> str:
    """Get CSS class for progress bar based on score."""
    if score >= 80:
        return "good"
    elif score >= 60:
        return "fair"
    else:
        return "poor"


def render_data_quality(report: DataQualityReport) -> None:
    """Render overall score, dimensional breakdown, and column issues."""
    st.markdown(DATA_QUALITY_CSS, unsafe_allow_html=True)
    
    grade_class = _get_grade_class(report.grade)
    bar_class = _get_bar_class(report.overall_score)
    
    # Main score card
    st.markdown(
        f"""
        <div class="quality-score-card">
            <div class="quality-grade-badge {grade_class}">
                {report.grade}
            </div>
            <div class="quality-score-details">
                <div class="quality-score-value">{report.overall_score:.0f}<span style="font-size: 1rem; color: #6B7280; font-weight: 500;">/100</span></div>
                <div class="quality-score-label">Overall Data Quality Score</div>
                <div class="quality-score-meta">
                    <div class="quality-meta-item">
                        <span class="quality-meta-label">Completeness</span>
                        <span class="quality-meta-value" style="color: {'#34D399' if report.completeness >= 80 else '#FBBF24' if report.completeness >= 60 else '#F87171'}">{report.completeness:.0f}%</span>
                    </div>
                    <div class="quality-meta-item">
                        <span class="quality-meta-label">Consistency</span>
                        <span class="quality-meta-value" style="color: {'#34D399' if report.consistency >= 80 else '#FBBF24' if report.consistency >= 60 else '#F87171'}">{report.consistency:.0f}%</span>
                    </div>
                    <div class="quality-meta-item">
                        <span class="quality-meta-label">Coverage</span>
                        <span class="quality-meta-value" style="color: {'#34D399' if report.coverage >= 80 else '#FBBF24' if report.coverage >= 60 else '#F87171'}">{report.coverage:.0f}%</span>
                    </div>
                    <div class="quality-meta-item">
                        <span class="quality-meta-label">Validity</span>
                        <span class="quality-meta-value" style="color: {'#34D399' if getattr(report, 'validity', 100) >= 80 else '#FBBF24' if getattr(report, 'validity', 100) >= 60 else '#F87171'}">{getattr(report, 'validity', 100):.0f}%</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Dimension bars
    dimensions = [
        ("Completeness", report.completeness),
        ("Consistency", report.consistency),
        ("Validity", getattr(report, "validity", 100)),
        ("Anomaly", getattr(report, "anomaly_score", 100)),
        ("Coverage", report.coverage),
    ]
    
    dims_html = ""
    for label, score in dimensions:
        dim_bar_class = _get_bar_class(score)
        dims_html += f"""
        <div class="quality-dimension">
            <span class="quality-dim-label">{label}</span>
            <div class="quality-dim-bar-track">
                <div class="quality-dim-bar-fill {dim_bar_class}" style="width: {score}%"></div>
            </div>
            <span class="quality-dim-value">{score:.0f}%</span>
        </div>
        """
    
    st.markdown(
        f"""
        <div class="quality-dimensions">
            {dims_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Summary text
    if report.summary:
        st.caption(f"💡 {report.summary}")
    
    # Column-level details
    if report.column_details:
        with st.expander("📋 Column-Level Quality Details", expanded=False):
            for col in report.column_details[:15]:
                issues = "; ".join(col.issues) if col.issues else "No issues detected"
                completeness_bar_class = _get_bar_class(col.completeness)
                
                st.markdown(
                    f"""
                    <div style="
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        padding: 0.625rem 1rem;
                        background: rgba(255,255,255,0.04);
                        border: 1px solid rgba(255,255,255,0.07);
                        border-radius: 8px;
                        margin-bottom: 0.5rem;
                        font-size: 0.825rem;
                    ">
                        <div style="font-weight: 600; color: #F3F4F6; min-width: 150px;">
                            {col.name}
                        </div>
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <span style="color: #9CA3AF; font-size: 0.75rem;">Completeness</span>
                                <div style="width: 50px; height: 5px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                    <div style="width: {col.completeness}%; height: 100%; background: {'#34D399' if col.completeness >= 80 else '#FBBF24' if col.completeness >= 60 else '#F87171'}; border-radius: 3px;"></div>
                                </div>
                                <span style="font-weight: 600; color: #E5E7EB; width: 35px;">{col.completeness:.0f}%</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <span style="color: #9CA3AF; font-size: 0.75rem;">Consistency</span>
                                <div style="width: 50px; height: 5px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                    <div style="width: {col.consistency}%; height: 100%; background: {'#34D399' if col.consistency >= 80 else '#FBBF24' if col.consistency >= 60 else '#F87171'}; border-radius: 3px;"></div>
                                </div>
                                <span style="font-weight: 600; color: #E5E7EB; width: 35px;">{col.consistency:.0f}%</span>
                            </div>
                        </div>
                        <div style="max-width: 250px; color: #9CA3AF; font-size: 0.75rem; text-align: right;">
                            {issues}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
