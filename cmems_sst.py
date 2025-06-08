from copernicusmarine import open_dataset
import os
from datetime import datetime, timedelta

# Credentials from GitHub Secrets (set in workflow)
CMEMS_USER = os.getenv("CMEMS_USER")
CMEMS_PASS = os.getenv("CMEMS_PASS")

# Use a 2-day lag for freshest available data
date = datetime.utcnow() - timedelta(days=2)
date_str = date.strftime('%Y-%m-%d')

# Dataset ID — confirmed from CMEMS catalogue
dataset_id = "SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001"

# Goa bounding box
bbox = [73.5, 14.8, 74.5, 15.8]  # [west, south, east, north]

# Output filename
output_file = f"sst_{date_str}.nc"

try:
    print("Fetching SST from CMEMS...")

    ds = (
        open_dataset(dataset_id, credentials=(CMEMS_USER, CMEMS_PASS))
        .filter(time=date_str)
        .filter(variables=["analysed_sst"])
        .filter(bbox=bbox)
        .to_xarray()
    )

    ds.to_netcdf(output_file)
    print(f"✅ SST data saved to {output_file}")

except Exception as e:
    print(f"❌ CMEMS SST fetch error: {e}")
