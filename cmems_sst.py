import os
from datetime import datetime, timedelta, timezone
import logging
from copernicusmarine import open_dataset, set_credentials

# Configure logging
logging.basicConfig(level=logging.INFO)

# === 1. CMEMS Credentials ===
CMEMS_USER = os.getenv("CMEMS_USER")
CMEMS_PASS = os.getenv("CMEMS_PASS")

if not CMEMS_USER or not CMEMS_PASS:
    raise ValueError("CMEMS_USER or CMEMS_PASS not found in environment variables.")

set_credentials(username=CMEMS_USER, password=CMEMS_PASS)

# === 2. Dataset Selection ===
# Using Reprocessed SST for Global: https://data.marine.copernicus.eu/product/SST_GLO_SST_L4_REP_OBSERVATIONS_010_011
DATASET_ID = "SST_GLO_SST_L4_REP_OBSERVATIONS_010_011"

# === 3. Time Range ===
date = datetime.now(timezone.utc) - timedelta(days=5)
start_date = date.strftime("%Y-%m-%dT00:00:00")
end_date = date.strftime("%Y-%m-%dT23:59:59")

# === 4. Goa Region ===
# (Lat, Lon) box around Goa: [South, North, West, East]
BBOX = [14.8, 15.8, 73.6, 74.4]

# === 5. Output File ===
output_file = f"sst_{date.strftime('%Y%m%d')}.nc"

try:
    logging.info("Fetching SST from CMEMS...")
    ds = open_dataset(
        dataset_id=DATASET_ID,
        start_datetime=start_date,
        end_datetime=end_date,
        bbox=BBOX,
        variables=["analysed_sst"],
    )
    ds.to_netcdf(output_file)
    logging.info(f"SST data saved to: {output_file}")
except Exception as e:
    logging.error(f"❌ CMEMS SST fetch error: {e}")
