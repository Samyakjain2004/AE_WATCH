import math  
from config import SETTINGS  
from openfda import total, count  
  
def q(s: str) -> str:  
    return '"' + s.replace('"', '\\"') + '"'  
  
def date_filter(start="20210101", end="20251231") -> str:  
    return f"receivedate:[{start} TO {end}]"  
  
def N_reports() -> int:  
    return total(date_filter())  
  
def nD(drug_query: str) -> int:  
    return total(f"{date_filter()} AND ({drug_query})")  
  
def nE(event_pt: str) -> int:  
    return total(f"{date_filter()} AND patient.reaction.reactionmeddrapt.exact:{q(event_pt)}")  
  
def nDE(drug_query: str, event_pt: str) -> int:  
    return total(  
        f"{date_filter()} AND ({drug_query}) AND patient.reaction.reactionmeddrapt.exact:{q(event_pt)}"  
    )  
  
def serious_frac(drug_query: str, event_pt: str) -> float:  
    all_ = nDE(drug_query, event_pt)  
    if all_ == 0: return 0.0  
    ser = total(  
        f"{date_filter()} AND ({drug_query}) AND patient.reaction.reactionmeddrapt.exact:{q(event_pt)} AND serious:1"  
    )  
    return ser / all_  
  
def top_events_for_drug(drug_query: str, k=50):  
    rows = count(f"{date_filter()} AND ({drug_query})", "patient.reaction.reactionmeddrapt.exact", limit=1000)  
    pairs = [(r["term"], int(r["count"])) for r in rows]  
    pairs.sort(key=lambda x: -x[1])  
    return pairs[:k]  
  
def ror_ci(nDE_: int, nD_: int, nE_: int, N_: int, cc=0.5):  
    a = nDE_  
    b = max(nD_ - nDE_, 0)  
    c = max(nE_ - nDE_, 0)  
    d = max(N_ - nD_ - nE_ + nDE_, 0)  
  
    a2, b2, c2, d2 = a + cc, b + cc, c + cc, d + cc  
    ror = (a2 / b2) / (c2 / d2)  
    se = math.sqrt(1/a2 + 1/b2 + 1/c2 + 1/d2)  
    lcl = math.exp(math.log(ror) - 1.96 * se)  
    ucl = math.exp(math.log(ror) + 1.96 * se)  
    return float(ror), float(lcl), float(ucl)  