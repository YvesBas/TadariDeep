#!/usr/bin/env python3ecrirelog
# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import os
from datetime import *
import time
import glob
import sys

baseprog = os.getcwd()
logfile = baseprog + "/logcrech3.log"
if os.path.exists(logfile):
	os.remove(logfile)

# -----------------------
def ecrirelog(texte):
	datef = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	texte2 = texte + "   ("+ datef  + ")"
	with open(logfile, 'a+') as file:
		file.write(texte2+"\n")
	print(texte)
# -----------------------
	
# lire les parametres en entree
nbpe = len(sys.argv)
if nbpe <2:
	ecrirelog("parametres repertoire et numero classifier manquants")
	os._exit(0)
if nbpe == 2:
	ecrirelog("deux parametres necessaires : repertoire et numero classifier")
	os._exit(0)
nompar = "classifiers.csv"
nparnecessaire = 9
sepa = "--"
sc=";"
mincol = 10

repima = sys.argv[1]
snumcla = sys.argv[2]
souscasvoulu = ""
if nbpe == 4:
	souscasvoulu = sys.argv[3]
	#ecrirelog("souscasvoulu="+souscasvoulu)
#time.sleep(0.5)

if not os.path.exists(nompar):
	ecrirelog("fichier classifiers.csv non trouve !")
	os._exit(0)

listima = []
if os.path.isdir(repima):
	os.chdir(repima)
	listima = sorted(glob.glob("*.jpg"))
	if len(listima) < 1:
		ecrirelog("aucun fichier image trouvé : abandon !")
		os._exit(0)
	os.chdir(baseprog)
else:
	ecrirelog("repertoire images non trouve !")
	os._exit(0)

affitest = repima.replace("\\","")
affitest = affitest.replace("/","")
affitest = affitest.replace(":","")
#ecrirelog("affitest="+affitest)

trouvecla = False
with open(nompar,"r") as flp:
	tlpar = flp.read().splitlines()
	nl = 0
	for ligne in tlpar:
		nl = nl + 1
		if nl == 1:
			continue
		tpar = ligne.split(";")
		if tpar[0] == snumcla:
			if souscasvoulu != "":
				if souscasvoulu != tpar[1]:
					#ecrirelog(str(nl)+") bonne valeur de numcla "+snumcla+" mais mauvaise valeur de souscasvoulu "+tpar[1])
					continue
				#else:
					#ecrirelog(str(nl)+") bonne valeur de numcla "+snumcla+" et de souscasvoulu "+tpar[1])
			trouvecla = True
			break
if not trouvecla:
	ecrirelog("classifier "+snumcla+" non trouve !")
	os._exit(0)
if len(tpar) < nparnecessaire:
	ecrirelog("nbre de parametre insuffisant pour le classifier "+snumcla)

	
try:
	numcla = int(snumcla)
except:
	ecrirelog("exception sur numero classifier")
	os._exit(0)
	
snumoiseaux = tpar[3]
snbepochs = tpar[2]

tepochs = snbepochs.split(",")
lep = len(tepochs)
if lep==1:
	multifreq = False
	nbre_bases = 1
else:
	print("version multifreq non maintenue")
	sys._exit(0)
	
for i in range(0,lep):
	try:
		nep = int(tepochs[i])
		if nep < 1 or nep > 999:
			ecrirelog("valeur incoherente pour le parametre nbepoch")
			os._exit(0)
	except:
		ecrirelog("exception sur lecture du parametre nbepoch")
	
listecla = "classes" + snumoiseaux + ".csv"
if not os.path.exists(listecla):
	ecrirelog("fichier "+listecla+" inexistant ! Arret !!!")
	os._exit(0)

	
moteur = int(tpar[4])
batch_size = int(tpar[5])
dimx  = int(tpar[6])
dimy  = int(tpar[7])
ndense= int(tpar[8])
if moteur < 1 or moteur > 3 or batch_size < 1 or batch_size > 64 or dimx < 100 or dimx > 2000 or dimy < 64 or dimy > 1000 or ndense < 32 or ndense > 2048:
	print("parametre hors limites")
	os._exit(1)
	


# ----------------------------------------------------------------------------------

import tensorflow as tf

from tensorflow import keras

#from keras.applications.xception import Xception, preprocess_input
from tensorflow import keras
if moteur == 1:
	from tensorflow.keras.applications.xception import Xception, preprocess_input
if moteur == 2:
	from tensorflow.keras.applications.mobilenet import MobileNet, preprocess_input
if moteur == 3:
	from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
if moteur !=1 and moteur!=2 and moteur!=3:
	ecrirelog("parametre moteur incorrect")
	os._exit(1)
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dense,GlobalAveragePooling2D, Activation
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint
# ----------------------------------------------------------------------------------
#-----------------------------------------
def predict(filename,classeattendue,fichier,numcri,logpred):
	bon = 0
	affi = ""
	#ecrirelog(filename)
	img = image.load_img(filename, target_size=(dimx,dimy)) #load image
	x = image.img_to_array(img) #convert it to array
	x = np.expand_dims(x, axis=0) #simulate batch dimension
	x = preprocess_input(x) #preprocessing
	pred = model.predict(x) #classes prediction
	class_pred = labels[np.argmax(pred)] #find class with highest confidence
	if not classe_attendue=="":
		if class_pred == classeattendue:
			bon = 1
			affi = "OK   "
		else:
			affi = "NOK  "
		sbon = str(bon)
	else:
		
		sbon = ""
	conf = pred[0,np.argmax(pred)] #confidence
	rconf=round(100*conf,1)
	sc=";"
	ligne_debut = classeattendue+sc+str(numtest)+"_"+snbepoch+"_"+affitest+sc+f+sc+fichier+sc+numcri+sc+class_pred+sc+str(rconf)+sc+sbon
	#
	ligne_fin = ""
	confat = 100
	ligne_milieu = sc + "0"
	for k in range(0,len(labels)):
		confj = pred[0,k]
		rconfj = round(100*confj,1)
		#ecrirelog(labels[k]+"  :  "+str(rconfj))
		ligne_fin=ligne_fin + sc + str(rconfj)
		if labels[k]==classeattendue:
			ligne_milieu = sc + str(rconfj)
			confat = rconfj
			#ecrirelog(fichier+" : confiance pour la classe attendue = "+str(confat))
	ligne = ligne_debut + ligne_milieu + ligne_fin
	with open(logpred, 'a+') as file:
		file.write(ligne+"\n")
	ecrirelog(affi+filename+"   :   "+"Class : "+class_pred+" -> "+str(rconf))
	
	return(bon,conf)
ecrirelog("-------------------------------------------------------------------------------------------")
# initialisations avant grande boucle

#depart = (int)(time.time()) 

leslistes = []
snumoiseauxdepart = snumoiseaux

finboucle = 1
affinbepochs = snbepochs

logpred = baseprog + "/txt/predictions_"+ snumcla + "_" + affinbepochs + "_" + snumoiseaux + "_" + affitest + ".csv"

	
if os.path.exists(logpred):
	os.remove(logpred)
if not os.path.exists(baseprog + "/txt"):
	os.mkdir(baseprog + "/txt")
ecrirelog("")
ecrirelog("")
ecrirelog("-------------------------")

if moteur == 1:
	base_model = Xception(include_top=False, weights="imagenet",input_shape=(dimx,dimy,3))
if moteur == 2:
	base_model = MobileNet(include_top=False, weights="imagenet",input_shape=(dimx,dimy,3))
if moteur == 3:
	base_model = ResNet50(include_top=False, weights="imagenet",input_shape=(dimx,dimy,3))
# -----------
labels = []
tcor = {}
tcor2 = {}

with open(listecla,"r") as flc:
	tlistecla = flc.read().splitlines()
nl = 0
for ligne in tlistecla:
	nl = nl + 1
	if nl == 1:
		continue
	tcla = ligne.split(";")
	if len(tcla)>0:
		labels.append(tcla[0])
		clacor = ""
		if len(tcla) > 1:
			clacor = tcla[1]
			if len(clacor) > 0:
				tcor[tcla[0]] = clacor
		if len(tcla) > 2:
			clacor2 = tcla[2]
			if len(clacor) > 0:
				tcor2[tcla[0]] = clacor2
labels = sorted(labels)
	
nbclasses = len(labels)
ecrirelog("nombre de classes : "+str(nbclasses))

if nbclasses < 1:
	ecrirelog("classes non trouvees !")
	os._exit(1)

# -----------
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(ndense)(x) #256,1024, etc. may work as well
x = Dense(nbclasses)(x) #number of classes
preds = Activation("softmax")(x)
model0 = Model(inputs=base_model.input,outputs=preds)
model0.compile(optimizer = "sgd", loss = 'categorical_crossentropy',metrics = ['accuracy'])
# -----------

lignentete = "classe attendue"+sc+"classif._rep."+sc+"fichier jpg"+sc+"fichier wav"+sc+"numcri"+sc+"classe predite"+sc+"pourcentage prediction"+sc+"ok"+sc+"pourcentage classe attendue"
for k in range(0,nbclasses):
	lignentete=lignentete+sc+labels[k]
with open(logpred, 'a+') as file:
	file.write(lignentete+"\n")

ecrirelog("")
ecrirelog("-------------------------------------------------------------------------------------------")
ecrirelog("-------------------------------------------------------------------------------------------")
ecrirelog("-------------------------------------------------------------------------------------------")
# PHASE 1
ecrirelog("Phase 1 : Prédictions pour le traitement des images dans "+repima)
	
for j in range(0,finboucle):
	#if j==5:
	#	continue
# ---------------------
	if multifreq:
		#ecrirelog("(bande de fréquence "+str(j+1)+")")
		numtest = numcla + j + 1
		snbepoch = tepochs[j]
		#jeutest = jeutestdepart * 100 + j + 1 - un seul jeu de test maintenant (calcul de listes maintenant)
		snumoiseaux = snumoiseauxdepart + str(j + 1)
		listetest = leslistes[j]
	else:
		numtest = numcla
		snbepoch = snbepochs
		listetest = listima
	ecrirelog("debut")
	ecrirelog("classifier = "+str(numtest))
	time.sleep(2)
	ecrirelog("base : "+snumoiseaux)
	ecrirelog("nbepochs : "+snbepoch)
	tabnbtests = {}
	tabnbbons = {}
	tabscore = {}
	
	for esp in labels:
		tabnbtests[esp] = 0
		tabnbbons[esp] = 0
		tabscore[esp] = 0.0

	# -----------
	## Loading the data using generators
	## Checkpoint
	#weightpath = "c:\\atest5\\weights-010.hdf5"
	if int(snbepoch) <10:
		weightpath = baseprog + "/weights/weights" + str(numtest) + "-00" + snbepoch + ".hdf5"
	else:
		if int(snbepoch) <100:
			weightpath = baseprog + "/weights/weights" + str(numtest) + "-0" + snbepoch + ".hdf5"
		else:
			weightpath = baseprog + "/weights/weights" + str(numtest) + "-" + snbepoch + ".hdf5"
	checkpoint = ModelCheckpoint(weightpath)

	ecrirelog("recuperation du fichier weights")
	model = model0
	model.load_weights(weightpath)
	#ecrirelog("fin de recuperation")
		
	## Prediction
	from tensorflow.keras.preprocessing import image
	import numpy as np

	nbesp = len(labels)
	nbpreds = 0
	bilanpred = 0.0
	nbtestsbons = 0
	debpred = (int)(time.time()*1000)
	c= 0
	z = 0
	for f in listetest:
		c = c + 1
		z = z + 1
		if z==100:
			print(str(c)+") traitement de "+f)
			z = 0
			time.sleep(0.2)
		tabj = f.split(sepa)
		ltabj = len(tabj)
		#if ltabj==6 or ltabj ==7 or ltabj ==8:
		if ltabj==6 or ltabj ==8 or ltabj==9 or ltabj ==11:
			if ltabj ==8 or ltabj == 11:
				araj = 2
				classe_attendue = tabj[0]
				if not classe_attendue in labels:
					ecrirelog(classe_attendue+" pas dans labels")
					continue
			else:
				araj = 0
				classe_attendue = ""
			numcri=tabj[araj+1]
			bon,confiance = predict(repima+"/"+f,classe_attendue,tabj[araj],numcri,logpred)
			nbpreds = nbpreds + 1
			if not classe_attendue == "":
				nbtestsbons = nbtestsbons + bon
				tabnbtests[classe_attendue] = tabnbtests[classe_attendue] + 1
				tabnbbons[classe_attendue] = tabnbbons[classe_attendue] + bon
				bilanpred = bilanpred + bon * confiance
		else:
			ecrirelog("format du fichier "+f+" non reconnu")
			continue
		time.sleep(0.08)
	if nbpreds < 1 and not multifreq:
		ecrirelog("aucune prediction effectuee")
		if multifreq:
			continue
		else:
			os._exit(0)
	finpred = (int)(time.time()*1000)
	#tempsmoyenpred = round((finpred-debpred) / nbpreds,1)

	#predictionmoyenne = round(100 * (bilanpred / nbpreds),1)
	#exscoreglobal = round(100*(nbtestsbons/nbpreds),1)
	ecrirelog("-------------------------")
	#ecrirelog("Prediction moyenne : "+str(predictionmoyenne))
	scoreglobal = 0
	nbespreelles = 0
	for esp in labels:
		if tabnbtests[esp]>0:
			tabscore[esp]=round(100*(tabnbbons[esp]/tabnbtests[esp]),1)
			scoreglobal = scoreglobal + tabscore[esp]
			nbespreelles = nbespreelles +1
			ecrirelog("      "+esp+"  :  "+str(tabnbbons[esp])+" / "+str(tabnbtests[esp])+"   --> "+str(tabscore[esp])+" %")
	if nbespreelles >0:
		scoreglobal = round(scoreglobal/nbespreelles,1)
		ecrirelog("numtest="+str(numtest)+"  : pourcentage de bonnes predictions : "+str(scoreglobal))
		#ecrirelog("      temps moyen prediction : "+str(tempsmoyenpred))
		ecrirelog("-------------------------")
	#else
		# ecrirelog("phase 1 : nbre especes attendues = 0")
	
	time.sleep(5)
# $$$ FIN PHASE 1
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$ DEBUT PHASE 2
# PHASE 2 : creation du fichier de prediction par ligne avec les 3 meilleures predictions pour chaque ligne
# et un bilan par classes
# suite correspondant au code de selectionne_par_ligne.py
# envisager aussi un bilab par classes de correspondances (équivalent de reselectionne_15_classes.py
#numoiseaux = S

seuil = 3

ecrirelog("Phase 2 : creation du fichier de prediction par ligne avec les 3 meilleures predictions pour chaque ligne")

logpredfinal = baseprog+ "/txt/resume_par_cri_"+ snumcla + "_" + affinbepochs + "_" + snumoiseauxdepart + "_" + affitest+".csv"
logbilan     = baseprog+ "/txt/bilan_cris_par_espece_" + snumcla + "_" + affinbepochs + "_" + snumoiseauxdepart + "_" + affitest+".csv"
if os.path.exists(logpredfinal):
	os.remove(logpredfinal)
if os.path.exists(logbilan):
	os.remove(logbilan)
	
lentetepredf = "classe attendue"+sc+"fichier jpg"+sc+"fichier wav"+sc+"numcri"
for k in range(1,4):
	lentetepredf = lentetepredf + sc + "Pred. " + str(k) + sc + "Conf. " + str(k) + sc + "ok" + str(k)
with open(logpredfinal, 'a+') as flf:
	flf.write(lentetepredf+"\n")
	
lentetebil = "Espece"+ sc + "Pred1" + sc + "Pred2" + sc + "Pred3" + sc + "Total"

tabokesp = []
for k in range(0,4):
	tabokesp.append({})
	
# --------------------------------
#Phase 2 a : on boucle sur logpred
ligmeilleure = -1
with open(logpred, 'r') as fpred1:
	tabpred1 = fpred1.read().splitlines()
cwav = ""


c = 0
nconserves = 3
premcol = 9
meilleurs_scores = []
meilleurs = []
classespred = []
for j in range(0,nconserves):
	meilleurs_scores.append(-1)
	meilleurs.append(-1)
	classespred.append("")

tabesp = []
for i in range(0,len(tabpred1)):
	ligne = tabpred1[i]
	tabj = ligne.split(sc)
	c = c + 1
	if c == 1:
		nesp = 0
		for j in range(premcol,len(tabj)):
			tabesp.append(tabj[j])
			#ecrirelog(str(nesp)+") "+tabesp[nesp])
			nesp = nesp + 1
		continue

	if len(tabj) < mincol:
		continue
	classat = tabj[0]

	lignefinale = ""
	for k in range(0,5):
		if k==1:
			continue
		lignefinale = lignefinale + tabj[k] + sc
	#lignefinale = lignefinale + classat 
	aumoins1 = False
	classec = classat
	
	for cf in range(0,nconserves):
		#ecrirelog("cf="+str(cf))
		meilleurs[cf] = -1
		meilleurs_scores[cf] = -1
		classespred[cf] = ""
		#for kf in range(0,curseurwav):
		indona = False
		if len(tabj) > premcol:
			kf = 0
			for kf in range(premcol,len(tabj)):
				onpeutprendre = True
				if cf > 0:
					for l in range(0,cf):
						if meilleurs[l] ==kf:
							onpeutprendre = False 
							break
				if len(tabj[kf]) > 0:
					predu = float(tabj[kf])
					clpred = tabesp[kf-premcol]
				else:
					continue
				if cf > 0:
					for l in range(0,cf):
						if classespred[l] ==clpred:
							onpeutprendre = False 
							break
				
				if onpeutprendre:
					if predu > meilleurs_scores[cf] and predu > seuil:
						#ecrirelog("selection "+str(cf+1)+" provisoire de "+str(clpred)+" : "+str(predu))
						meilleurs_scores[cf] = predu
						meilleurs[cf] = kf
						classespred[cf] = clpred
						indona = True
						if clpred==classat:
							ok = 1
						else:
							ok = 0
						if classat == "":
							affiok = ""
						else:
							affiok = str(ok)
						ajouterlignefinale = clpred+sc+str(predu)+sc+affiok+sc
				kf = kf + 1
		if indona == True:
			if not classat == "":
				if cf == 0:
					if not classat in tabokesp[0]:
						for l in range(0,4):
							tabokesp[l][classat] = 0
					tabokesp[0][classat] = tabokesp[0][classat] + 1
				tabokesp[1+cf][classat] = tabokesp[1+cf][classat] + ok
			lignefinale = lignefinale + ajouterlignefinale
			aumoins1 = True
		#else:
		#ecrirelog("on n'a pas ! pour ligne = "+ligne+"    cf="+str(cf))
		#ecrirelog("- cf="+str(cf))
				
	if aumoins1 == True:
		with open(logpredfinal, 'a+') as flf:
			flf.write(lignefinale+"\n")
			ecrirelog("phase2) ecriture ligne finale : "+lignefinale)
			
				
# --------------------------------
# Phase 2 b : calcul des bilans par espèces
nesp = 0
t4 = []

for j in range(0,4):
	t4.append(0)
for esp in tabokesp[0]:
	nlig = tabokesp[0][esp]
	ecrirelog("phase2) esp : nlig="+str(nlig))
	ligne = esp 
	if nlig > 0:
		nesp = nesp + 1
		tok = []
		t3 = 0
		for l in range(0,3):
			t3 = t3 + tabokesp[1+l][esp]
			#ecrirelog(esp+" : nlig="+str(nlig)+"  tok("+str(l)+")="+str(tabokesp[1+l][esp]))
				
			tok.append(round((100*tabokesp[1+l][esp])/nlig,1))
		tok.append(round((100*t3)/nlig,1))
		for l in range(0,4):
			ligne = ligne + sc + str(tok[l])
			t4[l] = t4[l] + tok[l]
			
		ligne = ligne + sc + sc + str(tabokesp[1][esp]) + sc + str(nlig)

		ecrirelog("phase 2 ecriture ligne bilan : "+ligne+" pour esp : "+esp)
		with open(logbilan, 'a+') as fbil:
			if nesp == 1:
				fbil.write(lentetebil+"\n")
			fbil.write(ligne+"\n")
			ecrirelog("phase 2 : ecriture ligne bilan : "+ligne)
if nesp > 0:
	
	lignetot = "Moyenne"
	for l in range(0,4):
		lignetot = lignetot + sc + str(round(t4[l]/nesp,1))
	with open(logbilan, 'a+') as fbil:
		fbil.write(lignetot+"\n")
else:
	ecrirelog("phase 2 : nbre especes pour bilan = 0")

# $$$ FIN PHASE 2
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$ DEBUT PHASE3
# PHASE 3 : creation du bilan avec les 15 classes...
# equivalent de l'ancien programme reselectionne_15_classes.py

if len(tcor) > 0:
	ecrirelog("Phase 3 : creation du bilan 3 avec les classes regroupees comme par exemple otherbirds")


	cl_other = "Otherbirds"
	sepa = "--"
	sc= ";"

	seuil = 3

	#logpredfinal3 = baseprog+ "/txt/predictions_lcl_esp_"+ snumcla + "_" + snumoiseauxdepart + "_" + affitest + "_" + affinbepochs+".csv"
	logbilan3     = baseprog+ "/txt/bilan_cris_par_especes_regroupees_" + snumcla + "_" + affinbepochs + "_" + snumoiseauxdepart + "_" + affitest +".csv"

	tabokesp = []

	for k in range(0,4):
		tabokesp.append({})
		
	#if os.path.exists(logpredfinal3):
	#	os.remove(logpredfinal3)
	if os.path.exists(logbilan3):
		os.remove(logbilan3)
		
	# ------------------------------------------------------------------------------
	#Phase 3a : on boucle sur logpred
	ligmeilleure = -1
	with open(logpred, 'r') as fpred1:
		tabpred1 = fpred1.read().splitlines()
	c = 0
	aumoins1regroupement = False
	nconserves = 3
	meilleurs_scores = []
	meilleurs = []
	classespred = []
	for j in range(0,nconserves):
		meilleurs_scores.append(-1)
		meilleurs.append(-1)
		classespred.append("")

	lentetebil = "Espece"+ sc + "Pred1" + sc + "Pred2" + sc + "Pred3" + sc + "Total"

	tabesp = []
	for i in range(0,len(tabpred1)):
		ligne = tabpred1[i]
		tabj = ligne.split(sc)
		c = c + 1
		if c == 1:
			nesp = 0
			for j in range(9,len(tabj)):
				tabesp.append(tabj[j])
				#ecrirelog(str(nesp)+") "+tabesp[nesp])
				nesp = nesp + 1
				#time.sleep(0.05)
			continue
		#ecrirelog("c="+str(c))
		if len(tabj) < mincol:
			continue
		classat = tabj[0]
		#ecrirelog(" ")
		#ecrirelog("--------")
		#ecrirelog("ligne="+ligne+" : ")
		#ecrirelog(" ")

		#ecrirelog("classat = "+classat)
		
		if classat in tcor:
			classat15 = tcor[classat]
			aumoins1regroupement = True
		else:
			classat15 = classat
	# - - -		
		lignefinale = ""
		for k in range(0,5):
			lignefinale = lignefinale + tabj[k] + sc
		#lignefinale = lignefinale + classat 
		aumoins1 = False
		pourcomp = []
		for k in range(0,nconserves):
			pourcomp.append("")
		for cf in range(0,nconserves):
			meilleurs[cf] = -1
			meilleurs_scores[cf] = -1
			classespred[cf] = ""
			indona = False
			
			if len(tabj) >= mincol:
				kf = 0
				for kf in range(premcol,len(tabj)):
					onpeutprendre = True
					if cf > 0:
						for l in range(0,cf):
							if meilleurs[l] ==kf:
								onpeutprendre = False 
								break
					if len(tabj[kf]) > 0:
						predu = float(tabj[kf])
						clpred = tabesp[kf-premcol]
						if clpred in tcor:
							clpred15 = tcor[clpred]
						else:
							clpred15 = clpred
					else:
						continue
					if cf > 0:
						for l in range(0,cf):
							if classespred[l] ==clpred:
								onpeutprendre = False 
								break
					if onpeutprendre:
						if predu > meilleurs_scores[cf] and predu > seuil:
							#ecrirelog("selection "+str(cf+1)+" provisoire de "+str(clpred)+" : "+str(predu))
							meilleurs_scores[cf] = predu
							meilleurs[cf] = kf
							classespred[cf] = clpred
							indona = True
							if clpred15==classat15:
								ok = 1
							else:
								ok = 0
							if classat15 == "":
								affiok = ""
							else:
								affiok = str(ok)
							ajouterlignefinale = clpred+sc+str(predu)+sc+affiok+sc
							clpred15sel = clpred15
					kf = kf + 1
			if indona == True:
				#ecrirelog("selection "+str(cf+1)+" de "+str(classespred[cf]))
				#ecrirelog("selection en kf = "+str(meilleurs[cf]))
				
				if not classat == "":
					if cf == 0:
						if not classat15 in tabokesp[0]:
							for l in range(0,4):
								tabokesp[l][classat15] = 0
						tabokesp[0][classat15] = tabokesp[0][classat15] + 1
					okret = ok
					#ecrirelog("ok="+str(ok))
					if cf > 0 and okret == 1:
						for l in range(0,cf):
							if pourcomp[l] == classat15:
								#ecrirelog("      -> mise a zero : cf="+str(cf)+"  classat15 = "+classat15+"  pourcomp("+str(l)+")="+pourcomp[l])
								okret = 0
								break
					tabokesp[1+cf][classat15] = tabokesp[1+cf][classat15] + okret
				lignefinale = lignefinale + ajouterlignefinale
				pourcomp[cf] = clpred15sel
				aumoins1 = True
			#else:
				#ecrirelog("on n'a pas !")
		#if aumoins1 == True:
			#with open(logpredfinal3, 'a+') as file:
			#	file.write(lignefinale+"\n")
			#	ecrirelog("phase3) ecriture ligne finale : "+lignefinale)
	# - - -		
	# ------------------------------------------------------------------------------
	if aumoins1regroupement:
		nesp = 0
		t4 = []
		for j in range(0,4):
			t4.append(0)
		for esp in tabokesp[0]:
			nlig = tabokesp[0][esp]
			#ecrirelog(esp+" : nlig="+str(nlig))
			ligne = esp 
			if nlig > 0:
				nesp = nesp + 1
				tok = []
				t3 = 0
				for l in range(0,3):
					t3 = t3 + tabokesp[1+l][esp]
					#ecrirelog(esp+" : nlig="+str(nlig)+"  tok("+str(l)+")="+str(tabokesp[1+l][esp]))
						
					tok.append(round((100*tabokesp[1+l][esp])/nlig,1))
				tok.append(round((100*t3)/nlig,1))
				for l in range(0,4):
					ligne = ligne + sc + str(tok[l])
					t4[l] = t4[l] + tok[l]
				ligne = ligne + sc + sc + str(tabokesp[1][esp]) + sc + str(nlig)
					
				with open(logbilan3, 'a+') as fbil:
					if nesp == 1:
						fbil.write(lentetebil+"\n")
					ecrirelog("phase3) ecriture ligne bilan : "+ligne+" pour esp : "+esp)
					fbil.write(ligne+"\n")
		if nesp > 0:
			lignetot = "Moyenne"
			for l in range(0,4):
				lignetot = lignetot + sc + str(round(t4[l]/nesp,1))
			with open(logbilan3, 'a+') as fbil:
				fbil.write(lignetot+"\n")
		else:
			ecrirelog("phase 3 : nbre especes pour bilan = 0")
	else:
		ecrirelog("aucune espece regroupee : pas de bilan cris par especes regroupees")
else:
	ecrirelog("pas de regroupement d'especes, donc pas de bilan par especes regroupees")
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# $$$ FIN PHASE 3

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$ DEBUT PHASE4
# PHASE 4 : creation du fichier de prediction par fichier wav avec les 3 meilleures predictions pour chaque fichier wav
# ----------
# Phase 4  - etape 1 : creation d'une nouvelle liste triée des prédictions par fichier wav
ecrirelog("Phase 4 : creation du fichier de prediction par fichier wav avec les 3 meilleures predictions pour chaque fichier wav")


tabspe = []
sepspe = "-;-"
for i in range(1,len(tabpred1)):
	ligne = tabpred1[i]
	tabj = ligne.split(sc)
	if len(tabj) > 5:
		clespe = tabj[3]+sepspe+tabj[2]+sepspe+tabj[0]+sepspe+str(i)
		tabspe.append(clespe)
tabspe = sorted(tabspe)
tabpred4 = []
tabpred4.append(tabpred1[0])
nbred = 0
j = 0
tcol3 = []
for clespe in tabspe:
	tablc = clespe.split(sepspe)
	if len(tablc) > 3:
		i = int(tablc[3])
		ligne = tabpred1[i]
		tabpred4.append(ligne)
		tli = ligne.split(sc)
		if len(tli) > 3:
			col3 = tli[3]
		else:
			continue
		tcol3.append(col3)
		if j > 1:
			if col3 == tcol3[j-1]:
				nbred = nbred + 1
		j = j + 1
			
ecrirelog("fin de tri du tableau tabpred4 : nbre de redondances wav : "+str(nbred))
if nbred == 0:
	ecrirelog("aucune redondance de fichiers wav : phase 4 non lancée")
	FAIREPHASE4 = False
else:
	FAIREPHASE4 = True

#with open("test.csv","a+") as file:	
#	for ligne in tabpred4:
#		file.write(ligne+"\n")
# ----------
if FAIREPHASE4:
	#logpredfinal4 = baseprog+ "/txt/predictions_esp_"+ snumcla + "_" + snumoiseauxdepart + "_" + affitest + "_" + affinbepochs+".csv"
	#logbilan4     = baseprog+ "/txt/bilan4_" + snumcla + "_" + snumoiseauxdepart + "_" + affitest + "_" + affinbepochs+".csv"
	#logbilan5     = baseprog+ "/txt/bilan5_cl_" + snumcla + "_" + snumoiseauxdepart + "_" + affitest + "_" + affinbepochs+".csv"

	logpredfinal4 = baseprog+ "/txt/resume_par_wav_"+ snumcla + "_" + affinbepochs + "_" + snumoiseauxdepart + "_" + affitest+".csv"
	logbilan4     = baseprog+ "/txt/bilan_wav_par_espece_" + snumcla + "_" + affinbepochs + "_" + snumoiseauxdepart + "_" + affitest+".csv"
	logbilan5     = baseprog+ "/txt/bilan_wav_par_especes_regroupees_" + snumcla + "_" + affinbepochs + "_" + snumoiseauxdepart + "_" + affitest+".csv"

	tabokesp = []
	tabok15 = []

	for k in range(0,4):
		tabokesp.append({})
		tabok15.append({})
		
	if os.path.exists(logpredfinal4):
		os.remove(logpredfinal4)
	if os.path.exists(logbilan4):
		os.remove(logbilan4)
	if os.path.exists(logbilan5):
		os.remove(logbilan5)

	lentetepredw = "classe attendue" + sc + "fichier wav" 
	for k in range(1,4):
		lentetepredw = lentetepredw + sc + "Cri" + sc + "Pred. " + str(k) + sc + "Conf. " + str(k) + sc + "ok" + str(k)
	with open(logpredfinal4, 'a+') as flf:
		flf.write(lentetepredw+"\n")

		
# -----------------------------------
# Phase 4  -  Etape 2 : on boucle sur logpred
	ligmeilleure = -1
	clignes = []
	curseur = 0
	cwav = ""
	c = 0
	z = 0

	nconserves = 3
	meilleurs_scores = []
	meilleurs = []
	classespred = []
	for j in range(0,nconserves):
		meilleurs_scores.append(-1)
		meilleurs.append("")
		classespred.append("")

	finboucle = len(tabpred4)+1
	classatwav = ""
	exclassatwav = ""

	classec = ""
	exclassec = ""

	lentetebil = "Espece"+ sc + "Pred1" + sc + "Pred2" + sc + "Pred3" + sc + "Total"

	for i in range(0,finboucle):
	#for ligne in tabpred4:
		c = c + 1
		z = z + 1
		if c == 1:
			continue
		#ecrirelog("c="+str(c))
		onchange = False
		fwav = tabj[3]
		if i == finboucle-1:
			onchange = True
			ligne = ""
		else:
			ligne = tabpred4[i]
			tabj = ligne.split(sc)
			if len(tabj) < 25:
				continue
			classatwav = tabj[0]
			if not fwav == cwav:
				onchange = True
		if onchange == True:
			classatwav = tabj[0]
			# µµµµµµµµµ
			if len(clignes) > 0 and not exclassatwav == "":
				for uneligne in clignes:
					tabju = uneligne.split(sc)
					if len(tabju) < mincol:
						continue
					averif = tabju[0]
					if not averif == exclassatwav:
						exclassatwav = ""
						#ecrirelog("annulation de exclassatwav a cause de valeur differente")
						break
			# µµµµµµµµµ
			
			#lignefinale = cwav + sc + exclassatwav 
			lignefinale = exclassatwav + sc + cwav
			aumoins1 = False
			classec = classatwav
			pourcomp = []
			for k in range(0,nconserves):
				pourcomp.append("")
			for cf in range(0,nconserves):
				meilleurs[cf] = ""
				meilleurs_scores[cf] = -1
				classespred[cf] = ""
				#for kf in range(0,curseurwav):
				indona = False
				if len(clignes) > 0:
					kf = 0
					for uneligne in clignes:
						tabju = uneligne.split(sc)
						if len(tabju) < mincol:
							continue
						clpred = tabju[5]
						onpeutprendre = True
						if cf > 0:
							for l in range(0,cf):
								if meilleurs[l] ==clpred:
									onpeutprendre = False 
									break
						predu = float(tabju[6])
						ncri = tabju[4]
						if clpred in tcor:
							clpred15 = tcor[clpred]
						else:
							clpred15 = clpred
						if onpeutprendre:
							if predu > meilleurs_scores[cf] and predu > seuil:
								meilleurs_scores[cf] = predu
								classeattendue = tabju[0]
								meilleurs[cf] = clpred
								fima = tabju[2]
								classespred[cf] = clpred
								indona = True
								if clpred==exclassatwav:
									ok = 1
								else:
									ok = 0
								if classatwav=="":
									affiok=""
								else:
									affiok=str(ok)
								clpred15sel = clpred15
								ajouterlignefinale = ncri+sc+clpred+sc+str(predu)+sc+affiok
						kf = kf + 1
				if indona == True:
					if not exclassatwav == "":
						if exclassatwav in tcor:
							classat15 = tcor[exclassatwav]
						else:
							classat15 = exclassatwav
						if clpred15sel==classat15:
							ok15 = 1
						else:
							ok15 = 0
						if classat15=="":
							affiok=""
						else:
							affiok=str(ok15)
							
						ajouterlignefinale = ajouterlignefinale + sc + affiok
						if cf == 0:
							if not exclassatwav in tabokesp[0]:
								for l in range(0,4):
									tabokesp[l][exclassatwav] = 0
							tabokesp[0][exclassatwav] = tabokesp[0][exclassatwav] + 1
							if not classat15 in tabok15[0]:
								for l in range(0,4):
									tabok15[l][classat15] = 0
							tabok15[0][classat15] = tabok15[0][classat15] + 1
						tabokesp[1+cf][exclassatwav] = tabokesp[1+cf][exclassatwav] + ok
						#ecrirelog(cwav+" cf = "+str(cf)+"   ok="+str(ok))
							
						okret = ok15
						if cf > 0 and okret == 1:
							for l in range(0,cf):
								if pourcomp[l] == classat15:
									#ecrirelog("      -> mise a zero : cf="+str(cf)+"  classat15 = "+classat15+"  pourcomp("+str(l)+")="+pourcomp[l])
									okret = 0
									break
						#ecrirelog(cwav+" cf = "+str(cf)+"   okret="+str(okret))
						#ecrirelog("pour bilan 5 :incrementation de tabok15("+str(cf)+") pour espece "+classat15)
						tabok15[1+cf][classat15] = tabok15[1+cf][classat15] + okret
					lignefinale = lignefinale + sc + ajouterlignefinale
					pourcomp[cf] = clpred15sel
					aumoins1 = True
					
			if aumoins1 == True:
				with open(logpredfinal4, 'a+') as file:
					file.write(lignefinale+"\n")
					
			clignes = []
		clignes.append(ligne)
		cwav = fwav
		exclassatwav = classatwav
	# -----------------------------------
	nesp = 0
	t4 = []
	for j in range(0,4):
		t4.append(0)
	for esp in tabokesp[0]:
		nlig = tabokesp[0][esp]
		#ecrirelog(esp+" : nlig="+str(nlig))
		ligne = esp 
		if nlig > 0:
			nesp = nesp + 1
			tok = []
			t3 = 0
			for l in range(0,3):
				t3 = t3 + tabokesp[1+l][esp]
				#ecrirelog(esp+" : nlig="+str(nlig)+"  tok("+str(l)+")="+str(tabokesp[1+l][esp]))
				
				tok.append(round((100*tabokesp[1+l][esp])/nlig,1))
			tok.append(round((100*t3)/nlig,1))
			for l in range(0,4):
				ligne = ligne + sc + str(tok[l])
				t4[l] = t4[l] + tok[l]
			ligne = ligne + sc + sc + str(tabokesp[1][esp]) + sc + str(nlig)

			with open(logbilan4, 'a+') as fbil:
				if nesp == 1:
					fbil.write(lentetebil+"\n")
				ecrirelog("phase4) ecriture ligne bilan 4: "+ligne+" pour esp : "+esp)
				fbil.write(ligne+"\n")
	if nesp > 0:
		lignetot = "Moyenne"
		for l in range(0,4):
			lignetot = lignetot + sc + str(round(t4[l]/nesp,1))
		with open(logbilan4, 'a+') as fbil:
			fbil.write(lignetot+"\n")
	# tableau bilan par classes :
	nesp = 0
	t4 = []
	for j in range(0,4):
		t4.append(0)
	for esp in tabok15[0]:
		nlig = tabok15[0][esp]
		ligne = esp 
		if nlig > 0:
			nesp = nesp + 1
			tok = []
			t3 = 0
			for l in range(0,3):
				t3 = t3 + tabok15[1+l][esp]
				#ecrirelog(esp+" : nlig="+str(nlig)+"  tok("+str(l)+")="+str(tabok15[1+l][esp]))
				tok.append(round((100*tabok15[1+l][esp])/nlig,1))
			tok.append(round((100*t3)/nlig,1))
			for l in range(0,4):
				ligne = ligne + sc + str(tok[l])
				t4[l] = t4[l] + tok[l]
			ligne = ligne + sc + sc + str(tabok15[1][esp]) + sc + str(nlig)
				
			with open(logbilan5, 'a+') as fbil:
				if nesp == 1:
					fbil.write(lentetebil+"\n")
				ecrirelog("phase4) ecriture ligne bilan 5 : "+ligne+" pour esp : "+esp)
				fbil.write(ligne+"\n")
	if nesp > 0:
		lignetot = "Moyenne"
		for l in range(0,4):
			lignetot = lignetot + sc + str(round(t4[l]/nesp,1))
		with open(logbilan5, 'a+') as fbil:
			fbil.write(lignetot+"\n")
# µµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµµ
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# $$$ FIN PHASE 4
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$ DEBUT PHASE6
# PHASE 6 :  équivalent phase 3 mais creation du bilan avec les classes de la 3ème colonne (autre classification en regroupements)

if len(tcor2) > 0:
	ecrirelog("Phase 6 : creation du bilan 6 avec les classes regroupees de la 3eme colonne de classes[...].csv")


	cl_other = "Otherbirds"
	sc= ";"

	seuil = 3

	logbilan6     = baseprog+ "/txt/bilan_cris_par_espece_deuxieme_regroupement_" + snumcla + "_" + affinbepochs + "_" + snumoiseauxdepart + "_" + affitest + ".csv"

	tabokesp = []

	for k in range(0,4):
		tabokesp.append({})
		
	#if os.path.exists(logpredfinal3):
	#	os.remove(logpredfinal3)
	if os.path.exists(logbilan6):
		os.remove(logbilan6)
		
	# ------------------------------------------------------------------------------
	#Phase 6a : on boucle sur logpred
	ligmeilleure = -1
	with open(logpred, 'r') as fpred1:
		tabpred1 = fpred1.read().splitlines()
	c = 0
	aumoins1deuxiemeregr = False

	nconserves = 3
	meilleurs_scores = []
	meilleurs = []
	classespred = []
	for j in range(0,nconserves):
		meilleurs_scores.append(-1)
		meilleurs.append(-1)
		classespred.append("")

	lentetebil = "Espece"+ sc + "Pred1" + sc + "Pred2" + sc + "Pred3" + sc + "Total"

	tabesp = []
	for i in range(0,len(tabpred1)):
		ligne = tabpred1[i]
		tabj = ligne.split(sc)
		c = c + 1
		if c == 1:
			nesp = 0
			for j in range(9,len(tabj)):
				tabesp.append(tabj[j])
				#ecrirelog(str(nesp)+") "+tabesp[nesp])
				nesp = nesp + 1
				#time.sleep(0.05)
			continue
		#ecrirelog("c="+str(c))
		if len(tabj) < mincol:
			continue
		classat = tabj[0]
		#ecrirelog(" ")
		#ecrirelog("--------")
		#ecrirelog("ligne="+ligne+" : ")
		#ecrirelog(" ")

		#ecrirelog("classat = "+classat)
		
		if classat in tcor2:
			classat15 = tcor2[classat]
			aumoins1deuxiemeregr = True
		else:
			classat15 = classat
	# - - -		
		lignefinale = ""
		for k in range(0,5):
			lignefinale = lignefinale + tabj[k] + sc
		#lignefinale = lignefinale + classat 
		aumoins1 = False
		pourcomp = []
		for k in range(0,nconserves):
			pourcomp.append("")
		for cf in range(0,nconserves):
			meilleurs[cf] = -1
			meilleurs_scores[cf] = -1
			classespred[cf] = ""
			indona = False
			
			if len(tabj) >= mincol:
				kf = 0
				for kf in range(premcol,len(tabj)):
					onpeutprendre = True
					if cf > 0:
						for l in range(0,cf):
							if meilleurs[l] ==kf:
								onpeutprendre = False 
								break
					if len(tabj[kf]) > 0:
						predu = float(tabj[kf])
						clpred = tabesp[kf-premcol]
						if clpred in tcor2:
							clpred15 = tcor2[clpred]
						else:
							clpred15 = clpred
					else:
						continue
					if cf > 0:
						for l in range(0,cf):
							if classespred[l] ==clpred:
								onpeutprendre = False 
								break
					if onpeutprendre:
						if predu > meilleurs_scores[cf] and predu > seuil:
							#ecrirelog("selection "+str(cf+1)+" provisoire de "+str(clpred)+" : "+str(predu))
							meilleurs_scores[cf] = predu
							meilleurs[cf] = kf
							classespred[cf] = clpred
							indona = True
							if clpred15==classat15:
								ok = 1
							else:
								ok = 0
							if classat15=="":
								affiok=""
							else:
								affiok=str(ok)
								
							ajouterlignefinale = clpred+sc+str(predu)+sc+affiok+sc
							clpred15sel = clpred15
					kf = kf + 1
			if indona == True:
				#ecrirelog("selection "+str(cf+1)+" de "+str(classespred[cf]))
				#ecrirelog("selection en kf = "+str(meilleurs[cf]))
				
				if not classat == "":
					if cf == 0:
						if not classat15 in tabokesp[0]:
							for l in range(0,4):
								tabokesp[l][classat15] = 0
						tabokesp[0][classat15] = tabokesp[0][classat15] + 1
					okret = ok
					#ecrirelog("ok="+str(ok))
					if cf > 0 and okret == 1:
						for l in range(0,cf):
							if pourcomp[l] == classat15:
								#ecrirelog("      -> mise a zero : cf="+str(cf)+"  classat15 = "+classat15+"  pourcomp("+str(l)+")="+pourcomp[l])
								okret = 0
								break
					tabokesp[1+cf][classat15] = tabokesp[1+cf][classat15] + okret
				lignefinale = lignefinale + ajouterlignefinale
				pourcomp[cf] = clpred15sel
				aumoins1 = True
			#else:
				#ecrirelog("on n'a pas !")
		#if aumoins1 == True:
			#with open(logpredfinal3, 'a+') as file:
			#	file.write(lignefinale+"\n")
			#	ecrirelog("phase3) ecriture ligne finale : "+lignefinale)
	# - - -		
	# ------------------------------------------------------------------------------
	if aumoins1deuxiemeregr:
		nesp = 0
		t4 = []
		for j in range(0,4):
			t4.append(0)
		for esp in tabokesp[0]:
			nlig = tabokesp[0][esp]
			#ecrirelog(esp+" : nlig="+str(nlig))
			ligne = esp 
			if nlig > 0:
				nesp = nesp + 1
				tok = []
				t3 = 0
				for l in range(0,3):
					t3 = t3 + tabokesp[1+l][esp]
					#ecrirelog(esp+" : nlig="+str(nlig)+"  tok("+str(l)+")="+str(tabokesp[1+l][esp]))
						
					tok.append(round((100*tabokesp[1+l][esp])/nlig,1))
				tok.append(round((100*t3)/nlig,1))
				for l in range(0,4):
					ligne = ligne + sc + str(tok[l])
					t4[l] = t4[l] + tok[l]
				ligne = ligne + sc + sc + str(tabokesp[1][esp]) + sc + str(nlig)
					
				with open(logbilan6, 'a+') as fbil:
					if nesp == 1:
						fbil.write(lentetebil+"\n")
					ligne = ligne + sc + sc + str(tabokesp[1][esp]) + sc + str(nlig)
					ecrirelog("phase 6) ecriture ligne bilan : "+ligne+" pour esp : "+esp)
					fbil.write(ligne+"\n")
		if nesp > 0:
			lignetot = "Moyenne"
			for l in range(0,4):
				lignetot = lignetot + sc + str(round(t4[l]/nesp,1))
			with open(logbilan6, 'a+') as fbil:
				fbil.write(lignetot+"\n")
		else:
			ecrirelog("phase 6 : nbre especes pour bilan = 0")
	else:
		ecrirelog("aucun deuxieme regroupement de classe trouve dans les classes attendues : donc pas de bilan deuxieme regroupement")
else:
	ecrirelog("pas de deuxieme regroupement des classes, donc pas de bilan cris par espece deuxieme regroupement")
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# $$$ FIN PHASE 6

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
