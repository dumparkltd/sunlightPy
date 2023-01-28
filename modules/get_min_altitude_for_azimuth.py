import math
from nautical_calculations.operations import get_point

# import matplotlib.pyplot as plt

# -*- coding: utf-8 -*-
def get_min_altitude_for_azimuth(column, row, azimuth, d_alt, dem, elev_max_dem, to_crs, from_crs):

    dem_data = dem.read(1)
    # dem[y][x]
    elevation_origin = dem_data[row, column]
    altitude_min = 0
    
    # TODO check for NaN
    if (elevation_origin != 0):
        # figure out transect start in lat/lon
        x, y = dem.xy(row, column)
        lat, lon = to_crs.transform(x, y)
        # calculate maximum possible difference in elevation
        d_vert_max = elev_max_dem - elevation_origin
        i = 0
        while True:
            i = i + 1
            d_horiz_i = d_alt * i
            lat_i, lon_i = get_point(lat, lon, azimuth, d_horiz_i / 1000) # to km!
            x_i, y_i = from_crs.transform(lat_i, lon_i)
            row_i, column_i = dem.index(x_i, y_i)
            if (row_i >= 0 and row_i < dem.height and column_i >= 0 and column_i < dem.width):
                elev_i = dem_data[row_i, column_i]
                d_vert_i = elev_i - elevation_origin
                if (d_vert_i > 0 and d_horiz_i != 0):
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
            else:
                break
                     
    return altitude_min
