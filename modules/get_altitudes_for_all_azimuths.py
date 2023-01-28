# -*- coding: utf-8 -*-
import time
import math
import numpy as np
import rasterio
from datetime import datetime

import get_altitudes_for_azimuth 

def get_altitudes_for_all_azimuths(
        dem,
        settings,
        to_crs,
        from_crs
    ):
    
    # figure out optimal step for sampling altitudes
    res_min = min(dem.res)
    
    for azimuth in range(settings.azimuth_min, settings.azimuth_max + settings.azimuth_step, settings.azimuth_step):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Altitudes for azimuth: " + str(azimuth), current_time)
        if (azimuth % 90 > 45):
            d_alt = (res_min / math.sin(math.radians(azimuth % 90))) * settings.downscale_factor_alt
        else: 
            d_alt = (res_min / math.cos(math.radians(azimuth % 90))) * settings.downscale_factor_alt
        
        altitudes = get_altitudes_for_azimuth.get_altitudes_for_azimuth(
            dem,
            azimuth,
            d_alt,
            to_crs,
            from_crs
        )
        
        
        ### WRITE ALTITUDES AS RASTER
        
        alt_file = settings.fileLocationTmp \
            + "/altitudes_azi-" + str(azimuth) \
            + "_ds-" + str(settings.downscale_factor_dem) \
            + "_da-" + str(settings.downscale_factor_alt) \
            + "_" + str(int(time.time())) + ".tif"
            
        profile = dem.profile.copy()
        alts = rasterio.open(
            alt_file,
            'w',
            **profile
        )  
        alts.write(
          np.array(altitudes).astype(rasterio.float32),
          1
        )
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Altitudes written..." + alt_file, current_time)
        alts.close()