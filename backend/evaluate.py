"""Measures real accuracy of the reader on labelled documents. Usage: python backend/evaluate.py [claude|auto]"""
import json, sys, time, collections
sys.path.insert(0, "backend"); from reader import read_document
eng = sys.argv[1] if len(sys.argv) > 1 else "auto"
L = json.load(open("data/labels.json")); ok = collections.Counter(); tot = collections.Counter(); t0 = time.time()
FIELD = {"society":["name","pan","regno"],"pan":["name","pan"],"land":["name","area"],"noc":["name","validTill"],"fire":["name","validTill"]}
for x in L:
    r = read_document(open(x["file"],"rb").read(), x["file"], eng)
    tot["type"] += 1; ok["type"] += r["type"] == x["type"]
    for k in FIELD[x["type"]]:
        tot[k] += 1; ok[k] += str(r.get(k) or "").strip().lower() == str(x[k]).lower()
    tot["all_fields"] += 1; ok["all_fields"] += all(str(r.get(k) or "").strip().lower() == str(x[k]).lower() for k in FIELD[x["type"]])
print(f"engine={eng} docs={len(L)} time/doc={(time.time()-t0)/len(L):.2f}s")
for k in tot: print(f"  {k:11s} {ok[k]}/{tot[k]} = {100*ok[k]/tot[k]:.1f}%")
