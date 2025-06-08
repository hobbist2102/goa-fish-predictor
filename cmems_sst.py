import os
from datetime import datetime, timedelta, timezone
from copernicusmarine import subset
import xarray as xr

# Set your CMEMS credentials from environment variables
USERNAME = os.getenv("CMEMS_USER")
PASSWORD = os.getenv("CMEMS_PASS")

# Configuration for the dataset
DATASET_ID = "cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m"
VARIABLES = ["sohtc"]  # Use a list for 'variables'
OUTPUT_DIR = "."
LON_MIN, LON_MAX = 73.5, 75.5
LAT_MIN, LAT_MAX = 14.5, 16.5

# Use a timezone-aware date and subtract lag
date = datetime.now(timezone.utc) - timedelta(days=2)  # CMEMS data is typically available with 1–2 day lag
DATE = date.strftime("%Y-%m-%d")

print("Fetching SST from CMEMS...")

try:
    subset_result = subset(
        username=USERNAME,
        password=PASSWORD,
        dataset_id=DATASET_ID,
        variables=VARIABLES,  # ✅ FIXED HERE
        minimum_longitude=LON_MIN,
        maximum_longitude=LON_MAX,
        minimum_latitude=LAT_MIN,
        maximum_latitude=LAT_MAX,
        start_datetime=DATE,
        end_datetime=DATE,
        output_filename=f"{OUTPUT_DIR}/sst_{DATE}.nc",
    )

    print(f"✅ SST data downloaded: sst_{DATE}.nc")

    # Optional: validate using xarray
    ds = xr.open_dataset(f"{OUTPUT_DIR}/sst_{DATE}.nc")
    print(ds)

except Exception as e:
    print(f"⚠️ CMEMS SST fetch error: {e}")
    print("SST: None")
