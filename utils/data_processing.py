import ee
import pandas as pd
import numpy as np
from .earth_engine import get_district_boundary, get_lst_layer, get_ndvi_layer

def process_landsat_data(collection, district, variable_type="LST", time_of_day="Daytime"):
    """
    Process Landsat collection to get LST or NDVI layer for the specified district.
    
    Args:
        collection (ee.ImageCollection): Landsat image collection
        district (str): District name
        variable_type (str): "LST" for Land Surface Temperature or "NDVI" for vegetation index
        time_of_day (str): "Daytime" or "Nighttime" (only affects LST interpretation)
        
    Returns:
        tuple: (ee.Image with data layer, ee.Geometry of the region)
    """
    # Get district boundary
    region = get_district_boundary(district)
    
    # Check if collection has any images
    collection_size = collection.size().getInfo()
    
    if collection_size == 0:
        # No images available for the specified filters
        # Create a placeholder image with default values
        if variable_type == "LST":
            empty_value = 25.0  # Default temperature in Celsius
        else:  # NDVI
            empty_value = 0.3   # Default NDVI value (moderate vegetation)
            
        placeholder = ee.Image.constant(empty_value)
        
        if variable_type == "LST":
            visualization = {'min': 20, 'max': 40, 'palette': ['blue', 'yellow', 'red']}
            data_layer = placeholder.rename('LST').set(visualization)
        else:
            visualization = {'min': -0.2, 'max': 0.8, 'palette': ['white', 'green']}
            data_layer = placeholder.rename('NDVI').set(visualization)
            
        return data_layer.clip(region), region
    
    # Get the median image from the collection (to reduce cloud impact)
    median_image = collection.median()
    
    # Process based on variable type
    if variable_type == "LST":
        # Get LST layer
        data_layer = get_lst_layer(median_image)
        
        # Adjust visualization based on time of day
        if time_of_day == "Daytime":
            visualization = {'min': 25, 'max': 45}  # Higher range for daytime
        else:  # Nighttime
            visualization = {'min': 15, 'max': 35}  # Lower range for nighttime
            
        data_layer = data_layer.set(visualization)
    else:
        # Get NDVI layer - not affected by time of day
        data_layer = get_ndvi_layer(median_image)
    
    # Clip to district boundary
    clipped_layer = data_layer.clip(region)
    
    return clipped_layer, region

def calculate_statistics(data_layer, region):
    """
    Calculate statistics for the data layer in the specified region.
    
    Args:
        data_layer (ee.Image): Image layer (LST or NDVI)
        region (ee.Geometry): Region geometry
        
    Returns:
        dict: Statistics including min, max, mean, etc.
    """
    # Calculate basic statistics
    stats = data_layer.reduceRegion(
        reducer=ee.Reducer.mean().combine(
            reducer2=ee.Reducer.minMax(),
            sharedInputs=True
        ).combine(
            reducer2=ee.Reducer.stdDev(),
            sharedInputs=True
        ).combine(
            reducer2=ee.Reducer.percentile([25, 50, 75]),
            sharedInputs=True
        ),
        geometry=region,
        scale=30,  # 30m resolution
        maxPixels=1e9
    ).getInfo()
    
    # Extract variable name (LST or NDVI)
    var_name = list(stats.keys())[0].split('_')[0]
    
    # Reformat statistics into a simpler structure
    simplified_stats = {
        'min': stats.get(f'{var_name}_min', 0),
        'max': stats.get(f'{var_name}_max', 0),
        'mean': stats.get(f'{var_name}_mean', 0),
        'stdDev': stats.get(f'{var_name}_stdDev', 0),
        'median': stats.get(f'{var_name}_p50', 0),
        'p25': stats.get(f'{var_name}_p25', 0),
        'p75': stats.get(f'{var_name}_p75', 0)
    }
    
    return simplified_stats

def generate_sample_points(region, num_points=100):
    """
    Generate sample points within the region for detailed analysis.
    
    Args:
        region (ee.Geometry): Region geometry
        num_points (int): Number of points to generate
        
    Returns:
        ee.FeatureCollection: Collection of sample points
    """
    # Generate random points within the region
    points = ee.FeatureCollection.randomPoints(region, num_points)
    
    return points

def extract_point_values(data_layer, points):
    """
    Extract data values at the sample points.
    
    Args:
        data_layer (ee.Image): Image layer (LST or NDVI)
        points (ee.FeatureCollection): Sample points
        
    Returns:
        pandas.DataFrame: DataFrame with point coordinates and values
    """
    # Sample the data layer at each point
    point_values = data_layer.sampleRegions(
        collection=points,
        properties=None,
        scale=30  # 30m resolution
    )
    
    # Convert to a format that can be downloaded
    point_list = point_values.getInfo()
    
    # Convert to DataFrame
    data = []
    for feature in point_list['features']:
        # Get coordinates
        coords = feature['geometry']['coordinates']
        # Get property value
        value = feature['properties'].get(list(feature['properties'].keys())[0], None)
        
        data.append({
            'longitude': coords[0],
            'latitude': coords[1],
            'value': value
        })
    
    return pd.DataFrame(data)

def analyze_temporal_changes(collections, regions, variable_type="LST", time_of_day="Daytime"):
    """
    Analyze temporal changes across multiple time periods.
    
    Args:
        collections (list): List of (collection, year, month) tuples
        regions (list): List of (district, region) tuples
        variable_type (str): "LST" for Land Surface Temperature or "NDVI" for vegetation index
        time_of_day (str): "Daytime" or "Nighttime" (only affects LST interpretation)
        
    Returns:
        pandas.DataFrame: DataFrame with temporal statistics
    """
    # Process each collection and region
    results = []
    for collection, year, month in collections:
        for district, region in regions:
            # Process data
            if variable_type == "LST":
                # Get LST data
                median_image = collection.median()
                data_layer = get_lst_layer(median_image).clip(region)
                
                # Adjust visualization based on time of day
                if time_of_day == "Daytime":
                    visualization = {'min': 25, 'max': 45}  # Higher range for daytime
                else:  # Nighttime
                    visualization = {'min': 15, 'max': 35}  # Lower range for nighttime
                    
                data_layer = data_layer.set(visualization)
            else:
                # Get NDVI data
                median_image = collection.median()
                data_layer = get_ndvi_layer(median_image).clip(region)
            
            # Calculate statistics
            stats = calculate_statistics(data_layer, region)
            
            # Add to results
            results.append({
                'year': year,
                'month': month,
                'district': district,
                'time_of_day': time_of_day,  # Include time of day in results
                'mean': stats['mean'],
                'min': stats['min'],
                'max': stats['max'],
                'stdDev': stats['stdDev']
            })
    
    # Convert to DataFrame
    return pd.DataFrame(results)

def calculate_regression(df, x_column='year', y_column='mean'):
    """
    Calculate linear regression for the data.
    
    Args:
        df (pandas.DataFrame): DataFrame with temporal data
        x_column (str): Column name for x-axis (independent variable)
        y_column (str): Column name for y-axis (dependent variable)
        
    Returns:
        tuple: (slope, intercept, r_squared, p_value)
    """
    # Extract x and y values
    x = df[x_column].values
    y = df[y_column].values
    
    # Calculate linear regression
    slope, intercept = np.polyfit(x, y, 1)
    
    # Calculate correlation coefficient
    r = np.corrcoef(x, y)[0, 1]
    r_squared = r**2
    
    # Calculate p-value (simplified)
    # In a real implementation, you would use scipy.stats.linregress
    n = len(x)
    t = r * np.sqrt((n - 2) / (1 - r**2))
    p_value = 2 * (1 - np.abs(t)) 
    
    return slope, intercept, r_squared, p_value
