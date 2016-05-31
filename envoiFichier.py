#!/usr/bin/env python
# encoding:utf-8

import http.client as http
import logging as log
import os.path as op
import urllib.parse as urlp
import urllib.parse as up
import urllib.request as ur

from postUsingMIME import encode_multipart_formdata as encodeMulti

log.basicConfig(level=log.DEBUG)


# Est utilisé pour générer la galerie APRES que les photos est été envoyées.
def genererGalerie(url, nomCollection):
    log.debug("Lancement de 'GenererGalerie' avec l'url %s", url)
    result = ur.urlopen(url + "?" + up.urlencode({"collection": nomCollection}))
    log.debug("Retour de la création de la galerie :\n" + result.read().decode())


class EnvoiFichiers:
    def __init__(self, url):
        log.debug("Initialisation de 'EnvoiFichiers' avec l'url %s", url)
        data_url = urlp.urlparse(url)
        self.serveur = data_url.netloc
        self.cheminServeur = data_url.path

    def _preparerRequete(self, cheminFichier, collection, nomFichier, typeFich):
        log.debug("Preparation de la requete: %s, %s, %s, type:%s", cheminFichier, collection, nomFichier, typeFich)
        if not nomFichier:
            nomFichier = op.split(cheminFichier)[-1]
        if not collection:
            chemin = op.split(cheminFichier)[0]
            collection = op.split(chemin)[-1]

        fd = open(cheminFichier, "rb")
        dataFichier = fd.read()
        log.debug("Taille du fichier %s : %d", cheminFichier, len(dataFichier))

        log.debug("Header -> collection: %s, nomFichier: %s", collection, nomFichier)
        header = {"collection": collection, "nomFichier": nomFichier, "typeImage": typeFich}
        content_type, body = encodeMulti(header, [["imageEnvoyee", nomFichier, dataFichier]])

        return (content_type, body)

    def _envoyerRequete(self, content_type, body):
        log.debug("Connexion au serveur %s", self.serveur)
        connexion = http.HTTPConnection(self.serveur)
        connexion.putrequest('POST', self.cheminServeur)
        connexion.putheader('content-type', content_type)
        connexion.putheader('content-length', str(len(body)))
        connexion.endheaders()

        connexion.send(body)
        reponse = connexion.getresponse().read()
        connexion.close()

        return reponse

    def envoyerFichier(self, cheminFichier, collection="", nomFichier=""):

        (content_type, body) = self._preparerRequete(cheminFichier, collection, nomFichier, "Main")

        log.debug("Envoi du fichier %s de la collection %s.", nomFichier, collection)
        log.debug("Taille des données envoyées : %s octets", len(body))

        return self._envoyerRequete(content_type, body)

    def envoyerFichierGal(self, cheminFichier, collection="", nomFichier=""):

        (content_type, body) = self._preparerRequete(cheminFichier, collection, nomFichier, "Gal")

        log.debug("Envoi du fichier de galerie %s de la collection %s.", nomFichier, collection)
        log.debug("Taille des données envoyées : %s octets", len(body))

        return self._envoyerRequete(content_type, body)

    def envoyerFichierThumb(self, cheminFichier, collection="", nomFichier=""):

        (content_type, body) = self._preparerRequete(cheminFichier, collection, nomFichier, "Thumb")

        log.debug("Envoi du fichier %s de la collection %s.", nomFichier, collection)
        log.debug("Taille des données envoyées : %s octets", len(body))

        return self._envoyerRequete(content_type, body)


if __name__ == '__main__':
    usage = "<nom du fichier a envoyer> <url> <collection>"
    import sys

    args = sys.argv[1:]

    if len(args) != 3:
        print(usage)
        sys.exit(0)

    (nomFichier, url, col) = args

    envF = EnvoiFichiers(url)
    reponse = envF.envoyerFichier(nomFichier, collection=col)
    print("status:", reponse.status)
    print("message:", reponse.msg)
    print("raison:", reponse.reason)
    print("data:", reponse.read())
