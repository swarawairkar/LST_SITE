import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
import os
import ee
import json
from datetime import datetime

from utils.earth_engine import initialize_earth_engine, get_landsat_collection, get_district_boundary
from utils.data_processing import process_landsat_data, calculate_statistics, generate_sample_points, extract_point_values, analyze_temporal_changes, calculate_regression
from utils.visualization import create_map, create_spatial_heatmap, create_temporal_chart, create_regression_chart
from utils.data_loader import load_lst_data, load_ndvi_data, load_district_boundaries, load_temporal_data, load_comparison_data

st.set_page_config(
    page_title="Advanced Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Advanced Satellite Data Analysis")
st.write("Explore detailed analyses of Landsat satellite data, including time series, regression, and comparative studies.")

# Initialize Earth Engine
def init_ee():
    """Initialize Earth Engine and return authentication status."""
    try:
        ee_initialized = initialize_earth_engine()
        return ee_initialized
    except Exception as e:
        # Just log error without showing it to the user
        st.info("Authentication needed to access Earth Engine data.")
        return False

# Sidebar for analysis selection
with st.sidebar:
    st.header("Analysis Parameters")
    
    # Analysis type selection
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["Temporal Trends", "Spatial Patterns", "Regional Comparison"]
    )
    
    # Initialize Earth Engine
    ee_initialized = init_ee()
    if ee_initialized:
        st.success("Earth Engine initialized successfully")
    else:
        # Add a button to try authentication
        if st.button("Authenticate with Earth Engine", key="ee_auth_btn"):
            with st.spinner("Initializing Earth Engine..."):
                success = initialize_earth_engine()
                if success:
                    st.success("Earth Engine initialized successfully!")
                    st.rerun()
                else:
                    st.info("Authentication needed. Please try again.")
    
    # Common parameters
    variable_type = st.selectbox(
        "Variable",
        ["LST (Land Surface Temperature)", "NDVI (Vegetation Index)"]
    )
    
    # Simplify variable_type
    variable = "LST" if "LST" in variable_type else "NDVI"
    
    # Specific parameters based on analysis type
    if analysis_type == "Temporal Trends":
        st.subheader("Time Period Selection")
        years = st.multiselect(
            "Years",
            options=[2018, 2019, 2020, 2021, 2022, 2023, 2024],
            default=[2018, 2020, 2024]
        )
        
        months = st.multiselect(
            "Months",
            options=[(1, "January"), (4, "April"), (7, "July"), (10, "October")],
            default=[(4, "April")],
            format_func=lambda x: x[1]
        )
        
        # Extract month numbers
        month_numbers = [m[0] for m in months]
        
        district = st.selectbox(
            "District",
            ["Chennai", "Coimbatore", "Madurai", "Erode", "Ariyalur", "Cuddalore", "Dharmapuri", "Dindigul", "Tirunelveli"]
        )
        
        if variable == "LST":
            time_of_day = st.radio(
                "Time of Day",
                ["Daytime", "Nighttime"],
                horizontal=True
            )
        else:
            time_of_day = "Daytime"  # Not applicable for NDVI but kept for consistency
    
    elif analysis_type == "Spatial Patterns":
        st.subheader("Location and Time")
        
        year = st.selectbox("Year", options=[2018, 2019, 2020, 2021, 2022, 2023, 2024], index=6)
        
        month = st.selectbox(
            "Month",
            options=[(1, "January"), (2, "February"), (3, "March"), (4, "April"),
                     (5, "May"), (6, "June"), (7, "July"), (8, "August"),
                     (9, "September"), (10, "October"), (11, "November"), (12, "December")],
            index=3,
            format_func=lambda x: x[1]
        )[0]  # Extract month number
        
        district = st.selectbox(
            "Region",
            ["All", "Chennai", "Coimbatore", "Madurai", "Erode", "Ariyalur", "Cuddalore", "Dharmapuri", "Dindigul", "Tirunelveli"]
        )
        
        if variable == "LST":
            time_of_day = st.radio(
                "Time of Day",
                ["Daytime", "Nighttime"],
                horizontal=True
            )
        else:
            time_of_day = "Daytime"  # Not applicable for NDVI but kept for consistency
            

    else:  # Regional Comparison
        st.subheader("Compare Multiple Districts")
        
        year = st.selectbox("Year", options=[2018, 2019, 2020, 2021, 2022, 2023, 2024], index=6)
        
        month = st.selectbox(
            "Month",
            options=[(1, "January"), (2, "February"), (3, "March"), (4, "April"),
                     (5, "May"), (6, "June"), (7, "July"), (8, "August"),
                     (9, "September"), (10, "October"), (11, "November"), (12, "December")],
            index=3,
            format_func=lambda x: x[1]
        )[0]  # Extract month number
        
        districts = st.multiselect(
            "Districts",
            options=["Chennai", "Coimbatore", "Madurai", "Erode", "Ariyalur", "Cuddalore", "Dharmapuri", "Dindigul", "Tirunelveli"],
            default=["Chennai", "Coimbatore", "Madurai"]
        )
        
        if variable == "LST":
            time_of_day = st.radio(
                "Time of Day",
                ["Daytime", "Nighttime"],
                horizontal=True
            )
        else:
            time_of_day = "Daytime"  # Not applicable for NDVI but kept for consistency
    
    # Help text
    st.markdown("---")
    st.caption("Need help? Check the Help & FAQ page for guidance on using the analysis tools.")

# Main content based on selected analysis
if analysis_type == "Temporal Trends":
    st.header(f"Temporal Trends Analysis: {variable}")
    
    # Introduction text
    st.markdown(f"""
    This analysis shows how {variable} changes over time for {district}.
    Data is shown for the selected years ({', '.join(map(str, years))}) and months ({', '.join([datetime(2000, m, 1).strftime('%B') for m in month_numbers])}).
    """)
    
    # Temporal data processing
    if 'ee_initialized' in locals() and ee_initialized:
        # Process through Earth Engine
        try:
            # Prepare data structures for temporal analysis
            collections_data = []
            regions_data = [(district, get_district_boundary(district))]
            
            for year in years:
                for month in month_numbers:
                    collection = get_landsat_collection(year, month, time_of_day)
                    collections_data.append((collection, year, month))
            
            # Perform temporal analysis
            with st.spinner(f"Processing temporal {variable} data through Earth Engine..."):
                temporal_data = analyze_temporal_changes(collections_data, regions_data, variable_type=variable)
        except Exception as e:
            st.error(f"Error processing Earth Engine data: {str(e)}")
            temporal_data = None
    else:
        # Load sample data for demonstration
        with st.spinner(f"Loading sample temporal {variable} data for demonstration..."):
            temporal_data = load_temporal_data(district, years, month_numbers, time_of_day, variable_type=variable)
    
    # Display temporal chart
    st.subheader("Temporal Trend Chart")
    
    # Create two columns for the temporal analysis
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Temporal trend chart
        fig = create_temporal_chart(temporal_data, variable_type=variable, district=district)
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table (if data available)
        if temporal_data is not None and isinstance(temporal_data, pd.DataFrame) and not temporal_data.empty:
            st.subheader("Data Table")
            st.dataframe(temporal_data, use_container_width=True)
        
    with col2:
        # Regression analysis
        st.subheader("Regression Analysis")
        
        if temporal_data is not None and isinstance(temporal_data, pd.DataFrame) and not temporal_data.empty:
            # Check if we have enough data points for regression
            if len(temporal_data) >= 3:
                # Calculate regression
                slope, intercept, r_squared, p_value = calculate_regression(temporal_data)
                
                # Display regression statistics
                st.markdown(f"""
                **Trend Statistics:**
                
                - Slope: {slope:.4f} {("°C" if variable == "LST" else "")} per year
                - R² value: {r_squared:.4f}
                - p-value: {p_value:.4f}
                
                **Interpretation:**
                
                {("The temperature is " if variable == "LST" else "Vegetation is ")}
                {("increasing" if slope > 0 else "decreasing")} 
                at a rate of {abs(slope):.4f} {("°C" if variable == "LST" else "")} per year.
                
                This trend is statistically 
                {("significant" if p_value < 0.05 else "not significant")}.
                """)
            else:
                st.info("Not enough data points for regression analysis. Please select more time periods.")
        else:
            # Create a sample regression chart for demonstration
            fig = create_regression_chart(variable_type=variable, district=district)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("This is a sample visualization. To see actual regression analysis, please select more time periods and authenticate with Earth Engine.")
    
    # Additional insights
    st.subheader("Key Insights")
    
    if variable == "LST":
        st.markdown("""
        **Interpreting Temperature Trends:**
        
        - Rising temperatures may indicate urban development, deforestation, or climate change impacts
        - Seasonal variations show natural annual cycles
        - Sudden changes might indicate extreme weather events or land use changes
        - Compare with regional or global trends to contextualize local changes
        """)
    else:
        st.markdown("""
        **Interpreting Vegetation Trends:**
        
        - Decreasing NDVI may indicate deforestation, urbanization, or drought conditions
        - Increasing NDVI suggests reforestation, agricultural expansion, or recovery from disturbance
        - Seasonal patterns reflect natural vegetation cycles
        - Sudden changes might indicate fires, floods, or other disturbances
        """)

elif analysis_type == "Spatial Patterns":
    st.header(f"Spatial Patterns Analysis: {variable}")
    
    # Introduction text
    st.markdown(f"""
    This analysis shows how {variable} varies spatially across {district if district != "All" else "Tamil Nadu"}.
    Data is shown for {datetime(year, month, 1).strftime('%B %Y')}, {time_of_day if variable == "LST" else "using daytime imagery"}.
    """)
    
    # Spatial data processing
    if 'ee_initialized' in locals() and ee_initialized:
        # Process through Earth Engine
        try:
            # Get Landsat collection
            collection = get_landsat_collection(year, month, time_of_day)
            
            # Process the collection to get LST or NDVI layer
            with st.spinner(f"Processing {variable} data through Earth Engine..."):
                data_layer, region = process_landsat_data(collection, district, variable_type=variable)
                
                # Calculate statistics
                stats = calculate_statistics(data_layer, region)
                
                # Generate sample points for heatmap
                points = generate_sample_points(region, num_points=500)
                sample_data = extract_point_values(data_layer, points)
        except Exception as e:
            st.error(f"Error processing Earth Engine data: {str(e)}")
            data_layer, region, stats, sample_data = None, None, None, None
    else:
        # Load sample data for demonstration
        with st.spinner(f"Loading sample {variable} data for demonstration..."):
            if variable == "LST":
                data = load_lst_data(year, month, district if district != "All" else "Tamil Nadu", time_of_day)
            else:
                data = load_ndvi_data(year, month, district if district != "All" else "Tamil Nadu")
            
            if data:
                stats = data.get('stats', {})
                # For demonstration - in a real implementation, you would extract the layer and region
                data_layer, region = None, None
                sample_data = None
            else:
                stats, data_layer, region, sample_data = None, None, None, None
    
    # Create two columns for the spatial analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Map visualization
        st.subheader("Spatial Distribution Map")
        
        if data_layer is not None and region is not None:
            # Create map with Earth Engine layer
            m = create_map(data_layer, region)
            folium_static(m, width=700)
        else:
            # Create heatmap with sample data or demo data
            m = create_spatial_heatmap(variable, sample_data=sample_data)
            folium_static(m, width=700)
    
    with col2:
        # Statistics display
        st.subheader("Spatial Statistics")
        
        if stats:
            # Format for display
            if variable == "LST":
                st.metric("Mean Temperature", f"{stats.get('mean', 0):.2f} °C")
                
                # Create statistics cards
                cols = st.columns(2)
                with cols[0]:
                    st.metric("Minimum", f"{stats.get('min', 0):.2f} °C")
                with cols[1]:
                    st.metric("Maximum", f"{stats.get('max', 0):.2f} °C")
            else:
                st.metric("Mean NDVI", f"{stats.get('mean', 0):.3f}")
                
                # Create statistics cards
                cols = st.columns(2)
                with cols[0]:
                    st.metric("Minimum", f"{stats.get('min', 0):.3f}")
                with cols[1]:
                    st.metric("Maximum", f"{stats.get('max', 0):.3f}")
        else:
            # Sample statistics for demonstration
            if variable == "LST":
                st.metric("Mean Temperature", "33.5 °C")
                
                # Create statistics cards
                cols = st.columns(2)
                with cols[0]:
                    st.metric("Minimum", "28.2 °C")
                with cols[1]:
                    st.metric("Maximum", "39.8 °C")
            else:
                st.metric("Mean NDVI", "0.547")
                
                # Create statistics cards
                cols = st.columns(2)
                with cols[0]:
                    st.metric("Minimum", "0.124")
                with cols[1]:
                    st.metric("Maximum", "0.812")
            
            st.info("These are sample statistics. For actual data, please authenticate with Earth Engine.")
        
        # Interpretation guidance
        st.subheader("Interpretation")
        
        if variable == "LST":
            st.markdown("""
            **Land Surface Temperature Patterns:**
            
            - Urban areas typically show higher temperatures (urban heat islands)
            - Water bodies appear cooler
            - Vegetation areas are generally cooler than bare soil or built-up areas
            - Temperature gradients may indicate microclimatic variations
            """)
        else:
            st.markdown("""
            **Vegetation Index Patterns:**
            
            - Higher NDVI values (greener) indicate dense, healthy vegetation
            - Lower values suggest sparse vegetation, bare soil, or urban areas
            - Water bodies typically show negative NDVI values
            - Sharp transitions may indicate boundaries between land use types
            """)

else:  # Regional Comparison
    st.header(f"Regional Comparison Analysis: {variable}")
    
    # Introduction text
    st.markdown(f"""
    This analysis compares {variable} across multiple districts in Tamil Nadu.
    Data is shown for {datetime(year, month, 1).strftime('%B %Y')}, {time_of_day if variable == "LST" else "using daytime imagery"}.
    """)
    
    # Check if districts were selected
    if len(districts) < 1:
        st.warning("Please select at least one district for comparison.")
        st.stop()
    
    # Regional comparison data processing
    if 'ee_initialized' in locals() and ee_initialized:
        # Process through Earth Engine
        try:
            # Get Landsat collection
            collection = get_landsat_collection(year, month, time_of_day)
            
            # Process each district
            district_data = []
            
            with st.spinner(f"Processing {variable} data for multiple districts through Earth Engine..."):
                for district in districts:
                    # Process data for this district
                    data_layer, region = process_landsat_data(collection, district, variable_type=variable)
                    stats = calculate_statistics(data_layer, region)
                    
                    # Add to district data
                    district_data.append({
                        'district': district,
                        'mean': stats.get('mean', 0),
                        'min': stats.get('min', 0),
                        'max': stats.get('max', 0),
                        'stdDev': stats.get('stdDev', 0)
                    })
                
                # Convert to DataFrame
                comparison_df = pd.DataFrame(district_data)
                
        except Exception as e:
            st.error(f"Error processing Earth Engine data: {str(e)}")
            comparison_df = None
    else:
        # Load sample data for demonstration
        with st.spinner(f"Loading sample {variable} comparison data for demonstration..."):
            comparison_df = load_comparison_data(year, month, districts, time_of_day, variable_type=variable)
    
    # Display regional comparison
    if comparison_df is not None and not comparison_df.empty:
        # Create columns for different visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"{variable} by District")
            
            # Bar chart
            if variable == "LST":
                fig = px.bar(
                    comparison_df,
                    x='district',
                    y='mean',
                    error_y='stdDev',
                    labels={'district': 'District', 'mean': 'Mean Temperature (°C)'},
                    title=f'Mean Temperature by District',
                    color='mean',
                    color_continuous_scale='RdYlBu_r'
                )
            else:
                fig = px.bar(
                    comparison_df,
                    x='district',
                    y='mean',
                    error_y='stdDev',
                    labels={'district': 'District', 'mean': 'Mean NDVI'},
                    title=f'Mean NDVI by District',
                    color='mean',
                    color_continuous_scale='YlGn'
                )
            
            # Update layout
            fig.update_layout(
                height=450,
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Range Comparison")
            
            # Range plot (min to max)
            if variable == "LST":
                fig = go.Figure()
                
                # Add range lines
                for i, row in comparison_df.iterrows():
                    fig.add_trace(go.Scatter(
                        x=[row['district'], row['district']],
                        y=[row['min'], row['max']],
                        mode='lines',
                        line=dict(width=2, color='rgba(255, 87, 34, 0.5)'),
                        showlegend=False
                    ))
                
                # Add mean points
                fig.add_trace(go.Scatter(
                    x=comparison_df['district'],
                    y=comparison_df['mean'],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color='rgb(255, 87, 34)',
                        line=dict(width=1, color='black')
                    ),
                    name='Mean Temperature'
                ))
                
                # Update layout
                fig.update_layout(
                    title='Temperature Range by District',
                    xaxis_title='District',
                    yaxis_title='Temperature (°C)',
                    height=450,
                    template="plotly_white"
                )
            else:
                fig = go.Figure()
                
                # Add range lines
                for i, row in comparison_df.iterrows():
                    fig.add_trace(go.Scatter(
                        x=[row['district'], row['district']],
                        y=[row['min'], row['max']],
                        mode='lines',
                        line=dict(width=2, color='rgba(76, 175, 80, 0.5)'),
                        showlegend=False
                    ))
                
                # Add mean points
                fig.add_trace(go.Scatter(
                    x=comparison_df['district'],
                    y=comparison_df['mean'],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color='rgb(76, 175, 80)',
                        line=dict(width=1, color='black')
                    ),
                    name='Mean NDVI'
                ))
                
                # Update layout
                fig.update_layout(
                    title='NDVI Range by District',
                    xaxis_title='District',
                    yaxis_title='NDVI',
                    height=450,
                    template="plotly_white"
                )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("Comparison Data Table")
        
        # Format the table based on variable type
        if variable == "LST":
            display_df = comparison_df.copy()
            display_df['mean'] = display_df['mean'].map('{:.2f} °C'.format)
            display_df['min'] = display_df['min'].map('{:.2f} °C'.format)
            display_df['max'] = display_df['max'].map('{:.2f} °C'.format)
            display_df['stdDev'] = display_df['stdDev'].map('{:.2f} °C'.format)
            
            # Rename columns for display
            display_df.columns = ['District', 'Mean Temp', 'Min Temp', 'Max Temp', 'Std Dev']
        else:
            display_df = comparison_df.copy()
            display_df['mean'] = display_df['mean'].map('{:.3f}'.format)
            display_df['min'] = display_df['min'].map('{:.3f}'.format)
            display_df['max'] = display_df['max'].map('{:.3f}'.format)
            display_df['stdDev'] = display_df['stdDev'].map('{:.3f}'.format)
            
            # Rename columns for display
            display_df.columns = ['District', 'Mean NDVI', 'Min NDVI', 'Max NDVI', 'Std Dev']
        
        st.dataframe(display_df, use_container_width=True)
        
        # Rankings
        st.subheader("District Rankings")
        
        # Rank districts based on mean value
        if variable == "LST":
            # For LST, lower temperatures might be considered better (less heat stress)
            ranked_df = comparison_df.sort_values('mean')
            message = "Districts with lower average temperatures:"
        else:
            # For NDVI, higher values indicate more vegetation
            ranked_df = comparison_df.sort_values('mean', ascending=False)
            message = "Districts with higher vegetation coverage:"
        
        st.write(message)
        
        # Display top 3 or all if fewer
        for i, (_, row) in enumerate(ranked_df.iterrows()):
            if i < 3:
                if variable == "LST":
                    st.markdown(f"{i+1}. **{row['district']}**: {row['mean']:.2f} °C")
                else:
                    st.markdown(f"{i+1}. **{row['district']}**: {row['mean']:.3f}")
        
    else:
        # Create sample comparison for demonstration
        st.info("No comparison data available. Showing sample visualization.")
        
        # Sample district data
        sample_districts = districts if len(districts) > 0 else ["Chennai", "Coimbatore", "Madurai"]
        
        if variable == "LST":
            # Sample temperature data
            sample_data = {
                'district': sample_districts,
                'mean': [34.2, 30.5, 32.8],
                'min': [28.5, 25.2, 27.1],
                'max': [39.7, 36.1, 38.4],
                'stdDev': [2.3, 1.9, 2.1]
            }
        else:
            # Sample NDVI data
            sample_data = {
                'district': sample_districts,
                'mean': [0.35, 0.62, 0.48],
                'min': [0.12, 0.38, 0.25],
                'max': [0.58, 0.83, 0.71],
                'stdDev': [0.11, 0.09, 0.12]
            }
        
        # Create DataFrame
        sample_df = pd.DataFrame(sample_data)
        
        # Create columns for different visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"Sample {variable} by District")
            
            # Bar chart
            if variable == "LST":
                fig = px.bar(
                    sample_df,
                    x='district',
                    y='mean',
                    error_y='stdDev',
                    labels={'district': 'District', 'mean': 'Mean Temperature (°C)'},
                    title=f'Sample Mean Temperature by District',
                    color='mean',
                    color_continuous_scale='RdYlBu_r'
                )
            else:
                fig = px.bar(
                    sample_df,
                    x='district',
                    y='mean',
                    error_y='stdDev',
                    labels={'district': 'District', 'mean': 'Mean NDVI'},
                    title=f'Sample Mean NDVI by District',
                    color='mean',
                    color_continuous_scale='YlGn'
                )
            
            # Update layout
            fig.update_layout(
                height=450,
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Sample Range Comparison")
            
            # Range plot (min to max)
            if variable == "LST":
                fig = go.Figure()
                
                # Add range lines
                for i, row in sample_df.iterrows():
                    fig.add_trace(go.Scatter(
                        x=[row['district'], row['district']],
                        y=[row['min'], row['max']],
                        mode='lines',
                        line=dict(width=2, color='rgba(255, 87, 34, 0.5)'),
                        showlegend=False
                    ))
                
                # Add mean points
                fig.add_trace(go.Scatter(
                    x=sample_df['district'],
                    y=sample_df['mean'],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color='rgb(255, 87, 34)',
                        line=dict(width=1, color='black')
                    ),
                    name='Mean Temperature'
                ))
                
                # Update layout
                fig.update_layout(
                    title='Sample Temperature Range by District',
                    xaxis_title='District',
                    yaxis_title='Temperature (°C)',
                    height=450,
                    template="plotly_white"
                )
            else:
                fig = go.Figure()
                
                # Add range lines
                for i, row in sample_df.iterrows():
                    fig.add_trace(go.Scatter(
                        x=[row['district'], row['district']],
                        y=[row['min'], row['max']],
                        mode='lines',
                        line=dict(width=2, color='rgba(76, 175, 80, 0.5)'),
                        showlegend=False
                    ))
                
                # Add mean points
                fig.add_trace(go.Scatter(
                    x=sample_df['district'],
                    y=sample_df['mean'],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color='rgb(76, 175, 80)',
                        line=dict(width=1, color='black')
                    ),
                    name='Mean NDVI'
                ))
                
                # Update layout
                fig.update_layout(
                    title='Sample NDVI Range by District',
                    xaxis_title='District',
                    yaxis_title='NDVI',
                    height=450,
                    template="plotly_white"
                )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Note:** This is a sample visualization showing what the comparison would look like with actual data. 
        To see real comparisons, please authenticate with Earth Engine.
        """)

# Footer with additional resources
st.markdown("---")
st.markdown("""
### Additional Resources

- **Help & FAQ**: Visit the Help page for guidance on interpreting analysis results
- **About**: Learn more about this application and the data sources

""")

# Button to return to main dashboard
if st.button("Return to Main Dashboard"):
    st.switch_page("app.py")
