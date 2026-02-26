##Note file paths and confidential information removed. This is example code and does not run as is.

#Load libraries ---------------------------------------------------------------
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt

#Set working directory --------------------------------------------------------
os.chdir("")

#Read in data -----------------------------------------------------------------
dat = pd.read_csv("all_service_losses.csv")
GIS_template = "Template.gdb"
subareas = gpd.read_file(GIS_template,layer="Subareas_Primary")
area_boundary = gpd.read_file(GIS_template,layer="boundary").to_crs(subareas.crs)

#Edit subareas base_name to merge with dat Area_Name --------------------------
subareas.loc[subareas['base_name']=="River,'base_name'] = subareas['River_Sb'].str.replace(" ","")

#Filter subareas to only include those in dat and clip to Pueblo boundary -----
filtered_subareas = subareas[subareas['base_name'].isin(dat['Area_Name'])]
clipped_subareas = gpd.clip(filtered_subareas,area_boundary)

#Plot clipped subareas for checking -------------------------------------------
fig, ax = plt.subplots(figsize=(10,10))
area_boundary.plot(ax=ax,color="lightblue",edgecolor="black")
clipped_subareas.plot(ax=ax,color="red",alpha=0.5)
plt.show()

#Average SL columns -----------------------------------------------------------
dat['Geologic'] = dat[['Soil','Sediment','ResourceWeighted']].stack().reset_index(level=1,drop=True)

SL_cols = ['Avian', 'RESRAD', 'BMI', 'Geologic']
dat.loc[:,SL_cols] = dat.loc[:,SL_cols] * 100 #Convert to percentage
dat['Avg_SL'] = dat[SL_cols].mean(axis=1)

#Merge data -------------------------------------------------------------------
merged = clipped_subareas.merge(dat,left_on='base_name',right_on="Area_Name",how="inner")

#Make basic choropleth map ----------------------------------------------------
def plot_SL(merged,boundary,column_name,title,vmin,vmax):
    """
    Creates and saves a choropleth map of Service Loss (%) for a given column.
    
    The map is plotted over a boundary layer and saved as a JPEG file to the Report
    figures directory. The color scale is fixed across all plots
    using vmin and vmax to allow for comparison between columns.
    
    Parameters
    ----------
    merged : GeoDataFrame
        The main GeoDataFrame containing the data to be plotted.
    boundary : GeoDataFrame
        The boundary GeoDataFrame to be plotted in the background.
    column_name : str
        The name of the column in merged to plot. Also used to name the
        output file (choroplethMap_SL_{column_name}.jpeg).
    title : str
        The title to display at the top of the plot.
    vmin : float
        The minimum value for the color scale.
    vmax : float
        The maximum value for the color scale.
    
    Returns
    -------
    None
        Saves the figure to:
        Report/choroplethMap_SL_{column_name}.jpeg
    
    Example
    -------
    >>> plot_SL(merged, area_boundary, 'Avian', 'Avian Service Loss', 0, 100)
    """
    base_path = "03_Figures/Report/"
    save_path = f"{base_path}choroplethMap_SL_{column_name}.jpeg"

    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(12, 10))

    boundary.plot(ax=ax, color='lightgrey', edgecolor='black')

    merged.plot(
        column = column_name,
        ax=ax,
        legend=True,
        cmap='OrRd',
        edgecolor='black',
        linewidth=0.5,
        vmin = vmin,
        vmax = vmax,
        legend_kwds={
            'label':"Service Loss (%)",
            'orientation': 'vertical'
        }
    )
    
    ax.axis('off')
    ax.set_title(title,fontsize=16)
    #plt.show()
    plt.savefig(save_path)
    plt.close()
    print("Done")

#Define columns and save paths to plot
col_info = {
    'Avian' : "Avian",
    'RESRAD': "Elk Radiological",
    'BMI': "Benthic Macroinvertebrates",
    'RESRAD_SubareaSL': "Subarea Radiological",
    'Geologic': "Geologic",
    'Avg_SL': "Average Across Evidence Streams"
    }

#Determine min and max of SL color gradient
vmin = merged[col_info.keys()].min().min()
vmax = merged[col_info.keys()].max().max()

#Look through and plot each column
for col, (label) in col_info.items():
    plot_SL(
        merged = merged,
        boundary = area_boundary,
        column_name = col,
        title = label,
        vmin = vmin,
        vmax = vmax)
