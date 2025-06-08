import copernicusmarine
import xarray as xr
import os
from datetime import datetime, timedelta

# Load credentials from GitHub Actions environment (set via GitHub Secrets)
CMEMS_USER = os.getenv("CMEMS_USER")
CMEMS_PASS = os.getenv("CMEMS_PASS")

copernicusmarine.set_credentials(username=CMEMS_USER, password=CMEMS_PASS)

# New valid CMEMS cloud-native dataset ID
DATASET_ID = "cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m"
VARIABLE = "thetao"  # temperature

LAT, LON = 15.5, 73.8  # Goa
DELTA = 0.05  # bounding box margin

def fetch_sst(date: datetime):
    try:
        print("Fetching SST from CMEMS...")

        bbox = {
            "north": LAT + DELTA,
            "south": LAT - DELTA,
            "east": LON + DELTA,
            "west": LON - DELTA,
        }

        # Cloud-native API call with correct variable and dimensions
        result = copernicusmarine.subset(
            dataset_id=DATASET_ID,
            variables=[VARIABLE],
            minimum_longitude=bbox["west"],
            maximum_longitude=bbox["east"],
            minimum_latitude=bbox["south"],
            maximum_latitude=bbox["north"],
            start_datetime=date,
            end_datetime=date,
            output_filename="sst_result.nc",
            overwrite=True
        )

        ds = xr.open_dataset("sst_result.nc")
        temp = ds[VARIABLE].isel(depth=0).mean().item()
        ds.close()
        os.remove("sst_result.nc")

        print(f"SST: {temp:.2f} °C")
        return temp

    except Exception as e:
        print(f"⚠️ CMEMS SST fetch error: {e}")
        return None

if __name__ == "__main__":
    today = datetime.utcnow() - timedelta(days=2)  # safest delay
    fetch_sst(today)
