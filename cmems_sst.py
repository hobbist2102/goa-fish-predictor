import os
from datetime import datetime, timedelta, timezone
from copernicusmarine import subset
import xarray as xr

USERNAME = os.getenv("CMEMS_USER")
PASSWORD = os.getenv("CMEMS_PASS")

DATASET_ID = "GLOBAL_ANALYSISFORECAST_PHY_001_024"
VARIABLES = ["thetao"]
LAT, LON = 15.5, 73.8  # Goa
DELTA = 0.05

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
        minimum_longitude=LON - DELTA,
        maximum_longitude=LON + DELTA,
        minimum_latitude=LAT - DELTA,
        maximum_latitude=LAT + DELTA,
        start_datetime=DATE_STR,
        end_datetime=DATE_STR,
        output_filename=OUT_FILE,
        overwrite=True,
    )
    ds = xr.open_dataset(OUT_FILE)
    sst_value = float(ds["thetao"].isel(depth=0).mean().item())
    ds.close()
    print(f"✅ SST processed: {sst_value:.2f} °C")
    # keep file for app use
except Exception as e:
    print(f"❌ CMEMS SST fetch error: {e}")
