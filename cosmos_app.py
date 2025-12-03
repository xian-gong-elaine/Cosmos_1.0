import os

import pandas as pd
import pydeck as pdk
import plotly.express as px
import streamlit as st


# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Interactive Data Playground",
    layout="wide",
)

st.title("🧪 Interactive Data Playground")
st.caption("Explore your dataset with maps, charts and ridgeline-style time series.")


# ----------------- LOAD DATA -----------------
DATA_PATH = "~/Data/Cosmos_Dataset.parquet"  # <- change this if needed

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    return df

if not os.path.exists(DATA_PATH):
    st.error(
        f"CSV not found at `{DATA_PATH}`.\n\n"
        "Put your dataset there or update DATA_PATH in app.py."
    )
    st.stop()

df = load_data(DATA_PATH)

st.sidebar.success(f"Loaded dataset with shape: {df.shape[0]} rows × {df.shape[1]} columns")

with st.expander("Preview data", expanded=False):
    st.dataframe(df.head())


# ----------------- COLUMN TYPES -----------------
numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
non_numeric_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

# "Categorical" = non-numeric OR low-cardinality numeric
categorical_cols = non_numeric_cols.copy()
for col in numeric_cols:
    if df[col].nunique() < 30:
        categorical_cols.append(col)

# remove duplicates but keep order
seen = set()
categorical_cols = [c for c in categorical_cols if not (c in seen or seen.add(c))]


# ----------------- DYNAMIC GLOBAL FILTERS -----------------
st.sidebar.header("Global Filters")

# how many filters do we currently have?
if "n_filters" not in st.session_state:
    st.session_state["n_filters"] = 1  # start with one filter

# buttons to add / reset filters
btn_cols = st.sidebar.columns([1, 1])
with btn_cols[0]:
    if st.button("➕ Add"):
        st.session_state["n_filters"] += 1
with btn_cols[1]:
    if st.button("🔄 Reset"):
        st.session_state["n_filters"] = 1

filtered_df = df.copy()

all_cols = df.columns.tolist()

for i in range(st.session_state["n_filters"]):
    st.sidebar.markdown(f"---")
    st.sidebar.markdown(f"**Filter {i + 1}**")

    col_name = st.sidebar.selectbox(
        f"Column for filter {i + 1}",
        options=["(none)"] + all_cols,
        key=f"filter_col_{i}",
    )

    if col_name == "(none)":
        # skip if user hasn't chosen a column
        continue

    # decide if this column is numeric or not
    is_numeric = pd.api.types.is_numeric_dtype(df[col_name])

    if is_numeric:
        # numeric → range slider
        col_min = float(filtered_df[col_name].min())
        col_max = float(filtered_df[col_name].max())
        r_min, r_max = st.sidebar.slider(
            f"Range for `{col_name}`",
            col_min,
            col_max,
            (col_min, col_max),
            key=f"num_range_{i}",
        )
        filtered_df = filtered_df[filtered_df[col_name].between(r_min, r_max)]
    else:
        # categorical / text → multiselect of values
        vals = sorted(filtered_df[col_name].dropna().unique().tolist())
        selected_vals = st.sidebar.multiselect(
            f"Values for `{col_name}`",
            options=vals,
            default=vals,
            key=f"cat_vals_{i}",
        )
        if selected_vals:
            filtered_df = filtered_df[filtered_df[col_name].isin(selected_vals)]
        else:
            # if user deselects all values → filter everything out
            filtered_df = filtered_df.iloc[0:0]

st.write(f"**Rows after global filters:** {len(filtered_df)}")

if filtered_df.empty:
    st.warning("No data left after applying global filters. Adjust filters in the sidebar.")
    st.stop()

# ----------------- CHART TYPE SELECTION -----------------
st.sidebar.header("Chart Builder")

chart_type = st.sidebar.radio(
    "Choose chart type",
    # options=["Map", "Bar", "Line", "Pie", "Histogram", "Scatter", "Faceted Time Series"],
    options=["Bar", "Line", "Histogram", "Scatter"],
)


# ----------------- HELPER: SAFE COLUMN PICKERS -----------------
def pick_column(label, options, key, allow_none: bool = False):
    """
    Robust column picker that works when `options` is a list, Index, etc.
    """
    # Convert to a plain list so pandas Index doesn't break truth tests
    if options is None:
        options_list = []
    else:
        options_list = list(options)

    if len(options_list) == 0:
        st.sidebar.warning(f"No available columns for: {label}")
        return None

    if allow_none:
        options_list = ["(none)"] + options_list

    selected = st.sidebar.selectbox(label, options=options_list, key=key)

    if allow_none and selected == "(none)":
        return None
    return selected


# # ----------------- MAP (PYDECK) -----------------
# if chart_type == "Map":
#     st.subheader("🗺️ Map")

#     cols = filtered_df.columns.tolist()

#     lat_col = pick_column("Latitude column", cols, key="lat_col")
#     lon_col = pick_column("Longitude column", cols, key="lon_col")

#     if lat_col is None or lon_col is None:
#         st.info("Select latitude and longitude columns from the sidebar.")
#     else:
#         geo_df = filtered_df.copy()
#         geo_df = geo_df.dropna(subset=[lat_col, lon_col])
#         geo_df[lat_col] = pd.to_numeric(geo_df[lat_col], errors="coerce")
#         geo_df[lon_col] = pd.to_numeric(geo_df[lon_col], errors="coerce")
#         geo_df = geo_df.dropna(subset=[lat_col, lon_col])

#         if geo_df.empty:
#             st.warning("No valid rows after cleaning latitude/longitude.")
#         else:
#             tooltip_col = pick_column(
#                 "Tooltip column (shown on hover)",
#                 [c for c in geo_df.columns if c not in [lat_col, lon_col]],
#                 key="tooltip_map",
#                 allow_none=True,
#             )

#             mid_lat = geo_df[lat_col].mean()
#             mid_lon = geo_df[lon_col].mean()

#             view_state = pdk.ViewState(
#                 latitude=mid_lat,
#                 longitude=mid_lon,
#                 zoom=3.5,
#                 pitch=0,
#             )

#             layer = pdk.Layer(
#                 "ScatterplotLayer",
#                 data=geo_df,
#                 get_position=f"[{lon_col}, {lat_col}]",
#                 get_radius=200,
#                 get_fill_color="[200, 30, 0, 160]",
#                 pickable=True,
#             )

#             if tooltip_col:
#                 tooltip = {"text": f"{tooltip_col}: {{{tooltip_col}}}"}
#             else:
#                 tooltip = {"text": f"{lat_col}: {{{lat_col}}}\n{lon_col}: {{{lon_col}}}"}

#             deck = pdk.Deck(
#                 layers=[layer],
#                 initial_view_state=view_state,
#                 tooltip=tooltip,
#             )

#             st.pydeck_chart(deck)


# ----------------- BAR CHART -----------------
if chart_type == "Bar":
    st.subheader("📊 Bar Chart")

    x_col = pick_column("X (category)", categorical_cols, key="bar_x")
    y_col = pick_column("Y (numeric)", numeric_cols, key="bar_y")

    agg_func = st.sidebar.selectbox(
        "Aggregation",
        options=["count", "sum", "mean"],
        key="bar_agg",
    )

    if x_col and y_col:
        grouped = filtered_df.groupby(x_col)[y_col]
        if agg_func == "count":
            plot_df = grouped.count().reset_index(name="value")
        elif agg_func == "sum":
            plot_df = grouped.sum().reset_index(name="value")
        else:
            plot_df = grouped.mean().reset_index(name="value")

        fig = px.bar(
            plot_df,
            x=x_col,
            y="value",
            title=f"{agg_func.capitalize()} of {y_col} by {x_col}",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select both X (categorical) and Y (numeric) columns.")


# ----------------- LINE CHART -----------------
elif chart_type == "Line":
    st.subheader("📈 Line Chart")

    x_col = pick_column("X (typically time or numeric)", df.columns, key="line_x")
    y_col = pick_column("Y (numeric)", numeric_cols, key="line_y")

    if x_col and y_col:
        plot_df = filtered_df[[x_col, y_col]].dropna()

        try:
            plot_df[x_col] = pd.to_datetime(plot_df[x_col], errors="ignore")
        except Exception:
            pass

        fig = px.line(
            plot_df.sort_values(by=x_col),
            x=x_col,
            y=y_col,
            title=f"{y_col} over {x_col}",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select X and Y columns for the line chart.")


# # ----------------- PIE CHART -----------------
# elif chart_type == "Pie":
#     st.subheader("🥧 Pie Chart")

#     names_col = pick_column("Category (slice)", categorical_cols, key="pie_names")
#     values_col = pick_column(
#         "Values (numeric, optional)",
#         numeric_cols,
#         key="pie_values",
#         allow_none=True,
#     )

#     if names_col:
#         if values_col:
#             plot_df = filtered_df[[names_col, values_col]].dropna()
#             fig = px.pie(
#                 plot_df,
#                 names=names_col,
#                 values=values_col,
#                 title=f"Distribution of {values_col} by {names_col}",
#             )
#         else:
#             counts = (
#                 filtered_df[names_col]
#                 .value_counts(dropna=True)
#                 .reset_index()
#                 .rename(columns={"index": names_col, names_col: "count"})
#             )
#             fig = px.pie(
#                 counts,
#                 names=names_col,
#                 values="count",
#                 title=f"Count of {names_col}",
#             )
#         st.plotly_chart(fig, use_container_width=True)
#     else:
#         st.info("Choose a categorical column for the pie slices.")


# ----------------- HISTOGRAM -----------------
elif chart_type == "Histogram":
    st.subheader("📦 Histogram")

    col = pick_column("Numeric column", numeric_cols, key="hist_col")
    bins = st.sidebar.slider("Number of bins", 5, 100, 30, key="hist_bins")

    if col:
        fig = px.histogram(
            filtered_df,
            x=col,
            nbins=bins,
            title=f"Histogram of {col}",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select a numeric column for the histogram.")


# ----------------- SCATTER PLOT -----------------
elif chart_type == "Scatter":
    st.subheader("🔹 Scatter Plot")

    x_col = pick_column("X (numeric)", numeric_cols, key="scat_x")
    y_col = pick_column("Y (numeric)", numeric_cols, key="scat_y")
    color_col = pick_column(
        "Color by (categorical, optional)",
        categorical_cols,
        key="scat_color",
        allow_none=True,
    )

    if x_col and y_col:
        fig = px.scatter(
            filtered_df,
            x=x_col,
            y=y_col,
            color=color_col if color_col else None,
            title=f"{y_col} vs {x_col}",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select X and Y numeric columns for the scatter plot.")


# # ----------------- FACETED TIME SERIES (RIDGELINE-LIKE) -----------------
# elif chart_type == "Faceted Time Series":
#     st.subheader("⛰️ Faceted Time Series (ridgeline style)")

#     # Choose columns
#     entity_col = pick_column("Entity column (e.g., technology)", categorical_cols, key="ridge_entity")
#     time_col = pick_column("Time column", df.columns, key="ridge_time")
#     value_col = pick_column("Value column (numeric)", numeric_cols, key="ridge_value")
#     color_col = pick_column(
#         "Color by (theme/category, optional)",
#         categorical_cols,
#         key="ridge_color",
#         allow_none=True,
#     )

#     if entity_col and time_col and value_col:
#         plot_df = filtered_df[[entity_col, time_col, value_col] + ([color_col] if color_col else [])].dropna()

#         # Parse time
#         try:
#             plot_df[time_col] = pd.to_datetime(plot_df[time_col], errors="coerce")
#         except Exception:
#             pass
#         plot_df = plot_df.dropna(subset=[time_col])

#         # Let user choose which entities to show (to avoid 100+ strips)

#         # plot_df[entity_col] should normally be a Series, but if it is a
#         # DataFrame (e.g. because entity_col was somehow list-like), handle it.
#         col_data = plot_df[entity_col]

#         if isinstance(col_data, pd.DataFrame):
#             # flatten all values from all columns
#             unique_vals = pd.unique(col_data.values.ravel())
#         else:
#             unique_vals = col_data.dropna().unique()

#         all_entities = sorted([v for v in unique_vals if pd.notna(v)])

#         default_n = min(15, len(all_entities))  # default: first 15 entities
#         default_entities = all_entities[:default_n]


#         selected_entities = st.sidebar.multiselect(
#             "Entities to show (rows of strips)",
#             options=all_entities,
#             default=default_entities,
#             key="ridge_entities",
#         )

#         if not selected_entities:
#             st.info("Select at least one entity to display.")
#         else:
#             plot_df = plot_df[plot_df[entity_col].isin(selected_entities)]

#             # Order entities for nicer stacking (reverse so first is at top)
#             entity_order = list(reversed(selected_entities))

#             height = 120 * len(selected_entities)  # control overall figure height

#             fig = px.area(
#                 plot_df.sort_values(by=[entity_col, time_col]),
#                 x=time_col,
#                 y=value_col,
#                 facet_row=entity_col,
#                 color=color_col if color_col else None,
#                 category_orders={entity_col: entity_order},
#                 height=height,
#             )

#             # Make it look more like ridgeline strips
#             fig.update_yaxes(matches=None, showticklabels=False, title=None)
#             fig.update_xaxes(showgrid=False)
#             fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

#             fig.update_layout(
#                 showlegend=True if color_col else False,
#                 hovermode="x unified",
#                 margin=dict(l=60, r=20, t=40, b=40),
#             )

#             st.plotly_chart(fig, use_container_width=True)
#     else:
#         st.info("Select entity, time and value columns for the faceted time series.")


# ----------------- DOWNLOAD FILTERED DATA -----------------
st.subheader("💾 Download filtered data")
csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download current filtered dataset as CSV",
    data=csv_bytes,
    file_name="filtered_data.csv",
    mime="text/csv",
)
