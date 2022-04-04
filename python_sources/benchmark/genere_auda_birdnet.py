import glob
import os
import shutil
import time
import random

reptxt = "c:/birdnet/SampleV1/txt2"
repauda = "c:/birdnet/SampleV1/auda2"

seuil = 10

sept = "\t"
	
if not os.path.isdir(rep0):
	print("repertoire inexistant "+rep0)
	os._exit(0)
if not os.path.isdir(reptxt):
	print("repertoire inexistant "+reptxt)
	os._exit(0)
if not os.path.isdir(repauda):
	os.mkdir(repauda)

# phase1 : tableau des predictions
ilig =0
os.chdir(reptxt)

listetxt = sorted(glob.glob("*.selections.txt"))
ifi = 0
for ftxt in  listetxt:
	fichtxt = repauda + "/" + ftxt.replace(".BirdNET.selections","_birdnet")
	listelignes = {}
	with open(ftxt, 'r') as ficha:
		tablig = ficha.read().splitlines()
		ilig = 0
		for row in tablig:
			ilig = ilig + 1
			if ilig == 1:
				continue
			print(str(ilig))
			tabj = row.split(sept)
			if len(tabj) > 11:
				classepred = tabj[9]
				conf = round(float(tabj[10])*100,1)
				if float(conf) > seuil:
					t_start = tabj[4]
					t_end = tabj[5]
					rang = tabj[11]
					ligne = t_start + sept + t_end + sept + classepred +" - "+rang+" - " +str(conf)
					cle = str(int(float(t_start))+100000)+"_"+str(tabj[0])
					listelignes[cle] = ligne
	if len(listelignes) > 0:
		with open(fichtxt, 'a+') as file:
			for cle in sorted(listelignes):
				file.write(listelignes[cle]+"\n")
	ifi = ifi + 1
