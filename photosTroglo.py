# encoding: utf-8

VERSION="1.3"

from Tkinter import *
import tkFileDialog, tkMessageBox

from os.path import join, split, splitext
from os import listdir, close, unlink
import re
import traiterImage as tm

from envoiFichier import EnvoiFichiers
from envoiFichier import genererGalerie
import tempfile

import webbrowser

import logging as log
log.basicConfig(level=log.DEBUG)


def cleanup(nom):
		nvNom = re.sub("[^\._\-a-zA-Z0-9]", '', nom)
		return nvNom


URL_BASE = "http://www.marache.net/envoiPhotos/"
URL_UPLOAD = URL_BASE + "upload.cgi"
URL_CREERGALERIE = URL_BASE + "galerie.cgi"

class Application(Frame):
	def DemanderRep(self):
		self.nomRep = tkFileDialog.askdirectory()
		
		if self.nomRep:
			self.labelRep["text"] = self.nomRep
			self.nomCollec.set( cleanup( split(self.nomRep)[-1] ) )
			self.entreeNomCollec["state"] = NORMAL
			
			for f in listdir(self.nomRep):
				ext = splitext(f)[-1]
				if ext.lower() in (".jpg", ".jpeg"):	
					self.liste.insert(END, f)

	def changerStatus(self, nvStatus):
		self.labelRep["text"] = nvStatus
	
	def _contacterUpload(self):
		nombreErreurs = 0
		nomCollection = cleanup(self.nomCollec.get())
		connEnv = EnvoiFichiers(URL_UPLOAD)
		while self.liste.size() > 0:
			try:
				nomFichier = self.liste.get(0)
				self.changerStatus(u"Envoi de %s en cours..."%(nomFichier))
				fd,fichierTemp = tempfile.mkstemp(suffix=".jpg")
				fdT,fichierTempT = tempfile.mkstemp(suffix=".jpg")
				fdG,fichierTempG = tempfile.mkstemp(suffix=".jpg")
				close(fd) # Pas besoin de ce fichier ouvert, juste le nom
				close(fdT) # Pas besoin de ce fichier ouvert, juste le nom
				close(fdG) # Pas besoin de ce fichier ouvert, juste le nom
				
				# Changement de taille des images (dans un fichier temporaire)
				tm.traiter(join(self.nomRep, nomFichier), fichierTemp, self.scale.get())
				tm.traiter(join(self.nomRep, nomFichier), fichierTempT, -1) # create thumbnail
				tm.traiter(join(self.nomRep, nomFichier), fichierTempG, 0) # create thumbnail
				self.master.update()
				
				# Envoi de ce fichier temporaire
				reponse = connEnv.envoyerFichier(fichierTemp, nomCollection, cleanup(nomFichier))
				log.debug("Réponse de l'upload de %s : \n%s", nomFichier, reponse) 
				if reponse[:2] != "OK": raise Exception("Erreur lors de l'envoi du fichier main " + nomFichier)

				reponse = connEnv.envoyerFichierThumb(fichierTempT, nomCollection, cleanup(nomFichier))
				log.debug("Réponse de l'upload de %s : \n%s", nomFichier, reponse) 
				if reponse[:2] != "OK": raise Exception("Erreur lors de l'envoi du fichier thumb " + nomFichier)
				
				reponse = connEnv.envoyerFichierGal(fichierTempG, nomCollection, cleanup(nomFichier))
				log.debug("Réponse de l'upload de %s : \n%s", nomFichier, reponse) 
				if reponse[:2] != "OK": raise Exception("Erreur lors de l'envoi du fichier Gal " + nomFichier)

				unlink(fichierTemp) # fichier temporaire devenu inutile
				unlink(fichierTempT) # fichier temporaire devenu inutile
				unlink(fichierTempG) # fichier temporaire devenu inutile
				self.liste.delete(0)
				self.master.update()
			except Exception as e:
				nombreErreurs += 1
				log.warn("Erreur lors de l'envoie du fichier ! : %s", str(e))
				if nombreErreurs > 5:
					tkMessageBox.showinfo("Petit problème", "Il y a eu un problème lors de l'envoi de l'image. Plus d'explications ci-après (bon courage) :\n>>> " + str(e)+ "\n")
					return False
		self.changerStatus(u"Envoi des fichiers terminé")
		return True


	def _creerGalerie(self):
		nomCollection = cleanup(self.nomCollec.get())
		galerieOk = False
		nombreErreurs = 0
		while not galerieOk:
			try:
				genererGalerie(URL_CREERGALERIE, nomCollection)
				galerieOk = True
			except Exception as e:
				nombreErreurs += 1
				log.warn("Erreur lors de la création de la galerie ! : %s", str(e))
				if nombreErreurs > 5:
					tkMessageBox.showinfo("Petit problème", "Il y a eu un problème lors de l'envoi de l'image. Plus d'explications ci-après (bon courage) :\n>>> " + str(e)+ "\n")
					self.quit()
			
		self.changerStatus("La galerie a été crée sur le serveur")
		tkMessageBox.showinfo(u"Bonne nouvelle !", u"Images disponibles à l'adresse : " + URL_BASE + nomCollection + u"\nUn navigateur va s'ouvrir à cette page")
		webbrowser.open(URL_BASE + nomCollection)

				
	def envoyerFichiers(self):
		self.btEnvoiFichiers["state"] = DISABLED
		
		if self.liste.size() == 0:
			tkMessageBox.showwarning(
						"Pas de fichiers", 
						"Il n'y a pas de fichiers à envoyer." +
						"Cliquez sur le bouton 'Choisir un répertoire' " +
						"pour sélectionner les photos à envoyer")
		elif cleanup(self.nomCollec.get()) == "":
			tkMessageBox.showwarning(
						"Nom de collection invalide", 
						"Le nom de la collection est invalide. " +
						"Si il n'est pas vide, essayez de retirer les caractères " + 
						"spéciaux type éàçùµ£$ qui ne sont pas autorisés" 
						)			
		else:
			if self._contacterUpload():
				self._creerGalerie()					
					
		self.btEnvoiFichiers["state"] = NORMAL
		
		
		
	def createWidgets(self):
		
		self.frameBoutons = Frame(self)
		self.frameBoutons.pack({"side": "left"}, fill=Y, expand=NO)
		

		self.choixRep = Button(self.frameBoutons)
		self.choixRep["text"] = "1) Choisir un repertoire"
		self.choixRep["command"] = self.DemanderRep
		self.choixRep.pack({"side": "top"}, fill=X, pady=40)
		
		self.labelExpl = Label(self.frameBoutons)
		self.labelExpl["text"] = "2) Nom de la collection"
		self.labelExpl.pack({"side": "top"}, fill=X)

		self.labelRep = Label(self)
		self.labelRep["text"] = u"<Pas de répertoire sélectionné>"
		self.labelRep.pack({"side": "top"})

		self.liste = Listbox(self)
		self.liste.pack({"side": "top"}, fill=BOTH, expand=YES)		

		self.nomCollec = StringVar(self)
		self.nomCollec.set("<Nom de la collection>")
		self.entreeNomCollec = Entry(self.frameBoutons, textvariable=self.nomCollec,width=30)
		self.entreeNomCollec.pack({"side": "top"}, fill=X)
		self.entreeNomCollec["state"] = DISABLED
		
		self.labelScale = Label(self.frameBoutons)
		self.labelScale["text"] = "3) Qualité des images"
		self.labelScale.pack({"side": "top"}, fill=X, pady=[40,0])

		self.scale = Scale(self.frameBoutons, from_=0, to=3, orient=HORIZONTAL)
		self.scale.set(2)
		self.scale.pack({"side": "top"}, fill=X)

		self.btEnvoiFichiers = Button(self.frameBoutons)
		self.btEnvoiFichiers["text"] = "4) Envoyer les fichiers"
		self.btEnvoiFichiers["command"] = self.envoyerFichiers
		self.btEnvoiFichiers.pack({"side": "top"}, fill=X, pady=40)

		self.QUIT = Button(self.frameBoutons)
		self.QUIT["text"] = "Quitter"
		self.QUIT["command"] =  self.quit
		self.QUIT.pack({"side": "top"})


	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.pack(fill=BOTH, expand=YES)
		self.createWidgets()

root = Tk()
root.geometry("650x384")
root.title("Envoi de photos v"+VERSION)
app = Application(master=root)
app.mainloop()
root.destroy()