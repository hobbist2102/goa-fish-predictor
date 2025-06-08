import requests
import csv
from datetime import datetime, timedelta
from io import StringIO

def _get_today_incois_url():
    """Generates today's INCOIS tide CSV URL for Vasco (Goa)."""
    now = datetime.utcnow() + timedelta(hours=5, minutes=30)  # IST
    date_str = now.strftime("%d%m%Y")
    return f"https://www.incois.gov.in/portal/ptide/AllStations/VSCO{date_str}.csv"

def _download_csv(url):
    """Fetches CSV data from INCOIS."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print("⚠️ INCOIS fetch failed:", e)
        return None

def _parse_csv(csv_text):
    """Parses the INCOIS tide CSV and returns time–height list."""
    reader = csv.reader(StringIO(csv_text))
    times, heights = [], []

    for row in reader:
        try:
            t = datetime.strptime(row[0], "%H:%M")
            h = float(row[1])
            times.append(t)
            heights.append(h)
        except:
            continue
    return times, heights

def _interpolate_height(times, heights, target_time):
    """Linearly interpolates tide height at a given datetime."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dt_target = today + timedelta(hours=target_time.hour, minutes=target_time.minute)

    for i in range(1, len(times)):
        t1 = today + timedelta(hours=times[i - 1].hour, minutes=times[i - 1].minute)
        t2 = today + timedelta(hours=times[i].hour, minutes=times[i].minute)

        if t1 <= dt_target <= t2:
            h1 = heights[i - 1]
            h2 = heights[i]
            delta = (dt_target - t1).total_seconds() / (t2 - t1).total_seconds()
            return h1 + delta * (h2 - h1)

    return heights[-1]  # fallback to last value

def get_tide_height(time_of_day=None):
    """
    Returns interpolated tide height (in meters) for a given datetime.time.
    Defaults to now (IST).
    """
    if time_of_day is None:
        now = datetime.utcnow() + timedelta(hours=5, minutes=30)
        time_of_day = now.time()

    url = _get_today_incois_url()
    csv_data = _download_csv(url)

    if not csv_data:
        return None

    times, heights = _parse_csv(csv_data)

    return round(_interpolate_height(times, heights, time_of_day), 2)
