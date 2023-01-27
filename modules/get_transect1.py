from geographiclib.geodesic import Geodesic
import math

geod = Geodesic.WGS84

# dem[y][x]
def get_transect1(x, y, azimuth, dem, to_crs, from_crs):
    # figure out transect start in lat/lon
    res_x = dem.res[1]
    res_y = dem.res[0]

    y_in, x_in = dem.index(x * res_x * -1, y * res_y)
    x_in = x_in * res_x * -1 
    y_in = y_in * res_y
    if (x == 2 and y == 1):
        print('x,y ', x_in, y_in)
    lat, lon = to_crs.transform(
        x_in,
        y_in
    )
    # figure out transect end in lat/lon, using max length of dem
    max_length = max(abs(dem.bounds.left - dem.bounds.right), abs(dem.bounds.top - dem.bounds.bottom))
    g = geod.Direct(lat, lon, azimuth, max_length)
    lat2 = g['lat2']
    lon2 = g['lon2']
    
    # define transect line
    line = geod.InverseLine(lat, lon, lat2, lon2)
    # sample interval based on resolution
    d_s = min(res_x, res_y) # same as min(dem.res[0], dem.res[1])
    # steps
    n = int(math.ceil(line.s13 / d_s))
    # figure out transect sample points
    viewpoints = []
    viewpoints_xy = []
    viewpoints_lonx_laty = []
    
    if (x == 2 and y == 1):
        print('lat, lon, lat2, lon2, d_s, n', lat, lon, g['lat2'], g['lon2'], d_s, n)
    
    for i in range(n):
        if (i > 0):
            d_i = min(d_s * i, line.s13)

            point_i = line.Position(d_i, Geodesic.STANDARD | Geodesic.LONG_UNROLL)
            x_i, y_i = from_crs.transform(
                point_i['lat2'],
                point_i['lon2']
            )
            if (i < 10 and x == 2 and y == 1):
                print('i, d_i, lat_i, lon_i', i, d_i, point_i['lat2'], point_i['lon2'])
            viewpoints.append(point_i)
            viewpoints_xy.append((x_i, y_i))
            viewpoints_lonx_laty.append((point_i['lon2'], point_i['lat2']))
    elevations = []
    # get elevation for viewpoints
    for elevation in dem.sample(viewpoints_xy, 1, True):
        if (elevation[0] != -3.4e+38):
            # print(elevation[0], elevation[0] != -3.4e+38, elevation[0] == -3.4e+38)
            elevations.append(elevation[0])
        
    return type('obj', (object,), {'points' : viewpoints, 'elevations': elevations}) 