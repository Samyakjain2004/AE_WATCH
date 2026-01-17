import json  
from pipeline import run  
  
def normalize(s):   
    return (s or "").strip().upper()  
  
def eval_file(path: str, k=10):  
    rows = [json.loads(l) for l in open(path, "r", encoding="utf-8")]  
    hit = 0  
    total = 0  
  
    for r in rows:  
        out = run(transcript=r["transcript"])  
        preds = out["flags"][:k]  
        pred_pairs = set((normalize(p.get("drug")), normalize(p.get("event_meddra_pt"))) for p in preds)  
  
        exp = r.get("expected", [])  
        for e in exp:  
            total += 1  
            if (normalize(e["drug"]), normalize(e["event"])) in pred_pairs:  
                hit += 1  
  
    recall_at_k = hit / total if total else 0.0  
    print(f"Recall@{k}: {recall_at_k:.3f} ({hit}/{total})")  
  
if __name__ == "__main__":  
    eval_file("sample_data/sample_transcript.jsonl", k=10)  