#!/usr/bin/python
# encoding: utf-8

import cgi, re
import os.path as op
import zipfile
import os
import shutil

import cgitb
cgitb.enable()


DEFAULT_INDEX = """
<html xml:lang="fr" lang="fr">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<meta name="generator" content="Adobe Lightroom"/>
<title>%s</title>
<!-- Download SimpleViewer at www.airtightinteractive.com/simpleviewer -->
<script type="text/javascript" src="swfobject.js"></script>
<style type="text/css">	
	/* hide from ie on mac \*/
	html {
		height: 100%%;
		overflow: hidden;
	}
	
	#flashcontent {
		height: 100%%;
	}
	/* end hide */

	body {
		height: 100%%;
		margin: 0;
		padding: 0;
		background-color: #181818;
		color:#ffffff;
	}
	p {
		text-align:center;
	}
		
	a:link {
		color: #AAAAAA;
	}
	
	a:visited: {
		#AAAAAA;
	}
</style>
</head>
<body>
	<p>Vous pouvez télécharger l'ensemble des %d images en cliquant <a href="archive.zip">ici</a></p>
	<div id="flashcontent">SimpleViewer requires Adobe Flash. <a href="http://www.macromedia.com/go/getflashplayer/">Get Adobe Flash.</a> If you have Flash installed, <a href="index.html?detectflash=false">click to view gallery</a>.</div>	
	<script type="text/javascript">
		var fo = new SWFObject("viewer.swf", "viewer", "100%%", "100%%", "7", "#333333");	
		fo.addVariable("preloaderColor", "0xffffff");
		fo.addVariable("xmlDataPath", "galerie.xml");	
		fo.addVariable( "langOpenImage", "Ouvrir l'image dans une nouvelle fenêtre" );
		fo.addVariable("langAbout", "A propos de");	
		fo.write("flashcontent");	
	</script>	
</body>
</html>
"""

XML_BEGIN = """<?xml version="1.0" encoding="UTF-8"?>
<simpleviewerGallery maxImageWidth="1024" maxImageHeight="1024" textColor="0xFFFFFF" frameColor="0xFFFFFF" frameWidth="5" stagePadding="10" thumbnailColumns="3" thumbnailRows="5" navPosition="left" title="%s" enableRightClickOpen="true" backgroundImagePath="" imagePath="images/" thumbPath="thumbs/">"""
XML_PART  = """
	<image>
		<filename>%s</filename>
		<caption></caption>
	</image>"""
XML_END   = """
</simpleviewerGallery>"""

def cleanup(nom):
	"""Nettoyage du nom : On ne conserve que :
	 - les lettres (majuscule/minuscule)
	 - les chiffres
	 - Les caractères ".", "-", et "_"
	 """ 
	return re.sub("[^\.\-_a-zA-Z0-9]", '', nom)

def isImage(cheminFichier):
	"""Vérifie que le fichier existe et a une extension correspondant à une image"""
	if op.isfile(cheminFichier):
		_, ext = op.splitext(cheminFichier)
		if ext.lower() in [".jpg", ".jpeg", ".png"]:
			return True
	return False


def creerGalerie(collection, listeImages):
	"""Crée le fichier "galerie.xml" contenant les paramètres de la galerie"""
	fd = open(op.join(collection, "galerie.xml"), "w")
	fd.write(XML_BEGIN%(collection,))
	for nomIm in listeImages:
		fd.write(XML_PART%(nomIm,))
	fd.write(XML_END)
	fd.close()
	
	shutil.copy("swfobject.js", collection)
	shutil.copy("viewer.swf", collection)
	
	
def creerIndex(collection, nbImages):
	"""Crée le fichier index.html"""
	fd = open(op.join(collection,"index.html"), "w")
	fd.write(DEFAULT_INDEX%(collection, nbImages))
	fd.close()


def listerFichierCollection(collection):
	"""Renvoie un tuple contenant tous les fichiers de la collection"""
	listeF = os.listdir(collection)	
	return listeF

#########################
##### Démarrage du script
#########################

status = "Démarrage" + "\n"

try:
	form = cgi.FieldStorage()
	if "collection" in form:
		collection  = cleanup(form["collection"].value)
		if not os.path.isdir(collection):
			status += "Erreur critique, collection inexistante"
		else:
			zipColl = zipfile.ZipFile(op.join(collection,"archive.zip"), "w")
	
			listeFichiers = listerFichierCollection(collection)
			listeDesImages = []
			for nomFichier in listeFichiers:
				cheminFichier = op.join(collection,nomFichier)
				if isImage(cheminFichier):
					listeDesImages.append(nomFichier)
					zipColl.write(cheminFichier)
			zipColl.close()
			creerIndex(collection, len(listeDesImages))
			creerGalerie(collection, listeDesImages)
				
		status += "Terminé"
	else:
		status += "Pas d'arguments trouvée"
except Exception, e:
	status += "Erreur :" + str(e)
	
print "Content-type: text/html; charset=utf-8\n\n" + status