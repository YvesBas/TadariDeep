import os
import sys
import time
import glob
from PIL import Image

nbpar = len(sys.argv)
if nbpar < 2:
	print("manque parametre repertoire des images a convertir")
	os._exit(0)
repima = sys.argv[1]

if not os.path.isdir(repima):
	print(repima+" : repertoire ima2 non trouve : abandon !")
os.chdir(repima)
listima2 = sorted(glob.glob("*.png"))
if len(listima2) < 1:
	print("aucune image ima2 creee par tadaridaD : abandon !")
for f in listima2:
	try:
		img_png = Image.open(f)
		f2 = f.replace(".png",".jpg")
		img_png.save(f2, "JPEG",quality=100)
		print("conversion de "+f+" en "+f2)
		os.remove(f)
	except:
		print("Exception lors de la conversion du fichier "+f)
		try:
			print("detail exception :")
			print("   "+str(sys.exc_info()[0]))	
			print("   "+str(sys.exc_info()[1]))
		except:
			print("   messages de l'exception non recuperes")
		