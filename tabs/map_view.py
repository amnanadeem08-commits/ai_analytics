"""
tabs/map_view.py — Geographic map analysis (choropleth, bubble, heatmap).

Auto-detects location columns and visualizes a selected numeric metric on a map.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

GEO_COLUMN_HINTS = {
    "country": ["country", "country_name", "nation"],
    "city": ["city", "city_name", "town", "location"],
    "region": ["region", "state", "province", "zone", "area", "district"],
    "latitude": ["lat", "latitude"],
    "longitude": ["lon", "lng", "longitude"],
}

# Top world cities → (lat, lon) for bubble maps when only city names are present.
CITY_COORDS: dict[str, tuple[float, float]] = {
    "karachi": (24.86, 67.01),
    "lahore": (31.55, 74.35),
    "islamabad": (33.69, 73.04),
    "mumbai": (19.08, 72.88),
    "delhi": (28.61, 77.21),
    "bangalore": (12.97, 77.59),
    "london": (51.51, -0.13),
    "paris": (48.86, 2.35),
    "berlin": (52.52, 13.41),
    "madrid": (40.42, -3.70),
    "rome": (41.90, 12.50),
    "new york": (40.71, -74.01),
    "los angeles": (34.05, -118.24),
    "chicago": (41.88, -87.63),
    "houston": (29.76, -95.37),
    "toronto": (43.65, -79.38),
    "mexico city": (19.43, -99.13),
    "sao paulo": (-23.55, -46.63),
    "buenos aires": (-34.60, -58.38),
    "dubai": (25.20, 55.27),
    "riyadh": (24.71, 46.67),
    "jeddah": (21.54, 39.17),
    "cairo": (30.04, 31.24),
    "lagos": (6.52, 3.38),
    "nairobi": (-1.29, 36.82),
    "johannesburg": (-26.20, 28.04),
    "moscow": (55.76, 37.62),
    "istanbul": (41.01, 28.98),
    "tokyo": (35.68, 139.69),
    "osaka": (34.69, 135.50),
    "seoul": (37.57, 126.98),
    "beijing": (39.90, 116.41),
    "shanghai": (31.23, 121.47),
    "hong kong": (22.32, 114.17),
    "singapore": (1.35, 103.82),
    "bangkok": (13.76, 100.50),
    "jakarta": (-6.21, 106.85),
    "manila": (14.60, 120.98),
    "sydney": (-33.87, 151.21),
    "melbourne": (-37.81, 144.96),
    "france": (46.23, 2.21),  # country centroid fallback
    "germany": (51.17, 10.45),
    "spain": (40.46, -3.75),
    "usa": (37.09, -95.71),
    "united states": (37.09, -95.71),
    "united kingdom": (55.38, -3.44),
    "china": (35.86, 104.20),
    "india": (20.59, 78.96),
    "pakistan": (30.38, 69.35),
    "canada": (56.13, -106.35),
    "australia": (-25.27, 133.78),
    "brazil": (-14.24, -51.93),
    "japan": (36.20, 138.25),
    "uae": (23.42, 53.85),
}

_CHOROPLETH_SCALE = [
    [0, "rgba(108,99,255,0.1)"],
    [0.5, "rgba(108,99,255,0.6)"],
    [1, "#6C63FF"],
]

_GEO_LAYOUT = dict(
    bgcolor="rgba(0,0,0,0)",
    lakecolor="rgba(0,0,0,0)",
    landcolor="#1A1D2E",
    showland=True,
    showlakes=True,
    coastlinecolor="rgba(255,255,255,0.1)",
    countrycolor="rgba(255,255,255,0.08)",
    showframe=False,
)


def detect_geo_columns(df: pd.DataFrame) -> dict[str, str]:
    """Map geo types (country, city, …) to actual column names in df."""
    found: dict[str, str] = {}
    for geo_type, hints in GEO_COLUMN_HINTS.items():
        for col in df.columns:
            if col.lower().strip() in hints:
                found[geo_type] = col
                break
    return found


def _resolve_city_coords(df: pd.DataFrame, city_col: str) -> pd.DataFrame:
    """Attach _map_lat / _map_lon from CITY_COORDS lookup."""
    work = df.copy()
    lats, lons = [], []
    for raw in work[city_col].astype(str):
        key = raw.strip().lower()
        coords = CITY_COORDS.get(key)
        if coords:
            lats.append(coords[0])
            lons.append(coords[1])
        else:
            lats.append(None)
            lons.append(None)
    work["_map_lat"] = lats
    work["_map_lon"] = lons
    return work.dropna(subset=["_map_lat", "_map_lon"])


def _base_layout(fig, *, height: int = 480, show_colorbar: bool = True) -> None:
    layout_kwargs: dict = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=30, b=0),
        font=dict(color="#E8E8F0"),
        height=height,
    )
    if hasattr(fig, "update_geos"):
        fig.update_geos(**_GEO_LAYOUT)
    fig.update_layout(**layout_kwargs)
    if show_colorbar and fig.layout.coloraxis.colorbar:
        fig.update_layout(
            coloraxis_colorbar=dict(
                bgcolor="rgba(0,0,0,0)",
                tickfont=dict(color="#9CA3AF"),
                thickness=12,
            )
        )


def _render_choropleth(map_df: pd.DataFrame, loc_col: str, metric_col: str, scope: str) -> None:
    fig = px.choropleth(
        map_df,
        locations=loc_col,
        locationmode="country names",
        color=metric_col,
        color_continuous_scale=_CHOROPLETH_SCALE,
        hover_name=loc_col,
        hover_data={metric_col: ":,.0f"},
    )
    fig.update_layout(
        geo=dict(scope=scope, **_GEO_LAYOUT),
        coloraxis_colorbar=dict(
            bgcolor="rgba(0,0,0,0)",
            tickfont=dict(color="#9CA3AF"),
            title=dict(font=dict(color="#9CA3AF"), text=metric_col),
            thickness=12,
        ),
    )
    _base_layout(fig, show_colorbar=False)
    st.plotly_chart(fig, use_container_width=True)


def _render_bubble(
    df: pd.DataFrame,
    geo_cols: dict[str, str],
    metric_col: str,
    label_col: str,
) -> None:
    lat_col = geo_cols.get("latitude")
    lon_col = geo_cols.get("longitude")

    if lat_col and lon_col:
        plot_df = df[[lat_col, lon_col, metric_col]].dropna()
        if plot_df.empty:
            st.warning("No rows with valid latitude/longitude values.")
            return
        fig = px.scatter_geo(
            plot_df,
            lat=lat_col,
            lon=lon_col,
            size=metric_col,
            color=metric_col,
            hover_name=label_col if label_col in df.columns else None,
            color_continuous_scale=["#1A1D2E", "#6C63FF", "#00D9A3"],
            size_max=40,
            projection="natural earth",
        )
    elif "city" in geo_cols:
        city_col = geo_cols["city"]
        plot_df = _resolve_city_coords(df, city_col)
        if plot_df.empty:
            st.warning(
                "City names were not found in the built-in coordinates lookup. "
                "Add lat/lon columns or use known city names (e.g. Karachi, Lahore, London)."
            )
            return
        st.caption(f"Showing {len(plot_df):,} rows with matched city coordinates.")
        fig = px.scatter_geo(
            plot_df,
            lat="_map_lat",
            lon="_map_lon",
            size=metric_col,
            color=metric_col,
            hover_name=city_col,
            color_continuous_scale=["#1A1D2E", "#6C63FF", "#00D9A3"],
            size_max=40,
            projection="natural earth",
        )
    else:
        st.warning("Bubble map requires latitude/longitude columns or a city column.")
        return

    _base_layout(fig)
    st.plotly_chart(fig, use_container_width=True)


def _render_heatmap(
    df: pd.DataFrame,
    geo_cols: dict[str, str],
    metric_col: str,
    map_df: pd.DataFrame,
    loc_col: str | None,
) -> None:
    lat_col = geo_cols.get("latitude")
    lon_col = geo_cols.get("longitude")

    if lat_col and lon_col:
        work = df[[lat_col, lon_col, metric_col]].dropna().copy()
        if work.empty:
            st.warning("No rows with valid coordinates for heatmap.")
            return
        work["lat_bin"] = work[lat_col].astype(float).round(1)
        work["lon_bin"] = work[lon_col].astype(float).round(1)
        agg = work.groupby(["lat_bin", "lon_bin"], as_index=False)[metric_col].sum()
        fig = px.scatter_geo(
            agg,
            lat="lat_bin",
            lon="lon_bin",
            size=metric_col,
            color=metric_col,
            color_continuous_scale=["#1A1D2E", "#FFB547", "#FF6B6B"],
            size_max=55,
            projection="natural earth",
            opacity=0.85,
        )
        _base_layout(fig)
        st.plotly_chart(fig, use_container_width=True)
        return

    if loc_col and not map_df.empty:
        fig = px.choropleth(
            map_df,
            locations=loc_col,
            locationmode="country names",
            color=metric_col,
            color_continuous_scale=["#1A1D2E", "#FFB547", "#FF6B6B"],
            hover_name=loc_col,
            hover_data={metric_col: ":,.0f"},
        )
        scope = "world" if "country" in geo_cols else "asia"
        fig.update_layout(geo=dict(scope=scope, **_GEO_LAYOUT))
        _base_layout(fig, show_colorbar=False)
        st.plotly_chart(fig, use_container_width=True)
        return

    st.warning("Heatmap requires lat/lon columns or a country/region column.")


def render(df: pd.DataFrame, domain_cfg, kpis) -> None:
    """Entry point — geographic map analysis tab."""
    st.markdown("### 🗺️ Map Analysis")
    st.caption(
        f"Geographic breakdown of your data · Domain: **{getattr(domain_cfg, 'label', 'General')}**"
    )

    if df is None or df.empty:
        st.info("Upload a dataset with location columns to use map analysis.")
        return

    geo_cols = detect_geo_columns(df)
    if not geo_cols:
        st.info(
            "No location columns detected. Add a column named 'country', 'city', "
            "'region', 'lat', or 'lon' to enable map view."
        )
        return

    detected = ", ".join(f"**{k}** → `{v}`" for k, v in geo_cols.items())
    st.caption(f"Detected: {detected}")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        st.warning("No numeric columns found to visualize on the map.")
        return

    metric_col = st.selectbox("Metric to map", numeric_cols, key="map_metric")
    map_type = st.radio("Map type", ["Choropleth", "Bubble Map", "Heatmap"], horizontal=True)

    loc_col = geo_cols.get("country") or geo_cols.get("region")
    map_df = pd.DataFrame()
    if loc_col:
        map_df = df.groupby(loc_col, observed=True)[metric_col].sum().reset_index()

    # ── Render selected map type ─────────────────────────────────────────────
    if map_type == "Choropleth":
        if loc_col and not map_df.empty:
            scope = "world" if "country" in geo_cols else "asia"
            if "country" not in geo_cols and "region" in geo_cols:
                scope = st.selectbox(
                    "Map scope",
                    ["asia", "europe", "africa", "north america", "south america", "world"],
                    index=0,
                    key="map_choro_scope",
                )
            _render_choropleth(map_df, loc_col, metric_col, scope)
        else:
            st.warning("Choropleth requires a **country** or **region** column.")

    elif map_type == "Bubble Map":
        label_col = (
            geo_cols.get("city")
            or geo_cols.get("region")
            or geo_cols.get("country")
            or df.columns[0]
        )
        _render_bubble(df, geo_cols, metric_col, label_col)
        if loc_col and map_df.empty:
            map_df = df.groupby(label_col, observed=True)[metric_col].sum().reset_index()
            loc_col = label_col

    else:  # Heatmap
        _render_heatmap(df, geo_cols, metric_col, map_df, loc_col)

    # ── Summary table ────────────────────────────────────────────────────────
    if map_df.empty and loc_col:
        map_df = df.groupby(loc_col, observed=True)[metric_col].sum().reset_index()

    if map_df.empty:
        label_col = geo_cols.get("city") or geo_cols.get("region")
        if label_col:
            map_df = df.groupby(label_col, observed=True)[metric_col].sum().reset_index()
            loc_col = label_col

    if not map_df.empty:
        st.markdown("#### Ranked locations")
        map_df_sorted = map_df.sort_values(metric_col, ascending=False).reset_index(drop=True)
        map_df_sorted.index += 1
        max_val = float(map_df[metric_col].max()) or 1.0
        st.dataframe(
            map_df_sorted,
            use_container_width=True,
            column_config={
                metric_col: st.column_config.ProgressColumn(
                    metric_col,
                    min_value=0,
                    max_value=max_val,
                )
            },
        )
