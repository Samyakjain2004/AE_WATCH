import json, time, os, hashlib  
  
class SimpleCache:  
    def __init__(self, path=".cache.json", ttl_sec=24*3600):  
        self.path = path  
        self.ttl = ttl_sec  
        self.data = {}  
        if os.path.exists(path):  
            try:  
                self.data = json.load(open(path, "r", encoding="utf-8"))  
            except Exception:  
                self.data = {}  
  
    def _k(self, key: str) -> str:  
        return hashlib.sha256(key.encode("utf-8")).hexdigest()  
  
    def get(self, key: str):  
        k = self._k(key)  
        v = self.data.get(k)  
        if not v:  
            return None  
        if time.time() > v["exp"]:  
            self.data.pop(k, None)  
            return None  
        return v["val"]  
  
    def set(self, key: str, val, ttl_sec=None):  
        k = self._k(key)  
        exp = time.time() + (ttl_sec if ttl_sec is not None else self.ttl)  
        self.data[k] = {"exp": exp, "val": val}  
        json.dump(self.data, open(self.path, "w", encoding="utf-8"))  
  
CACHE = SimpleCache()  