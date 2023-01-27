import rasterio
from rasterio.enums import Resampling
from pyproj import CRS, Transformer
import numpy as np
from datetime import datetime
import time

import get_altitudes_for_azimuth 
  
### VARIABLES

azimuth = 90
downscale_factor_dem = 10
downscale_factor_alt = 10

fileLocation = "c:/users/timo/documents/projects/inrae/data"
fileLocationTmp = fileLocation + '/tmp'

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Start..." + "downscale_factor: " + str(downscale_factor_dem), current_time)

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
        int(dem.height / downscale_factor_dem),
        int(dem.width / downscale_factor_dem)
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
+ "/tmp_" + str(azimuth) \
+ "_ds-" + str(downscale_factor_dem) \
+ "_da-" + str(downscale_factor_alt) \
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

### CALCULATE ALTITUDES FOR AZIMUTH ########################################

altitudes = get_altitudes_for_azimuth.get_altitudes_for_azimuth(
    dst,
    azimuth,
    transform_to_target_crs,
    transform_from_target_crs,
    downscale_factor_alt
)

# print(altitudes)
# print(dst.read())

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Altitudes complete...", current_time)

### WRITE ALTITUDES AS RASTER

alt_file = fileLocationTmp \
    + "/altitudes_azi-" + str(azimuth) \
    + "_ds-" + str(downscale_factor_dem) \
    + "_da-" + str(downscale_factor_alt) \
    + "_" + str(int(time.time())) + ".tif"
    
profile = dst.profile.copy()
alts = rasterio.open(
    alt_file,
    'w',
    **profile
)  
alts.write(
  np.array(altitudes).astype(rasterio.float32),
  1
)
print("Altitudes written..." + alt_file, current_time)

alts.close()
dst.close()
# print(altitudes)