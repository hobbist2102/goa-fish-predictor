import os
import datetime
import xarray as xr
from copernicusmarine import subset

# Credentials come from ~/.netrc written in GitHub Actions
# Dataset details
DATASET_ID = "SST_GLO_SST_L4_REP_OBSERVATIONS_010_011"
VARIABLES = ["analysed_sst"]
LAT = 15.5
LON = 73.8
DELTA = 0.05
DATE = datetime.datetime.utcnow() - datetime.timedelta(days=2)

# Bounding box
BBOX = {
    "north": LAT + DELTA,
    "south": LAT - DELTA,
    "east": LON + DELTA,
    "west": LON - DELTA,
}
OUTPUT_FILENAME = f"sst_{LAT}_{LON}_{DATE.strftime('%Y%m%d')}.nc"

print("Fetching SST from CMEMS...")

try:
    subset(
        dataset_id=DATASET_ID,
        variables=VARIABLES,
        bounding_box={
            "north": BBOX["north"],
            "south": BBOX["south"],
            "east": BBOX["east"],
            "west": BBOX["west"],
        },
        date=DATE,
        output_filename=OUTPUT_FILENAME,
        overwrite=True,
    )

    ds = xr.open_dataset(OUTPUT_FILENAME)
    value = float(ds[VARIABLES[0]].isel(time=0).mean().values)
    print(f"SST for {DATE.date()}: {value:.2f} °C")
    ds.close()

except Exception as e:
    print(f"❌ CMEMS SST fetch error: {e}")
    print("SST: None")
