import copernicusmarine
import os
from datetime import datetime, timedelta

# Set date to 2 days ago (data lag)
date = datetime.utcnow() - timedelta(days=2)
date_str = date.strftime('%Y-%m-%d')

# Dataset info for global SST
dataset_id = "SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001"
variables = ["analysed_sst"]

# Goa bounding box
bbox = [73.5, 14.8, 74.5, 15.8]  # [lon_min, lat_min, lon_max, lat_max]

# Output path
output_file = f"sst_{date_str}.nc"

try:
    print("Fetching SST from CMEMS...")

    copernicusmarine.subset(
        dataset_id=dataset_id,
        variables=variables,
        bounding_box=bbox,
        date=date_str,
        output_filename=output_file,
        overwrite=True
    )

    print(f"✅ SST saved to {output_file}")
except Exception as e:
    print(f"❌ CMEMS SST fetch error: {e}")
