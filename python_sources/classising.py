#!/usr/bin/env python3
# -*- coding: utf-8 -*-

numtest = 1001
numoiseaux = 1000
jeutest = 1500
nbre_bases = 1
baseprog = "c:/tadarideeptest"
#baseprog = "/sps/mnhn/vigiechiro/vigiechiro-prod-datastore/traitements/test5"

moteur = 2
nbepochs = 2
batch_size = 4
nb_steps_max = 50
dimx  = 500
dimy  = 128
ndense= 512

#ordi = "in2p3"
ordi = "perso"

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

import os
from datetime import *
import time
basetxt = baseprog + "/txt"
baseweights = baseprog + "/weights"

if not os.path.isdir(baseprog):
	print("repertoire de travail "+baseprog+" inexistant !")
	os._exit(0)
if not os.path.isdir(basetxt):
	os.mkdir(basetxt)
if not os.path.isdir(baseweights):
	os.mkdir(baseweights)


import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dense,GlobalAveragePooling2D, Activation
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint

## Prediction
from tensorflow.keras.preprocessing import image
import numpy as np

#os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

listemoteurs=["Xception","MobileNet","ResNet50","MobileNetV2","NASNetMobile","DenseNet","EfficientNet","InceptionResNetV2","InceptionV3","ResNet","ResNetV2","VGG16","VGG19"]
sc=";"

# ---------------------------------------------------------------------------------------------
def predict(filename,classeattendue,repb,fichier,numcri,logpred):
	bon = 0
	#print(filename)
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
	ligne=classeattendue+sc+repb+sc+fichier+sc+numcri+sc+class_pred+sc+str(rconf)+sc+str(bon)
	for k in range(0,len(labels)):
		confj = pred[0,k]
		rconfj = round(100*confj,1)
		#print(labels[k]+"  :  "+str(rconfj))
		ligne=ligne+sc+str(rconfj)
	with open(logpred, 'a+') as file:
		file.write(ligne+"\n")
	#print(affi+filename+"   :   "+"Class : "+class_pred+" -> "+str(rconf))
	return(bon,conf)

# ---------------------------------------------------------------------------------------------
numtestdepart = numtest
# for j in range(0,1)
finboucle = nbre_bases
dimxdep = dimx
dimydep = dimy

print("debut")

for j in range(0,finboucle):
	numtest = numtestdepart + j
	#logpred = basetxt + "/predictions_"+str(numtest)+".txt"
	dimx = dimxdep
	dimy = dimydep

	if moteur==5:
		dimx = 224
		dimy = 224
	
# ----------------------------------------
	if moteur == 1:
		from tensorflow.keras.applications.xception import Xception, preprocess_input
	if moteur == 2:
		from tensorflow.keras.applications.mobilenet import MobileNet, preprocess_input
		print("import mobilenet")
	if moteur == 3:
		from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
	if moteur == 4:
		from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
	if moteur == 5:
		from tensorflow.keras.applications.nasnet import NASNetMobile, preprocess_input
	if moteur == 6:
		from tensorflow.keras.applications.densenet import DenseNet121, preprocess_input
	if moteur == 7:
		from tensorflow.keras.applications.efficientnet import EfficientNetB0, preprocess_input
	if moteur == 8:
		from tensorflow.keras.applications.inception_resnet_v2 import InceptionResNetV2, preprocess_input
	if moteur == 9:
		from tensorflow.keras.applications.inception_v3 import InceptionV3, preprocess_input
	if moteur == 10:
		from tensorflow.keras.applications.resnet import ResNet101, preprocess_input
	if moteur == 11:
		from tensorflow.keras.applications.resnet_v2 import ResNet101V2, preprocess_input
	if moteur == 12:
		from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
	if moteur == 13:
		from tensorflow.keras.applications.vgg19 import VGG19, preprocess_input
	# ----------------------------------------
	if moteur <1 or moteur>13:
		print("parametre moteur incorrect")
		os._exit(1)
	
	print("numtest="+str(numtest))
	depart = (int)(time.time()) 
	## Parameters
	## Transfer-Learning model : we construct the classification part
	if moteur == 1:
		base_model = Xception(include_top=False, weights="imagenet",input_shape=(dimx,dimy,3))
	if moteur == 2:
		base_model = MobileNet(include_top=False, weights="imagenet",input_shape=(dimx,dimy,3))
	if moteur == 3:
		base_model = ResNet50(include_top=False, weights="imagenet",input_shape=(dimx,dimy,3))
	if moteur == 4:
		base_model = MobileNetV2(include_top=False, weights="imagenet",input_tensor=tf.keras.layers.Input(shape=(dimx,dimy,3)))
	if moteur == 5:
		base_model = NASNetMobile(include_top=False, weights="imagenet",input_shape=(dimx,dimy,3))
	if moteur == 6:
		base_model = DenseNet121(include_top=False, weights="imagenet",input_shape=(dimx,dimy,3))
	if moteur == 7:
		base_model = EfficientNetB0(include_top=False, weights="imagenet",input_shape=(dimx,dimy,3))
	if moteur == 8:
		base_model = InceptionResNetV2(include_top=False, weights="imagenet",input_shape=(dimx,dimy,3))
	if moteur == 9:
		base_model = InceptionV3(include_top=False, weights="imagenet",input_shape=(dimx,dimy,3))
	if moteur == 10:
		base_model = ResNet101(include_top=False, weights="imagenet",input_shape=(dimx,dimy,3))
	if moteur == 11:
		base_model = ResNet101V2(include_top=False, weights="imagenet",input_shape=(dimx,dimy,3))
	if moteur == 12:
		base_model = VGG16(include_top=False, weights="imagenet",input_shape=(dimx,dimy,3))
	if moteur == 13:
		base_model = VGG19(include_top=False, weights="imagenet",input_shape=(dimx,dimy,3))

	#repbasecourt = "oiseaux" + str(numoiseaux) + "0" + str(j+1)
	if nbre_bases==1:
		repbasecourt = "oiseaux" + str(numoiseaux)
	else:
		repbasecourt = "oiseaux" + str(numoiseaux) + str(101+j)[1:3]
	
	repbaselong  = baseprog + "/" + repbasecourt
	nbclasses = 0
	nbtotoiseaux = 0

	labels = []

	tabnbtests = {}
	tabnbbons = {}
	tabscore = {}
	for f in sorted(os.listdir(repbaselong)):
		if os.path.isdir(os.path.join(repbaselong, f)):
			labels.append(f)
			nbclasses = nbclasses + 1 
			for g in os.listdir(repbaselong+"/"+f):
				nbtotoiseaux = nbtotoiseaux + 1
			
	print("nombre de classes : "+str(nbclasses))

	if nbclasses < 1:
		print("classes non trouvees !")
		os._exit(1)
		
		
	x = base_model.output
	x = GlobalAveragePooling2D()(x)
	x = Dense(ndense)(x) #256,1024, etc. may work as well
	x = Dense(nbclasses)(x) #number of classes

	preds = Activation("softmax")(x)

	model = Model(inputs=base_model.input,outputs=preds)
	model.compile(optimizer = "sgd", loss = 'categorical_crossentropy',metrics = ['accuracy'])

	## Loading the data using generators

	if Data_Augmentation == 0:
		data_generator = ImageDataGenerator(preprocessing_function = preprocess_input,
										   validation_split = validation_split)

	else:
		data_gen_args = {}
		data_gen_args["preprocessing_function"] = preprocess_input	
		if validation_split > 0:
			data_gen_args["validation_split"] = validation_split
		if width_shift_range > 0:
			data_gen_args["width_shift_range"] = width_shift_range
		if height_shift_range > 0:
			data_gen_args["height_shift_range"] = height_shift_range
		if horizontal_flip:
			data_gen_args["horizontal_flip"] = True
		if vertical_flip:
			data_gen_args["vertical_flip"] = True
		if brightness_range_inf > 0 and brightness_range_sup > brightness_range_inf:
			data_gen_args["brightness_range"] =[brightness_range_inf,brightness_range_sup]
		if zoom_range > 0:
			data_gen_args["zoom_range"] = zoom_range
		if rotation_range > 0:
			data_gen_args["rotation_range"] = rotation_range
		data_generator = ImageDataGenerator(**data_gen_args)
										   
	train_generator = data_generator.flow_from_directory(directory = repbaselong+"/",
		batch_size = batch_size,
		class_mode = 'categorical',
		target_size = (dimx,dimy),
		subset = 'training')

	validation_generator = data_generator.flow_from_directory(directory = repbaselong+"/",
		batch_size = batch_size,
		class_mode = 'categorical',
		target_size = (dimx,dimy),
		subset = 'validation')

	## Checkpoint
	weightpath = baseweights + "/weights" + str(numtest) + "-{epoch:03d}.hdf5"
	checkpoint = ModelCheckpoint(weightpath)

	print("avant training")
	## Training
	#model.fit(train_generator, validation_data = , epochs = nbepochs, callbacks = [checkpoint])
	
	#nb_steps = int(nbtotoiseaux * 8/(10 * batch_size))
	#if nb_steps > nb_steps_max:
	nb_steps = nb_steps_max
	
	print("nb_steps="+str(nb_steps))

	history = model.fit_generator(train_generator,validation_data=validation_generator, steps_per_epoch=nb_steps,epochs=nbepochs, callbacks = [checkpoint])
	
	print("apres training")
	nbesp = len(labels)
	if nbre_bases==1:
		repjeucourt = "jeutest"+str(jeutest)
	else:
		repjeucourt = "jeutest"+str(jeutest)+str(j+101)[1:3]
	repjeulong = baseprog + "/" + repjeucourt
	lignentete = "classe attendue"+sc+"repertoire"+sc+"fichier"+sc+"numcri"+sc+"classe predite"+sc+"pourcentage prediction"+sc+"ok"
	for k in range(0,nbclasses):
		lignentete=lignentete+sc+labels[k]

	# ------------------ boucle des predictions de nbepochs = 1 à vauleur initiale de nbepochs	
	for z in range(0,nbepochs):
	
		for esp in labels:
			tabnbtests[esp] = 0
			tabnbbons[esp] = 0
			tabscore[esp] = 0.0
	
		weightpath = baseweights + "/weights" + str(numtest) + "-" + str(1001+z)[1:4] + ".hdf5"
		#weightpath = "weights" + str(numtest) + "-0" + str(nbepochs) + ".hdf5"

		checkpoint = ModelCheckpoint(weightpath)

		print("recuperation du fichier weights calcule hier  pour le modele")
		model.load_weights(weightpath)
		print("fin de recuperation")
			
		logpred = basetxt + "/predictions_"+str(numtest)+"_"+str(z+1)+"_"+str(numoiseaux)+"_"+str(jeutest)+".txt"
		with open(logpred, 'a+') as file:
			file.write(lignentete+"\n")
		nbpreds = 0
		tabj = []
		bilanpred = 0.0
		nbtestsbons = 0
		sepa="--"
		debpred = (int)(time.time()*1000)
		for f in sorted(os.listdir(repjeulong)):
			tabj = f.split(sepa)
			if len(tabj)>2:
				classe_attendue = tabj[0]
				if classe_attendue in labels:
					print("classat = "+classe_attendue)
				else:
					print(classe_attendue+" pas dans labels")
					continue
				
				numcri=tabj[3].replace(".jpg","")
				bon,confiance = predict(repjeulong+"/"+f,classe_attendue,tabj[1],tabj[2],numcri,logpred)
				nbpreds = nbpreds + 1
				nbtestsbons = nbtestsbons + bon
				tabnbtests[classe_attendue] = tabnbtests[classe_attendue] + 1
				tabnbbons[classe_attendue] = tabnbbons[classe_attendue] + bon
				bilanpred = bilanpred + bon * confiance
		if nbpreds < 1:
			print("aucune prediction effectuee")
			os._exit(0)
		finpred = (int)(time.time()*1000)
		tempsmoyenpred = round((finpred-debpred) / nbpreds,1)

		predictionmoyenne = round(100 * (bilanpred / nbpreds),1)
		exscoreglobal = round(100*(nbtestsbons/nbpreds),1)
		print("-------------------------")
		scoreglobal = 0
		nbesp_pred = 0
		for esp in labels:
			if tabnbtests[esp]>0:
				tabscore[esp]=round(100*(tabnbbons[esp]/tabnbtests[esp]),1)
				scoreglobal = scoreglobal + tabscore[esp]
				nbesp_pred =  nbesp_pred + 1
			print("      "+esp+"  :  "+str(tabnbbons[esp])+" / "+str(tabnbtests[esp])+"   --> "+str(tabscore[esp])+" %")
		if nbesp_pred > 0:
			scoreglobal = round(scoreglobal/nbesp_pred,1)
		print("Score global : "+str(scoreglobal))
		print("-------------------------")

		#enregistrement du résultat
		logres = baseprog + "/resultats_sons.csv"
		datetest = datetime.now().strftime("%y %m %d %H %M %S")
		tempstest = (int)(time.time()) - depart
		nom_moteur = listemoteurs[moteur-1]
		infoacc = ""
		try:
			if "acc" in history.history:
				infoacc = str(history.history['acc'][z])
		except:
			infoacc = "!"
		texte = str(numtest)+";"+datetest+";"+ordi+";"+str(tempstest)+";"+nom_moteur+";"+str(z+1)+";"+str(batch_size)+";"+str(nb_steps)+";"+str(dimx)+";"+str(dimy)+";"+str(ndense)+";"+repbasecourt+";"+str(nbtotoiseaux)+";"+repjeucourt+";"+infoacc+";"+str(nbpreds)+";"+ str(nbtestsbons)+";"+str(predictionmoyenne)
		#for key in history.history:
		#	print("key: "+key+" : "+str(history.history[key]))

		param_augm = str(validation_split)+";"+str(round(width_shift_range,2))+";"+str(round(height_shift_range,2))+";"+str(horizontal_flip)+";"+str(vertical_flip)+";"+str(round(brightness_range_inf,2))+";"+str(round(brightness_range_sup,2))+";"+str(round(zoom_range,2))+";"+str(round(rotation_range,2))

		#texte=texte+";"+str(scoreglobal)+";"+param_augm
		texte=texte+";"+str(scoreglobal)
		for esp in labels:
			texte = texte + ";" + str(tabscore[esp])
		
		with open(logres, 'a+') as file:
			file.write(texte+"\n")
	# ---------------------------------- fin boucle des predictions
	if j< finboucle-1:
		time.sleep(30)

