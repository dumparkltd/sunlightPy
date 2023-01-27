import math
from nautical_calculations.operations import get_point

# import matplotlib.pyplot as plt

# -*- coding: utf-8 -*-
desample_factor = 10

def get_min_altitude_for_azimuth(column, row, azimuth, dem, elev_max_dem, to_crs, from_crs):

    dem_data = dem.read(1)
    # dem[y][x]
    elevation_origin = dem_data[row, column]
    altitude_min = 0
    
    # TODO check for NaN
    if (elevation_origin != 0):
        # figure out transect start in lat/lon
        res_x = dem.res[1]
        res_y = dem.res[0]

        x, y = dem.xy(row, column)
        lat, lon = to_crs.transform(x, y)
        # figure out transect end in lat/lon, using max length of dem
        # WARNING assumes dem units of meters/m
        max_length = max(abs(dem.bounds.left - dem.bounds.right), abs(dem.bounds.top - dem.bounds.bottom))
        # returns the coordinate (lat1,long1) at a particular distance and angle (azimuth) from the given point (lat,long
        lat2, lon2 = get_point(lat, lon, azimuth, max_length / 1000) # to km!

        # sample interval based on resolution
        d_s = min(res_x, res_y) # same as min(dem.res[0], dem.res[1])
        # steps
        n = int(math.ceil(max_length / d_s))
        
        # calculate maximum possible difference in elevation
        d_vert_max = elev_max_dem - elevation_origin
            
        for i in range(n):
            if (i > 0):
                d_horiz_i = d_s * i * desample_factor
                lat_i, lon_i = get_point(lat, lon, azimuth, d_horiz_i / 1000) # to km!
                x_i, y_i = from_crs.transform(lat_i, lon_i)
                row_i, column_i = dem.index(x_i, y_i)
                if (row_i < dem.height and column_i < dem.width):
                    elev_i = dem_data[row_i, column_i]
                    d_vert_i = elev_i - elevation_origin
                    if (d_vert_i > 0):
                        if (d_horiz_i != 0):
                        # calculate angle
                            altitude_target = math.degrees(math.atan(d_vert_i/d_horiz_i))
                            # remember angle if greater than previous
                            if (altitude_target > altitude_min):
                                altitude_min = altitude_target
                            else:
                                # check if higher altitude is feasible
                                altitude_max = math.degrees(math.atan(d_vert_max/d_horiz_i))
                                if (altitude_max < altitude_min):
                                    break
                        
    return altitude_min
