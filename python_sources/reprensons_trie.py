#!/usr/bin/99python3
# -*- coding: utf-8 -*-

numtest = 1001
moteur = 2
nbepochs = 2
batch_size = 4
nb_steps = 50
dimx  = 500
dimy  = 128
ndense= 512
numoiseaux = 1000

jeutest = 2100
jeutest2 = 2101

npos = 50
nconserves = 1

#baseprog = "/sps/mnhn/vigiechiro/vigiechiro-prod-datastore/traitements/test5"
baseprog = "c:/tadarideep"

basetxt = baseprog + "/txt"
baseweights = baseprog + "/weights"
ordi = "in2p3"
#ordi = "perso"

Data_Augmentation = 0
validation_split = 0.15

# parametres pour data_augmentation
width_shift_range= 0.20
height_shift_range= 0.20
horizontal_flip = True
vertical_flip = False
brightness_range_inf = 0.85
brightness_range_sup = 1.15
zoom_range= 0.30
rotation_range = 0

les_scores = []
les_ima2 = []
for j in range(0,npos):
	les_scores.append(-1)
	les_ima2.append("")

meilleurs_scores = []
meilleurs = []


for j in range(0,nconserves):
	meilleurs_scores.append(-1)
	meilleurs.append(-1)
	

import os
from datetime import *
import time
import shutil
import glob
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
	print("parametre moteur incorrect")
	os._exit(1)
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dense,GlobalAveragePooling2D, Activation
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint


logpred = basetxt +"/predictions_"+str(numtest)+"_"+str(nbepochs)+"_"+str(numoiseaux)+"_"+str(jeutest)+".txt"
sc=";"

listasuppr = "listasuppr.txt"
logfile = baseprog + "/rt"+str(numtest)+"-"+str(jeutest)+".log"
if os.path.exists(logfile):
	os.remove(logfile)
if os.path.exists(logpred):
	os.remove(logpred)
#-----------------------------------------
def ecrirelog(texte):
	print(texte)
	with open(logfile, 'a+') as file:
		file.write(texte+"\n")

def predict(filename,classeattendue,f,fichier,numcri,logpred):
	bon = 0
	ecrirelog("predict: "+filename)
	img = image.load_img(filename, target_size=(dimx,dimy)) #load image
	x = image.img_to_array(img) #convert it to array
	x = np.expand_dims(x, axis=0) #simulate batch dimension
	x = preprocess_input(x) #preprocessing
	pred = model.predict(x) #classes prediction
	class_pred = labels[np.argmax(pred)] #find class with highest confidence
	if class_pred == classeattendue:
		bon = 1
		affi = "OK   "
	else:
		affi = "NOK  "
	conf = pred[0,np.argmax(pred)] #confidence
	rconf=round(100*conf,1)
	sc=";"
	#ligne=classeattendue+sc+repb+sc+fichier+sc+numcri+sc+class_pred+sc+str(rconf)+sc+str(bon)
	#ligne=classeattendue+sc+str(numtest)+"_"+str(jeutest)+sc+fichier+sc+numcri+sc+class_pred+sc+str(rconf)+sc+str(bon)
	ligne_debut = classeattendue+sc+str(numtest)+"_"+str(jeutest)+sc+f+sc+fichier+sc+numcri+sc+class_pred+sc+str(rconf)+sc+str(bon)
	ligne_fin = ""
	confat = 100
	ligne_milieu = sc + "0"
	for k in range(0,len(labels)):
		confj = pred[0,k]
		rconfj = round(100*confj,1)
		#print(labels[k]+"  :  "+str(rconfj))
		ligne_fin=ligne_fin + sc + str(rconfj)
		if labels[k]==classeattendue:
			ligne_milieu = sc + str(rconfj)
			confat = rconfj
			print(fichier+" : confat = "+str(confat))
	ligne = ligne_debut + ligne_milieu + ligne_fin
	with open(logpred, 'a+') as file:
		file.write(ligne+"\n")
	print(affi+filename+"   :   "+"Class : "+class_pred+" -> "+str(rconf))

	return(bon,conf,confat)
#-----------------------------------------
depart = (int)(time.time()) 

numtestdepart = numtest
# for j in range(0,1)
finboucle = 1


for j in range(0,finboucle):
# ---------------------

	print("debut")
	if moteur == 1:
		base_model = Xception(include_top=False, weights="imagenet",input_tensor=tf.keras.layers.Input(shape=(dimx,dimy,3)))
	if moteur == 2:
		base_model = MobileNet(include_top=False, weights="imagenet",input_tensor=tf.keras.layers.Input(shape=(dimx,dimy,3)))
	if moteur == 3:
		base_model = ResNet50(include_top=False, weights="imagenet",input_tensor=tf.keras.layers.Input(shape=(dimx,dimy,3)))


		
	repoiseaux = baseprog + "/oiseaux" + str(numoiseaux)
	import os
	nbclasses = 0
	nbtotoiseaux = 0
	labels = []
	tabnbtests = {}
	tabnbbons = {}
	tabscore = {}
	for f in sorted(os.listdir(repoiseaux)):
		if os.path.isdir(os.path.join(repoiseaux, f)):
			labels.append(f)
			nbclasses = nbclasses + 1 
			for g in os.listdir(repoiseaux+"/"+f):
				nbtotoiseaux = nbtotoiseaux + 1
	
	for esp in labels:
		tabnbtests[esp] = 0
		tabnbbons[esp] = 0
		tabscore[esp] = 0.0
			
	print("nombre de classes : "+str(nbclasses))

	if nbclasses < 1:
		print("classes non trouvees !")
		os._exit(1)

	lignentete = "classe attendue"+sc+"repertoire"+sc+"fichier jpg"+sc+"fichier wav"+sc+"numcri"+sc+"classe predite"+sc+"pourcentage prediction"+sc+"ok"+sc+"pourcentage classe attendue"
	for k in range(0,nbclasses):
		lignentete=lignentete+sc+labels[k]
	with open(logpred, 'a+') as file:
		file.write(lignentete+"\n")

	x = base_model.output
	x = GlobalAveragePooling2D()(x)
	x = Dense(ndense)(x) #256,1024, etc. may work as well
	x = Dense(nbclasses)(x) #number of classes
	preds = Activation("softmax")(x)

	model = Model(inputs=base_model.input,outputs=preds)

	model.compile(optimizer = "sgd", loss = 'categorical_crossentropy',metrics = ['accuracy'])

	
	## Loading the data using generators
	## Checkpoint
	if nbepochs < 10:
		weightpath = baseweights + "/weights" + str(numtest) + "-00" + str(nbepochs) + ".hdf5"
	else:
		weightpath = baseweights + "/weights" + str(numtest) + "-0" + str(nbepochs) + ".hdf5"
	
	checkpoint = ModelCheckpoint(weightpath)

	print("recuperation du fichier weights calcule hier  pour le modele")
	model.load_weights(weightpath)
	print("fin de recuperation")
		
	## Prediction
	from tensorflow.keras.preprocessing import image
	import numpy as np

	nbesp = len(labels)
	nbpreds = 0
	repjeutest = baseprog + "/jeutest"+str(jeutest)
	repjeutest2 = baseprog + "/jeutest"+str(jeutest2)
	tabj = []
	bilanpred = 0.0
	nbtestsbons = 0
	sepa = "--"
	debpred = (int)(time.time()*1000)
	
	nomwavprec = ""
	curseurwav = 0

	colig = 0
	zz = 0
	os.chdir(repjeutest)
	listejpg = sorted(glob.glob("*.jpg"))
	lenli = len(listejpg)
	for f in listejpg:
		time.sleep(0.05)
		colig = colig + 1
		tabj = f.split(sepa)
		if len(tabj)>3:
			classe_attendue = tabj[0]
			if not classe_attendue in labels:
				ecrirelog(classe_attendue+" pas dans labels")
				continue
			if len(tabj)==7:
				numcri=tabj[2]
				nomwav = tabj[1]
			else:
				numcri=tabj[3]
				nomwav = tabj[2]
			bon,confiance,confat = predict(repjeutest+"/"+f,classe_attendue,f,nomwav,numcri,logpred)
			nbpreds = nbpreds + 1
			nbtestsbons = nbtestsbons + bon
			tabnbtests[classe_attendue] = tabnbtests[classe_attendue] + 1
			tabnbbons[classe_attendue] = tabnbbons[classe_attendue] + bon
			bilanpred = bilanpred + bon * confiance
			# ---
			seriefinie = False
			if nomwav == nomwavprec:
				ecrirelog("nomwav=nomprec")
				
				if curseurwav < npos-1:
					les_scores[curseurwav] = confat
					les_ima2[curseurwav] = f
					curseurwav = curseurwav + 1
				if colig == lenli:
					seriefinie = True
			else:
				ecrirelog("colig="+str(colig)+"  nomwav="+nomwav+"  nomwavprec="+nomwavprec)
				seriefinie = True
			
				# selection des meilleurs scores
#$$$$$$$$$$$$$$$$
				# tri des meilleurs
			if seriefinie:
				for cf in range(0,nconserves):
					#ecrirelog("cf="+str(cf))
					meilleurs[cf] = -1
					meilleurs_scores[cf] = -1
					for kf in range(0,curseurwav):
						if kf >= npos:
							break
						onpeutprendre = True
						if cf > 0:
							for l in range(0,cf):
								if meilleurs[l] ==kf:
									onpeutprendre = False 
									break
						if onpeutprendre:
							if les_scores[kf] > meilleurs_scores[cf]:
								meilleurs_scores[cf] = les_scores[kf]
								meilleurs[cf] = kf
					# copie dans deuxieme jeu de test5
					if meilleurs[cf]>-1:
						nomfi = les_ima2[meilleurs[cf]]
						ecrirelog("copie de "+nomfi)
						shutil.copyfile(repjeutest + "/" + nomfi,repjeutest2 + "/" + nomfi)
						
						#print("selection de "+nomfi+" comme meilleur numero "+str(cf+1))
				# reinitialisations pour la suite
				les_scores[0] = confat
				les_ima2[0] = f
				curseurwav = 1
			nomwavprec = nomwav
		else:
			ecrirelog("len tabj < 3 !")
		
			#ecrirelog("affectation de nomwavprec = "+nomwavprec)
	if nbpreds < 1:
		print("aucune prediction effectuee")
		os._exit(0)
	finpred = (int)(time.time()*1000)
	tempsmoyenpred = round((finpred-debpred) / nbpreds,1)

	predictionmoyenne = round(100 * (bilanpred / nbpreds),1)
	exscoreglobal = round(100*(nbtestsbons/nbpreds),1)
	print("-------------------------")
	print("Prediction moyenne : "+str(predictionmoyenne))
	scoreglobal = 0
	nbespreelles = 0
	for esp in labels:
		if tabnbtests[esp]>0:
			tabscore[esp]=round(100*(tabnbbons[esp]/tabnbtests[esp]),1)
			scoreglobal = scoreglobal + tabscore[esp]
			nbespreelles = nbespreelles +1
		print("      "+esp+"  :  "+str(tabnbbons[esp])+" / "+str(tabnbtests[esp])+"   --> "+str(tabscore[esp])+" %")
	scoreglobal = round(scoreglobal/nbespreelles,1)
	print("Pourcentage de bonnes predictions : "+str(scoreglobal))
	print("      temps moyen prediction : "+str(tempsmoyenpred))
	print("-------------------------")
	#enregistrement du résultat
	logres = "resultats_sons.txt"
	datetest = datetime.now().strftime("%y %m %d %H %M %S")
	tempstest = 0
	if moteur==1:
		nom_moteur = "xception"
	if moteur==2:
		nom_moteur = "mobilenet"
	if moteur==3:
		nom_moteur = "resnet50"
	texte = str(numtest)+";"+datetest+";"+ordi+";"+str(tempstest)+";"+nom_moteur+";"+str(nbepochs)+";"+str(batch_size)+";"+str(nb_steps)+";"+str(dimx)+";"+str(dimy)+";"+str(ndense)+";"+repoiseaux+";"+str(nbtotoiseaux)+";"+repjeutest+";"+str(nbpreds)+";"+ str(nbtestsbons)+";"+str(predictionmoyenne)
	#texte = str(numtest)+";"+datetest+";"+ordi+";"+str(tempstest)+";"+nom_moteur+";"+str(nbepochs)+";"+str(batch_size)+";"+str(nb_steps)+";"+str(dimx)+";"+str(dimy)+";"+str(ndense)+";"+repbasecourt+";"+str(nbtotoiseaux)+";"+repjeucourt+";"+str(nbpreds)+";"+ str(nbtestsbons)+";"+str(predictionmoyenne)

	param_augm = str(validation_split)+";"+str(round(width_shift_range,2))+";"+str(round(height_shift_range,2))+";"+str(horizontal_flip)+";"+str(vertical_flip)+";"+str(round(brightness_range_inf,2))+";"+str(round(brightness_range_sup,2))+";"+str(round(zoom_range,2))+";"+str(round(rotation_range,2))
	#texte=texte+";"+str(scoreglobal)+";"+param_augm
	texte=texte+";"+str(scoreglobal)
	
	for esp in labels:
		texte = texte + ";" + str(tabscore[esp])	
	
	with open(logres, 'a+') as file:
		file.write(texte+"\n")



