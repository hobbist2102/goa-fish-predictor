import os
from datetime import datetime, timedelta, timezone
from copernicusmarine import subset
import xarray as xr

USERNAME = os.getenv("CMEMS_USER")
PASSWORD = os.getenv("CMEMS_PASS")

DATASET_ID = "SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001"  # OSTIA global SST
VARIABLES = ["analysed_sst"]
LON_MIN, LON_MAX = 73.5, 75.5
LAT_MIN, LAT_MAX = 14.5, 16.5

date = datetime.now(timezone.utc) - timedelta(days=1)
DATE_STR = date.strftime("%Y-%m-%d")
OUT_FILE = f"sst_{DATE_STR}.nc"

print("Fetching SST from CMEMS...")

try:
    subset(
        username=USERNAME,
        password=PASSWORD,
        dataset_id=DATASET_ID,
        variables=VARIABLES,
        minimum_longitude=LON_MIN,
        maximum_longitude=LON_MAX,
        minimum_latitude=LAT_MIN,
        maximum_latitude=LAT_MAX,
        start_datetime=DATE_STR,
        end_datetime=DATE_STR,
        output_filename=OUT_FILE,
        overwrite=True,
    )
    ds = xr.open_dataset(OUT_FILE)
    print(ds)
    ds.close()
    print(f"✅ SST file saved: {OUT_FILE}")
except Exception as e:
    print(f"❌ CMEMS error: {e}")
