import copernicusmarine
import xarray as xr
import os
from datetime import datetime, timedelta

CMEMS_USER = os.getenv("CMEMS_USER")
CMEMS_PASS = os.getenv("CMEMS_PASS")

# ✅ Working dataset for ocean temperature (thetao = SST at depth=0)
DATASET_ID = "cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m"
VARIABLE = "thetao"
LAT, LON = 15.5, 73.8
DELTA = 0.05

def fetch_sst(date: datetime):
    try:
        print("Fetching SST from CMEMS...")

        bbox = {
            "north": LAT + DELTA,
            "south": LAT - DELTA,
            "east": LON + DELTA,
            "west": LON - DELTA,
        }

        output_file = "sst_result.nc"

        copernicusmarine.subset(
            dataset_id=DATASET_ID,
            variables=[VARIABLE],
            minimum_longitude=bbox["west"],
            maximum_longitude=bbox["east"],
            minimum_latitude=bbox["south"],
            maximum_latitude=bbox["north"],
            start_datetime=date,
            end_datetime=date,
            output_filename=output_file,
            overwrite=True,
            username=CMEMS_USER,
            password=CMEMS_PASS
        )

        ds = xr.open_dataset(output_file)
        sst_value = ds[VARIABLE].isel(depth=0).mean().item()
        ds.close()
        os.remove(output_file)

        print(f"✅ SST: {sst_value:.2f} °C")
        return sst_value

    except Exception as e:
        print(f"⚠️ CMEMS SST fetch error: {e}")
        return None

if __name__ == "__main__":
    date = datetime.utcnow() - timedelta(days=2)  # CMEMS data lag
    fetch_sst(date)
