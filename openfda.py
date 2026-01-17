import os, time, random  
import requests  
  
BASE = "https://api.fda.gov/drug/event.json"  
API_KEY = os.getenv("OPENFDA_API_KEY", "").strip()  
DISABLE = os.getenv("OPENFDA_DISABLE", "0") == "1"  
DEBUG = os.getenv("OPENFDA_DEBUG", "0") == "1"  
  
_session = requests.Session()  
  
def _get(params: dict) -> dict:  
    if DISABLE:  
        return {"results": []}  
  
    params = dict(params)  
    if API_KEY:  
        params["api_key"] = API_KEY  
  
    last_err = None  
  
    for attempt in range(6):  
        try:  
            r = _session.get(  
                BASE,  
                params=params,  
                headers={"Accept": "application/json", "User-Agent": "ae-watch/0.1"},  
                timeout=30,  
            )  
  
            if DEBUG:  
                print("openFDA URL:", r.url)  
                print("openFDA status:", r.status_code)  
  
            if r.status_code == 200:  
                return r.json()  
  
            body = (r.text or "")[:800]  
            last_err = f"HTTP {r.status_code}: {body}"  
  
            # permanent errors (don’t bother retrying)  
            if r.status_code in (400, 401, 403, 404, 414):  
                break  
  
            # retry-able errors  
            if r.status_code in (429, 500, 502, 503, 504):  
                time.sleep((2 ** attempt) + random.random())  
                continue  
  
            time.sleep(1 + random.random())  
  
        except Exception as e:  
            last_err = repr(e)  
            time.sleep((2 ** attempt) + random.random())  
  
    raise RuntimeError(f"openFDA request failed: {last_err}")  
  
def total(search: str) -> int:  
    """  
    Returns openFDA meta.results.total for a given search.  
    """  
    d = _get({"search": search, "limit": "1"})  
    return int(d.get("meta", {}).get("results", {}).get("total", 0))  

def count(search: str, count_field: str, limit: int = 1000):  
    d = _get({"search": search, "count": count_field, "limit": str(limit)})  
    return d.get("results", [])  