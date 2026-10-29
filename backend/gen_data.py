"""Synthetic dataset: N documents per type with known ground truth (SIH allows synthetic data)."""
import random, json, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(7)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
A = ["Sunrise","Bharat","Gyan","Nalanda","Himalaya","Vidya","Kaveri","Aryabhatta","Tagore","Saraswati","Lakshmi","Ganga"]
B = ["Institute of Technology","College of Engineering","Polytechnic","Technical Campus","Institute of Management"]
def pan(): return "".join(random.choices("ABCDEFGHJKLMNPRSTUVWXYZ",k=5))+str(random.randint(1000,9999))+random.choice("ABCDEFGHJKLM")
def date(y0,y1): return f"{random.randint(y0,y1)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
def rec():
    return dict(name=f"{random.choice(A)} {random.choice(B)}", pan=pan(), regno=f"SOC/{random.randint(2005,2020)}/{random.randint(100,999)}",
                validTill=date(2026,2031), area=str(random.randint(4000,20000)))
def lines(t, r):
    return {"society":["CERTIFICATE OF REGISTRATION","Registrar of Societies, Govt. of India",f"Society: {r['name']}",f"PAN: {r['pan']}",f"Reg No: {r['regno']}"],
     "pan":["INCOME TAX DEPARTMENT","Permanent Account Number Card",f"Name: {r['name']}",f"PAN: {r['pan']}"],
     "land":["LAND DOCUMENT","Sale Deed - Ownership Record",f"Owner: {r['name']}",f"Area: {r['area']} sq m"],
     "noc":["NO OBJECTION CERTIFICATE","University Affiliation Letter",f"Institute: {r['name']}",f"Valid till: {r['validTill']}"],
     "fire":["FIRE SAFETY CERTIFICATE","Fire Department Clearance",f"Premises: {r['name']}",f"Valid till: {r['validTill']}"]}[t]
def render(ls):
    im = Image.new("RGB",(1000,520),(250,248,240)); d = ImageDraw.Draw(im)
    f = ImageFont.load_default(size=34); y = 50
    d.rectangle([20,20,980,500],outline=(60,60,60),width=4)
    for l in ls: d.text((60,y),l,fill=(20,20,20),font=f); y += 70
    im = im.rotate(random.uniform(-1.5,1.5),fillcolor=(250,248,240)).filter(ImageFilter.GaussianBlur(random.choice([0,0.4,0.8])))
    return im
os.makedirs("data/docs",exist_ok=True); labels=[]
for t in ["society","pan","land","noc","fire"]:
    for i in range(N):
        r = rec(); fn = f"data/docs/{t}_{i}.png"; render(lines(t,r)).save(fn)
        labels.append(dict(file=fn,type=t,**{k:r[k] for k in ("name","pan","regno","validTill","area")}))
json.dump(labels,open("data/labels.json","w"),indent=1); print(len(labels),"documents generated")
