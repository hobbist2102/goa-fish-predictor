import os
import requests
import datetime
from copernicus_marine_client import CopernicusMarineClient

# Load credentials from environment (set via Streamlit secrets or OS env)
CMEMS_USER = os.getenv("CMEMS_USER")
CMEMS_PASS = os.getenv("CMEMS_PASS")

# Client setup
client = CopernicusMarineClient(
    username=CMEMS_USER,
    password=CMEMS_PASS,
)

# Dataset ID: Global Ocean Gridded L4 Sea Surface Temperature
# You can change this if you want a different resolution/product
DATASET_ID = "cmems_mod_glo_sst_l4_my_010_012"
VARIABLE = "analysed_sst"

# Define function to download SST for a lat/lon box on a given date
def fetch_sst(lat: float, lon: float, date: datetime.date) -> float:
    try:
        # CMEMS requires bounding box, even if very small
        delta = 0.05
        bbox = {
            "north": lat + delta,
            "south": lat - delta,
            "east": lon + delta,
            "west": lon - delta,
        }

        # Format time window (daily snapshot)
        date_str = date.strftime("%Y-%m-%dT12:00:00")

        # Output path
        out_path = f"sst_{lat}_{lon}_{date.strftime('%Y%m%d')}.nc"

        # Download data
        client.download(
            dataset_id=DATASET_ID,
            variables=[VARIABLE],
            minimum_longitude=bbox["west"],
            maximum_longitude=bbox["east"],
            minimum_latitude=bbox["south"],
            maximum_latitude=bbox["north"],
            start_datetime=date_str,
            end_datetime=date_str,
            output_filename=out_path,
        )

        # Load and parse SST
        import xarray as xr
        ds = xr.open_dataset(out_path)
        sst_array = ds[VARIABLE].values
        sst_value = float(sst_array[0][0][0])  # extract single value
        ds.close()
        os.remove(out_path)
        return sst_value

    except Exception as e:
        print(f"Error fetching SST: {e}")
        return None

# Example call (if running as a script)
if __name__ == "__main__":
    lat, lon = 15.5, 73.8  # Goa coast
    today = datetime.date.today() - datetime.timedelta(days=2)  # CMEMS has a 1–2 day lag
    print("Fetching SST for:", today)
    sst = fetch_sst(lat, lon, today)
    print("SST:", sst, "°C")
