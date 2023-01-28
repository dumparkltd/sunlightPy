
import rasterio
from rasterio.enums import Resampling
from pyproj import CRS, Transformer
from datetime import datetime
from suncalc import get_position, get_times
import math

import get_altitudes_for_all_azimuths
  
### VARIABLES
fileLocation = "c:/users/timo/documents/projects/inrae/data"
fileLocationTmp = fileLocation + '/tmp'

settings =  type(
    'obj', 
    (object,),
    {
        'azimuth_min': 246, # adjusted to local range below
        'azimuth_max': 246, # adjusted to local range below
        'azimuth_step': 10,
        'downscale_factor_dem': 25, # downsample dem resolution
        'downscale_factor_alt': 1, # distances between points for sampling elevation
        'fileLocation': fileLocation,
        'fileLocationTmp': fileLocationTmp
    }
) 

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Start..." + "downscale_factor: " + str(settings.downscale_factor_dem), current_time)

### READ ORIGINAL RASTER #####################################################

dem = rasterio.open(
    fileLocation + '/raster1.tif',
    mode = 'r',
    driver='GTiff'
)

### DOWNSAMPLE RASTER #####################################################

# resample data to target shape
dem_small = dem.read(
    out_shape=(
        dem.count,
        int(dem.height / settings.downscale_factor_dem),
        int(dem.width / settings.downscale_factor_dem)
    ),
    resampling=Resampling.bilinear
)

# scale image transform
dst_transform = dem.transform * dem.transform.scale(
    (dem.width / dem_small.shape[-1]),
    (dem.height / dem_small.shape[-2])
)

# Write outputs
# set properties for output
dem_small_args = dem.meta.copy()
dem_small_args.update(
    {
        "crs": dem.crs,
        "transform": dst_transform,
        "width": dem_small.shape[-1],
        "height": dem_small.shape[-2],
        "nodata": dem.nodata,  
    }
)

dem.close()

dem_small_file = fileLocationTmp \
+ "/tmp_ds-" + str(settings.downscale_factor_dem) \
+ ".tif"

print(dem_small_file)
dst = rasterio.open(dem_small_file, "w", **dem_small_args)
# iterate through bands
for i in range(dem_small.shape[0]):
    dst.write(dem_small[i].astype(rasterio.uint32), i+1)
dst.close()

# dst[y][x]
dst = rasterio.open(
    dem_small_file,
    mode = 'r',
    driver='GTiff'
)
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Resample complete..." + dem_small_file, current_time)

### RE-PROJECTION ###########################################################

in_crs = CRS.from_proj4(dst.crs.to_proj4())
target_crs = CRS.from_string('epsg:4326')
transform_to_target_crs = Transformer.from_crs(in_crs, target_crs)
transform_from_target_crs = Transformer.from_crs(target_crs, in_crs)


### GET SUN RISE SUN SET TIMES ###########################################################

x, y = dst.xy(0, 0)
lat, lon = transform_to_target_crs.transform(x, y)
# WARNING N Hemisphere only
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

settings.azimuth_min = math.floor(math.degrees(slp_sunrise['azimuth'])+180)
settings.azimuth_max = math.ceil(math.degrees(slp_sunset['azimuth'])+180)

print ('azimuth range: ', str(settings.azimuth_min), str(settings.azimuth_max))

### CALCULATE ALTITUDES FOR AZIMUTH ########################################

get_altitudes_for_all_azimuths.get_altitudes_for_all_azimuths(
    dst,
    settings,
    transform_to_target_crs,
    transform_from_target_crs
)

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Altitudes complete...", current_time)

dst.close()
# print(altitudes)