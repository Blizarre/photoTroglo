#!/usr/bin/python
# encoding: utf-8

import cgitb

cgitb.enable()

import sys

sys.stdout.write("Content-type: text/html\n\n")

import cgi, os, re
import traceback
import os.path as op


def create_directory(collection, nom):
    """Cree le sous-repertoire "nom" dans le repertoire de la collection
    "collection". Renvoie le chemin join(collection, nom)"""
    nomRep = op.join(collection, nom)
    if not op.isdir(nomRep): os.mkdir(nomRep)
    return nomRep


def is_filename_ok(name):
    fileOk = False
    base, extension = os.path.splitext(name)
    if base and re.search("\.(jpg|png|jpeg|JPG|JPEG)", extension):
        fileOk = True
    return fileOk


def cleanup(nom):
    return re.sub("[^\.\-_a-zA-Z0-9]", '', nom)


form = []
status = "Demarrage\n"

try:
    form = cgi.FieldStorage()

    if "collection" in form and "nomFichier" in form:
        struct_fichier = form["imageEnvoyee"]

        nomFichier = cleanup(struct_fichier.filename)
        collection = cleanup(form["collection"].value)
        typeImage = cleanup(form["typeImage"].value)

        if nomFichier and is_filename_ok(nomFichier) and collection:
            if not op.isdir(collection):
                os.mkdir(collection)
                status += "Creation du repertoire" + collection + "\n"

            if typeImage == "Gal":
                nomRep = create_directory(collection, "images")
            elif typeImage == "Thumb":
                nomRep = create_directory(collection, "thumbs")
            else:
                nomRep = collection

            file_path = op.join(nomRep, nomFichier)
            fdOut = open(file_path, "w")
            fdOut.write(struct_fichier.file.read())
            fdOut.close()

            status = "OK - Fichier %s (%s) ajoute dans la collection %s\n" % (nomFichier, typeImage, collection)
        else:
            status = "Nom de fichier non conforme ou fichier non conforme : " + nomFichier + "\n"
    else:
        status = "Pas de fichiers/Collection trouves, contient : " + " ".join([str(i) for i in form.keys()])
except Exception as e:
    print("Erreur '" + str(e) + "', form contient : " + " ".join([str(i) for i in form]))
    traceback.print_exc(file=sys.stdout)

# cgi.log(status)
sys.stdout.write(status + "\n")
