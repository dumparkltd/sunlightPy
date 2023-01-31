
import rasterio
from pyproj import CRS, Transformer
from datetime import datetime
import numpy as np

from suncalc import get_position, get_times
import math
from matplotlib import pyplot

def is_shade(altitude_sun, altitudes):
    alt_data = altitudes.read(1)
    shades = [[0 for column in range(0, altitudes.width)] for row in range(0, altitudes.height)]

    for row in range(0, altitudes.height):
        for column in range(0, altitudes.width):
            
            alt_min = alt_data[row, column]
            # record sunlight
            if (altitude_sun > alt_min):
                shades[row][column] = 0
            # record shade
            else:
                shades[row][column] = 1
            
    return shades

def main():   
    ### VARIABLES
    file_location = "c:/users/timo/documents/projects/inrae/data"
    file_location_out = file_location + '/tmp'
    dem_location = file_location + '/raster1.tif'

    settings =  {
        'azimuth_min': 246, # adjusted to local range below
        'azimuth_max': 246, # adjusted to local range below
        'azimuth_step': 1,
        'downscale_factor_dem': 10, # downsample dem resolution
        'downscale_factor_alt': 1, # distances between points for sampling elevation
        'file_location': file_location,
        'file_location_out': file_location_out,
        'threading_enabled': True
    }
    test_time = datetime(2023, 6, 21, 7, 0) # local time

    # ### READ ORIGINAL RASTER #####################################################
    
    dem = rasterio.open(
        dem_location,
        mode = 'r',
        driver='GTiff'
    )    
    in_crs = CRS.from_string(dem.crs.to_string().lower())
    target_crs = CRS.from_string('epsg:4326')
    transform_to_target_crs = Transformer.from_crs(in_crs, target_crs)
    x, y = dem.xy(0, 0)
    lat, lon = transform_to_target_crs.transform(x, y)
    sun_position = get_position(
      test_time,
      lon,
      lat
    )
    dem.close()
    # the test azimuth
    azimuth = math.degrees(sun_position['azimuth'])+180
    altitude = math.degrees(sun_position['altitude'])
    print('lat, lon, azimuth, altitude', lat, lon, azimuth, altitude)
    azimuth = math.floor(azimuth)
    date_longest_N = datetime(2023, 6, 21, 12, 0)
    suntimes = get_times(date_longest_N, lon, lat)
    
    slp_sunrise = get_position(
      suntimes['sunrise'],
      lon,
      lat
    )
    slp_sunset = get_position(
      suntimes['sunset'],
      lon,
      lat
    )
    
    settings['azimuth_min'] = math.floor(math.degrees(slp_sunrise['azimuth'])+180)
    settings['azimuth_max'] = math.ceil(math.degrees(slp_sunset['azimuth'])+180)
    if (azimuth >= settings['azimuth_min'] and azimuth <= settings['azimuth_max']):
        
        alt_filename = file_location_out + '/full_10m/altitudes_azi-' + str(azimuth) + '_ds-' + str(settings['downscale_factor_dem']) + '_da-1.tif'
        alts = rasterio.open(
            alt_filename,
            mode = 'r',
            driver='GTiff'
        ) 
        altitude = math.degrees(sun_position['altitude'])
        shades = is_shade(
            altitude,
            alts
        )
        pyplot.imshow(shades, cmap='pink')
        shade_filename = file_location_out + '/full_10m/shade_azi-' + str(azimuth) + '_alt-' + str(altitude) + '_ds-' + str(settings['downscale_factor_dem']) + '.tif'
        alt_profile = alts.profile.copy()
        shade_file = rasterio.open(
            shade_filename,
            mode = 'w',
            **alt_profile
        )
        shade_file.write(
          np.array(shades).astype(rasterio.float32),
          1
        )
        shade_file.close()
if __name__ == '__main__':
    main()