import pandas as pd
import json
import os
import streamlit as st
import numpy as np
from pathlib import Path

def ensure_data_dir():
    """Ensure the data directory exists."""
    os.makedirs('data', exist_ok=True)
    return os.path.abspath('data')

def load_lst_data(year, month, district, time_of_day):
    """
    Load LST data from a JSON file.
    
    Args:
        year (int): Year
        month (int): Month
        district (str): District name
        time_of_day (str): 'Daytime' or 'Nighttime'
        
    Returns:
        dict: Dictionary with LST data and statistics
    """
    data_dir = ensure_data_dir()
    
    # Try to find matching file
    file_pattern = f"lst_{year}_{month:02d}_{district.lower()}_{time_of_day.lower()}.json"
    file_path = os.path.join(data_dir, file_pattern)
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            st.error(f"Error loading LST data: {str(e)}")
            return None
    else:
        # Try to find any LST data file
        lst_files = [f for f in os.listdir(data_dir) if f.startswith('lst_') and f.endswith('.json')]
        
        if lst_files:
            # Use the most recent file
            lst_files.sort(reverse=True)
            file_path = os.path.join(data_dir, lst_files[0])
            
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                st.warning(f"Exact data not found. Using data from {lst_files[0]}")
                return data
            except Exception as e:
                st.error(f"Error loading LST data: {str(e)}")
                return None
        else:
            st.warning("No LST data files found. Please upload data files first.")
            return None

def load_ndvi_data(year, month, district, time_of_day=None):
    """
    Load NDVI data from a JSON file.
    
    Args:
        year (int): Year
        month (int): Month
        district (str): District name
        time_of_day (str, optional): Not applicable for NDVI but kept for consistency
        
    Returns:
        dict: Dictionary with NDVI data and statistics
    """
    data_dir = ensure_data_dir()
    
    # Try to find matching file
    file_pattern = f"ndvi_{year}_{month:02d}_{district.lower()}.json"
    file_path = os.path.join(data_dir, file_pattern)
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            st.error(f"Error loading NDVI data: {str(e)}")
            return None
    else:
        # Try to find any NDVI data file
        ndvi_files = [f for f in os.listdir(data_dir) if f.startswith('ndvi_') and f.endswith('.json')]
        
        if ndvi_files:
            # Use the most recent file
            ndvi_files.sort(reverse=True)
            file_path = os.path.join(data_dir, ndvi_files[0])
            
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                st.warning(f"Exact data not found. Using data from {ndvi_files[0]}")
                return data
            except Exception as e:
                st.error(f"Error loading NDVI data: {str(e)}")
                return None
        else:
            st.warning("No NDVI data files found. Please upload data files first.")
            return None

def load_district_boundaries():
    """
    Load district boundaries from a JSON file.
    
    Returns:
        dict: Dictionary with district boundaries
    """
    data_dir = ensure_data_dir()
    file_path = os.path.join(data_dir, 'district_boundaries.json')
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            st.error(f"Error loading district boundaries: {str(e)}")
            return None
    else:
        st.warning("District boundaries file not found. Please upload data files first.")
        return None

def load_temporal_data(district, years, months, time_of_day, variable_type="LST"):
    """
    Load temporal analysis data from a CSV file.
    
    Args:
        district (str): District name
        years (list): List of years
        months (list): List of months
        time_of_day (str): 'Daytime' or 'Nighttime'
        variable_type (str): 'LST' or 'NDVI'
        
    Returns:
        pandas.DataFrame: DataFrame with temporal analysis data
    """
    data_dir = ensure_data_dir()
    
    # Try to find matching file
    file_pattern = f"temporal_{variable_type.lower()}_{district.lower()}.csv"
    file_path = os.path.join(data_dir, file_pattern)
    
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            
            # Filter by years and months if present in the dataframe
            if 'year' in df.columns:
                df = df[df['year'].isin(years)]
            
            if 'month' in df.columns:
                df = df[df['month'].isin(months)]
            
            if 'time_of_day' in df.columns and variable_type == "LST":
                df = df[df['time_of_day'].str.lower() == time_of_day.lower()]
            
            return df
        except Exception as e:
            st.error(f"Error loading temporal data: {str(e)}")
            return None
    else:
        # Try to find any temporal data file
        temporal_files = [f for f in os.listdir(data_dir) if f.startswith(f'temporal_{variable_type.lower()}_') and f.endswith('.csv')]
        
        if temporal_files:
            # Use the first available file
            file_path = os.path.join(data_dir, temporal_files[0])
            
            try:
                df = pd.read_csv(file_path)
                # Extract district from filename
                file_district = temporal_files[0].split('_')[-1].split('.')[0]
                
                st.warning(f"Data for {district} not found. Using data for {file_district}")
                
                # Filter by years and months if present in the dataframe
                if 'year' in df.columns:
                    df = df[df['year'].isin(years)]
                
                if 'month' in df.columns:
                    df = df[df['month'].isin(months)]
                
                if 'time_of_day' in df.columns and variable_type == "LST":
                    df = df[df['time_of_day'].str.lower() == time_of_day.lower()]
                
                return df
            except Exception as e:
                st.error(f"Error loading temporal data: {str(e)}")
                return None
        else:
            st.warning(f"No temporal {variable_type} data found. Please authenticate with Earth Engine to access satellite data.")
            return None

def load_comparison_data(year, month, districts, time_of_day, variable_type="LST"):
    """
    Load district comparison data from a CSV file.
    
    Args:
        year (int): Year
        month (int): Month
        districts (list): List of district names
        time_of_day (str): 'Daytime' or 'Nighttime'
        variable_type (str): 'LST' or 'NDVI'
        
    Returns:
        pandas.DataFrame: DataFrame with district comparison data
    """
    data_dir = ensure_data_dir()
    
    # Try to find matching file
    file_pattern = f"comparison_{variable_type.lower()}_{year}_{month:02d}.csv"
    file_path = os.path.join(data_dir, file_pattern)
    
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            
            # Filter by districts if 'district' column exists
            if 'district' in df.columns:
                df = df[df['district'].isin(districts)]
            
            # Filter by time_of_day if applicable
            if 'time_of_day' in df.columns and variable_type == "LST":
                df = df[df['time_of_day'].str.lower() == time_of_day.lower()]
            
            return df
        except Exception as e:
            st.error(f"Error loading comparison data: {str(e)}")
            return None
    else:
        # Try to find any comparison data file
        comparison_files = [f for f in os.listdir(data_dir) if f.startswith(f'comparison_{variable_type.lower()}_') and f.endswith('.csv')]
        
        if comparison_files:
            # Use the most recent file
            comparison_files.sort(reverse=True)
            file_path = os.path.join(data_dir, comparison_files[0])
            
            try:
                df = pd.read_csv(file_path)
                st.warning(f"Exact comparison data not found. Using data from {comparison_files[0]}")
                
                # Filter by districts if 'district' column exists
                if 'district' in df.columns:
                    df = df[df['district'].isin(districts)]
                
                # Filter by time_of_day if applicable
                if 'time_of_day' in df.columns and variable_type == "LST":
                    df = df[df['time_of_day'].str.lower() == time_of_day.lower()]
                
                return df
            except Exception as e:
                st.error(f"Error loading comparison data: {str(e)}")
                return None
        else:
            st.warning(f"No {variable_type} comparison data found. Please authenticate with Earth Engine to access satellite data.")
            return None

def save_uploaded_file(uploaded_file, file_type):
    """
    Save an uploaded file to the data directory.
    
    Args:
        uploaded_file (UploadedFile): File uploaded via Streamlit
        file_type (str): Type of file ('lst', 'ndvi', 'boundaries', 'temporal', 'comparison')
        
    Returns:
        str: Path to saved file, or None if error
    """
    data_dir = ensure_data_dir()
    
    try:
        # Ensure filename has correct prefix
        file_name = uploaded_file.name
        
        if not file_name.startswith(file_type + '_'):
            file_name = f"{file_type}_{file_name}"
        
        file_path = os.path.join(data_dir, file_name)
        
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    except Exception as e:
        st.error(f"Error saving uploaded file: {str(e)}")
        return None

def process_uploaded_csv(file_path):
    """
    Process an uploaded CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: Processed data
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"Error processing CSV file: {str(e)}")
        return None

def process_uploaded_json(file_path):
    """
    Process an uploaded JSON file.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        dict: Processed data
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Error processing JSON file: {str(e)}")
        return None

def get_available_data_files():
    """
    Get a list of available data files.
    
    Returns:
        dict: Dictionary with lists of available files by type
    """
    data_dir = ensure_data_dir()
    
    # Get all files in data directory
    if not os.path.exists(data_dir):
        return {
            'lst': [],
            'ndvi': [],
            'boundaries': [],
            'temporal': [],
            'comparison': []
        }
    
    files = os.listdir(data_dir)
    
    # Categorize files by type
    lst_files = [f for f in files if f.startswith('lst_')]
    ndvi_files = [f for f in files if f.startswith('ndvi_')]
    boundary_files = [f for f in files if f.startswith('district_boundaries')]
    temporal_files = [f for f in files if f.startswith('temporal_')]
    comparison_files = [f for f in files if f.startswith('comparison_')]
    
    return {
        'lst': lst_files,
        'ndvi': ndvi_files,
        'boundaries': boundary_files,
        'temporal': temporal_files,
        'comparison': comparison_files
    }
