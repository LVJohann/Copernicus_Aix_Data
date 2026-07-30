import math
import util
import numpy as np
import matplotlib.pyplot as plt


class ImageDonnee:

    def __init__(self, tab2DIni, nom, x, y, largeur, hauteur, source, type_donnee):
        self.nom = nom + "_" + type_donnee
        self.x = x
        self.y = y
        self.hauteur = hauteur
        self.largeur = largeur
        self.type_donnee = type_donnee

        self.tab2D = util.rognerImage(
            tab2DIni,
            self.x,
            self.y,
            self.largeur,
            self.hauteur,
            source,
            self.nom
        )

        if len(self.tab2D) == 0 or len(self.tab2D[0]) == 0:
            raise ValueError("Image vide")

        self.effectif = len(self.tab2D) * len(self.tab2D[0])

        self.moyenne = self.calculerMoyenne()
        self.ecart_type = self.calculerEcartType()

        self.tab1D = self.tab2DToTab1D()
        self.tabSorted = sorted(self.tab1D)

        self.Q1 = 0
        self.Q2 = 0
        self.Q3 = 0

        self.calculerQuartiles()


    def calculerMoyenne(self):
        if self.effectif <= 0:
            raise ValueError("Effectif nul")

        somme = sum(
            elt
            for ligne in self.tab2D
            for elt in ligne
        )

        return somme / self.effectif


    def calculerEcartType(self):
        variance = sum(
            (elt - self.moyenne) ** 2
            for ligne in self.tab2D
            for elt in ligne
        )

        variance /= self.effectif

        if variance < 0:
            raise ValueError("Variance négative")

        return math.sqrt(variance)


    def calculerQuartiles(self):

        nQ1 = int((self.effectif - 3) / 4)
        nQ2 = int((self.effectif + 1) / 2)
        nQ3 = int((3 * self.effectif + 1) / 4)

        if nQ1 < 0 or nQ2 < 0 or nQ3 < 0:
            raise ValueError("Erreur de calcul des quartiles")

        self.Q1 = self.tabSorted[nQ1]
        self.Q2 = self.tabSorted[nQ2]
        self.Q3 = self.tabSorted[nQ3]


    def tab2DToTab1D(self):
        return [
            elt
            for ligne in self.tab2D
            for elt in ligne
        ]


    def toString(self):

        print("====================", self.nom, "====================")
        print("Type :", self.type_donnee)
        print("Moyenne :", self.moyenne)
        print("Ecart-type :", self.ecart_type)
        print("Q1 :", self.Q1)
        print("Q2 :", self.Q2)
        print("Q3 :", self.Q3)
        print("Minimum :", self.tabSorted[0])
        print("Maximum :", self.tabSorted[-1])

        print("\n")


    def genererPNG(self, fichier):

        tab = np.array(self.tab2D, dtype=float)

        if self.type_donnee == "NDVI":

            vmin = -1
            vmax = 1
            cmap = plt.cm.YlGn
            unite = "NDVI"
            dossier = "output/image/ndvi/"

        elif self.type_donnee == "LST":

            vmin = 20
            vmax = 45
            cmap = plt.cm.jet
            unite = "Température (°C)"
            dossier = "output/image/lst/"

        else:
            raise ValueError("Type inconnu")


        plt.figure(figsize=(8, 6))

        image = plt.imshow(
            tab,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax
        )

        plt.axis("off")

        cbar = plt.colorbar(
            image,
            fraction=0.046,
            pad=0.04
        )

        cbar.set_label(unite)

        plt.savefig(
            dossier + fichier,
            bbox_inches="tight",
            dpi=300
        )

        plt.close()



class NDVI(ImageDonnee):

    def __init__(self, tab2DIni, nom, x, y, largeur, hauteur,
                 source="image/NDVI.tif"):

        super().__init__(
            tab2DIni,
            nom,
            x,
            y,
            largeur,
            hauteur,
            source,
            "NDVI"
        )

        self.top050 = util.nbValAuDessusTab2D(0.5, self.tab2D)
        self.sub050 = util.nbValEnDessousTab2D(0.5, self.tab2D)
        self.top020 = util.nbValAuDessusTab2D(0.2, self.tab2D)


    def toString(self):

        super().toString()

        print(
            "Taux végétation forte (NDVI > 0.5) :",
            self.top050 / self.effectif
        )

        print(
            "Taux végétation faible (0.2 < NDVI < 0.5) :",
            (self.top020 - self.top050) / self.effectif
        )

        print("\n")



class LST(ImageDonnee):

    def __init__(self, tab2DIni, nom, x, y, largeur, hauteur,
                 source="image/LST.tif"):

        super().__init__(
            tab2DIni,
            nom,
            x,
            y,
            largeur,
            hauteur,
            source,
            "LST"
        )