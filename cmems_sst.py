import os
import tempfile
import xarray as xr
from datetime import datetime
import subprocess

# Load credentials from Streamlit secrets (CMEMS)
CMEMS_USER = os.getenv("CMEMS_USER")
CMEMS_PASS = os.getenv("CMEMS_PASS")

# Define dataset URL and constraints
PRODUCT = "SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001"
SERVICE_ID = "GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS"
DATASET_ID = "cmems_mod_glo_phy_anfc_0.083deg_P1D-m"
VARIABLE = "analysed_sst"

LAT_MIN, LAT_MAX = 15.0, 16.0
LON_MIN, LON_MAX = 73.0, 74.0

def fetch_sst():
    """
    Downloads SST NetCDF file for today over Goa and returns mean SST (°C).
    """
    now = datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")

    # Temporary file for SST
    temp_file = tempfile.NamedTemporaryFile(suffix=".nc", delete=False).name

    # Build motuclient command
    cmd = [
        "motuclient",
        "--motu", "https://nrt.cmems-du.eu/motu-web/Motu",
        "--service-id", SERVICE_ID,
        "--product-id", PRODUCT,
        "--username", CMEMS_USER,
        "--password", CMEMS_PASS,
        "--longitude-min", str(LON_MIN),
        "--longitude-max", str(LON_MAX),
        "--latitude-min", str(LAT_MIN),
        "--latitude-max", str(LAT_MAX),
        "--date-min", f"{date_str} 00:00:00",
        "--date-max", f"{date_str} 23:59:59",
        "--variable", VARIABLE,
        "--out-dir", os.path.dirname(temp_file),
        "--out-name", os.path.basename(temp_file)
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        ds = xr.open_dataset(temp_file)
        sst_c = ds[VARIABLE].mean().item() - 273.15  # Convert from K to °C
        return round(sst_c, 2)
    except Exception as e:
        print("⚠️ CMEMS SST fetch failed:", e)
        return None
    finally:
        try:
            os.remove(temp_file)
        except:
            pass
