# encoding: utf-8

import pdb

from Tkinter import *
import tkFileDialog, tkMessageBox

from glob import glob
from os.path import join, split, splitext
from os import listdir
import os, re
import traiterImage as tm

from envoiFichier import EnvoiFichiers

import tempfile
import traceback

def cleanup(nom):
        nvNom = re.sub("[^\._\-a-zA-Z0-9]", '', nom)
        print nvNom
        return nvNom


class Application(Frame):
    def DemanderRep(self):
        self.nomRep = tkFileDialog.askdirectory()
        
        self.labelRep["text"] = self.nomRep
        self.nomCollec.set( cleanup( split(self.nomRep)[-1] ) )
        self.entreeNomCollec["state"] = NORMAL
        
        for f in listdir(self.nomRep):
            ext = splitext(f)[-1]
            if ext.lower() in (".jpg", ".jpeg"):    
                self.liste.insert(END, f)

    def envoyerFichiers(self):
        if tkMessageBox.askyesno("Envoi de fichiers", message="Voulez-vous lancer l'envoi des fichiers ?"):
            
            try:
                connEnv = EnvoiFichiers("http://www.marache.net/envoiPhotos/upload.cgi")
                while self.liste.size() > 0:
                    nomFichier = self.liste.get(0)
                    self.labelRep["text"] = "Envoi de %s en cours..."%(nomFichier)
                    self.master.update_idletasks()
                    
                    fd,fichierTemp = tempfile.mkstemp(suffix=".jpg")
                    os.close(fd) # Pas besoin de ce fichier ouvert, juste le nom
                    tm.traiter(join(self.nomRep, nomFichier), fichierTemp, self.scale.get())
                    connEnv.envoyerFichier(fichierTemp, cleanup(self.nomCollec.get()), cleanup(nomFichier))
                    self.liste.delete(0)
                    self.master.update_idletasks()
                    
                self.labelRep["text"] = "Envoi des fichiers terminé"
                tkMessageBox.showinfo("Bonne nouvelle !", "Envoi des fichiers terminé !")
            except Exception as e:
                    tkMessageBox.showinfo("Petit problème", "Il y a eu un problème lors de l'envoi de l'image. Plus d'explications ci-après (bon courage) :\n>>> " + str(e)+ "\n")
                    traceback.print_exc()
                
        
        
    def createWidgets(self):
        
        self.frameBoutons = Frame(self)
        self.frameBoutons.pack({"side": "left"})

        self.labelRep = Label(self)
        self.labelRep["text"] = u"<Pas de répertoire sélectionné>"
        self.labelRep.pack({"side": "bottom"})

        self.liste = Listbox(self)
        self.liste.pack({"side": "right"}, fill=BOTH, expand=YES)


        self.QUIT = Button(self.frameBoutons)
        self.QUIT["text"] = "Quitter"
        self.QUIT["command"] =  self.quit
        self.QUIT.pack({"side": "bottom"})
                  
        self.btEnvoiFichiers = Button(self.frameBoutons)
        self.btEnvoiFichiers["text"] = "4) Envoyer les fichiers"
        self.btEnvoiFichiers["command"] = self.envoyerFichiers
        self.btEnvoiFichiers.pack({"side": "bottom"}, fill=X, pady=40)
        
        self.scale = Scale(self.frameBoutons, from_=0, to=3, orient=HORIZONTAL)
        self.scale.set(2)
        self.scale.pack({"side": "bottom"}, fill=X)
        
        self.labelScale = Label(self.frameBoutons)
        self.labelScale["text"] = "3) Qualité des images"
        self.labelScale.pack({"side": "bottom"}, fill=X, pady=[40,0])

        self.nomCollec = StringVar(self)
        self.nomCollec.set("<Nom de la collection>")
        
        self.entreeNomCollec = Entry(self.frameBoutons, textvariable=self.nomCollec,width=30)
        self.entreeNomCollec.pack({"side": "bottom"}, fill=X)
        self.entreeNomCollec["state"] = DISABLED
        
        self.labelExpl = Label(self.frameBoutons)
        self.labelExpl["text"] = "2) Nom de la collection"
        self.labelExpl.pack({"side": "bottom"}, fill=X)
                
        self.choixRep = Button(self.frameBoutons)
        self.choixRep["text"] = "1) Choisir un repertoire"
        self.choixRep["command"] = self.DemanderRep
        self.choixRep.pack({"side": "bottom"}, fill=X, pady=40)


    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack(fill=BOTH)
        self.createWidgets()

root = Tk()
root.geometry("650x384")
app = Application(master=root)
app.mainloop()
root.destroy()