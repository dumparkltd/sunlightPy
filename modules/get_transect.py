import math
from nautical_calculations.operations import get_point

# dem[y][x]
def get_transect(column, row, azimuth, dem, to_crs, from_crs):
    dem_data = dem.read(1)
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
    # figure out transect sample points
    viewpoints = []
    
    for i in range(n):
        if (i > 0):
            d_i = d_s * i
            lat_i, lon_i = get_point(lat, lon, azimuth, d_i / 1000) # to km!
            x_i, y_i = from_crs.transform(lat_i, lon_i)
            row_i, column_i = dem.index(x_i, y_i)
            if (row_i < dem.height and column_i < dem.width):
                elev_i = dem_data[row_i, column_i]
                viewpoints.append(
                    type(
                        'obj', 
                        (object,), 
                        {
                            'lat' : lat_i,
                            'lon': lon_i,
                            'x': x_i,
                            'y': y_i,
                            'row_i': row_i,
                            'column_i': column_i,
                            'distance': d_i,
                            'elevation': elev_i
                        }
                    )
                )

    return viewpoints