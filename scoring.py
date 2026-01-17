# scoring.py  
import math  
  
def _sigmoid(x: float) -> float:  
    return 1.0 / (1.0 + math.exp(-x))  
  
def predict_probs(*, symptom_present: bool, timing_ok: bool|None, tier: int,  
                  serious_fraction: float, ror_lcl95: float|None,  
                  has_red_flag: bool = False) -> tuple[float, float]:  
    # p_ae_now: “is this AE happening now?”  
    x = -2.2  
    x += 1.4 if symptom_present else 0.0  
    x += 0.8 if timing_ok is True else (-0.8 if timing_ok is False else -0.3)  # unknown timing penalized  
    x += 0.6 * tier  
    x += 0.5 * math.log1p(max(ror_lcl95 or 0.0, 0.0))  
    p_ae_now = _sigmoid(x)  
  
    # p_serious_24_72h: “will this become serious soon?”  
    y = -3.2  
    y += 2.0 * (serious_fraction or 0.0)  
    y += 1.5 if has_red_flag else 0.0  
    y += 0.4 * tier  
    p_serious = _sigmoid(y)  
  
    return float(p_ae_now), float(p_serious)  

def timing_plausible(med_start_days_ago: int | None,  
                     med_change_days_ago: int | None,  
                     symptom_onset_days_ago: int | None) -> bool | None:  
    """  
    days_ago: bigger number = further in past.  
    Symptom after start means symptom_onset_days_ago < med_start_days_ago.  
    """  
    if symptom_onset_days_ago is None:  
        return None  
  
    anchor = med_change_days_ago if med_change_days_ago is not None else med_start_days_ago  
    if anchor is None:  
        return None  
  
    return symptom_onset_days_ago <= anchor   
  
def faers_tier(ror_lcl95: float, nDE: int) -> int:  
    if nDE < 5: return 0  
    if ror_lcl95 >= 4: return 3  
    if ror_lcl95 >= 2: return 2  
    if ror_lcl95 >= 1.2: return 1  
    return 0  
  
def score( *,  
    symptom_present: bool,  
    timing_ok: bool | None,  
    tier: int,  
    serious_fraction: float  
) -> tuple[int, str]:  
    s = 0  
    if symptom_present: s += 6  
    if timing_ok is None: s -= 2 
    if timing_ok is True: s += 3  
    if timing_ok is False: s -= 6  # strong penalty if symptom predates med  
    s += tier * 2  
    if serious_fraction >= 0.3: s += 2  

    # triage logic  
    if symptom_present and timing_ok is None and tier >= 2:  
    # do not mark urgent purely from FAERS if you lack exposure timing  
        return s, "monitor" 
    if symptom_present and serious_fraction >= 0.3 and tier >= 2 and (timing_ok is not False):  
        return s, "urgent"  
    if s >= 8 and symptom_present:  
        return s, "urgent"  
    if s >= 6:  
        return s, "monitor"  
    return s, "none"  