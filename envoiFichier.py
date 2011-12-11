#!/usr/bin/env python
# encoding:utf-8

import httplib as http
import urlparse as urlp
import os.path as op
import pdb

import logging as log
from postUsingMIME import encode_multipart_formdata as encodeMulti

log.basicConfig(level=log.DEBUG)

class EnvoiFichiers:
    
    def __init__(self, url):
        log.debug("Initialisation de 'EnvoiFichiers' avec l'url %s", url)
        data_url = urlp.urlparse(url)
        self.serveur = data_url.netloc
        self.cheminServeur = data_url.path
    
    def _preparerRequete(self, cheminFichier, collection, nomFichier):
        log.debug("Preparation de la requete: %s, %s, %s", cheminFichier, collection, nomFichier)
        if not nomFichier:
            nomFichier = op.split(cheminFichier)[-1]
        if not collection:
            chemin = op.split(cheminFichier)[0]
            collection = op.split(chemin)[-1]
                
        with open(cheminFichier, "rb") as fd:
            dataFichier = fd.read()
        log.debug("Taille du fichier %s : %d", cheminFichier, len(dataFichier))

        log.debug("Header -> collection: %s, nomFichier: %s", collection, nomFichier)
        header = {"collection":collection, "nomFichier":nomFichier}
        content_type, body = encodeMulti(header, [["imageEnvoyee", nomFichier, dataFichier]] )
    
        return (content_type, body)
    
    def envoyerFichier(self, cheminFichier, collection="", nomFichier=""):
        
        (content_type, body) = self._preparerRequete(cheminFichier, collection, nomFichier)
        
        log.debug("Connexion au serveur %s", self.serveur)
        connexion = http.HTTPConnection(self.serveur)

        connexion.putrequest('POST', self.cheminServeur)
        connexion.putheader('content-type', content_type)
        connexion.putheader('content-length', str(len(body)))
        connexion.endheaders()
        
        log.debug("Envoi du fichier %s de la collection %s.", nomFichier, collection)
        log.debug("Taille des données envoyées : %s octets", len(body))
        connexion.send(body)
        
        reponse = connexion.getresponse()
        connexion.close()
        
        return reponse


if __name__ == '__main__':
    usage="<nom du fichier a envoyer> <url> <collection>"
    import sys
    import os.path
    
    args = sys.argv[1:]
    
    if len(args) != 3:
        print usage
        sys.exit(0)
    
    (nomFichier, url, col) = args
    
    envF = EnvoiFichiers(url)
    reponse = envF.envoyerFichier(nomFichier, collection=col)
    print "status:", reponse.status
    print "message:"; reponse.msg
    print "raison:", reponse.reason
    print "data:", reponse.read()
    
