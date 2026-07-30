import math
import rasterio
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import json



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
    
def chargerRequete(fichier):
    with open(f"requetes/{fichier}.json", "r", encoding="utf-8") as f:
        return json.load(f)

def telechargerImage(content, nom):
    with open(f"image/{nom}.tif", "wb") as f:
        f.write(content)


def supprimer_tif(dossier="./image"):
    dossier = Path(dossier)

    for fichier in dossier.glob("*.tif"):
        fichier.unlink()

    for fichier in dossier.glob("*.tiff"):
        fichier.unlink()



def verifierImages(img1, img2):
    if img1.effectif != img2.effectif:
        raise ValueError("Les images n'ont pas le même effectif")

    if len(img1.tab2D) != len(img2.tab2D):
        raise ValueError("Les images n'ont pas la même hauteur")

    if len(img1.tab2D[0]) != len(img2.tab2D[0]):
        raise ValueError("Les images n'ont pas la même largeur")


def condition(valeur, seuil, operateur):
    if operateur == ">":
        return valeur >= seuil

    if operateur == "<":
        return valeur <= seuil

    raise ValueError("Opérateur invalide ('<' ou '>')")

def correlation(img1, img2):

    verifierImages(img1, img2)

    if img1.ecart_type == 0 or img2.ecart_type == 0:
        raise ValueError("Variance nulle")

    covariance = 0

    for y in range(len(img1.tab2D)):
        for x in range(len(img1.tab2D[0])):

            covariance += (
                (img1.tab2D[y][x] - img1.moyenne)
                * (img2.tab2D[y][x] - img2.moyenne)
            )

    covariance /= img1.effectif

    return covariance / (img1.ecart_type * img2.ecart_type)



def confiance(img1, img2,
               seuil1, seuil2,
               operateur1, operateur2):

    verifierImages(img1, img2)

    antecedent = 0
    intersection = 0

    for y in range(len(img1.tab2D)):
        for x in range(len(img1.tab2D[0])):

            A = condition(
                img1.tab2D[y][x],
                seuil1,
                operateur1
            )

            B = condition(
                img2.tab2D[y][x],
                seuil2,
                operateur2
            )

            if A:
                antecedent += 1

                if B:
                    intersection += 1

    if antecedent == 0:
        raise ValueError("Antécédent absent")

    return intersection / antecedent


def lift(img1, img2,
         seuil1, seuil2,
         operateur1, operateur2):

    verifierImages(img1, img2)

    antecedent = 0
    consequent = 0
    intersection = 0

    for y in range(len(img1.tab2D)):
        for x in range(len(img1.tab2D[0])):

            A = condition(
                img1.tab2D[y][x],
                seuil1,
                operateur1
            )

            B = condition(
                img2.tab2D[y][x],
                seuil2,
                operateur2
            )

            if A:
                antecedent += 1

            if B:
                consequent += 1

            if A and B:
                intersection += 1

    if antecedent == 0:
        raise ValueError("Antécédent absent")

    if consequent == 0:
        raise ValueError("Conséquent absent")

    confiance_regle = intersection / antecedent
    support_consequent = consequent / img1.effectif

    return confiance_regle / support_consequent


class ResultatRegle:
    def __init__(self, support, confiance, lift,
                 nb_A, nb_B, nb_AB, effectif):

        self.support = support
        self.confiance = confiance
        self.lift = lift

        self.nb_A = nb_A
        self.nb_B = nb_B
        self.nb_AB = nb_AB
        self.effectif = effectif

def verifierDeuxTableaux(tab1, tab2):

    if tab1 is None or tab2 is None:
        raise ValueError("Tableau nul")

    if len(tab1) == 0 or len(tab2) == 0:
        raise ValueError("Tableau vide")

    if len(tab1) != len(tab2):
        raise ValueError("Tailles différentes")

    if len(tab1[0]) != len(tab2[0]):
        raise ValueError("Largeurs différentes")

def calculerRegle(tab1, tab2,
                  seuil1, seuil2,
                  operateur1="<",
                  operateur2=">"):

    verifierDeuxTableaux(tab1, tab2)

    effectif = len(tab1) * len(tab1[0])

    nb_A = 0
    nb_B = 0
    nb_AB = 0


    for i in range(len(tab1)):
        for j in range(len(tab1[i])):

            valeur1 = tab1[i][j]
            valeur2 = tab2[i][j]


            if operateur1 == "<":
                A = valeur1 < seuil1
            elif operateur1 == ">":
                A = valeur1 > seuil1
            else:
                raise ValueError("Opérateur 1 invalide")


            if operateur2 == "<":
                B = valeur2 < seuil2
            elif operateur2 == ">":
                B = valeur2 > seuil2
            else:
                raise ValueError("Opérateur 2 invalide")


            if A:
                nb_A += 1

            if B:
                nb_B += 1

            if A and B:
                nb_AB += 1


    if nb_A == 0:
        raise ValueError("Antécédent absent")

    if nb_B == 0:
        raise ValueError("Conséquent absent")


    support = nb_AB / effectif

    confiance = nb_AB / nb_A

    probabilite_B = nb_B / effectif

    lift = confiance / probabilite_B


    return ResultatRegle(
        support,
        confiance,
        lift,
        nb_A,
        nb_B,
        nb_AB,
        effectif
    )


def regressionLineaire(tabX, tabY):

    verifierDeuxTableaux(tabX, tabY)


    valeursX = []
    valeursY = []


    for i in range(len(tabX)):
        for j in range(len(tabX[i])):
            valeursX.append(tabX[i][j])
            valeursY.append(tabY[i][j])


    n = len(valeursX)

    if n < 2:
        raise ValueError("Pas assez de valeurs")


    moyenneX = sum(valeursX) / n
    moyenneY = sum(valeursY) / n


    numerateur = 0
    denominateur = 0


    for i in range(n):

        numerateur += (
            (valeursX[i]-moyenneX)
            *
            (valeursY[i]-moyenneY)
        )

        denominateur += (
            (valeursX[i]-moyenneX)**2
        )


    if denominateur == 0:
        raise ValueError("NDVI constant")


    a = numerateur / denominateur

    b = moyenneY - a*moyenneX


    return a, b

def genererRegressionPNG(tabX, tabY, fichier):

    verifierDeuxTableaux(tabX, tabY)

    x = []
    y = []


    for i in range(len(tabX)):
        for j in range(len(tabX[i])):
            x.append(tabX[i][j])
            y.append(tabY[i][j])


    a,b = regressionLineaire(tabX, tabY)


    xmin = min(x)
    xmax = max(x)


    droiteX = [
        xmin,
        xmax
    ]

    droiteY = [
        a*xmin+b,
        a*xmax+b
    ]


    plt.figure(figsize=(8,6))

    plt.scatter(
        x,
        y,
        s=5
    )

    plt.plot(
        droiteX,
        droiteY
    )


    plt.xlabel("NDVI")
    plt.ylabel("LST (°C)")

    plt.title(
        f"LST = {a:.2f} NDVI + {b:.2f}"
    )


    plt.grid()

    plt.savefig(
        "output/regression/" + fichier,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()