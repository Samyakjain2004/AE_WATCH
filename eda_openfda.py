import pandas as pd  
import matplotlib.pyplot as plt  
from openfda import count, total  
from config import SETTINGS  
  
def date_filter(start="20210101", end="20251231") -> str:  
    return f"receivedate:[{start} TO {end}]"  
  
def run():  
    N = total(date_filter())  
    print("Total reports N =", N)  
  
    top_drugs = count(date_filter(), "patient.drug.medicinalproduct.exact", limit=50)  
    df_drugs = pd.DataFrame(top_drugs)  
    df_drugs.to_csv("eda_top_drugs.csv", index=False)  
  
    top_rxn = count(date_filter(), "patient.reaction.reactionmeddrapt.exact", limit=50)  
    df_rxn = pd.DataFrame(top_rxn)  
    df_rxn.to_csv("eda_top_reactions.csv", index=False)  
  
    serious = count(date_filter(), "serious", limit=10)  
    df_ser = pd.DataFrame(serious)  
    df_ser.to_csv("eda_serious.csv", index=False)  
  
    # simple plot  
    df_ser.plot(kind="bar", x="term", y="count", legend=False, title="Serious vs Non-serious (FAERS)")  
    plt.tight_layout()  
    plt.savefig("eda_serious.png")  
  
if __name__ == "__main__":  
    run()  