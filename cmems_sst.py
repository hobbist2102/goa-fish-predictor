import datetime
from copernicusmarine import subset

# Constants
DATASET_ID = "SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001"
VARIABLES = ["analysed_sst"]
AREA = [73.5, 15.0, 74.5, 15.75]  # Goa coast: [west, south, east, north]
DATE = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2)
OUTPUT_FILE = f"sst_{DATE.strftime('%Y%m%d')}.nc"

print("Fetching SST from CMEMS...")
try:
    subset(
        dataset_id=DATASET_ID,
        variables=VARIABLES,
        date=DATE.strftime("%Y-%m-%d"),
        area=AREA,
        output_filename=OUTPUT_FILE,
        overwrite=True
    )
    print(f"✅ SST data saved to {OUTPUT_FILE}")
except Exception as e:
    print(f"❌ CMEMS SST fetch error: {e}")
    print("SST: None")
