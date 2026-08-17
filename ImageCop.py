import math
import numpy as np
import matplotlib.pyplot as plt


class ImageDonnee:
    """
    Représente une zone d'image géographique et ses statistiques.

    La classe extrait une zone rectangulaire d'un tableau 2D puis calcule
    plusieurs indicateurs statistiques et spatiaux sur les pixels extraits.

    Les principales informations stockées sont la moyenne, l'écart-type,
    les quartiles, le nombre de valeurs différentes, la diversité spatiale
    et le taux de répétition.

    :param float[][] tab2DIni: Tableau 2D contenant l'image complète.
    :param str nom: Nom de la zone étudiée.
    :param int x: Coordonnée horizontale de départ de la zone.
    :param int y: Coordonnée verticale de départ de la zone.
    :param int largeur: Largeur de la zone en pixels.
    :param int hauteur: Hauteur de la zone en pixels.
    :param str source: Chemin vers le fichier TIFF source.
    :param str type_donnee: Type de donnée représentée, par exemple ``NDVI``
                            ou ``LST``.
    """
    def __init__(self, tab2DIni, nom, x, y, largeur, hauteur, source, type_donnee):
        """
        Initialise une image de données et calcule ses statistiques.

        La zone indiquée est extraite du tableau source puis les différents
        indicateurs statistiques sont calculés automatiquement.

        :param float[][] tab2DIni: Tableau 2D contenant l'image complète.
        :param str nom: Nom de la zone étudiée.
        :param int x: Coordonnée horizontale de départ.
        :param int y: Coordonnée verticale de départ.
        :param int largeur: Largeur de la zone à extraire.
        :param int hauteur: Hauteur de la zone à extraire.
        :param str source: Chemin vers le fichier TIFF source.
        :param str type_donnee: Type de donnée, par exemple ``NDVI`` ou ``LST``.
        :raises ValueError: Si la zone extraite est vide ou invalide.
        """
        import util
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
        self.valeursDifferentes = self.calculerValeursDifferentes()
        self.variance_spatiale = self.calculerVarianceSpatiale()
        self.tauxRepetition = 1-self.variance_spatiale

    def calculerMoyenne(self):
        """
        Calcule la moyenne arithmétique des pixels de l'image.

        :returns: Moyenne des valeurs présentes dans l'image.
        :rtype: float
        :raises ValueError: Si l'effectif de l'image est nul.
        """
        if self.effectif <= 0:
            raise ValueError("Effectif nul")

        somme = sum(
            elt
            for ligne in self.tab2D
            for elt in ligne
        )

        return somme / self.effectif


    def calculerEcartType(self):
        """
        Calcule l'écart-type de la distribution des valeurs de l'image.

        La variance utilisée est la variance de population, c'est-à-dire qu'elle
        est divisée par l'effectif total des pixels.

        :returns: Écart-type des valeurs de l'image.
        :rtype: float
        :raises ValueError: Si la variance calculée est négative.
        """
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
        """
        Calcule les premier, deuxième et troisième quartiles de l'image.

        Les valeurs de l'image sont préalablement triées puis les quartiles sont
        déterminés à partir des indices calculés selon l'effectif.

        Les résultats sont stockés dans les attributs ``Q1``, ``Q2`` et ``Q3``.

        :raises ValueError: Si les indices des quartiles sont invalides.
        """
        nQ1 = int((self.effectif - 3) / 4)
        nQ2 = int((self.effectif + 1) / 2)
        nQ3 = int((3 * self.effectif + 1) / 4)

        if nQ1 < 0 or nQ2 < 0 or nQ3 < 0:
            raise ValueError("Erreur de calcul des quartiles")

        self.Q1 = self.tabSorted[nQ1]
        self.Q2 = self.tabSorted[nQ2]
        self.Q3 = self.tabSorted[nQ3]


    def tab2DToTab1D(self):
        """
        Convertit le tableau 2D de l'image en tableau 1D.

        Les lignes du tableau sont parcourues successivement afin de construire
        une liste contenant tous les pixels de l'image.

        :returns: Liste contenant toutes les valeurs de l'image.
        :rtype: float[]
        """
        return [
            elt
            for ligne in self.tab2D
            for elt in ligne
        ]


    def toString(self):
        """
        Affiche dans la console un résumé statistique de l'image.

        Les informations affichées comprennent le type de donnée, la moyenne,
        l'écart-type, les quartiles, les valeurs minimale et maximale, le nombre
        de valeurs différentes, la diversité spatiale et le taux de répétition.
        """
        print("====================", self.nom, "====================")
        print("Type :", self.type_donnee)
        print("Moyenne :", self.moyenne)
        print("Ecart-type :", self.ecart_type)
        print("Q1 :", self.Q1)
        print("Q2 :", self.Q2)
        print("Q3 :", self.Q3)
        print("Minimum :", self.tabSorted[0])
        print("Maximum :", self.tabSorted[-1])
        print("Nombre de valeurs différentes :", self.valeursDifferentes)
        print("Indice d'hétérogénéité spatiale :", self.variance_spatiale)
        print("Taux de répétition :", self.tauxRepetition)

        print("\n")


    def genererPNG(self, fichier):
        """
        Génère une représentation graphique de l'image au format PNG.

        La palette, les bornes de valeurs et l'unité de la légende sont adaptées
        au type de donnée représenté.

        Pour une image NDVI, les valeurs sont représentées dans l'intervalle
        ``[-1, 1]``. Pour une image LST, l'intervalle utilisé est ``[20, 45]`` °C.

        :param str fichier: Nom du fichier PNG à générer.
        :raises ValueError: Si le type de donnée n'est pas reconnu.
        """
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

    def calculerVarianceSpatiale(self):
        """
        Calcule un indicateur de diversité spatiale de l'image.

        L'indicateur correspond au rapport entre le nombre de valeurs distinctes
        et le nombre total de pixels :

            diversité spatiale = valeurs distinctes / effectif

        Une valeur proche de 0 indique une faible diversité des valeurs tandis
        qu'une valeur proche de 1 indique une forte diversité.

        :returns: Indice de diversité spatiale compris entre 0 et 1.
        :rtype: float
        :raises ValueError: Si l'effectif de l'image est nul.
        """
        if self.effectif <= 0:
            raise ValueError("Effectif nul")

        return self.valeursDifferentes / self.effectif

    def calculerValeursDifferentes(self):
        """
        Compte le nombre de valeurs distinctes présentes dans l'image.

        :returns: Nombre de valeurs différentes présentes dans ``tab1D``.
        :rtype: int
        :raises ValueError: Si l'effectif de l'image est nul.
        """
        if self.effectif <= 0:
            raise ValueError("Effectif nul")

        return len(set(self.tab1D))


class NDVI(ImageDonnee):
    """
    Représente une image NDVI et calcule des indicateurs liés à la végétation.

    Cette classe hérite de :class:`ImageDonnee` et ajoute plusieurs indicateurs
    permettant notamment d'estimer la proportion de pixels présentant une
    végétation importante ou faible.

    :param float[][] tab2DIni: Tableau 2D contenant l'image NDVI complète.
    :param str nom: Nom de la zone étudiée.
    :param int x: Coordonnée horizontale de départ.
    :param int y: Coordonnée verticale de départ.
    :param int largeur: Largeur de la zone en pixels.
    :param int hauteur: Hauteur de la zone en pixels.
    :param str source: Chemin vers l'image NDVI source.
                         Par défaut ``image/NDVI.tif``.
    """
    def __init__(self, tab2DIni, nom, x, y, largeur, hauteur,
                 source="image/NDVI.tif"):
        """
        Initialise une image NDVI et calcule ses indicateurs de végétation.

        Trois indicateurs supplémentaires sont calculés :

        - le nombre de pixels avec NDVI supérieur ou égal à 0.5 ;
        - le nombre de pixels avec NDVI inférieur à 0.5 ;
        - le nombre de pixels avec NDVI supérieur ou égal à 0.2.

        :param float[][] tab2DIni: Tableau 2D contenant l'image NDVI complète.
        :param str nom: Nom de la zone étudiée.
        :param int x: Coordonnée horizontale de départ.
        :param int y: Coordonnée verticale de départ.
        :param int largeur: Largeur de la zone en pixels.
        :param int hauteur: Hauteur de la zone en pixels.
        :param str source: Chemin vers l'image NDVI source.
        :raises ValueError: Si la zone extraite est vide ou invalide.
        """
        import util

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
        """
        Affiche les statistiques générales de l'image ainsi que les indicateurs
        spécifiques au NDVI.

        Les indicateurs supplémentaires affichés sont :

        - le taux de végétation forte pour un NDVI supérieur ou égal à 0.5 ;
        - le taux de végétation faible pour un NDVI compris entre 0.2 et 0.5.
        """
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
    """
    Représente une image de température de surface terrestre (LST).

    Cette classe hérite de :class:`ImageDonnee` et identifie les données
    comme étant des températures de surface terrestre exprimées en degrés
    Celsius.

    :param float[][] tab2DIni: Tableau 2D contenant l'image LST complète.
    :param str nom: Nom de la zone étudiée.
    :param int x: Coordonnée horizontale de départ.
    :param int y: Coordonnée verticale de départ.
    :param int largeur: Largeur de la zone en pixels.
    :param int hauteur: Hauteur de la zone en pixels.
    :param str source: Chemin vers l'image LST source.
                         Par défaut ``image/LST.tif``.
    """
    def __init__(self, tab2DIni, nom, x, y, largeur, hauteur,
                 source="image/LST.tif"):
        """
        Initialise une image de température de surface terrestre.

        Les statistiques générales définies dans :class:`ImageDonnee` sont
        automatiquement calculées sur la zone extraite.

        :param float[][] tab2DIni: Tableau 2D contenant l'image LST complète.
        :param str nom: Nom de la zone étudiée.
        :param int x: Coordonnée horizontale de départ.
        :param int y: Coordonnée verticale de départ.
        :param int largeur: Largeur de la zone en pixels.
        :param int hauteur: Hauteur de la zone en pixels.
        :param str source: Chemin vers l'image LST source.
        :raises ValueError: Si la zone extraite est vide ou invalide.
        """
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