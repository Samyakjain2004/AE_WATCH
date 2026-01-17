# # # drug_label.py  
# # import requests  
  
# # def fetch_label_by_rxcui(rxcui: str, timeout=10):  
# #     url = f'https://api.fda.gov/drug/label.json?search=openfda.rxcui:"{rxcui}"&limit=1'  
# #     r = requests.get(url, timeout=timeout)  
# #     r.raise_for_status()  

# #     data = r.json()  
# #     if "results" not in data or not data["results"]:  
# #         raise ValueError(f"No label found for rxcui={rxcui}")  
# #     item = data["results"][0]
# #     #item = r.json()["results"][0]  
  
# #     def section(name):  
# #         val = item.get(name)  
# #         if isinstance(val, list):  
# #             return "\n".join(val)  
# #         return val  # may be None  
  
# #     openfda = item.get("openfda", {})  
# #     spl_set_id = (openfda.get("spl_set_id") or [None])[0]  
# #     label_url = (  
# #         f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={spl_set_id}"  
# #         if spl_set_id else None  
# #     )  
  
# #     drug_name = (openfda.get("generic_name") or [None])[0] or (openfda.get("brand_name") or [None])[0]  
  
# #     return {  
# #         "drug": drug_name,  
# #         "source": "openFDA",  
# #         "rxcui": str(rxcui),  
# #         "boxed_warning": section("boxed_warning"),  
# #         "contraindications": section("contraindications"),  
# #         "warnings_and_precautions": section("warnings_and_precautions"),  
# #         "drug_interactions": section("drug_interactions"),  
# #         "use_in_specific_populations": section("use_in_specific_populations"),  
# #         "adverse_reactions": section("adverse_reactions"),  
# #         "label_url": label_url,  
# #     }  
# import requests  
  
# def _extract(item, rxcui):  
#     def section(name):  
#         val = item.get(name)  
#         return "\n".join(val) if isinstance(val, list) else val  
  
#     openfda = item.get("openfda", {}) or {}  
#     spl_set_id = (openfda.get("spl_set_id") or [None])[0]  
#     label_url = (  
#         f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={spl_set_id}"  
#         if spl_set_id else None  
#     )  
#     drug_name = (openfda.get("generic_name") or [None])[0] or (openfda.get("brand_name") or [None])[0]  
  
#     return {  
#         "drug": drug_name,  
#         "source": "openFDA",  
#         "rxcui": str(rxcui) if rxcui is not None else None,  
#         "boxed_warning": section("boxed_warning"),  
#         "contraindications": section("contraindications"),  
#         "warnings_and_precautions": section("warnings_and_precautions"),  
#         "drug_interactions": section("drug_interactions"),  
#         "use_in_specific_populations": section("use_in_specific_populations"),  
#         "adverse_reactions": section("adverse_reactions"),  
#         "label_url": label_url,  
#     }  
  
# def fetch_label_by_rxcui(rxcui: str, timeout=10):  
#     base = "https://api.fda.gov/drug/label.json"  
#     r = requests.get(base, params={"search": f"openfda.rxcui:{rxcui}", "limit": 1}, timeout=timeout)  
  
#     if r.status_code == 404:  
#         return None  # <-- important: signal “not found”  
#     r.raise_for_status()  
  
#     item = r.json()["results"][0]  
#     return _extract(item, rxcui)  
  
# def fetch_label_by_name(drug_name: str, timeout=10):  
#     base = "https://api.fda.gov/drug/label.json"  
#     search = f'(openfda.generic_name:"{drug_name}" OR openfda.brand_name:"{drug_name}")'  
#     r = requests.get(base, params={"search": search, "limit": 1}, timeout=timeout)  
  
#     if r.status_code == 404:  
#         return None  
#     r.raise_for_status()  
  
#     item = r.json()["results"][0]  
#     return _extract(item, rxcui=None)  
  
# def fetch_label(rxcui: str, drug_name: str = None, timeout=10):  
#     label = fetch_label_by_rxcui(rxcui, timeout=timeout)  
#     if label is not None:  
#         return label  
  
#     if drug_name:  
#         label = fetch_label_by_name(drug_name, timeout=timeout)  
#         if label is not None:  
#             label["rxcui"] = str(rxcui)  
#             return label  
  
#     return {  
#         "drug": drug_name,  
#         "source": "openFDA",  
#         "rxcui": str(rxcui),  
#         "boxed_warning": None,  
#         "contraindications": None,  
#         "warnings_and_precautions": None,  
#         "drug_interactions": None,  
#         "use_in_specific_populations": None,  
#         "adverse_reactions": None,  
#         "label_url": None,  
#         "error": f"No openFDA drug/label found for rxcui={rxcui}" + (f" or name={drug_name}" if drug_name else ""),  
#     }  
# drug_label.py  
import requests  
  
OPENFDA_LABEL = "https://api.fda.gov/drug/label.json"  
RXNAV = "https://rxnav.nlm.nih.gov/REST"  
  
HEADERS = {  
    "User-Agent": "drug-label-fetcher/1.0 (contact: you@example.com)"  
}  
  
  
def _section(item, name):  
    val = item.get(name)  
    return "\n".join(val) if isinstance(val, list) else val  
  
  
def _extract(item, rxcui=None):  
    openfda = item.get("openfda", {}) or {}  
  
    spl_set_id = (openfda.get("spl_set_id") or [None])[0]  
    label_url = (  
        f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={spl_set_id}"  
        if spl_set_id else None  
    )  
  
    drug_name = (openfda.get("generic_name") or [None])[0] or (openfda.get("brand_name") or [None])[0]  
  
    return {  
        "drug": drug_name,  
        "source": "openFDA",  
        "rxcui": str(rxcui) if rxcui is not None else None,  
        "boxed_warning": _section(item, "boxed_warning"),  
        "contraindications": _section(item, "contraindications"),  
        "warnings_and_precautions": _section(item, "warnings_and_precautions"),  
        "drug_interactions": _section(item, "drug_interactions"),  
        "use_in_specific_populations": _section(item, "use_in_specific_populations"),  
        "adverse_reactions": _section(item, "adverse_reactions"),  
        "label_url": label_url,  
    }  
  
  
def _openfda_get(search: str, limit=1, timeout=15):  
    r = requests.get(  
        OPENFDA_LABEL,  
        params={"search": search, "limit": limit},  
        headers=HEADERS,  
        timeout=timeout,  
    )  
    if r.status_code == 404:  
        return None  
    r.raise_for_status()  
    js = r.json()  
    results = js.get("results") or []  
    return results[0] if results else None  
  
  
def fetch_label_by_rxcui(rxcui: str, timeout=15):  
    # IMPORTANT: quote the rxcui value  
    item = _openfda_get(f'openfda.rxcui:"{rxcui}"', timeout=timeout)  
    return _extract(item, rxcui) if item else None  
  
  
def fetch_label_by_name(drug_name: str, timeout=15):  
    if not drug_name:  
        return None  
    dn = drug_name.replace('"', '\\"')  
    item = _openfda_get(  
        f'(openfda.generic_name:"{dn}" OR openfda.brand_name:"{dn}")',  
        timeout=timeout  
    )  
    return _extract(item, rxcui=None) if item else None  
  
  
def rxnorm_name_from_rxcui(rxcui: str, timeout=15):  
    url = f"{RXNAV}/rxcui/{rxcui}/property.json"  
    r = requests.get(url, params={"propName": "RxNorm Name"}, headers=HEADERS, timeout=timeout)  
    r.raise_for_status()  
    grp = r.json().get("propConceptGroup", {}) or {}  
    props = grp.get("propConcept") or []  
    return props[0].get("propValue") if props else None  
  
  
def ndcs_from_rxcui(rxcui: str, timeout=15):  
    url = f"{RXNAV}/rxcui/{rxcui}/ndcs.json"  
    r = requests.get(url, headers=HEADERS, timeout=timeout)  
    r.raise_for_status()  
    ndcs = (((r.json() or {}).get("ndcGroup") or {}).get("ndcList") or {}).get("ndc") or []  
    # RxNav usually returns hyphenated NDCs already  
    return [n for n in ndcs if isinstance(n, str) and n.strip()]  
  
  
def fetch_label_by_ndc(ndc: str, timeout=15):  
    if not ndc:  
        return None  
    n = ndc.replace('"', '\\"')  
    item = _openfda_get(  
        f'(openfda.package_ndc:"{n}" OR openfda.product_ndc:"{n}")',  
        timeout=timeout  
    )  
    return _extract(item, rxcui=None) if item else None  
  
  
def fetch_label(rxcui: str, drug_name: str = None, timeout=15):  
    attempts = {"rxcui": str(rxcui), "name_used": None, "ndc_tried": []}  
  
    # 1) RxCUI  
    label = fetch_label_by_rxcui(rxcui, timeout=timeout)  
    if label:  
        return label  
  
    # 2) Name (use provided name; if missing, derive from RxNav)  
    if not drug_name:  
        drug_name = rxnorm_name_from_rxcui(rxcui, timeout=timeout)  
    attempts["name_used"] = drug_name  
  
    if drug_name:  
        label = fetch_label_by_name(drug_name, timeout=timeout)  
        if label:  
            label["rxcui"] = str(rxcui)  
            return label  
  
    # 3) NDC fallback  
    try:  
        for ndc in ndcs_from_rxcui(rxcui, timeout=timeout)[:25]:  
            attempts["ndc_tried"].append(ndc)  
            label = fetch_label_by_ndc(ndc, timeout=timeout)  
            if label:  
                label["rxcui"] = str(rxcui)  
                if not label.get("drug"):  
                    label["drug"] = drug_name  
                return label  
    except Exception:  
        pass  
  
    return {  
        "drug": drug_name,  
        "source": "openFDA",  
        "rxcui": str(rxcui),  
        "boxed_warning": None,  
        "contraindications": None,  
        "warnings_and_precautions": None,  
        "drug_interactions": None,  
        "use_in_specific_populations": None,  
        "adverse_reactions": None,  
        "label_url": None,  
        "error": "No openFDA drug/label found via RxCUI, name, or NDC",  
        "debug": attempts,  
    }  