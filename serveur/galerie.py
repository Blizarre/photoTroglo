#!/usr/bin/python
# encoding: utf-8

import cgi
import cgitb
import os
import os.path as op
import re
import shutil
import zipfile

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
    <div id="flashcontent">SimpleViewer requires Adobe Flash.
        <a href="http://www.macromedia.com/go/getflashplayer/">Get Adobe Flash.</a>
        If you have Flash installed, <a href="index.html?detectflash=false">click to view gallery</a>.
    </div>
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
<simpleviewerGallery maxImageWidth="1024" maxImageHeight="1024" textColor="0xFFFFFF" frameColor="0xFFFFFF"
frameWidth="5" stagePadding="10" thumbnailColumns="3" thumbnailRows="5" navPosition="left" title="%s"
enableRightClickOpen="true" backgroundImagePath="" imagePath="images/" thumbPath="thumbs/">"""
XML_PART = """
    <image>
        <filename>%s</filename>
        <caption></caption>
    </image>"""
XML_END = """
</simpleviewerGallery>"""


def cleanup(nom):
    """Nettoyage du nom : On ne conserve que :
    - les lettres (majuscule/minuscule)
    - les chiffres
    - Les caractères ".", "-", et "_"
     """
    return re.sub("[^\.\-_a-zA-Z0-9]", '', nom)


def is_image(file_path):
    """Vérifie que le fichier existe et a une extension correspondant à une image"""
    if op.isfile(file_path):
        _, ext = op.splitext(file_path)
        if ext.lower() in [".jpg", ".jpeg", ".png"]:
            return True
    return False


def creer_galerie(coll, liste_images):
    """Crée le fichier "galerie.xml" contenant les paramètres de la galerie"""
    fd = open(op.join(coll, "galerie.xml"), "w")
    fd.write(XML_BEGIN % (coll,))
    for nomIm in liste_images:
        fd.write(XML_PART % (nomIm,))
    fd.write(XML_END)
    fd.close()

    shutil.copy("swfobject.js", coll)
    shutil.copy("viewer.swf", coll)


def creer_index(coll, nb_images):
    """Crée le fichier index.html"""
    fd = open(op.join(coll, "index.html"), "w")
    fd.write(DEFAULT_INDEX % (coll, nb_images))
    fd.close()


def lister_fichier_collection(coll):
    """Renvoie un tuple contenant tous les fichiers de la collection"""
    list_files = os.listdir(coll)
    return list_files


#########################
# Démarrage du script
#########################

status = "Démarrage" + "\n"

try:
    form = cgi.FieldStorage()
    if "collection" in form:
        collection = cleanup(form["collection"].value)
        if not os.path.isdir(collection):
            status += "Erreur critique, collection inexistante"
        else:
            zipColl = zipfile.ZipFile(op.join(collection, "archive.zip"), "w")

            liste_fichiers = lister_fichier_collection(collection)
            liste_fichiers.sort()

            liste_Images = []
            for nom_fichier in liste_fichiers:
                chemin_fichier = op.join(collection, nom_fichier)
                if is_image(chemin_fichier):
                    liste_Images.append(nom_fichier)
                    zipColl.write(chemin_fichier)
                    os.remove(chemin_fichier)
            zipColl.close()
            status += "Ajout de " + str(len(liste_Images)) + " images."
            creer_index(collection, len(liste_Images))
            creer_galerie(collection, liste_Images)

        status += "Terminé"
    else:
        status += "Pas d'arguments trouvée"
except Exception, e:
    status += "Erreur :" + str(e)

print "Content-type: text/html; charset=utf-8\n\n" + status
