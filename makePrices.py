import tabula
import json
import math

pdf_path = "https://ftp.hadiko.de/int/hadiko/diverses/gema/Preisliste.pdf"
pdf_lpath ="Preisliste.pdf"

df = tabula.read_pdf(pdf_lpath, pages="all", stream=True)

prices = {}
sizes = {}
db = []


def calcPrice(dataPoint):
	name = dataPoint[0]
	price = float(dataPoint[2].split(" ")[0].replace("," , "."))
	for x in dataPoint:
		if "x" in x and x is not name:
			size = x.split("x")[1].strip(" ")
			numBottles = float(x.split("x")[0].strip(" "))



	db.append({"name":name, "price":round((price/numBottles)*1.05, 2), "size":size})


for i in {0,1,2,3,4,6}:
	for j in df[i].values:
		calcPrice(j)

print(db)

dbFile = open("priceDB2.json", "w")
json.dump(db, dbFile)
dbFile.close()
