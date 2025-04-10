import streamlit as st

st.set_page_config(
    page_title="Help & FAQ",
    page_icon="❓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("❓ Help & Frequently Asked Questions")
st.write("Find answers to common questions about using the Landsat Satellite Data Analysis Dashboard.")

# FAQ categories
categories = [
    "General Questions",
    "Using Earth Engine",
    "Data Analysis",
    "Visualization Features",
    "Troubleshooting"
]

selected_category = st.selectbox("Select a category", categories)

if selected_category == "General Questions":
    with st.expander("What is this dashboard for?", expanded=True):
        st.markdown("""
        This dashboard provides interactive visualization and analysis tools for Landsat satellite data, with a focus on Land Surface Temperature (LST) and vegetation indices (NDVI) in Tamil Nadu, India.
        
        It allows you to:
        - View spatial patterns of temperature and vegetation
        - Analyze temporal trends over multiple years
        - Compare different regions and time periods
        - Export data and visualizations for reports or further analysis
        """)
        
    with st.expander("How is the data sourced?"):
        st.markdown("""
        Data is sourced directly from Google Earth Engine:

        When you authenticate with Earth Engine, the dashboard can directly access and process Landsat satellite data from NASA/USGS.
        
        All data comes from the Landsat satellite program, specifically Landsat 7, 8, and 9 satellite imagery.
        """)
        
    with st.expander("What regions are covered?"):
        st.markdown("""
        The dashboard currently focuses on districts in Tamil Nadu, India, including:
        
        - Chennai
        - Coimbatore
        - Madurai
        - Ariyalur
        - Cuddalore
        - Dharmapuri
        - Dindigul
        - Erode
        - Tirunelveli
        
        Support for additional regions can be added by modifying the boundary data.
        """)
        
    with st.expander("What time periods are available?"):
        st.markdown("""
        The dashboard supports data from the following time periods:
        
        - Landsat 7: 1999-2013
        - Landsat 8: 2013-2022
        - Landsat 9: 2022-present
        
        For most analyses, we recommend using data from 2013 onwards for the best quality and consistency. The dashboard's default view shows data from 2018, 2020, and recent data from 2024.
        """)

elif selected_category == "Using Earth Engine":
    with st.expander("How do I authenticate with Earth Engine?", expanded=True):
        st.markdown("""
        Authentication with Google Earth Engine is handled through the sidebar of the main dashboard:
        
        1. Click on the "Authentication" section in the sidebar
        2. Follow the prompts to complete direct Google authentication
        
        You'll need a Google account that's registered with Earth Engine (like "ee-swaraw") to access Earth Engine data.
        """)
        
    with st.expander("Why am I seeing authentication errors?"):
        st.markdown("""
        Common causes of authentication errors:
        
        - **Not registered with Earth Engine**: You need to sign up for Earth Engine access at [signup.earthengine.google.com](https://signup.earthengine.google.com/)
        - **Network issues**: Earth Engine requires internet access to authenticate
        - **Session timeout**: Sometimes you may need to re-authenticate after a period of inactivity
        
        Try refreshing the page if you encounter persistent errors.
        """)
        
    with st.expander("How does Earth Engine processing work?"):
        st.markdown("""
        When using Earth Engine integration:
        
        1. The dashboard sends a request to Earth Engine's servers with your query parameters
        2. Earth Engine processes the Landsat data on Google's cloud infrastructure
        3. The results are returned to the dashboard for visualization
        
        This approach allows for efficient processing of large datasets without downloading all the raw satellite data. Earth Engine handles the heavy computational work on their servers.
        """)

elif selected_category == "Data Analysis":
    with st.expander("What is Land Surface Temperature (LST)?", expanded=True):
        st.markdown("""
        Land Surface Temperature (LST) is the temperature of the Earth's surface as measured by satellites. It differs from air temperature in that it measures how hot the actual ground or surface features are, rather than the temperature of the air above them.
        
        LST is an important indicator for:
        - Urban heat islands
        - Climate change impacts
        - Drought monitoring
        - Agricultural analysis
        
        In this dashboard, LST is derived from Landsat thermal bands and displayed in degrees Celsius.
        """)
        
    with st.expander("What is NDVI and why is it important?"):
        st.markdown("""
        NDVI (Normalized Difference Vegetation Index) is a simple graphical indicator that can be used to analyze remote sensing measurements, typically but not necessarily from a space platform, and assess whether the target being observed contains live green vegetation or not.
        
        NDVI values range from -1 to 1:
        - Higher values (0.6 to 0.9) indicate dense vegetation
        - Medium values (0.2 to 0.5) indicate sparse vegetation
        - Low values (0 to 0.1) indicate bare soil
        - Negative values often indicate water, snow, or clouds
        
        NDVI is useful for monitoring:
        - Vegetation health and density
        - Changes in vegetation over time
        - Drought impacts
        - Agricultural productivity
        """)
        
    with st.expander("How are temporal trends calculated?"):
        st.markdown("""
        Temporal trends in the dashboard are calculated by:
        
        1. **Data collection**: Gathering LST or NDVI data for each time period (year/month)
        2. **Statistical aggregation**: Computing mean, min, max, and standard deviation for each period
        3. **Regression analysis**: Calculating the slope, intercept, and correlation coefficient for the trend line
        4. **Significance testing**: Determining if the observed trends are statistically significant
        
        The resulting trend charts show how temperature or vegetation patterns have changed over time, with regression lines to highlight long-term trends.
        """)
        
    with st.expander("What statistical methods are used?"):
        st.markdown("""
        The dashboard employs several statistical methods:
        
        - **Descriptive statistics**: Mean, median, min, max, standard deviation, percentiles
        - **Linear regression**: For trend line calculation and rate of change estimation
        - **Spatial statistics**: Hotspot analysis, spatial correlation
        - **Time series analysis**: Seasonal decomposition, trend extraction
        
        These methods help identify patterns, trends, and relationships in the satellite data that might not be immediately apparent from visual inspection alone.
        """)



elif selected_category == "Visualization Features":
    with st.expander("What visualization tools are available?", expanded=True):
        st.markdown("""
        The dashboard offers several visualization tools:
        
        - **Interactive maps**: Folium-based maps with layer controls for spatial data
        - **Temporal charts**: Line charts showing changes over time
        - **Regression analysis**: Scatter plots with trend lines
        - **Spatial heatmaps**: Visualizations of data distribution across regions
        - **Comparison charts**: Bar and radar charts for comparing multiple districts
        - **Statistical summaries**: Box plots and histograms for data distribution
        
        Each visualization is interactive, allowing you to hover for details, zoom, pan, and export images.
        """)
        
    with st.expander("Can I customize the visualizations?"):
        st.markdown("""
        Yes, many aspects of the visualizations can be customized:
        
        - **Map layers**: Toggle different data layers on/off
        - **Color scales**: Adjust the color range for better contrast
        - **Time periods**: Select specific years, months, or seasons
        - **Regions**: Focus on specific districts or areas
        - **Variables**: Switch between LST, NDVI, or other derived variables
        - **Aggregation**: Choose different statistical aggregations (mean, median, max, etc.)
        
        Use the controls in the sidebar and above each visualization to customize the view to your needs.
        """)
        
    with st.expander("How do I interpret the color scales?"):
        st.markdown("""
        **Land Surface Temperature (LST)**:
        - Blue/purple: Cooler temperatures
        - Green/yellow: Moderate temperatures
        - Orange/red: Warmer temperatures
        
        The typical range is 20-45°C, with the exact scale indicated in the legend.
        
        **NDVI**:
        - White/light green: Low vegetation (0-0.2)
        - Medium green: Moderate vegetation (0.2-0.5)
        - Dark green: Dense vegetation (0.5-0.8)
        
        The range is typically -0.2 to 0.8, with water bodies appearing in negative values.
        
        Hover over any point on the maps or charts to see the exact values.
        """)
        
    with st.expander("Can I export visualizations and data?"):
        st.markdown("""
        Yes, you can export both visualizations and data:
        
        **For visualizations**:
        - Hover over charts to see the export button (camera icon)
        - Click to download as PNG
        - Maps can be exported using the map controls
        
        **For data**:
        - Look for the "Export Data" button below visualizations
        - Data will be downloaded as CSV for most charts
        - Spatial data can be exported as GeoJSON
        - Raw statistics are available as JSON
        
        Exported files can be used in reports, presentations, or for further analysis in other software.
        """)

else:  # Troubleshooting
    with st.expander("Why isn't my data loading?", expanded=True):
        st.markdown("""
        Common reasons for data loading issues:
        
        1. **Authentication problems**: You may not be properly authenticated with Earth Engine
        2. **Invalid parameters**: The selected year, month, or district may not have available data
        3. **Network issues**: Check your internet connection if using Earth Engine access
        4. **Server load**: Earth Engine may occasionally be slow due to high demand
        
        Try refreshing the page or checking your authentication status with Earth Engine.
        """)
        
    with st.expander("Why are my visualizations not appearing?"):
        st.markdown("""
        Visualization issues can occur due to:
        
        1. **No data available**: The selected parameters may not have associated data
        2. **JavaScript errors**: Check your browser console for errors
        3. **Browser compatibility**: Try a different browser (Chrome is recommended)
        4. **Memory limitations**: Large visualizations may exceed browser memory
        5. **Conflicts with browser extensions**: Try disabling extensions temporarily
        
        The dashboard will typically show a message if no data is available. If visualizations are partially loading or appearing incorrectly, try adjusting the parameters or using a different browser.
        """)
        
    with st.expander("How do I report bugs or request features?"):
        st.markdown("""
        To report bugs or request features:
        
        1. Provide detailed information about the issue or feature
        2. Include steps to reproduce any bugs
        3. Specify your browser and operating system
        4. Include screenshots if applicable
        5. Describe what you expected to happen vs. what actually happened
        
        Send your report to the development team, who will assess and prioritize your feedback.
        """)
        
    with st.expander("What should I do if Earth Engine authentication fails?"):
        st.markdown("""
        If Earth Engine authentication fails:
        
        1. **Check your Earth Engine account**: Ensure you have registered at [signup.earthengine.google.com](https://signup.earthengine.google.com/)
        2. **Clear browser cache**: Clear cookies and cache related to Google services
        3. **Check your network**: Ensure your network allows connections to Earth Engine services
        
        If you continue to have issues, try accessing Earth Engine directly in the Google Earth Engine Code Editor to verify your account is working correctly.
        """)

# Contact information
st.markdown("---")
st.markdown("""
### Need More Help?

If your question isn't answered here, you can:

- Check the documentation for more detailed information
- Contact technical support for assistance with specific issues
- Visit the Google Earth Engine forums for help with Earth Engine-specific questions
""")

# Button to return to main dashboard
if st.button("Return to Main Dashboard"):
    st.switch_page("app.py")
