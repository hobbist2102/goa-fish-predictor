import os
import datetime
import xarray as xr
import copernicusmarine

# Credentials from Streamlit secrets or OS environment
CMEMS_USER = os.getenv("CMEMS_USER")
CMEMS_PASS = os.getenv("CMEMS_PASS")

# Configure credentials
copernicusmarine.set_credentials(username=CMEMS_USER, password=CMEMS_PASS)

# Dataset and variable configuration
DATASET_ID = "cmems_mod_glo_phy_my_0.25_P1D-m"  # Global Physical Ocean
VARIABLES = ["thetao"]  # Sea Temperature
DELTA = 0.05  # Latitude/Longitude bounding box delta

def fetch_sst(lat: float, lon: float, date: datetime.date) -> float:
    try:
        bbox = (lon - DELTA, lon + DELTA), (lat - DELTA, lat + DELTA)
        output_path = f"sst_{lat}_{lon}_{date.strftime('%Y%m%d')}_subset.nc"

        # Download subset
        copernicusmarine.subset(
            dataset_id=DATASET_ID,
            variables=VARIABLES,
            longitude=bbox[0],
            latitude=bbox[1],
            date=date,
            output_filename=output_path,
            overwrite=True,
        )

        # Extract SST
        ds = xr.open_dataset(output_path)
        sst_array = ds[VARIABLES[0]].values
        sst_value = float(sst_array[0][0][0])  # 3D data
        ds.close()
        os.remove(output_path)
        return sst_value

    except Exception as e:
        print(f"⚠️ Error fetching SST: {e}")
        return None

# Standalone test
if __name__ == "__main__":
    today = datetime.date.today() - datetime.timedelta(days=2)
    lat, lon = 15.5, 73.8  # Goa coast
    print("Fetching SST...")
    print("Result:", fetch_sst(lat, lon, today), "°C")
