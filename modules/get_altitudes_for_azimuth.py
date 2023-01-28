# -*- coding: utf-8 -*-
import get_min_altitude_for_azimuth

# dem[y][x]
def get_altitudes_for_azimuth(dem, azimuth, d_alt, to_crs, from_crs):
    # remember max value    
    elev_max_dem = dem.read(1).max()
    
    # altitudes[y][x]
    altitudes = [[0 for column in range(0, dem.width)] for row in range(0, dem.height)] 

    
    for row in range(0, dem.height):
        for column in range(0, dem.width):
            alt_min = get_min_altitude_for_azimuth.get_min_altitude_for_azimuth(
                column,
                row,
                azimuth,
                d_alt,
                dem,
                elev_max_dem,
                to_crs,
                from_crs
            )
            altitudes[row][column] = alt_min
        
    return altitudes
