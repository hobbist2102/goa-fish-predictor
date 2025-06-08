import os
import datetime
from datetime import timezone, timedelta
import xarray as xr
from copernicusmarine import open_dataset

# Get credentials from environment
CMEMS_USER = os.environ.get("CMEMS_USER")
CMEMS_PASS = os.environ.get("CMEMS_PASS")

# Use a timezone-aware UTC date
date = datetime.datetime.now(timezone.utc) - timedelta(days=2)
date_str = date.strftime("%Y-%m-%d")
year = date.strftime("%Y")
month = date.strftime("%m")

print("Fetching SST from CMEMS...")

try:
    ds = open_dataset(
        dataset_id="SST_GLO_SST_L4_REP_OBSERVATIONS_010_011",
        username=CMEMS_USER,
        password=CMEMS_PASS,
        variables=["analysed_sst"],
        minimum_longitude=72.5,
        maximum_longitude=74.5,
        minimum_latitude=14.0,
        maximum_latitude=16.5,
        start_datetime=date_str,
        end_datetime=date_str,
    )

    output_file = f"sst_{date.strftime('%Y%m%d')}.nc"
    ds.to_netcdf(output_file)
    print(f"✅ SST saved to {output_file}")

except Exception as e:
    print(f"❌ CMEMS SST fetch error: {e}")
