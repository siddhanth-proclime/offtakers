import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="Carbon Credits Retirement Analysis", layout="wide")

st.title("Buyers Dashboard")
st.markdown("Carbon Credits Retirement Analysis - to be integrated")

# Read the CSV file
df = pd.read_csv('vcus.csv', low_memory=False)

# Data preprocessing
df['Retirement/Cancellation Date'] = pd.to_datetime(df['Retirement/Cancellation Date'], errors='coerce')
df['Retirement Year'] = df['Retirement/Cancellation Date'].dt.year

if not pd.api.types.is_numeric_dtype(df['Quantity Issued']):
    df['Quantity Issued'] = pd.to_numeric(df['Quantity Issued'], errors='coerce')

# Sidebar filters
st.sidebar.header("Filters")

# Year range slider
min_year = int(df['Retirement Year'].min()) if not df['Retirement Year'].isna().all() else 2020
max_year = int(df['Retirement Year'].max()) if not df['Retirement Year'].isna().all() else 2024

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(2020, max_year),
    step=1
)

# Project Type filter (multiselect)
project_types = sorted(df['Project Type'].dropna().unique().tolist())
selected_project_types = st.sidebar.multiselect(
    "Select Project Type(s)",
    options=project_types,
    default=[],
    help="Select one or more project types, or leave empty for 'All'"
)

# Methodology filter (multiselect)
methodologies = sorted(df['Methodology'].dropna().unique().tolist())
selected_methodologies = st.sidebar.multiselect(
    "Select Methodology/Methodologies",
    options=methodologies,
    default=[],
    help="Select one or more methodologies, or leave empty for 'All'"
)

# Country filter (multiselect)
countries = sorted(df['Country/Area'].dropna().unique().tolist())
selected_countries = st.sidebar.multiselect(
    "Select Country/Countries",
    options=countries,
    default=[],
    help="Country of the carbon project. Select one or more countries, or leave empty for 'All'"
)

# Apply filters
filtered_df = df[
    (df['Retirement Year'] >= year_range[0]) & 
    (df['Retirement Year'] <= year_range[1])
].copy()

if len(selected_project_types) > 0:
    filtered_df = filtered_df[filtered_df['Project Type'].isin(selected_project_types)]

if len(selected_methodologies) > 0:
    filtered_df = filtered_df[filtered_df['Methodology'].isin(selected_methodologies)]

if len(selected_countries) > 0:
    filtered_df = filtered_df[filtered_df['Country/Area'].isin(selected_countries)]

# Create pivot table
if len(filtered_df) > 0:
    pivot_table = filtered_df.pivot_table(
        index='Retirement Beneficiary',
        columns='Retirement Year',
        values='Quantity Issued',
        aggfunc='sum',
        fill_value=0
    )
    
    # Adjust column names and add Grand Total
    pivot_table.columns = [str(int(c)) for c in pivot_table.columns]
    pivot_table['Grand Total'] = pivot_table.sum(axis=1)
    pivot_table = pivot_table.sort_values('Grand Total', ascending=False)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Beneficiaries", len(pivot_table))
    with col2:
        st.metric("Total Credits Issued", f"{pivot_table['Grand Total'].sum():,.0f}")
    with col3:
        st.metric("Years Covered", len([c for c in pivot_table.columns if c != 'Grand Total']))
    
    # Display pivot table
    st.subheader("Retirement Beneficiaries Pivot Table")
    st.dataframe(pivot_table, width='stretch', height=400)
    
    # Top 5 Beneficiaries Trend Chart
    st.subheader("Top 5 Retirement Beneficiaries - Trend Analysis")
    
    top_5 = pivot_table.head(5)
    year_columns = [col for col in pivot_table.columns if col != 'Grand Total']
    
    # Create line chart using Plotly
    fig = go.Figure()

    # Convert year columns to string (categorical)
    year_columns = [str(int(c)) for c in pivot_table.columns if c != 'Grand Total']
    
    for beneficiary in top_5.index:
        fig.add_trace(go.Scatter(
            x=year_columns,
            y=top_5.loc[beneficiary, year_columns].values,
            mode='lines+markers',
            name=beneficiary,
            line=dict(width=2),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Quantity Issued",
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        height=500,
        margin=dict(r=200)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")
