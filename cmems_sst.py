import os
import copernicusmarine
from datetime import datetime, timedelta

# Optional: Log progress
print("Fetching SST from CMEMS...")

# Parameters
DATASET_ID = "SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001"
VARIABLES = ["analysed_sst"]
LONGITUDE = (73.5, 74.5)     # Adjust to your Goa area
LATITUDE = (14.5, 15.5)
OUTPUT_DIR = "data"

# Generate target date (1-2 days back due to lag)
date = datetime.utcnow() - timedelta(days=2)
date_str = date.strftime('%Y%m%d')

# Output file path
output_file = os.path.join(OUTPUT_DIR, f"sst_{date_str}.nc")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fetch data
try:
    copernicusmarine.subset(
        dataset_id=DATASET_ID,
        variables=VARIABLES,
        longitude=LONGITUDE,
        latitude=LATITUDE,
        date=date,
        output_filename=output_file,
        overwrite=True
    )
    print(f"✅ SST saved: {output_file}")
except Exception as e:
    print(f"❌ CMEMS SST fetch error: {e}")
