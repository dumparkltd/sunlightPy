import geopandas as gpd
import numpy as np
import pandas as pd 
import rasterio
import matplotlib.pyplot as plt 

cross_sections = gpd.read_file(r'D:\GeoDelta\Cross Sections Extractor\Shapefiles\Cross sections.shp')

for ind, row in cross_sections.iterrows():
    
    XS_ID = row['xs_id']

    start_coords =  list([row.geometry][0].coords)[0]
    end_coords = list([row.geometry][0].coords)[1]
    
    lon = [start_coords[0]]
    lat = [start_coords[1]]
    
    n_points = 50
    
    for i in np.arange(1, n_points+1):
        x_dist = end_coords[0] - start_coords[0]
        y_dist = end_coords[1] - start_coords[1]
        point  = [(start_coords[0] + (x_dist/(n_points+1))*i), (start_coords[1] + (y_dist/(n_points+1))*i)]
        lon.append(point[0])
        lat.append(point[1])
        
    lon.append(end_coords[0])
    lat.append(end_coords[1])
    
    
    df = pd.DataFrame({'Latitude': lat, 
                       'Longitude': lon})
    
    gdf = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df.Longitude, df.Latitude))
    gdf.crs = {'init': 'epsg:4326'}
    
    gdf_pcs = gdf.to_crs(epsg = 3857)
    
    gdf_pcs['h_distance'] = 0
    
    for index, row in gdf_pcs.iterrows():
        gdf_pcs['h_distance'].loc[index] = gdf_pcs.geometry[0].distance(gdf_pcs.geometry[index])
        
    # Extracting the elevations from the DEM     
    
    gdf_pcs['Elevation'] = 0
    
    dem = rasterio.open(r'D:\GeoDelta\Cross Sections Extractor\DEM.tif', mode = 'r')
    
    for index, row in gdf_pcs.iterrows():
        row, col = dem.index(row['Longitude'], row['Latitude'])
        dem_data = dem.read(1)
        
        gdf_pcs['Elevation'].loc[index] = dem_data[row, col]
        
    # Extract h_distance (x) and Elevation (y) columns into a Pandas DataFrame
    
    x_y_data = gdf_pcs[['h_distance', 'Elevation']]
    
    x_y_data.to_csv(r'D:\GeoDelta\Cross Sections Extractor\extracted_sections' + '\\'+ XS_ID + '.csv' )
    
    
    # Creating plots for each cross sectional profile 
    plt.plot(gdf_pcs['h_distance'], gdf_pcs['Elevation'])
    plt.xlabel('Distance (m)')
    plt.ylabel('Elevation (m)')
    plt.grid(True)
    plt.title(XS_ID)    
    plt.savefig(r'D:\GeoDelta\Cross Sections Extractor\extracted_sections' + '\\'+ XS_ID + '.png' )
    plt.show()









