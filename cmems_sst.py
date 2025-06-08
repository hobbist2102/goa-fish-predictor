import datetime
from datetime import timedelta
import logging
from copernicusmarine import open_dataset

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Use timezone-aware UTC datetime (avoid deprecation)
date = datetime.datetime.now(datetime.timezone.utc) - timedelta(days=2)
date_str = date.strftime('%Y-%m-%d')

logging.info("Fetching SST from CMEMS...")

try:
    ds = open_dataset(
        dataset_id="SST_GLO_SST_L4_REP_OBSERVATIONS_010_011",
        minimum_longitude=72.5,
        maximum_longitude=74.5,
        minimum_latitude=14.5,
        maximum_latitude=16.5,
        start_datetime=date_str,
        end_datetime=date_str,
    )
    output_filename = f"sst_{date_str}.nc"
    ds.to_netcdf(output_filename)
    logging.info(f"✅ SST data saved to {output_filename}")
except Exception as e:
    logging.error(f"❌ CMEMS SST fetch error: {e}")
    logging.info("SST: None")
