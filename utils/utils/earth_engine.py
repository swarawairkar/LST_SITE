import ee
import streamlit as st
import os
import json
import logging
from pathlib import Path
import webbrowser

# Setup logging to capture errors but not display them
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("earth_engine")

# Check if authentication token exists
def ee_token_exists():
    """Check if Earth Engine authentication token exists."""
    try:
        home_dir = str(Path.home())
        credential_file = os.path.join(home_dir, '.config', 'earthengine', 'credentials')
        return os.path.exists(credential_file)
    except:
        return False

# Initialize Earth Engine
def initialize_earth_engine():
    """
    Initialize the Google Earth Engine API using user authentication.
    This allows direct login with a Google account (like ee-swaraw).
    """
    try:
        try:
            # Use direct authentication with the specified project ID
            ee.Initialize(project='ee-swaraw')
            logger.info("Successfully initialized Earth Engine with user credentials")
            return True
        except Exception as e:
            # Just log the error without showing it to the user
            logger.info(f"Earth Engine initialization failed: {str(e)}")
            return False
    except Exception as e:
        # Just log the error without showing it to the user
        logger.info(f"Earth Engine initialization failed: {str(e)}")
        return False

# Get Landsat collection
def get_landsat_collection(year, month, time_of_day='Daytime'):
    """
    Get Landsat collection for the specified parameters.
    
    Args:
        year (int): Year for data collection (e.g., 2024)
        month (int): Month for data collection (1-12)
        time_of_day (str): 'Daytime' or 'Nighttime'
        
    Returns:
        ee.ImageCollection: Filtered Landsat collection
    """
    # Define time range
    start_date = ee.Date.fromYMD(year, month, 1)
    end_date = start_date.advance(1, 'month')
    
    # Determine which Landsat collection to use based on year
    if year >= 2022:
        # Landsat 9
        collection = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
    elif year >= 2013:
        # Landsat 8
        collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    else:
        # Landsat 7
        collection = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2')
    
    # Filter by date
    filtered = collection.filterDate(start_date, end_date)
    
    # Apply cloud cover filter
    filtered = filtered.filter(ee.Filter.lt('CLOUD_COVER', 20))
    
    # Apply time of day filter - for Landsat, this is based on the sun elevation
    if time_of_day == 'Daytime':
        # Sun elevation > 40 degrees is considered good daytime imagery
        filtered = filtered.filter(ee.Filter.gt('SUN_ELEVATION', 40))
    else:  # Nighttime
        # For demonstration, we'll use early morning or late evening images
        # Note: True nighttime thermal data would come from different satellites
        filtered = filtered.filter(ee.Filter.lt('SUN_ELEVATION', 40))
    
    return filtered

# Get Land Surface Temperature from Landsat collection
def get_lst_layer(image):
    """
    Calculate Land Surface Temperature from Landsat thermal band.
    
    Args:
        image (ee.Image): Landsat image
        
    Returns:
        ee.Image: Image with LST band
    """
    # Check if the image has a ST_B10 band (Landsat 8/9) or ST_B6 band (Landsat 7)
    # This ensures compatibility with different Landsat sensors
    
    # First, try to get the thermal band name
    band_names = image.bandNames()
    
    # For Landsat 8/9 (Collection 2 Level 2 products)
    if band_names.contains('ST_B10'):
        # The ST bands in Collection 2 Level 2 products are already in Kelvin
        # Scale factor is 0.00341802 and offset is 149.0
        thermal = image.select(['ST_B10']).multiply(0.00341802).add(149.0)
    # For Landsat 7 (Collection 2 Level 2 products)
    elif band_names.contains('ST_B6'):
        # The ST bands are already in Kelvin, apply the appropriate scaling
        thermal = image.select(['ST_B6']).multiply(0.00341802).add(149.0)
    else:
        # Fallback to B10 or B6 if ST_ bands not available (Collection 1 products)
        if band_names.contains('B10'):
            # Landsat 8/9 thermal band
            thermal = image.select(['B10']).multiply(0.00341802).add(149.0)
        elif band_names.contains('B6'):
            # Landsat 7 thermal band
            thermal = image.select(['B6']).multiply(0.00341802).add(149.0)
        else:
            # If no thermal band is found, create a default value
            # This ensures visualization doesn't break, but should be handled better in production
            thermal = ee.Image.constant(298)  # ~25°C as default
    
    # Convert to Celsius
    lst_celsius = thermal.subtract(273.15)
    
    # Set visualization parameters with temperature ranges appropriate for the data
    # Standard visualization for LST
    visualization = {
        'min': 20,
        'max': 40,
        'palette': [
            '040274', '040281', '0502a3', '0502b8', '0502ce', '0502e6',
            '0602ff', '235cb1', '307ef3', '269db1', '30c8e2', '32d3ef',
            '3be285', '3ff38f', '86e26f', '3ae237', 'b5e22e', 'd6e21f',
            'fff705', 'ffd611', 'ffb613', 'ff8b13', 'ff6e08', 'ff500d',
            'ff0000', 'de0101', 'c21301', 'a71001', '911003'
        ]
    }
    
    return lst_celsius.rename('LST').set(visualization)

# Get NDVI from Landsat collection
def get_ndvi_layer(image):
    """
    Calculate Normalized Difference Vegetation Index (NDVI) from Landsat.
    
    Args:
        image (ee.Image): Landsat image
        
    Returns:
        ee.Image: Image with NDVI band
    """
    # Calculate NDVI
    # NIR (B5) and Red (B4) bands
    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    
    # Set visualization parameters
    visualization = {
        'min': -0.2,
        'max': 0.8,
        'palette': [
            'FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
            '74A901', '66A000', '529400', '3E8601', '207401', '056201',
            '004C00', '023B01', '012E01', '011D01', '011301'
        ]
    }
    
    return ndvi.set(visualization)

# Get district boundaries for Tamil Nadu
def get_district_boundary(district_name):
    """
    Get the boundary for a district in Tamil Nadu, India.
    
    Args:
        district_name (str): District name
        
    Returns:
        ee.Feature: District boundary feature
    """
    # For demonstration, we'll use a simplified approach
    # In a real implementation, you'd use actual district boundaries from a source like GADM
    
    # Tamil Nadu state boundary (approximate)
    tamil_nadu = ee.Geometry.Rectangle([76.0, 8.0, 81.0, 14.0])
    
    if district_name == "All":
        return tamil_nadu
    else:
        # In a real application, you would query a proper boundary dataset
        # For now, we'll simulate with some fixed boundaries for key districts
        district_coords = {
            "Chennai": [80.1, 12.9, 80.3, 13.2],
            "Coimbatore": [76.8, 10.9, 77.1, 11.2],
            "Madurai": [78.0, 9.8, 78.3, 10.0],
            "Ariyalur": [79.0, 11.0, 79.3, 11.3],
            "Cuddalore": [79.5, 11.5, 79.8, 11.8],
            "Dharmapuri": [78.0, 12.0, 78.3, 12.3],
            "Dindigul": [77.8, 10.2, 78.1, 10.5],
            "Erode": [77.4, 11.2, 77.7, 11.5],
            "Tirunelveli": [77.6, 8.6, 77.9, 8.9],
            # Add more districts as needed
        }
        
        if district_name in district_coords:
            return ee.Geometry.Rectangle(district_coords[district_name])
        else:
            # Return a small portion of Tamil Nadu for districts without specific coordinates
            # In a real app, you would have all districts properly mapped
            return ee.Geometry.Rectangle([78.0, 11.0, 78.5, 11.5])
