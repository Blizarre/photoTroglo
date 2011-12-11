# encoding: utf-8

from PIL import Image

import logging as log

# Liste des qualité d'images
d_qualite = {
    0:(800, 50),
    1:(1024, 50),
    2:(1600, 70),
    3:(2500, 80)
}
def traiter(cheminImageIn, cheminImageOut, qualite):
    im = Image.open(cheminImageIn)
    o_X, o_Y = im.size
    t_X, qualJPG = d_qualite[qualite]
    
    # On cherche juste la nouvelle taille (sans augmenter la taille)
    if t_X > o_X:
        t_X, t_Y = (o_X, o_Y)
    else:
        t_Y =  int(float(t_X) / o_X * o_Y)
    
    log.debug("Mise à l'échelle de l'image : (%d,%d)->(%d,%d)", o_X, o_Y, t_X, t_Y)
    newIm = im.resize((t_X, t_Y), Image.ANTIALIAS)
    newIm.save(cheminImageOut, quality=qualJPG)
