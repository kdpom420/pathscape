"""Optional NASA POWER monthly data adapter."""
import pandas as pd


def load_nasa_gwangju(start=2001, end=2025, latitude=35.1595, longitude=126.8526):
    import requests
    response = requests.get("https://power.larc.nasa.gov/api/temporal/monthly/point",
        params={"parameters": "T2M,RH2M,WS2M", "community": "AG",
                "longitude": longitude, "latitude": latitude, "start": start,
                "end": end, "format": "JSON"}, timeout=90)
    response.raise_for_status()
    raw = response.json()["properties"]["parameter"]
    frames = []
    for source, target in {"T2M": "TEMP", "RH2M": "RH", "WS2M": "WS"}.items():
        records = [(int(k[:4]), int(k[4:6]), float(v)) for k, v in raw[source].items()
                   if len(k) == 6 and k.isdigit() and start <= int(k[:4]) <= end
                   and 1 <= int(k[4:6]) <= 12]
        frames.append(pd.DataFrame(records, columns=["year", "month", target])
                      .set_index(["year", "month"]))
    data = pd.concat(frames, axis=1).reset_index()
    for target in ("TEMP", "RH", "WS"):
        data.loc[data[target] <= -900, target] = float("nan")
    return data.sort_values(["year", "month"]).reset_index(drop=True)
