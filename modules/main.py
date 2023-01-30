
import rasterio
# from rasterio.enums import Resampling
from pyproj import CRS, Transformer
from datetime import datetime
import time
import numpy as np
from suncalc import get_position, get_times
import math
from multiprocessing import cpu_count
from concurrent.futures import as_completed, ProcessPoolExecutor

import get_altitudes_for_azimuth 

def task(worker):

    # azimuth, dem_data, dem_res, downscale_factor_alt, to_crs, from_crs,get_xy, get_index = worker
    # print('azimuth', azimuth)
    # print('dem_data', dem_data)
    # now = datetime.now()
    # current_time = now.strftime("%H:%M:%S")
    # print("Altitudes for azimuth: " + str(azimuth), current_time)
    
    dst = rasterio.open(
        worker['file_location_dem'],
        mode = 'r',
        driver='GTiff'
    )
    in_crs = CRS.from_proj4(dst.crs.to_proj4())
    target_crs = CRS.from_string('epsg:4326')
    transform_to_target_crs = Transformer.from_crs(in_crs, target_crs)
    transform_from_target_crs = Transformer.from_crs(target_crs, in_crs)
    get_xy = dst.xy
    get_index = dst.index
    dst_res = min(dst.res);
    if (worker['azimuth'] % 90 > 45):
        d_alt = (dst_res / math.sin(math.radians(worker['azimuth'] % 90))) * worker['downscale_factor_alt']
    else: 
        d_alt = (dst_res / math.cos(math.radians(worker['azimuth'] % 90))) * worker['downscale_factor_alt']
    
    alts = get_altitudes_for_azimuth.get_altitudes_for_azimuth(
        dst.read(1),
        worker['azimuth'],
        d_alt,
        transform_to_target_crs,
        transform_from_target_crs,
        get_xy,
        get_index
    )
    dst.close()
    return (worker['azimuth'], alts)

def main():   
    ### VARIABLES
    file_location = "c:/users/timo/documents/projects/inrae/data"
    file_location_out = file_location + '/tmp'
    dem_location = file_location + '/raster1.tif'
    settings =  {
        'azimuth_min': 246, # adjusted to local range below
        'azimuth_max': 246, # adjusted to local range below
        'azimuth_step': 10,
        'downscale_factor_dem': 10, # downsample dem resolution
        'downscale_factor_alt': 1, # distances between points for sampling elevation
        'file_location': file_location,
        'file_location_out': file_location_out,
        'threading_enabled': True
    } 
    
    # now = datetime.now()
    # current_time = now.strftime("%H:%M:%S")
    # print("Start..." + "downscale_factor: " + str(settings['downscale_factor_dem']), current_time)
    
    # ### READ ORIGINAL RASTER #####################################################
    
    dem = rasterio.open(
        dem_location,
        mode = 'r',
        driver='GTiff'
    )
    
    # ### DOWNSAMPLE RASTER #####################################################
    
    # # resample data to target shape
    # dem_small = dem.read(
    #     out_shape=(
    #         dem.count,
    #         int(dem.height / settings['downscale_factor_dem']),
    #         int(dem.width / settings['downscale_factor_dem'])
    #     ),
    #     resampling=Resampling.bilinear
    # )
    
    # # scale image transform
    # dst_transform = dem.transform * dem.transform.scale(
    #     (dem.width / dem_small.shape[-1]),
    #     (dem.height / dem_small.shape[-2])
    # )
    
    # # Write outputs
    # # set properties for output
    # dem_small_args = dem.meta.copy()
    # dem_small_args.update(
    #     {
    #         "crs": dem.crs,
    #         "transform": dst_transform,
    #         "width": dem_small.shape[-1],
    #         "height": dem_small.shape[-2],
    #         "nodata": dem.nodata,  
    #     }
    # )
    
    # dem.close()
    
    dem_small_file = file_location_out \
    + "/tmp_ds-" + str(settings['downscale_factor_dem']) \
    + ".tif"
    
    # dst = rasterio.open(dem_small_file, "w", **dem_small_args)
    # # iterate through bands
    # for i in range(dem_small.shape[0]):
    #     dst.write(dem_small[i].astype(rasterio.uint32), i+1)
    # dst.close()
    
    # dst[y][x]
    # dst = rasterio.open(
    #     dem_small_file,
    #     mode = 'r',
    #     driver='GTiff'
    # )
    # now = datetime.now()
    # current_time = now.strftime("%H:%M:%S")
    # print("Resample complete..." + dem_small_file, current_time)
    
    ### RE-PROJECTION ###########################################################
    
    in_crs = CRS.from_proj4(dem.crs.to_proj4())
    target_crs = CRS.from_string('epsg:4326')
    transform_to_target_crs = Transformer.from_crs(in_crs, target_crs)
    # transform_from_target_crs = Transformer.from_crs(target_crs, in_crs)
    
    
    ### GET SUN RISE SUN SET TIMES ###########################################################
    
    x, y = dem.xy(0, 0)
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
    
    settings['azimuth_min'] = math.floor(math.degrees(slp_sunrise['azimuth'])+180)
    settings['azimuth_max'] = math.ceil(math.degrees(slp_sunset['azimuth'])+180)
    
    print ('azimuth range: ', str(settings['azimuth_min']), str(settings['azimuth_max']))
    dem.close()
    ### CALCULATE ALTITUDES FOR AZIMUTH ########################################
    
    # get_xy = dst.xy
    # get_index = dst.index
    r = range(settings['azimuth_min'], settings['azimuth_max'] + settings['azimuth_step'], settings['azimuth_step'])
    workers = []
    for azimuth in r:
        workers.append({
            'azimuth': azimuth,
            'file_location_dem': dem_small_file,
            'downscale_factor_alt': settings['downscale_factor_alt'],
        })
#    results = [];
    # for worker in workers:
    #     results.append(task(worker))
    if (settings['threading_enabled']):
        with ProcessPoolExecutor(
            max_workers = cpu_count() - 2
        ) as executor:
            futures = [executor.submit(task, worker) for worker in workers]
            for future in as_completed(futures):
            	# get the result for the next completed task
                result = future.result() # blocks
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                # print("Altitudes complete...", current_time)
                ### WRITE ALTITUDES AS individual raster files
                # print('results', results)
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print("Writing altitudes as raster images..." , current_time)
                dst = rasterio.open(
                    dem_small_file,
                    mode = 'r',
                    driver='GTiff'
                )
                dst_profile = dst.profile.copy()
                dst.close()
                azimuth, altitudes = result
                alt_file = settings['file_location_out'] \
                    + "/altitudes_azi-" + str(azimuth) \
                    + "_ds-" + str(settings['downscale_factor_dem']) \
                    + "_da-" + str(settings['downscale_factor_alt']) \
                    + "_" + str(int(time.time())) + ".tif"
                    
                alts = rasterio.open(
                    alt_file,
                    'w',
                    **dst_profile
                )  
                alts.write(
                  np.array(altitudes).astype(rasterio.float32),
                  1
                )
                # print("Altitudes written..." + alt_file, current_time)
                alts.close()
    # get_altitudes_for_all_azimuths.get_altitudes_for_all_azimuths(
    #     dst.read(1),
    #     dst.profile.copy(),
    #     min(dst.res),
    #     settings,
    #     transform_to_target_crs,
    #     transform_from_target_crs,
    #     get_xy,
    #     get_index
    # )
    
    
    # dst.close()
# print(altitudes)

if __name__ == '__main__':
    main()