import os
import datetime
import xarray as xr
import copernicusmarine

# Set credentials
copernicusmarine.set_credentials(
    username=os.getenv("CMEMS_USER"),
    password=os.getenv("CMEMS_PASS")
)

DATASET_ID = "cmems_mod_glo_phy_my_0.25_P1D-m"
VARIABLE = "thetao"
DELTA = 0.05

def fetch_sst(lat=15.5, lon=73.8, date=None):
    if not date:
        date = datetime.date.today() - datetime.timedelta(days=2)

    lon_min, lon_max = lon - DELTA, lon + DELTA
    lat_min, lat_max = lat - DELTA, lat + DELTA
    out = f"sst_{lat}_{lon}_{date.strftime('%Y%m%d')}.nc"

    try:
        copernicusmarine.subset(
            dataset_id=DATASET_ID,
            variables=[VARIABLE],
            longitude=(lon_min, lon_max),
            latitude=(lat_min, lat_max),
            date=date,
            output_filename=out,
            overwrite=True
        )
        ds = xr.open_dataset(out)
        sst = float(ds[VARIABLE][0, 0, 0])
        ds.close()
        os.remove(out)
        return sst
    except Exception as e:
        print("⬇️ CMEMS SST fetch error:", e)
        return None
