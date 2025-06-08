#!/usr/bin/env python3
import os
import datetime
import copernicusmarine

def main():
    # 1 day behind current UTC (data is available up to 1 day before real time)
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    target = now_utc - datetime.timedelta(days=1)
    # human‐readable for logging
    date_str = target.strftime("%Y-%m-%d")
    # file name in YYYYMMDD
    fname = f"sst_{target.strftime('%Y%m%d')}.nc"

    print(f"Fetching SST from CMEMS for {date_str}…")
    try:
        copernicusmarine.subset(
            dataset_id="METOFFICE-GLO-SST-L4-NRT-OBS-SST-V2",
            variables=["analysed_sst"],
            start_datetime=date_str,
            end_datetime=date_str,
            username=os.getenv("CMEMS_USER"),
            password=os.getenv("CMEMS_PASS"),
            output_filename=fname,
            overwrite=True,
            disable_progress_bar=True
        )
        print(f"✅ SST saved to {fname}")
    except Exception as e:
        print("❌ CMEMS SST fetch error:", e)

if __name__ == "__main__":
    main()
