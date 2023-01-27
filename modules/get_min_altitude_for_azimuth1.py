import get_transect
import math
# import matplotlib.pyplot as plt

# -*- coding: utf-8 -*-

def get_min_altitude_for_azimuth(x, y, azimuth, dem, to_crs, from_crs):

    dem_data = dem.read(1)
    # dem[y][x]
    elevation_origin = dem_data[y,x]
    altitude_min = 0
    
    # TODO check for NaN
    if (elevation_origin != 0):
        elev_max_dem = dem_data.max()
        # calculate maximum possible difference in elevation
        d_vert_max = elev_max_dem - elevation_origin
            
        # sample transect
        transect = get_transect.get_transect(x, y, azimuth, dem, to_crs, from_crs)
        # {
        #   points: array of {'lat1': 42.86762204107126, 'lon1': 0.787002789558168, 'azi1': 89.9999999999958, 's12': 5985.0, 'a12': 0.05386140416146371, 'lat2': 42.86759861503738, 'lon2': 0.8602444219875206, 'azi2': 90.04982677317973},
        #   elevations: array of elevations sampled at coordinates (excluding no data values)
        # }
        
        points = transect.points
        elevations = transect.elevations

        # set minimum solar altitude
        for i, elevation in enumerate(elevations):
            d_vert = elevation - elevation_origin
            if (d_vert > 0):
                point = points[i]
                d_horiz = point["s12"]
                if (d_horiz != 0):
                # calculate angle
                    altitude_target = math.degrees(math.atan(d_vert/d_horiz))
                    # remember angle if greater than previous
                    if (altitude_target > altitude_min):
                        altitude_min = altitude_target
                    else:
                        altitude_max = math.degrees(math.atan(d_vert_max/d_horiz))
                        if (altitude_max < altitude_min):
                            break

    return altitude_min
