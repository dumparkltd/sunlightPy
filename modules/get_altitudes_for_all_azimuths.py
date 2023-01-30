# -*- coding: utf-8 -*-
import time
import math
import numpy as np
import rasterio
from datetime import datetime
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
    if (worker['azimuth'] % 90 > 45):
        d_alt = (worker['dem_res']/ math.sin(math.radians(worker['azimuth'] % 90))) * worker['downscale_factor_alt']
    else: 
        d_alt = (worker['dem_res'] / math.cos(math.radians(worker['azimuth'] % 90))) * worker['downscale_factor_alt']
    
    return get_altitudes_for_azimuth.get_altitudes_for_azimuth(
        worker['dem_data'],
        worker['azimuth'],
        d_alt,
        worker['to_crs'],
        worker['from_crs'],
        worker['get_xy'],
        worker['get_index']
    )
    # return ((worker['azimuth'], 1))

def a_function(a):
    print(a)

def get_altitudes_for_all_azimuths(
        dem_data,
        dem_profile,
        dem_res,
        settings,
        to_crs,
        from_crs,
        get_xy,
        get_index
    ):
    r = range(settings['azimuth_min'], settings['azimuth_max'] + settings['azimuth_step'], settings['azimuth_step'])
    workers = []
    for azimuth in r:
        workers.append({
            'azimuth': azimuth,
            'dem_data': dem_data,
            'dem_res': dem_res,
            'downscale_factor_alt': settings['downscale_factor_alt'],
            'to_crs': to_crs,
            'from_crs': from_crs,
            'get_xy': get_xy,
            'get_index': get_index
        })
    print('workers', len(workers))
    # set up multiprocessing
    # entry point
    results = [];
    # for worker in workers:
    #     results.append(task(worker))
    if (settings['threading_enabled']):
        if __name__ == 'get_altitudes_for_all_azimuths':
            with ProcessPoolExecutor(
                max_workers = cpu_count() - 2
            ) as executor:
                futures = [executor.submit(task, worker) for worker in workers]
                for future in as_completed(futures):
                	# get the result for the next completed task
                    result = future.result() # blocks
                    results.append(result)
    else:
        for worker in workers:
            results.append(task(worker))            
    
    print('results', len(results))
        # for i, azimuth in enumerate(r):

        #     p = Process(
        #         target = get_altitudes_for_azimuth.get_altitudes_for_azimuth, 
        #         args=(
        #             q,
        #             azimuth,
        #             dem_data,
        #             dem_res,
        #             settings,
        #             to_crs,
        #             from_crs,
        #             get_xy,
        #             get_index
        #         )
        #     )
        #     processes.append(p)
        #     p.start()
    
        # for p in processes:
        #     result = q.get() # will block
        #     results.append(result)
    
        # for P in processes:
        #     P.join()
            
            # result[i] = get_altitudes_for_azimuth.get_altitudes_for_azimuth(
            #     dem_data,
            #     azimuth,
            #     d_alt,
            #     to_crs,
            #     from_crs,
            #     get_xy,
            #     get_index
            # )
            # now = datetime.now()
            # current_time = now.strftime("%H:%M:%S")
            # print("Altitudes calculated..." + str(azimuth), current_time)
        
    # ### WRITE ALTITUDES AS individual raster files
    # print('results', results)
    # now = datetime.now()
    # current_time = now.strftime("%H:%M:%S")
    # print("Writing altitudes as raster images..." , current_time)
    # for result in results:    
    #     azimuth, altitudes = result
    #     alt_file = settings.file_location_out \
    #         + "/altitudes_azi-" + str(azimuth) \
    #         + "_ds-" + str(settings.downscale_factor_dem) \
    #         + "_da-" + str(settings.downscale_factor_alt) \
    #         + "_" + str(int(time.time())) + ".tif"
            
    #     alts = rasterio.open(
    #         alt_file,
    #         'w',
    #         **dem_profile
    #     )  
    #     alts.write(
    #       np.array(altitudes).astype(rasterio.float32),
    #       1
    #     )
    #     print("Altitudes written..." + alt_file, current_time)
    #     alts.close()