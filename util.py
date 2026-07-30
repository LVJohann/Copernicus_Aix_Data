import math
import rasterio
import numpy as np
from pathlib import Path



def moyenneAri1D(tableau):
    somme = 0
    n = 0

    for elt in tableau:
        somme += elt
        n += 1

    return somme/n if n else 0    

def moyenneAri2D(tableau)->float:
    moyenne = 0
    n = 0
    for ligne in tableau:
        for elt in ligne:
            moyenne += elt
            n += 1

    if n == 0:
        print("Tableau vide")
        return 0
    else:
        return moyenne/n


def rognerImage(tableau, x, y, largeur, hauteur, source, nom):

    hauteur_image = len(tableau)
    largeur_image = len(tableau[0])

    if x < 0 or y < 0 or x + largeur > largeur_image or y + hauteur > hauteur_image:
        raise ValueError("La zone de rognage dépasse les dimensions de l'image")

    resultat = []

    for ligne in range(y, y + hauteur):
        resultat.append(tableau[ligne][x:x + largeur])

    creerTif(resultat, nom, source)

    return resultat


def creerTif(tableau, nom, fichierOriginal):

    tableau = np.array(tableau)

    with rasterio.open(fichierOriginal) as src:

        profil = src.profile.copy()

        profil.update(
            width=tableau.shape[1],
            height=tableau.shape[0]
        )

        with rasterio.open("image/" + nom + ".tif", "w", **profil) as dst:
            dst.write(tableau, 1)

def nbValAuDessusTab2D(val, tab):
    n = 0
    for line in tab:
        for elt in line:
            if elt >= val:
                n += 1
    return n

def nbValEnDessousTab2D(val, tab):
    n = 0
    for line in tab:
        for elt in line:
            if elt < val:
                n += 1
    return n

def ecartTypeTab2D(tab):
    M = moyenneAri2D(tab)
    N = len(tab)*len(tab[0])

    Var = 0
    for line in tab:
        for elt in line:
            var += (elt - M)**2
    var /= N
    if var < 0:
        raise ValueError("Variance négative")

    return math.sqrt(var)

def chargerEvalscript(nom):
    with open(f"evalscript/{nom}.js", "r", encoding="utf-8") as f:
        return f.read()

def telechargerImage(content, nom):
    with open(f"image/{nom}.tif", "wb") as f:
        f.write(content)


def supprimer_tif(dossier="./image"):
    dossier = Path(dossier)

    for fichier in dossier.glob("*.tif"):
        fichier.unlink()

    for fichier in dossier.glob("*.tiff"):
        fichier.unlink()