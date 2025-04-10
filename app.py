mkdir -p .streamlit data pages/sections utils/analysisimport streamlit as st

st.set_page_config(
    page_title="About",
    page_icon="ℹ️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("ℹ️ About the Landsat Satellite Data Analysis Dashboard")

# Introduction
st.markdown("""
## Project Overview

The Landsat Satellite Data Analysis Dashboard is a comprehensive tool for visualizing and analyzing Land Surface Temperature (LST) 
and vegetation indices derived from Landsat satellite imagery. This application focuses on districts in Tamil Nadu, India, 
providing insights into temperature patterns, vegetation health, and environmental changes over time.

### Key Capabilities

- **Spatial Visualization**: Interactive maps showing LST and NDVI distribution across regions
- **Temporal Analysis**: Charts displaying changes in temperature and vegetation over different years
- **Statistical Analysis**: Regression trends, statistical summaries, and comparative analytics
- **Data Integration**: Direct connection to Google Earth Engine and import from Google Colab

### Target Users

This dashboard is designed for:

- **Researchers** studying climate change, urban heat islands, and environmental impacts
- **Policymakers** developing strategies for climate resilience and urban planning
- **Educators and students** learning about remote sensing and environmental monitoring
- **Environmental consultants** preparing reports and assessments
""")

# Two-column layout
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("""
    ## Technical Information
    
    ### Data Sources
    
    The dashboard utilizes data from the Landsat satellite program:
    
    - **Landsat 7 ETM+** (1999-2013): 30m resolution multispectral imagery
    - **Landsat 8 OLI/TIRS** (2013-2022): Enhanced thermal and optical sensors
    - **Landsat 9 OLI-2/TIRS-2** (2022-present): Latest generation with improved radiometric resolution
    
    All satellite data is accessed through the Google Earth Engine platform, which provides:
    
    - Cloud-based processing of large satellite datasets
    - Historical archive of satellite imagery
    - Pre-processed surface reflectance products
    
    ### Analysis Methods
    
    The dashboard employs several scientific methods for data analysis:
    
    - **Land Surface Temperature (LST)** calculation using thermal infrared bands
    - **Normalized Difference Vegetation Index (NDVI)** derived from near-infrared and red bands
    - **Statistical aggregation** of pixel values within administrative boundaries
    - **Temporal trend analysis** using regression and time series techniques
    - **Comparative analysis** across different regions and time periods
    """)
    
    st.markdown("""
    ## Implementation Details
    
    ### Technology Stack
    
    The dashboard is built using:
    
    - **Streamlit**: Main web application framework
    - **Earth Engine Python API**: Interface with Google Earth Engine
    - **Folium**: Interactive mapping library
    - **Plotly**: Advanced data visualization
    - **Pandas & NumPy**: Data manipulation and analysis
    
    ### Development Approach
    
    This project was developed using:
    
    - Modular design with separated data processing and visualization components
    - Integration with cloud-based processing to handle large datasets
    - Emphasis on interactive visualizations for exploratory analysis
    - Support for both real-time processing and pre-processed data workflows
    """)

with col2:
    st.markdown("""
    ## Use Cases
    
    ### Urban Heat Island Analysis
    Identify and quantify urban heat islands by comparing LST in urban centers versus surrounding rural areas, helping city planners develop cooling strategies.
    
    ### Vegetation Change Monitoring
    Track changes in vegetation health and distribution over time using NDVI, supporting forest management and agricultural planning.
    
    ### Climate Impact Assessment
    Analyze temperature trends over multiple years to assess local climate change impacts and identify vulnerable regions.
    
    ### Drought Monitoring
    Combine LST and NDVI data to identify areas experiencing drought conditions, aiding in water resource management.
    """)
    
    # Citations and references
    st.markdown("""
    ## References & Further Reading
    
    ### Landsat Program
    - [Landsat Science](https://landsat.gsfc.nasa.gov/)
    - [USGS Earth Explorer](https://earthexplorer.usgs.gov/)
    
    ### Earth Engine Resources
    - [Google Earth Engine Documentation](https://developers.google.com/earth-engine)
    - [Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets)
    
    ### Scientific Papers
    - Jiménez-Muñoz, J. C., et al. (2014). Land surface temperature retrieval methods from Landsat-8 thermal infrared sensor data. *IEEE Geoscience and Remote Sensing Letters*, 11(10), 1840-1843.
    - Zhou, Y., et al. (2019). Surface urban heat island in China's 32 major cities: Spatial patterns and drivers. *Remote Sensing of Environment*, 152, 51-61.
    """)

# Usage instructions  
st.markdown("""
## Getting Started

To begin using the dashboard:

1. Navigate to the **Main Dashboard** page
2. Select your data source (Earth Engine or uploaded data)
3. Choose parameters (year, month, district, etc.)
4. Explore the visualizations and analysis results

For detailed instructions, visit the **Help & FAQ** page or the **Google Colab Guide** for integration with Colab.
""")

# Footer
st.markdown("---")
st.markdown("""
<div style='display: flex; justify-content: space-between;'>
    <span style='font-size: 0.8rem; color: #666;'>© 2025 Landsat Satellite Data Analysis Dashboard</span>
    <span style='font-size: 0.8rem; color: #666;'>Version 1.0</span>
</div>
""", unsafe_allow_html=True)
