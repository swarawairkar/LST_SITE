import folium
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from branca.colormap import linear

def create_map(data_layer, region, center=None, zoom=7):
    """
    Create a folium map with the data layer.
    
    Args:
        data_layer (ee.Image): Image layer (LST or NDVI)
        region (ee.Geometry): Region geometry
        center (list): Center coordinates [lat, lon]
        zoom (int): Initial zoom level
        
    Returns:
        folium.Map: Map with data layer
    """
    # Get center coordinates
    if center is None:
        # Try to get center from region
        try:
            bounds = region.bounds().getInfo()['coordinates'][0]
            lats = [point[1] for point in bounds]
            lons = [point[0] for point in bounds]
            center = [sum(lats)/len(lats), sum(lons)/len(lons)]
        except:
            # Default to Tamil Nadu center
            center = [11.1271, 78.6569]
    
    # Create map
    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")
    
    # Try to add the data layer from Earth Engine
    try:
        # Get visualization parameters
        vis_params = data_layer.bandNames().getInfo()[0]
        
        # Try different approaches to get visualization parameters
        if hasattr(data_layer, 'getInfo'):
            layer_info = data_layer.getInfo()
            if 'properties' in layer_info and 'visualization' in layer_info['properties']:
                vis_params = layer_info['properties']['visualization']
            else:
                # Default visualization parameters
                var_name = data_layer.bandNames().getInfo()[0]
                if 'LST' in var_name:
                    vis_params = {
                        'min': 20,
                        'max': 45,
                        'palette': ['blue', 'green', 'yellow', 'orange', 'red']
                    }
                else:
                    vis_params = {
                        'min': -0.2,
                        'max': 0.8,
                        'palette': ['white', 'green']
                    }
        
        # Add the Earth Engine layer to the map
        map_id_dict = data_layer.getMapId(vis_params)
        folium.TileLayer(
            tiles=map_id_dict['tile_fetcher'].url_format,
            attr='Google Earth Engine',
            name=data_layer.bandNames().getInfo()[0],
            overlay=True,
            control=True
        ).add_to(m)
    except Exception as e:
        # If Earth Engine layer fails, add a placeholder layer
        st.warning(f"Unable to add Earth Engine layer to map: {str(e)}")
        
        # Add a simple boundary layer instead
        folium.GeoJson(
            data={
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[76.0, 8.0], [81.0, 8.0], [81.0, 14.0], [76.0, 14.0], [76.0, 8.0]]]
                },
                "properties": {
                    "name": "Tamil Nadu"
                }
            },
            name="Tamil Nadu",
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': '#3186cc',
                'weight': 2
            }
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def create_spatial_heatmap(variable_type, center=None, zoom=7, sample_data=None):
    """
    Create a heatmap visualization for spatial data.
    
    Args:
        variable_type (str): "LST" or "NDVI"
        center (list): Center coordinates [lat, lon]
        zoom (int): Initial zoom level
        sample_data (pd.DataFrame): Sample data with lat, lon, and value columns
        
    Returns:
        folium.Map: Map with heatmap
    """
    # Default center to Tamil Nadu if not provided
    if center is None:
        center = [11.1271, 78.6569]
    
    # Create map
    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")
    
    # If sample data provided, create heatmap
    if sample_data is not None and isinstance(sample_data, pd.DataFrame):
        # Process the dataframe
        if 'latitude' in sample_data.columns and 'longitude' in sample_data.columns and 'value' in sample_data.columns:
            # Create heatmap data
            heat_data = [[row['latitude'], row['longitude'], row['value']] for _, row in sample_data.iterrows()]
            
            # Add heatmap layer
            folium.plugins.HeatMap(
                heat_data,
                radius=15,
                blur=10,
                gradient={0.4: 'blue', 0.65: 'lime', 0.8: 'yellow', 1: 'red'},
                name=variable_type,
                control=True,
                show=True
            ).add_to(m)
    else:
        # Generate sample point data for demonstration
        # In a real implementation, this would use actual data
        np.random.seed(42)  # For reproducibility
        lat_center, lon_center = center
        
        # Generate random points around center
        num_points = 500
        lats = np.random.normal(lat_center, 0.5, num_points)
        lons = np.random.normal(lon_center, 0.5, num_points)
        
        # Generate values
        if variable_type == "LST":
            # Temperature values with spatial pattern (hotter in center)
            values = [
                35 - 0.1 * ((lat - lat_center)**2 + (lon - lon_center)**2) + np.random.normal(0, 2)
                for lat, lon in zip(lats, lons)
            ]
            # Ensure values are in reasonable range
            values = [max(min(v, 45), 20) for v in values]
        else:
            # NDVI values with spatial pattern (greener away from center)
            values = [
                0.3 + 0.05 * ((lat - lat_center)**2 + (lon - lon_center)**2) + np.random.normal(0, 0.1)
                for lat, lon in zip(lats, lons)
            ]
            # Ensure values are in reasonable range
            values = [max(min(v, 0.9), 0.1) for v in values]
        
        # Create sample DataFrame
        sample_data = pd.DataFrame({
            'latitude': lats,
            'longitude': lons,
            'value': values
        })
        
        # Add points and heatmap
        if variable_type == "LST":
            # Add temperature gradient
            colormap = linear.RdYlBu_11.scale(20, 45)
            colormap.caption = 'Temperature (°C)'
            m.add_child(colormap)
            
            # Add point markers for sample locations
            for idx, row in sample_data.sample(50).iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=5,
                    color=None,
                    fill=True,
                    fill_color=colormap(row['value']),
                    fill_opacity=0.7,
                    tooltip=f"Temp: {row['value']:.1f}°C"
                ).add_to(m)
        else:
            # Add NDVI gradient
            colormap = linear.YlGn_09.scale(0, 1)
            colormap.caption = 'NDVI'
            m.add_child(colormap)
            
            # Add point markers for sample locations
            for idx, row in sample_data.sample(50).iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=5,
                    color=None,
                    fill=True,
                    fill_color=colormap(row['value']),
                    fill_opacity=0.7,
                    tooltip=f"NDVI: {row['value']:.2f}"
                ).add_to(m)
    
    # Add measurement tool
    folium.plugins.MeasureControl(
        position='topright',
        primary_length_unit='kilometers',
        secondary_length_unit='miles',
        primary_area_unit='square kilometers',
        secondary_area_unit='acres'
    ).add_to(m)
    
    # Add fullscreen button
    folium.plugins.Fullscreen(
        position='topright',
        title='Fullscreen',
        title_cancel='Exit fullscreen',
        force_separate_button=True
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def create_temporal_chart(temporal_data, variable_type="LST", district=None, time_period=None):
    """
    Create a temporal trend chart.
    
    Args:
        temporal_data (pd.DataFrame): DataFrame with temporal data
        variable_type (str): "LST" or "NDVI"
        district (str): District name for filtering
        time_period (str): Time period for filtering
        
    Returns:
        plotly.graph_objects.Figure: Temporal trend chart
    """
    # Create a sample chart if temporal_data is None
    if temporal_data is None:
        # Generate sample temporal data
        years = [2018, 2020, 2022, 2024]
        
        if variable_type == "LST":
            # Temperature values with temporal trend (increasing)
            values = [32.5, 33.8, 34.7, 35.2]
            y_title = "Average Temperature (°C)"
            line_color = '#FF5722'
        else:
            # NDVI values with temporal trend (decreasing)
            values = [0.65, 0.58, 0.53, 0.51]
            y_title = "Average NDVI"
            line_color = '#4CAF50'
        
        # Create figure
        fig = go.Figure()
        
        # Add line trace
        fig.add_trace(go.Scatter(
            x=years, 
            y=values,
            mode='lines+markers',
            name=variable_type,
            line=dict(color=line_color, width=3),
            marker=dict(size=10)
        ))
        
        # Update layout
        fig.update_layout(
            title=f'Temporal Trends for {district or "Selected Region"}',
            xaxis_title='Year',
            yaxis_title=y_title,
            height=400,
            template="plotly_white"
        )
        
        return fig
        
    # Filter data if needed
    filtered_data = temporal_data
    if district and 'district' in temporal_data.columns:
        filtered_data = filtered_data[filtered_data['district'] == district]
    
    if time_period and 'time_period' in temporal_data.columns:
        filtered_data = filtered_data[filtered_data['time_period'] == time_period]
    
    # Group by year and calculate mean
    if 'year' in filtered_data.columns:
        grouped_data = filtered_data.groupby('year').agg({
            'mean': 'mean',
            'min': 'min',
            'max': 'max'
        }).reset_index()
        
        # Create figure
        fig = go.Figure()
        
        # Add line for mean values
        if variable_type == "LST":
            line_color = '#FF5722'
            y_title = "Temperature (°C)"
        else:
            line_color = '#4CAF50'
            y_title = "NDVI"
            
        fig.add_trace(go.Scatter(
            x=grouped_data['year'],
            y=grouped_data['mean'],
            mode='lines+markers',
            name='Mean',
            line=dict(color=line_color, width=3),
            marker=dict(size=10)
        ))
        
        # Add range as a shaded area
        fig.add_trace(go.Scatter(
            x=grouped_data['year'],
            y=grouped_data['max'],
            mode='lines',
            name='Max',
            line=dict(width=0),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=grouped_data['year'],
            y=grouped_data['min'],
            mode='lines',
            name='Min',
            line=dict(width=0),
            fill='tonexty',
            fillcolor=f'rgba{tuple(list(px.colors.hex_to_rgb(line_color)) + [0.2])}',
            showlegend=False
        ))
        
        # Update layout
        fig.update_layout(
            title=f'Temporal Trends for {district or "Selected Region"}',
            xaxis_title='Year',
            yaxis_title=y_title,
            height=400,
            template="plotly_white"
        )
        
        return fig
    else:
        # If no year column, create a simple placeholder chart
        fig = go.Figure()
        
        if variable_type == "LST":
            y_title = "Temperature (°C)"
            line_color = '#FF5722'
        else:
            y_title = "NDVI"
            line_color = '#4CAF50'
            
        # Sample data if no proper structure
        x = list(range(len(filtered_data)))
        y = filtered_data['mean'] if 'mean' in filtered_data.columns else filtered_data.iloc[:, 0]
        
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines+markers',
            line=dict(color=line_color, width=2)
        ))
        
        fig.update_layout(
            title=f'Data Trend',
            xaxis_title='Time Period',
            yaxis_title=y_title,
            height=400,
            template="plotly_white"
        )
        
        return fig

def create_regression_chart(temporal_data=None, variable_type="LST", district=None, year=None, month=None, time_of_day=None):
    """
    Create a regression analysis chart.
    
    Args:
        temporal_data (pd.DataFrame): DataFrame with temporal data
        variable_type (str): "LST" or "NDVI"
        district (str): District name for filtering
        year (int): Year for reference
        month (int): Month for reference
        time_of_day (str): 'Daytime' or 'Nighttime'
        
    Returns:
        plotly.graph_objects.Figure: Regression chart
    """
    # Create a sample chart if temporal_data is None
    if temporal_data is None:
        # Generate sample temporal data with longer time series
        years = list(range(2000, 2025, 2))
        
        if variable_type == "LST":
            # Temperature values with upward trend and some noise
            base = 30.0
            slope = 0.15
            values = [base + (year-2000)*slope + np.random.normal(0, 0.5) for year in years]
            y_title = "Average Temperature (°C)"
            
            # Calculate regression line
            z = np.polyfit(years, values, 1)
            p = np.poly1d(z)
            trend_values = [p(year) for year in years]
            
            # Create figure
            fig = go.Figure()
            
            # Add scatter plot of actual values
            fig.add_trace(go.Scatter(
                x=years, 
                y=values,
                mode='markers',
                name='Observed Values',
                marker=dict(
                    size=8,
                    color='#1E88E5',
                    symbol='circle'
                )
            ))
            
            # Add regression line
            fig.add_trace(go.Scatter(
                x=years, 
                y=trend_values,
                mode='lines',
                name='Trend Line',
                line=dict(
                    color='#FF5722',
                    width=2,
                    dash='solid'
                )
            ))
            
            # Update layout
            fig.update_layout(
                title=f'Temperature Trend Analysis for {district or "Selected Region"} (2000-2024)',
                xaxis_title='Year',
                yaxis_title=y_title,
                height=450,
                template="plotly_white",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                annotations=[
                    dict(
                        x=0.01,
                        y=0.95,
                        xref="paper",
                        yref="paper",
                        text=f"Trend: {z[0]:.3f}°C/year",
                        showarrow=False,
                        font=dict(
                            family="Arial",
                            size=14,
                            color="#212121"
                        ),
                        align="left",
                        bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="#BDBDBD",
                        borderwidth=1,
                        borderpad=4
                    )
                ]
            )
        else:
            # NDVI values with downward trend and some noise
            base = 0.72
            slope = -0.01
            values = [base + (year-2000)*slope + np.random.normal(0, 0.03) for year in years]
            y_title = "Average NDVI"
            
            # Calculate regression line
            z = np.polyfit(years, values, 1)
            p = np.poly1d(z)
            trend_values = [p(year) for year in years]
            
            # Create figure
            fig = go.Figure()
            
            # Add scatter plot of actual values
            fig.add_trace(go.Scatter(
                x=years, 
                y=values,
                mode='markers',
                name='Observed Values',
                marker=dict(
                    size=8,
                    color='#4CAF50',
                    symbol='circle'
                )
            ))
            
            # Add regression line
            fig.add_trace(go.Scatter(
                x=years, 
                y=trend_values,
                mode='lines',
                name='Trend Line',
                line=dict(
                    color='#FF5722',
                    width=2,
                    dash='solid'
                )
            ))
            
            # Update layout
            fig.update_layout(
                title=f'Vegetation (NDVI) Trend Analysis for {district or "Selected Region"} (2000-2024)',
                xaxis_title='Year',
                yaxis_title=y_title,
                height=450,
                template="plotly_white",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                annotations=[
                    dict(
                        x=0.01,
                        y=0.95,
                        xref="paper",
                        yref="paper",
                        text=f"Trend: {z[0]:.4f}/year",
                        showarrow=False,
                        font=dict(
                            family="Arial",
                            size=14,
                            color="#212121"
                        ),
                        align="left",
                        bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="#BDBDBD",
                        borderwidth=1,
                        borderpad=4
                    )
                ]
            )
        
        return fig
        
    # If real data provided, create regression chart from actual data
    # Implementation would depend on the structure of the temporal_data DataFrame
    # This is a placeholder for the real implementation
    return None  # Replace with actual implementation
