#!/usr/bin/python


import cgi, os, re
import sys
import traceback
import os.path as op
import Image

import cgitb
cgitb.enable()

def creerRep(collection, nom):
	"""Crée le sous-répertoire "nom" dans le répertoire de la collection
	"collection". Renvoie le chemin join(collection, nom)"""
	nomRep = op.join(collection, nom)
	if not op.isdir(nomRep): os.mkdir(nomRep)
	return nomRep

def creerThumbs(collection, nomImage):
	"""Crée les répertoires "thumb" et "images" dans la colection, et place deux
	versions réduites de l'image "nomImage". Une de 100x100 max	placée dans
	nomMicroThumb et une plus grande de 1000x1000 max dans nomThumb"""
	
	nomMicroThumb = op.join( creerRep(collection, "thumb"), nomImage)
	nomThumb = op.join( creerRep(collection, "images"), nomImage)
	
	im = Image.open(op.join(collection, nomImage))
	im2 = im.copy()
	
	im.thumbnail((100, 100), Image.ANTIALIAS)
	im.save(nomMicroThumb, quality=50)
	
	im2.thumbnail((1000, 1000), Image.ANTIALIAS)
	im2.save(nomThumb, quality=85)


def isFileOk(name):
	fileOk = False
	base, extension = os.path.splitext(name)
	if base and re.search("\.(jpg|png|jpeg|JPG|JPEG)", extension):
		fileOk = True
	return fileOk

def cleanup(nom):
	return re.sub("[^\.\-_a-zA-Z0-9]", '', nom)
	

try:
	form = cgi.FieldStorage()
	status = "Demarrage\n"
	if "collection" in form and "nomFichier" in form:
		struct_fichier  = form["imageEnvoyee"]
		
		nomFichier = cleanup( struct_fichier.filename )
		collection = cleanup( form["collection"].value )
			
		if nomFichier and isFileOk(nomFichier) and collection:
			if not os.path.isdir(collection):
				os.mkdir(collection)
				status += "Creation du repertoire" + collection + "\n"
				
			cheminFichier = op.join(collection, nomFichier)
			fdOut = open(cheminFichier, "w")
			fdOut.write(struct_fichier.file.read())
			fdOut.close()
			
			creerThumbs(collection, nomFichier)
			
			status = "Fichier '" + nomFichier + "' ajoute dans la collection '" + collection + "'\n"
		else:
			status = "Nom de fichier non conforme ou fichier non conforme : " + nomFichier + "\n"
	else:
		status = "Pas de fichiers/Collection trouves, contient : " + " ".join([str(i) for i in form.keys() ])
except Exception, e:
	sys.stdout.write("Content-type: text/html\n\n")
	print "Erreur '" + str(e) + "', form contient : " + " ".join([str(i) for i in form ])
	traceback.print_exc(file=sys.stdout)
	
sys.stdout.write("Content-type: text/html\n\n")
cgi.log(status)
sys.stdout.write(status + "\n")
