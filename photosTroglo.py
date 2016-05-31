# encoding: utf-8


import logging as log
import tempfile
import webbrowser
from os import listdir, close, unlink
from os.path import join, split, splitext
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog, messagebox

import parameters

import traiterImage as tm
from envoiFichier import EnvoiFichiers
from envoiFichier import genererGalerie

log.basicConfig(level=log.DEBUG)


def cleanup(nom):
    nvNom = re.sub("[^\._\-a-zA-Z0-9]", '', nom)
    return nvNom




class NomFichier:
    def __init__(self, _t):
        self.texte = _t
        self.commentaire = ""

    def __str__(self):
        return self.texte


class Application(Frame):
    def OnSelectListElement(self, event):
        app.entreeCommentaire["state"] = NORMAL
        app.nomCommentaire.set(self.liste.get(self.liste.curselection()).commentaire)

    def DemanderRep(self):
        self.nomRep = filedialog.askdirectory()

        if self.nomRep:
            self.labelRep["text"] = self.nomRep
            self.nomCollec.set(cleanup(split(self.nomRep)[-1]))
            self.entreeNomCollec["state"] = NORMAL

            for f in listdir(self.nomRep):
                ext = splitext(f)[-1]
                if ext.lower() in (".jpg", ".jpeg"):
                    self.liste.insert(END, NomFichier(f))

    def changerStatus(self, nvStatus):
        self.labelRep["text"] = nvStatus

    def _contacterUpload(self):
        nombreErreurs = 0
        nomCollection = cleanup(self.nomCollec.get())
        connEnv = EnvoiFichiers(parameters.URL_UPLOAD)
        while self.liste.size() > 0:
            try:
                nomFichier = self.liste.get(0)
                self.changerStatus(u"Envoi de %s en cours..." % (nomFichier))
                fd, fichierTemp = tempfile.mkstemp(suffix=".jpg")
                fdT, fichierTempT = tempfile.mkstemp(suffix=".jpg")
                fdG, fichierTempG = tempfile.mkstemp(suffix=".jpg")
                close(fd)  # Pas besoin de ce fichier ouvert, juste le nom
                close(fdT)  # Pas besoin de ce fichier ouvert, juste le nom
                close(fdG)  # Pas besoin de ce fichier ouvert, juste le nom

                # Changement de taille des images (dans un fichier temporaire)
                tm.traiter(join(self.nomRep, nomFichier), fichierTemp, self.scale.get())
                tm.traiter(join(self.nomRep, nomFichier), fichierTempT, -1)  # create thumbnail
                tm.traiter(join(self.nomRep, nomFichier), fichierTempG, 0)  # create thumbnail
                self.master.update()

                # Envoi de ce fichier temporaire
                reponse = connEnv.envoyerFichier(fichierTemp, nomCollection, cleanup(nomFichier))
                log.debug("Réponse de l'upload de %s : \n%s", nomFichier, reponse)
                if reponse[:2] != b"OK": raise Exception(
                    "Erreur lors de l'envoi du fichier main " + nomFichier + " " + str(reponse))

                reponse = connEnv.envoyerFichierThumb(fichierTempT, nomCollection, cleanup(nomFichier))
                log.debug("Réponse de l'upload de %s : \n%s", nomFichier, reponse)
                if reponse[:2] != b"OK": raise Exception("Erreur lors de l'envoi du fichier thumb " + nomFichier)

                reponse = connEnv.envoyerFichierGal(fichierTempG, nomCollection, cleanup(nomFichier))
                log.debug("Réponse de l'upload de %s : \n%s", nomFichier, reponse)
                if reponse[:2] != b"OK": raise Exception("Erreur lors de l'envoi du fichier Gal " + nomFichier)

                unlink(fichierTemp)  # fichier temporaire devenu inutile
                unlink(fichierTempT)  # fichier temporaire devenu inutile
                unlink(fichierTempG)  # fichier temporaire devenu inutile
                self.liste.delete(0)
                self.master.update()
            except Exception as e:
                raise e
                nombreErreurs += 1
                log.warning("Erreur lors de l'envoie du fichier ! : %s", str(e))
                if nombreErreurs > 5:
                    messagebox.showinfo("Petit problème",
                                        "Il y a eu un problème lors de l'envoi de l'image. Plus d'explications ci-après (bon courage) :\n>>> " + str(
                                            e) + "\n")
                    return False
        self.changerStatus(u"Envoi des fichiers terminé")
        return True

    def _creerGalerie(self):
        nomCollection = cleanup(self.nomCollec.get())
        galerieOk = False
        nombreErreurs = 0
        while not galerieOk:
            try:
                genererGalerie(parameters.URL_CREERGALERIE, nomCollection)
                galerieOk = True
            except Exception as e:
                raise e
                nombreErreurs += 1
                log.warning("Erreur lors de la création de la galerie ! : %s", str(e))
                if nombreErreurs > 5:
                    messagebox.showinfo("Petit problème",
                                        "Il y a eu un problème lors de l'envoi de l'image. Plus d'explications ci-après (bon courage) :\n>>> " + str(
                                            e) + "\n")
                    self.quit()

        self.changerStatus("La galerie a été crée sur le serveur")
        messagebox.showinfo(u"Bonne nouvelle !",
                            u"Images disponibles à l'adresse : " + parameters.URL_BASE + nomCollection + u"\nUn navigateur va s'ouvrir à cette page")
        webbrowser.open(parameters.URL_BASE + nomCollection)

    def envoyerFichiers(self):
        self.btEnvoiFichiers["state"] = DISABLED

        if self.liste.size() == 0:
            messagebox.showwarning(
                "Pas de fichiers",
                "Il n'y a pas de fichiers à envoyer." +
                "Cliquez sur le bouton 'Choisir un répertoire' " +
                "pour sélectionner les photos à envoyer")
        elif cleanup(self.nomCollec.get()) == "":
            messagebox.showwarning(
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
        ### Frame des boutons placé à gauche

        self.frameBoutons = Frame(self, pad=10)
        self.frameBoutons.pack({"side": "left"}, fill=Y, expand=NO)

        ### Commentaire (en bas)

        self.nomCommentaire = StringVar(self)
        self.nomCommentaire.set("<Commentaire de l'image (Optionnel)>")
        self.entreeCommentaire = Entry(self, textvariable=self.nomCommentaire, width=30)
        self.entreeCommentaire.pack({"side": "bottom"}, fill=X)
        self.entreeCommentaire["state"] = DISABLED

        ### Label indiquant le répertoire (Haut)

        self.labelRep = Label(self)
        self.labelRep["text"] = u"<Pas de répertoire sélectionné>"
        self.labelRep.pack({"side": "top"})

        ### Liste des fichiers (Centre)

        self.liste = Listbox(self)
        self.liste.pack({"side": "top"}, fill=BOTH, expand=YES)
        self.liste.bind('<Double-1>', self.OnSelectListElement)
        # wx.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectListElement, self.liste)

        ### Boutons

        self.choixRep = Button(self.frameBoutons)
        self.choixRep["text"] = "1) Choisir un repertoire"
        self.choixRep["command"] = self.DemanderRep
        self.choixRep.pack({"side": "top"}, fill=X, pady=40)

        self.labelExpl = Label(self.frameBoutons)
        self.labelExpl["text"] = "2) Nom de la collection"
        self.labelExpl.pack({"side": "top"}, fill=X)

        self.nomCollec = StringVar(self)
        self.nomCollec.set("<Nom de la collection>")
        self.entreeNomCollec = Entry(self.frameBoutons, textvariable=self.nomCollec, width=30)
        self.entreeNomCollec.pack({"side": "top"}, fill=X)
        self.entreeNomCollec["state"] = DISABLED

        self.labelScale = Label(self.frameBoutons)
        self.labelScale["text"] = "3) Qualité des images"
        self.labelScale.pack({"side": "top"}, fill=X, pady=[40, 0])

        self.scale = Scale(self.frameBoutons, from_=0, to=3, orient=HORIZONTAL)
        self.scale.set(2)
        self.scale.pack({"side": "top"}, fill=X)

        self.btEnvoiFichiers = Button(self.frameBoutons)
        self.btEnvoiFichiers["text"] = "4) Envoyer les fichiers"
        self.btEnvoiFichiers["command"] = self.envoyerFichiers
        self.btEnvoiFichiers.pack({"side": "top"}, fill=X, pady=40)

        self.QUIT = Button(self.frameBoutons)
        self.QUIT["text"] = "Quitter"
        self.QUIT["command"] = self.quit
        self.QUIT.pack({"side": "top"})

    def __init__(self, master=None):
        Frame.__init__(self, master, pad=5)
        self.pack(fill=BOTH, expand=YES)
        self.createWidgets()


root = Tk()
root.geometry("650x400")
root.title("Envoi de photos v" + parameters.VERSION)
app = Application(master=root)
app.mainloop()
root.destroy()
