# -*- coding: utf-8 -*-
import get_min_altitude_for_azimuth

# dem[y][x]
def get_altitudes_for_azimuth(
        dem_data,
        azimuth,
        d_alt,
        to_crs,
        from_crs,
        get_xy,
        get_index
    ):
    # remember max value    
    elev_max_dem = dem_data.max()
    height = len(dem_data)
    width = len(dem_data[0])
    # altitudes[y][x]
    altitudes = [[0 for column in range(0, width)] for row in range(0, height)] 

    for row in range(0, height):
        for column in range(0, width):
            alt_min = get_min_altitude_for_azimuth.get_min_altitude_for_azimuth(
                dem_data,
                column,
                row,
                azimuth,
                d_alt,
                elev_max_dem,
                to_crs,
                from_crs,
                get_xy,
                get_index
            )
            altitudes[row][column] = alt_min
        
    return altitudes
