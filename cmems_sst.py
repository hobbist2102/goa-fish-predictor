from copernicusmarine import open_dataset
from datetime import datetime, timedelta, timezone
import xarray as xr

# Calculate date (2 days lag is typical for CMEMS NRT)
date = datetime.now(timezone.utc) - timedelta(days=2)
date_str = date.strftime("%Y-%m-%d")

# Define dataset ID and variable name
dataset_id = "SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001"

try:
    print("Fetching SST from CMEMS...")

    # Open the dataset
    ds = open_dataset(
        dataset_id,
        minimum_longitude=72.5,
        maximum_longitude=74.5,
        minimum_latitude=14.5,
        maximum_latitude=16.5,
        start_datetime=date_str,
        end_datetime=date_str,
        variables=["analysed_sst"]
    )

    # Inspect the output
    print(ds)
    ds.to_netcdf("sst_{}.nc".format(date_str))
    print("✅ SST data saved successfully.")

except Exception as e:
    print(f"❌ CMEMS SST fetch error: {e}")
