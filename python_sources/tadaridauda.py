import glob
import os
import shutil
import time
import random

rep0 = "c:/sons"
seuil = 10
taillepetitwav = 10
fichpred = rep0 + "/predictions.csv"

sep = ";"
sept = "\t"
sepa = "--"
logfile = rep0 + "/csa4.log"

if os.path.exists(logfile):
	os.remove(logfile)

def ecrirelog(texte):
	print(texte)
	with open(logfile, 'a+') as file:
		file.write(texte+"\n")
	
if not os.path.isdir(rep0):
	ecrirelog("repertoire inexistant "+rep0)
	os._exit(0)
if not os.path.exists(fichpred):
	print("fichier "+fichpred+" inexistant !")
	os._exit(0)

# phase1 : tableau des predictions
ilig =0
with open(fichpred, 'r') as ficha:
	tabligcsv = ficha.read().splitlines()
	for row in tabligcsv:
		ilig = ilig + 1
		if ilig == 1:
			continue
		print(str(ilig))
		tabj = row.split(sep)
		if len(tabj) > 6:
			fima = tabj[2]
			classepred = tabj[5]
			conf = tabj[6]
			if float(conf) > seuil:
				tab2 = fima.split(sepa)
				radic2 = tab2[0]
				dertiret = radic2.rfind("-")
				if dertiret > 0:
					numwav = int(radic2[dertiret+2:len(radic2)]) - 1
					radic = radic2[0:dertiret]
				else:
					ecrirelog("pb nom du fichier "+fima)
					os._exit(0)
				finnom = tab2[5]
				ecrirelog("finnom="+finnom)
				starttime = finnom.replace(".jpg","")
				ecrirelog("starttime="+starttime)
				t_start = round(float(starttime)/1000 + taillepetitwav * numwav,3)
				t_end = round(t_start + float(tab2[3])/1000,3) 
				freq = tab2[4]
				fichtxt = rep0 + "/" + radic + "_tdauda.txt"
				ligne = str(t_start)+sept+str(t_end)+sept+classepred+" "+str(conf)+" - "+freq
				with open(fichtxt, 'a+') as file:
					file.write(ligne+"\n")
