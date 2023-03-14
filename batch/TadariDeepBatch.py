#!/usr/bin/env python3ecrirelog
# -*- coding: utf-8 -*-

from datetime import *
import time
deptime = (int)(time.time()) 


import os
import glob
import sys
import shutil
import librosa
import soundfile
import subprocess
import numpy as np
from PIL import Image
import wave
import time
import mutagen
from mutagen.wave import WAVE
from pydub import AudioSegment

baseprog = os.getcwd()
repsortie = baseprog + "/sortie"
repwavtmp = baseprog + "/wavtmp"

logfile = baseprog + "/logtdv2.log"
if os.path.exists(logfile):
	os.remove(logfile)

logpred0 = repsortie + "/predictions.csv"
if os.path.exists(logpred0):
	os.remove(logpred0)

if os.path.isdir(repsortie):
	print("sous-repertoire sortie existant : le supprimer ou renommer avant de relancer")
	os._exit(0)
	
#-----------------------------------------
def num(aa):
	resu = True
	try:
		bb = int(aa)
	except:
		resu = False
	return(resu)
# -----------------------
def ecrirelog(texte):
	datef = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	texte2 = texte + "   ("+ datef  + ")"
	with open(logfile, 'a+') as file:
		file.write(texte2+"\n")
	print(texte)
# -----------------------
def lance_commande(cmd):
	retour=-1
	try:
		ecrirelog("lancement commande "+cmd)
		a=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)	
		a.wait()
		s1=a.stdout.read()
		if len(s1)>2:
			ecrirelog("stdout : "+str(s1))
		s2=a.stderr.read()
		if len(s2)>2:
			ecrirelog("stderr : "+str(s2))
		retour = a.returncode
		ecrirelog("retour commande : "+str(retour))
	except Exception:
		ecrirelog("Exception lors du lancement de la commande "+cmd+" - Abandon")
		try:
			ecrirelog("detail exception :")
			ecrirelog("   "+str(sys.exc_info()[0]))	
			ecrirelog("   "+str(sys.exc_info()[1]))
			ecrirelog("   erreur ligne "+str(sys.exc_info()[2].tb_lineno))
		except:
			ecrirelog("   messages de l'exception non recuperes")
	return(retour)

# ----------------------------------------------------------------------------
# 0) Lecture des parametres d entree et initialisations
# appel : tadariDeep avec en entrees :
#         repertoire wav a traiter 	
#         numéro du classifier (numtets)
#         numéro d'ordre a prendre pour ce classifier dans classifiers.csv (inutile si valeur = 1)

# lire les parametres en entree
if not os.path.exists("tadaridad.exe"):
	ecrirelog("programme tadaridad.exe absent ! Abandon !")
	
nbpe = len(sys.argv)
if nbpe < 4:
	ecrirelog("3 parametres necessaires : repertoire wav, numero classifier et sous-cas voulu manquants")
	os._exit(0)
nompar = "classifiers.csv"
nparnecessaire = 9
sepa = "--"
sc=";"
mincol = 10
maxfi = 100
seuilmar = 5
exp = 10
pol = False

repwavsource = sys.argv[1]
if not os.path.isdir(repwavsource):
	ecrirelog("repertoire "+repwavsource+" inexistant !")
	os._exit(0)

snumcla = sys.argv[2]
souscasvoulu = sys.argv[3]
parsup = ""
latotale = False
modebug = False

if nbpe > 4:
	for j in range(4,nbpe):
		parsup = sys.argv[j]
		if parsup == "tdauda":
			latotale = True
		if parsup == "debug":
			modebug = True
		if parsup == "maxfi":
			if nbpe > j+1:
				if num(sys.argv[j+1]):
					maxfi = int(sys.argv[j+1])
				j = j + 1
		if parsup == "seuilmar":
			if nbpe > j+1:
				if num(sys.argv[j+1]):
					seuilmar = int(sys.argv[j+1])
				j = j + 1
		if parsup == "exp":
			if nbpe > j+1:
				if num(sys.argv[j+1]):
					exp = float(sys.argv[j+1])
					if not(exp==1 or exp==10):
						ecrirelog("parametre exp incorrect")
						os._exit(0)
				j = j + 1
		if parsup == "pol":
			pol = True
ecrirelog("maxfi="+str(maxfi))		
ecrirelog("seuilmar="+str(seuilmar))		
ecrirelog("exp="+str(exp))		
ecrirelog("pol="+str(pol))		

if pol:
	SRBASE = 16000
else:
	SRBASE = 44100

if not os.path.exists(nompar):
	ecrirelog("fichier classifiers.csv non trouve !")
	os._exit(0)
listima = []
if os.path.isdir(repwavsource):
	os.chdir(repwavsource)
	ListWav = sorted(glob.glob("*.wav"))
	if len(ListWav) < 1:
		ecrirelog("aucun fichier wav trouve dans le repertoire "+repwavsource)
		os._exit(0)
	os.chdir(baseprog)
else:
	ecrirelog("repertoire images non trouve !")
	os._exit(0)

if os.path.isdir(repsortie):
	ecrirelog("effacement du repertoire "+repsortie)
	shutil.rmtree(repsortie, ignore_errors=True)				
	if os.path.isdir(repsortie):
		ecrirelog("effacement du repertoire "+repsortie)
		ecrirelog("echec effacement de "+repsortie)
		os._exit(0)
os.mkdir(repsortie)
if os.path.isdir(repwavtmp):
	ecrirelog("effacement du repertoire "+repwavtmp)
	shutil.rmtree(repwavtmp, ignore_errors=True)				
	if os.path.isdir(repwavtmp):
		ecrirelog("effacement du repertoire "+repwavtmp)
		ecrirelog("echec effacement de "+repwavtmp)
		os._exit(0)
os.mkdir(repwavtmp)

if pol:
	repwav1 = repsortie + "/double"
	if not os.path.isdir(repwav1):
		os.mkdir(repwav1)
else:
	repwav1 = repsortie
	
duree = (int)(time.time()) - deptime
ecrirelog("etape 0 initialisations duree = "+str(duree))
if modebug:
	print("taper sur touche Entree")
	input()
# ----------------------------------------------------------------------------
# Etape 1 : traitement des fichiers .wav
deptime = (int)(time.time()) 

ecrirelog("Etape 1 : conversion des fichiers wav pour traitement")

# 03/01/2023 : attention : passe SRIMP en 4410 en raison de l'utilisation de sox avec speed 10
if exp == 10:
	SRIMP = int(SRBASE/10)
else :
	SRIMP = SRBASE

os.chdir(repwavsource)

llw = len(ListWav)
ecrirelog("Premiere phase de conversion des "+str(llw)+" fichiers wav de "+repwavsource)
n = 0
for fwav in ListWav:
	y, s = librosa.load(fwav, sr=SRIMP)
	NewName = repwavtmp + "/" + fwav
	soundfile.write(data=y,file=NewName,samplerate=SRIMP,subtype="PCM_16")
	if os.path.exists(NewName):
		n = n + 1
		ecrirelog("1a--> "+str(n)+") "+NewName)
os.chdir(repwavtmp)
#
listwav2 = glob.glob("*.wav")
llw2 = len(listwav2)
ecrirelog("fin de etape 1a")
duree = (int)(time.time()) - deptime
ecrirelog("etape 1a duree = "+str(duree))
if modebug:
	print("taper sur touche Entree")
	input()

ecrirelog("Deuxieme phase de conversion des fichiers wav de "+repwavsource)
deptime = (int)(time.time())
n = 0
for fwav in ListWav:
	OldName = repwavtmp + "/" + fwav
	NewName = repwav1 + "/" + fwav
	#+
	if exp==10:
		lance_commande(baseprog + "/sox " + OldName + " " + NewName + " speed 10 rate " + str(SRBASE))
	else:
		os.rename(OldName,NewName)
	#
	if os.path.exists(NewName):
		n = n + 1
		ecrirelog("1b--> "+str(n)+") "+NewName)
ecrirelog("effacement du repertoire "+repwavtmp)
time.sleep(1)
shutil.rmtree(repwavtmp, ignore_errors=True)			
ecrirelog("fin de etape 1b")
duree = (int)(time.time()) - deptime
ecrirelog("etape 1b duree = "+str(duree))
if modebug:
	print("taper sur touche Entree")
	input()
	
ecrirelog('fin de etape 1')

if pol:
	ecrirelog("Cas pollinisateurs : acceleration x 10 supplementaire avant lancement TadaridaD")
	deptime = (int)(time.time())
	n = 0
	for fwav in ListWav:
		OldName = repwav1 + "/" + fwav
		NewName = repsortie + "/" + fwav
		lance_commande(baseprog + "/sox " + OldName + " " + NewName + " speed 10 rate "+str(SRBASE*10))
		if os.path.exists(NewName):
			n = n + 1
			ecrirelog("1c--> "+str(n)+") "+NewName)
	ecrirelog("fin de etape 1c")
	duree = (int)(time.time()) - deptime
	ecrirelog("etape 1c duree = "+str(duree))
	if modebug:
		print("taper sur touche Entree")
		input()
			
ecrirelog('fin de etape 1')
			
# ----------------------------------------------------------------------------
# Etape 2 : lancement de TadaridaD
ecrirelog("Etape 2 : lancement de TadaridaD ")
deptime = (int)(time.time())
os.chdir(baseprog)
if pol:
	retour=lance_commande("tadaridad -x 1 -f 2 -p "+repsortie)
else:
	retour=lance_commande("tadaridad -x 1 -f 2 "+repsortie)
if not retour==0:
	ecrirelog("erreur au retour de TadaridaD : abandon !")
	os._exit(0)
ecrirelog("retour de TadaridaD")
duree = (int)(time.time()) - deptime
ecrirelog("etape 2 duree = "+str(duree))
if modebug:
	print("taper sur touche Entree")
	input()
ecrirelog('fin de etape 2')
# ----------------------------------------------------------------------------
# Etape 3 : conversion des images png en jpg
ecrirelog("Etape 3 : conversion des images png en jpg ")
deptime = (int)(time.time())
repima = repsortie + "/ima2"
os.chdir(repima)
listima2 = sorted(glob.glob("*.png"))
if len(listima2) < 1:
	ecrirelog("aucune image ima2 creee par tadaridaD : abandon !")
	os._exit(0)
n = 0
for f in listima2:
	n = n + 1
	img_png = Image.open(f)
	f2 = f.replace(".png",".jpg")
	img_png.save(f2, "JPEG",quality=100)
	time.sleep(0.01)
	os.remove(f)
	ecrirelog("3--> "+str(n)+") "+f2)
duree = (int)(time.time()) - deptime
ecrirelog("etape 3 duree = "+str(duree))
if modebug:
	print("taper sur touche Entree")
	input()
ecrirelog('fin de etape 3')
# ----------------------------------------------------------------------------
# Etape 4 : traitement deep_predict
#repima = repsortie + "/ima2"
ecrirelog("Etape 4 : traitement deep_predict")
deptime = (int)(time.time())
listima = []
if os.path.isdir(repima):
	os.chdir(repima)
	listima = sorted(glob.glob("*.jpg"))
	if len(listima) < 1:
		ecrirelog("aucun fichier image trouve dans le repertoire "+repima+" : abandon !")
		os._exit(0)
	os.chdir(baseprog)
else:
	ecrirelog("repertoire images non trouve !")
	os._exit(0)

affitest = repwavsource.replace("\\","")
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
	if lep != 8 and lep != 12:
		ecrirelog("nbre de valeurs du parametre nbepoch non compatible avec la version actuelle")
		os._exit(0)
	multifreq = True
	nbre_bases = lep
	
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
	#ecrirelog(affi+filename+"   :   "+"Class : "+class_pred+" -> "+str(rconf))
	
	return(bon,conf)
ecrirelog("-------------------------------------------------------------------------------------------")
# initialisations avant grande boucle

#deptime = (int)(time.time()) 

leslistes = []
snumoiseauxdepart = snumoiseaux

finboucle = 1
affinbepochs = snbepochs
basetxt = repsortie + "/txtpred"
logpred = basetxt + "/predictions_"+ snumcla + "_" + affinbepochs + "_" + snumoiseaux + "_" + affitest + ".csv"

	
if os.path.exists(logpred):
	os.remove(logpred)
if not os.path.exists(basetxt):
	os.mkdir(basetxt)
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
ecrirelog("fin de etape4 = initialisations classifier tensorflow")
duree = (int)(time.time()) - deptime
ecrirelog("etape 4a duree = "+str(duree))
if modebug:
	print("taper sur touche Entree")
	input()

ecrirelog("Etape 4b : prédictions pour chaque fichier jpg")
deptime = (int)(time.time())

# PHASE 1
ecrirelog("Phase 1 : Predictions pour le traitement des images dans "+repima)
	
for j in range(0,finboucle):
	#if j==5:
	#	continue
# ---------------------
	if multifreq:
		#ecrirelog("(bande de frequence "+str(j+1)+")")
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
		#if z==100:
		ecrirelog("4--> "+str(c)+") traitement de "+f)
		z = 0
		tabj = f.split(sepa)
		ltabj = len(tabj)
		#if ltabj==6 or ltabj ==7 or ltabj ==8:
		if ltabj==9:
			classe_attendue = ""
			numcri=tabj[1]
			nomfi = tabj[0]
			bon,confiance = predict(repima+"/"+f,classe_attendue,nomfi,numcri,logpred)
			nbpreds = nbpreds + 1
		else:
			ecrirelog("format du fichier "+f+" non reconnu")
			continue
		time.sleep(0.02)
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
	#else
		# ecrirelog("phase 1 : nbre especes attendues = 0")
	
	time.sleep(1)
# $$$ FIN PHASE 1
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# $$$ DEBUT PHASE 2
# PHASE 2 : creation du fichier de prediction par ligne avec les 3 meilleures predictions pour chaque ligne
# et un bilan par classes
# suite correspondant au code de selectionne_par_ligne.py
# envisager aussi un bilab par classes de correspondances (equivalent de reselectionne_15_classes.py
#numoiseaux = S

seuil = 1

ecrirelog("Phase 2 : creation du fichier de prediction par ligne avec les 3 meilleures predictions pour chaque ligne")

logpredfinal = basetxt + "/resume_par_cri_"+ snumcla + "_" + affinbepochs + "_" + snumoiseauxdepart + "_" + affitest+".csv"
if os.path.exists(logpredfinal):
	os.remove(logpredfinal)
	
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
# Phase 2 b : calcul des bilans par especes
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

	seuil = 1

	#logpredfinal3 = basetxt + "/predictions_lcl_esp_"+ snumcla + "_" + snumoiseauxdepart + "_" + affitest + "_" + affinbepochs+".csv"
	logbilan3     = basetxt + "/bilan_cris_par_especes_regroupees_" + snumcla + "_" + affinbepochs + "_" + snumoiseauxdepart + "_" + affitest +".csv"

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
# Phase 4  - etape 1 : creation d'une nouvelle liste triee des predictions par fichier wav
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
	ecrirelog("aucune redondance de fichiers wav : phase 4 non lancee")
	FAIREPHASE4 = False
else:
	FAIREPHASE4 = True

#with open("test.csv","a+") as file:	
#	for ligne in tabpred4:
#		file.write(ligne+"\n")
# ----------
if FAIREPHASE4:
	#logpredfinal4 = basetxt + "/predictions_esp_"+ snumcla + "_" + snumoiseauxdepart + "_" + affitest + "_" + affinbepochs+".csv"
	#logbilan4     = basetxt + "/bilan4_" + snumcla + "_" + snumoiseauxdepart + "_" + affitest + "_" + affinbepochs+".csv"
	#logbilan5     = basetxt + "/bilan5_cl_" + snumcla + "_" + snumoiseauxdepart + "_" + affitest + "_" + affinbepochs+".csv"

	logpredfinal4 = basetxt + "/resume_par_wav_"+ snumcla + "_" + affinbepochs + "_" + snumoiseauxdepart + "_" + affitest+".csv"
	logbilan4     = basetxt + "/bilan_wav_par_espece_" + snumcla + "_" + affinbepochs + "_" + snumoiseauxdepart + "_" + affitest+".csv"
	logbilan5     = basetxt + "/bilan_wav_par_especes_regroupees_" + snumcla + "_" + affinbepochs + "_" + snumoiseauxdepart + "_" + affitest+".csv"

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
# PHASE 6 :  equivalent phase 3 mais creation du bilan avec les classes de la 3eme colonne (autre classification en regroupements)

if len(tcor2) > 0:
	ecrirelog("Phase 6 : creation du bilan 6 avec les classes regroupees de la 3eme colonne de classes[...].csv")


	cl_other = "Otherbirds"
	sc= ";"

	seuil = 1

	logbilan6     = basetxt + "/bilan_cris_par_espece_deuxieme_regroupement_" + snumcla + "_" + affinbepochs + "_" + snumoiseauxdepart + "_" + affitest + ".csv"

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
# $$$ FIN PHASE 6
#shutil.rmtree(repsortie, ignore_errors=True)	
#on ne supprime plus wavtrav : voir doc

shutil.copy(logpred,logpred0)

duree = (int)(time.time()) - deptime
ecrirelog("etape 4b duree = "+str(duree))
if modebug:
	print("taper sur touche Entree")
	input()
ecrirelog('fin de etape 4')
# ----------------------------------------------------------------------------
# Etape 5 : recollage des fichiers wav en gros fichiers wav
deptime = (int)(time.time()) 
# ********************
repgwav = repsortie + "/Gwav"
#
fitxt = repsortie + "/rwb.txt"
if os.path.exists(fitxt):
	os.remove(fitxt)
	
depart = 0.0
#-----------------------------------------
def traite(f,premfi,depart,fitxt):
	try:
		audio = WAVE(f)
		audio_info = audio.info
		fr = f.replace(".wav","")
		ligne = fr + ";" + premfi + ";" + str(depart)
		with open(fitxt, 'a+') as file:
			file.write(ligne+"\n")
		length = audio_info.length
		depart = depart + length
		retour = True
	except:
		ecrirelog("exception sur "+f)
		retour = False
	return(retour,depart)
#-----------------------------------------
if not os.path.isdir(repgwav):
	os.mkdir(repgwav)
#-----------------------------------------
# version pollinisateurs : utilisation de repwav1 (qui vaut toujours repsortie sir pol == false)
#os.chdir(repsortie)
os.chdir(repwav1)
listec = sorted(glob.glob("*.wav"))
listedeslistes = []
listedespremfi = []
nlistes = 0
ecrirelog("Etape 5 phase 1 : constitution de toutes les listes de fichiers de meme radical")
cradic = ""
listencours = []
n = 0
ll = len(listec)
nfi = 0
premfi = ""
for f in listec:
	tabj = f.split("_")
	n = n + 1
	ecrirelog("5a--> "+str(n)+") "+f)
	ltj = len(tabj)
	if ltj > 1:
		radic = tabj[0]
		if ltj > 3:
			der = tabj[ltj-1].replace(".wav","")
			avant = tabj[ltj-2]
			if len(der) == 3 and num(der) and len(avant) == 6 and num(avant):
				radic = f.replace("_"+avant+"_"+der+".wav","")
		casdernier = False
		if n == ll:
			if radic == cradic:
				casdernier = True
				retour,dep = traite(f,premfi,depart,fitxt)
				if retour:
					listencours.append(f)
					nfi = nfi + 1
		#ecrirelog("avant test : nfi = "+str(nfi)+" maxfi="+str(maxfi))
		if (not radic == cradic or n==ll) or nfi == maxfi:
			l1 = len(listencours)
			if l1 > 0:
				ecrirelog("5a--> enregistrement de la liste "+str(nlistes+1)+" avec "+str(l1)+" fichiers")
				time.sleep(0.05)
				listedeslistes.append(listencours)
				listedespremfi.append(premfi)
				nlistes = nlistes + 1
			listencours = []
			nfi = 0
			cradic = radic
			if n < ll:
				depart = 0.0
		if nfi == 0:
			premfi = "G_"+f.replace(".wav","")
			#ecrirelog("nfi = 0 alimente premfi="+premfi)
		if not casdernier:
			retour,dep = traite(f,premfi,depart,fitxt)
			if retour:
				depart = dep
				listencours.append(f)
				nfi = nfi + 1
	
ecrirelog("Etape 5 phase 2 : fusion des fichiers wav pour chaque serie")
ili = 0
n = 0

for ili in range(0,nlistes):
	uneliste = listedeslistes[ili]
	gpremfi = listedespremfi[ili]
	l1 = len(uneliste)
	ecrirelog("5b--> "+str(ili)+") lancement de la fusion de "+str(l1)+" fichiers wav")
	time.sleep(1)
	n1 = 0
	outfile = repgwav + "/" + gpremfi + ".wav"
	nm = 0
	data= []
	
	for infile in uneliste:
		#w = wave.open(infile, 'rb')
		#data.append( [w.getparams(), w.readframes(w.getnframes())] )
		#w.close()
		if nm==0:
			sfusion = AudioSegment.from_wav(infile)
		else:
			sfusion = sfusion + AudioSegment.from_wav(infile)
		nm = nm + 1
	#output = wave.open(outfile, 'wb')
	#output.setparams(data[0][0])
	#for j in range(0,nm):
	#	output.writeframes(data[j][1])
	#output.close() 
	sfusion.export(outfile, format="wav")
	time.sleep(0.5)
# ********************
duree = (int)(time.time()) - deptime
ecrirelog("etape 5 duree = "+str(duree))
if modebug:
	print("taper sur touche Entree")
	input()
ecrirelog('fin de etape 5')
# ----------------------------------------------------------------------------
# Etape 6 : creation des marqueurs
deptime = (int)(time.time()) 
ecrirelog("Etape 6 : creation des marqueurs")
# ***********************
#seuil = 10
fichpred = repsortie + "/predictions.csv"
fitxt = repsortie + "/rwb.txt"
repmarq = repsortie + "/marqueurs"
if not os.path.isdir(repmarq):
	os.mkdir(repmarq)
	
sep = ";"
sept = "\t"
sepa = "--"
	
if not os.path.exists(fichpred):
	print("fichier "+fichpred+" inexistant !")
	os._exit(0)

# phase1 : lecture de rwb.txt
ecrirelog("Etape 6a : lecture de rwb.txt")
tabrad = {}
tabdep = {}
tablig1 = []
with open(fitxt, 'r') as ficht:
	tablig1 = ficht.read().splitlines()
if len(tablig1) < 1:
	ecrirelog("fichier "+fitxt+" manquant !")
	os._exit(0)
else:
	ecrirelog("6--> len(tablig1)="+str(len(tablig1)))
for row in tablig1:
	tabj = row.split(sep)
	if len(tabj)>2:
		f=tabj[0]
		gpremfi=tabj[1]
		depart=float(tabj[2])
		tabrad[f]=gpremfi
		tabdep[f]=depart
	if depart > 0:
		fichlim = repmarq + "/" + gpremfi.replace(".wav","") + "_limites.txt"
		ligne = str(depart)+sept+str(depart)+sept+"limite"
		with open(fichlim, 'a+') as fl:
			fl.write(ligne+"\n")
		

ecrirelog("Etape 6b : constitution des listes triees de marqueurs par gros fichier wav")
ilig =0
listelignes = {}
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
			if float(conf) > seuilmar:
				tab2 = fima.split(sepa)
				radicp = tab2[0]
				if radicp in tabrad:
					gpremfi = tabrad[radicp]
					depart = tabdep[radicp]
					finnom = tab2[5]
					starttime = finnom.replace(".jpg","")
					#t_start = round(depart/10+float(starttime)/1000,3)
					if pol:
						diviseur = 100
					else:
						diviseur = 1000
					#t_start = round(depart+float(starttime)/1000,3)
					#t_end = round(t_start + float(tab2[3])/1000,3) 
					t_start = round(depart+float(starttime)/diviseur,3)
					t_end = round(t_start + float(tab2[3])/diviseur,3) 
					freq = tab2[4]
					#fichtxt = rep0 + "/" + radicg + "_tdauda.txt"
					ligne = str(t_start)+sept+str(t_end)+sept+classepred+" "+str(conf)+" - "+freq
					cle = str(int(float(t_start)*1000)+1000000)+"_"+str(tabj[0])
					if not gpremfi in listelignes:
						listelignes[gpremfi] = {}
					listelignes[gpremfi][cle] = ligne
					#with open(fichtxt, 'a+') as file:
					#	file.write(ligne+"\n")
ecrirelog("Etape 6c : creation des fichiers de marqueurs")
for gpremfi in listelignes:
	fichtxt = repmarq + "/" + gpremfi.replace(".wav","") + "_tdauda.txt"
	if os.path.exists(fichtxt):
		os.remove(fichtxt)
	with open(fichtxt, 'a+') as file:
		for cle in sorted(listelignes[gpremfi]):
			file.write(listelignes[gpremfi][cle]+"\n")
# ***********************
duree = (int)(time.time()) - deptime
ecrirelog("etape 6 duree = "+str(duree))
if modebug:
	print("taper sur touche Entree")
	input()
ecrirelog('fin de etape 6')
# ----------------------------------------------------------------------------
