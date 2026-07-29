import math
import util
from PIL import Image as PILImage
import numpy as np
import matplotlib.pyplot as plt

class NDVI:
    def __init__(self, tab2DIni, nom, x, y, largeur, hauteur, source="image/NDVI.tif"):
        self.nom = nom + "_NDVI"
        self.x = x
        self.y = y
        self.hauteur = hauteur
        self.largeur = largeur
        self.tab2D = util.rognerImage(tab2DIni, self.x, self.y, self.largeur, self.hauteur, source, self.nom)
        self.effectif = len(self.tab2D)*len(self.tab2D[0])
        self.moyenne = self.calculerMoyenne()
        self.ecart_type = self.calculerEcartType()
        self.top050 = util.nbValAuDessusTab2D(0.5, self.tab2D)
        self.sub050 = util.nbValEnDessousTab2D(0.5, self.tab2D)
        self.tab1D = []
        self.tab2DToTab1D()
        self.tabSorted = sorted(self.tab1D)
        self.Q1 = 0
        self.Q2 = 0
        self.Q3 = 0
        self.calculerQuartiles()
        self.top020 = util.nbValAuDessusTab2D(0.2, self.tab2D)
        self.type_donnee = "NDVI"

    def calculerEcartType(self):      
        var = 0
        for line in self.tab2D:
            for elt in line:
                var += (elt - self.moyenne)**2
        var /= self.effectif
        if var < 0:
            raise ValueError("Variance négative")

        return math.sqrt(var)

    def calculerMoyenne(self):
        if (self.effectif <= 0):
            raise ValueError("Effectif nul")
        
        somme = 0
        for line in self.tab2D:
            for elt in line:
                somme += elt
        return somme/self.effectif

    def toString(self):
        print("====================", self.nom, "====================")
        print("Moyenne: ", self.moyenne)
        print("Taux de végétation forte (NDVI > 0.5): ", self.top050/self.effectif)
        print("Taux de végétation faible (NDVI > 0.2 et NDVI < 0.5): ", (self.top020-self.top050)/self.effectif)
        print("Ecart-type: ", self.ecart_type)
        print("Q1: ", self.Q1)
        print("Q2: ", self.Q2)
        print("Q3: ", self.Q3)
        print("Minimum: ", self.tabSorted[0])
        print("Maximum: ", self.tabSorted[len(self.tabSorted)-1])

        print("\n")

    def calculerQuartiles(self):
        nQ1 = int((self.effectif-3)/4)
        nQ2 = int((self.effectif+1)/2)
        nQ3 = int((3*self.effectif+1)/4)

        if (nQ1 < 0 or nQ2 < 0 or nQ3 < 0):
            raise ValueError("Erreur de calcul des quartiles")

        self.Q1 = self.tabSorted[nQ1]
        self.Q2 = self.tabSorted[nQ2]
        self.Q3 = self.tabSorted[nQ3]

    def tab2DToTab1D(self):
        self.tab1D = []
        for line in self.tab2D:
            for elt in line:
                self.tab1D.append(elt)

    def genererPNG(self, fichier, type_donnee="NDVI"):
        """
        Génère une image PNG colorée avec une légende.

        type_donnee :
            - NDVI
            - LST
        """

        tab = np.array(self.tab2D, dtype=float)

        if type_donnee == "NDVI":

            vmin = -1
            vmax = 1

            cmap = plt.cm.YlGn

            unite = "NDVI"

        elif type_donnee == "LST":

            vmin = 20
            vmax = 45

            cmap = plt.cm.jet

            unite = "Température (°C)"

        else:
            raise ValueError("Type inconnu : utiliser NDVI ou LST")


        # Création figure
        plt.figure(figsize=(8, 6))

        image = plt.imshow(
            tab,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax
        )

        plt.axis("off")


        # Ajout de la légende
        cbar = plt.colorbar(
            image,
            fraction=0.046,
            pad=0.04
        )

        cbar.set_label(unite)


        # Sauvegarde
        plt.savefig(
            "output/image/ndvi/" + fichier,
            bbox_inches="tight",
            dpi=300
        )

        plt.close()


class LST:
    def __init__(self, tab2DIni, nom, x, y, largeur, hauteur, source="image/LST.tif"):
        self.nom = nom + "_LST"
        self.x = x
        self.y = y
        self.hauteur = hauteur
        self.largeur = largeur
        self.tab2D = util.rognerImage(tab2DIni, self.x, self.y, self.largeur, self.hauteur, source, self.nom)
        self.effectif = len(self.tab2D)*len(self.tab2D[0])
        self.moyenne = self.calculerMoyenne()
        self.ecart_type = self.calculerEcartType()
        self.tab1D = []
        self.tab2DToTab1D()
        self.tabSorted = sorted(self.tab1D)
        self.Q1 = 0
        self.Q2 = 0
        self.Q3 = 0
        self.calculerQuartiles()
        self.type_donnee = "LST"

    def calculerEcartType(self):      
        var = 0
        for line in self.tab2D:
            for elt in line:
                var += (elt - self.moyenne)**2
        var /= self.effectif
        if var < 0:
            raise ValueError("Variance négative")

        return math.sqrt(var)

    def calculerMoyenne(self):
        if (self.effectif <= 0):
            raise ValueError("Effectif nul")
        
        somme = 0
        for line in self.tab2D:
            for elt in line:
                somme += elt
        return somme/self.effectif

    def toString(self):
        print("====================", self.nom, "====================")
        print("Moyenne: ", self.moyenne)
        print("Ecart-type: ", self.ecart_type)
        print("Q1: ", self.Q1)
        print("Q2: ", self.Q2)
        print("Q3: ", self.Q3)
        print("Minimum: ", self.tabSorted[0])
        print("Maximum: ", self.tabSorted[len(self.tabSorted)-1])

        print("\n")

    def calculerQuartiles(self):
        nQ1 = int((self.effectif-3)/4)
        nQ2 = int((self.effectif+1)/2)
        nQ3 = int((3*self.effectif+1)/4)

        if (nQ1 < 0 or nQ2 < 0 or nQ3 < 0):
            raise ValueError("Erreur de calcul des quartiles")

        self.Q1 = self.tabSorted[nQ1]
        self.Q2 = self.tabSorted[nQ2]
        self.Q3 = self.tabSorted[nQ3]

    def tab2DToTab1D(self):
        self.tab1D = []
        for line in self.tab2D:
            for elt in line:
                self.tab1D.append(elt)
                
    def genererPNG(self, fichier, type_donnee="LST"):
            """
            Génère une image PNG colorée avec une légende.
    
            type_donnee :
                - NDVI
                - LST
            """
    
            tab = np.array(self.tab2D, dtype=float)
    
            if type_donnee == "NDVI":
    
                vmin = -1
                vmax = 1
    
                cmap = plt.cm.YlGn
    
                unite = "NDVI"
    
            elif type_donnee == "LST":
    
                vmin = 20
                vmax = 45
    
                cmap = plt.cm.jet
    
                unite = "Température (°C)"
    
            else:
                raise ValueError("Type inconnu : utiliser NDVI ou LST")
    
    
            # Création figure
            plt.figure(figsize=(8, 6))
    
            image = plt.imshow(
                tab,
                cmap=cmap,
                vmin=vmin,
                vmax=vmax
            )
    
            plt.axis("off")
    
    
            # Ajout de la légende
            cbar = plt.colorbar(
                image,
                fraction=0.046,
                pad=0.04
            )
    
            cbar.set_label(unite)
    
    
            # Sauvegarde
            plt.savefig(
                "output/image/lst/" + fichier,
                bbox_inches="tight",
                dpi=300
            )
    
            plt.close()