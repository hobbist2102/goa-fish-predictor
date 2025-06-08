import os
import datetime
import xarray as xr
import copernicusmarine

DATASET_ID = "cmems_mod_glo_phy_my_0.25_P1D-m"
VARIABLE = "thetao"
DELTA = 0.05

def fetch_sst(lat=15.5, lon=73.8, date=None):
    if not date:
        date = datetime.date.today() - datetime.timedelta(days=2)

    lon_min, lon_max = lon - DELTA, lon + DELTA
    lat_min, lat_max = lat - DELTA, lat + DELTA
    out_file = f"sst_{lat}_{lon}_{date.strftime('%Y%m%d')}.nc"

    try:
        copernicusmarine.subset(
            dataset_id=DATASET_ID,
            variables=[VARIABLE],
            minimum_longitude=lon_min,
            maximum_longitude=lon_max,
            minimum_latitude=lat_min,
            maximum_latitude=lat_max,
            date=date,
            output_filename=out_file,
            overwrite=True,
            username=os.getenv("CMEMS_USER"),
            password=os.getenv("CMEMS_PASS")
        )

        ds = xr.open_dataset(out_file)
        sst = float(ds[VARIABLE][0, 0, 0])
        ds.close()
        os.remove(out_file)
        return sst
    except Exception as e:
        print("⚠️ CMEMS SST fetch error:", e)
        return None

# Optional test
if __name__ == "__main__":
    sst = fetch_sst()
    print("SST value:", sst)
