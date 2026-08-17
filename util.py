import rasterio
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import json

from ImageCop import ImageDonnee


def rognerImage(tableau, x:int, y:int, largeur:int, hauteur:int, source:str, nom:str):
    """
    Extrait une zone rectangulaire d'un tableau 2D et l'enregistre au format TIFF.

    La zone extraite commence aux coordonnées ``(x, y)`` et possède les
    dimensions indiquées par ``largeur`` et ``hauteur``.

    :param float[][] tableau: Tableau 2D représentant l'image source.
    :param int x: Coordonnée horizontale du coin supérieur gauche de la zone.
    :param int y: Coordonnée verticale du coin supérieur gauche de la zone.
    :param int largeur: Largeur de la zone à extraire en pixels.
    :param int hauteur: Hauteur de la zone à extraire en pixels.
    :param str source: Chemin vers le fichier TIFF original servant de référence
                       pour les métadonnées de l'image.
    :param str nom: Nom du fichier TIFF créé dans le dossier ``image/``.
    :returns: Tableau 2D correspondant à la zone extraite.
    :rtype: float[][]
    :raises ValueError: Si la zone demandée dépasse les dimensions du tableau.
    """
    hauteur_image = len(tableau)
    largeur_image = len(tableau[0])

    if x < 0 or y < 0 or x + largeur > largeur_image or y + hauteur > hauteur_image:
        raise ValueError("La zone de rognage dépasse les dimensions de l'image")

    resultat = []

    for ligne in range(y, y + hauteur):
        resultat.append(tableau[ligne][x:x + largeur])

    creerTif(resultat, nom, source)

    return resultat


def creerTif(tableau, nom:str, fichierOriginal:str):
    """
    Crée un fichier TIFF à partir d'un tableau 2D.

    Le profil du fichier TIFF original est utilisé afin de conserver ses
    métadonnées, notamment la projection, la transformation et le type de
    données. Les dimensions sont adaptées à celles du nouveau tableau.

    :param float[][] tableau: Tableau 2D contenant les données de l'image.
    :param str nom: Nom du fichier TIFF à créer dans le dossier ``image/``.
    :param str fichierOriginal: Chemin vers le fichier TIFF original dont le
                                profil est utilisé comme référence.
    """

    tableau = np.array(tableau)

    with rasterio.open(fichierOriginal) as src:

        profil = src.profile.copy()

        profil.update(
            width=tableau.shape[1],
            height=tableau.shape[0]
        )

        with rasterio.open("image/" + nom + ".tif", "w", **profil) as dst:
            dst.write(tableau, 1)


def nbValAuDessusTab2D(val:float, tab)->int:
    """
    Compte le nombre de valeurs supérieures ou égales à un seuil dans un tableau 2D.

    :param float val: Valeur seuil utilisée pour la comparaison.
    :param float[][] tab: Tableau 2D dans lequel effectuer la recherche.
    :returns: Nombre de valeurs supérieures ou égales au seuil.
    :rtype: int
    """
    n = 0
    for line in tab:
        for elt in line:
            if elt >= val:
                n += 1
    return n


def nbValEnDessousTab2D(val:float, tab)->int:
    """
    Compte le nombre de valeurs strictement inférieures à un seuil dans un tableau 2D.

    :param float val: Valeur seuil utilisée pour la comparaison.
    :param float[][] tab: Tableau 2D dans lequel effectuer la recherche.
    :returns: Nombre de valeurs strictement inférieures au seuil.
    :rtype: int
    """
    n = 0
    for line in tab:
        for elt in line:
            if elt < val:
                n += 1
    return n


def chargerEvalscript(nom:str)->str:
    """
    Charge le contenu d'un Evalscript depuis le dossier ``evalscript/``.

    L'Evalscript est recherché dans un fichier portant le nom fourni et
    possédant l'extension ``.js``.

    :param str nom: Nom de l'Evalscript sans son extension.
    :returns: Contenu textuel de l'Evalscript.
    :rtype: str
    :raises FileNotFoundError: Si le fichier correspondant n'existe pas.
    """
    with open(f"evalscript/{nom}.js", "r", encoding="utf-8") as f:
        return f.read()


def chargerRequete(fichier:str):
    """
    Charge une requête JSON depuis le dossier ``requetes/``.

    Le contenu du fichier est désérialisé en objet Python à l'aide du module
    :mod:`json`.

    :param str fichier: Nom du fichier JSON sans son extension.
    :returns: Données contenues dans le fichier JSON.
    :raises FileNotFoundError: Si le fichier n'existe pas.
    :raises json.JSONDecodeError: Si le fichier ne contient pas un JSON valide.
    """
    with open(f"requetes/{fichier}.json", "r", encoding="utf-8") as f:
        return json.load(f)


def telechargerImage(content:str, nom:str):
    """
    Enregistre le contenu binaire d'une image au format TIFF.

    Le fichier est créé dans le dossier ``image/`` avec l'extension ``.tif``.

    :param bytes content: Contenu binaire du fichier TIFF.
    :param str nom: Nom du fichier sans son extension.
    """
    with open(f"image/{nom}.tif", "wb") as f:
        f.write(content)


def supprimer_tif(dossier:str="./image"):
    """
    Supprime tous les fichiers TIFF présents dans un dossier.

    Les fichiers possédant les extensions ``.tif`` et ``.tiff`` sont supprimés.

    :param str dossier: Chemin du dossier dans lequel rechercher les fichiers.
                        Par défaut, ``./image``.
    """
    dossier = Path(dossier)

    for fichier in dossier.glob("*.tif"):
        fichier.unlink()

    for fichier in dossier.glob("*.tiff"):
        fichier.unlink()


def verifierImages(img1:ImageDonnee, img2:ImageDonnee):
    """
    Vérifie que deux images sont compatibles pour les calculs statistiques.

    Les deux images doivent avoir le même effectif ainsi que les mêmes
    dimensions spatiales.

    :param ImageDonnee img1: Première image à comparer.
    :param ImageDonnee img2: Deuxième image à comparer.
    :raises ValueError: Si les images n'ont pas le même nombre de pixels,
                        la même hauteur ou la même largeur.
    """
    if img1.effectif != img2.effectif:
        raise ValueError("Les images n'ont pas le même effectif")

    if len(img1.tab2D) != len(img2.tab2D):
        raise ValueError("Les images n'ont pas la même hauteur")

    if len(img1.tab2D[0]) != len(img2.tab2D[0]):
        raise ValueError("Les images n'ont pas la même largeur")


def condition(valeur:float, seuil:float, operateur:str)->bool:
    """
    Évalue une condition de comparaison entre une valeur et un seuil.

    L'opérateur ``">"`` correspond dans l'implémentation à une comparaison
    supérieure ou égale, tandis que ``"<"`` correspond à une comparaison
    inférieure ou égale.

    :param float valeur: Valeur à comparer.
    :param float seuil: Valeur seuil de comparaison.
    :param str operateur: Opérateur de comparaison, ``">"`` ou ``"<"``.
    :returns: ``True`` si la condition est respectée, sinon ``False``.
    :rtype: bool
    :raises ValueError: Si l'opérateur fourni n'est ni ``">"`` ni ``"<"``.
    """
    if operateur == ">":
        return valeur >= seuil

    if operateur == "<":
        return valeur <= seuil

    raise ValueError("Opérateur invalide ('<' ou '>')")


def correlation(img1, img2):
    """
    Calcule le coefficient de corrélation linéaire entre deux images.

    Chaque pixel de la première image est associé au pixel situé aux mêmes
    coordonnées dans la seconde image. Le coefficient obtenu correspond à la
    covariance normalisée par les écarts-types des deux images.

    :param ImageDonnee img1: Première image utilisée pour le calcul.
    :param ImageDonnee img2: Deuxième image utilisée pour le calcul.
    :returns: Coefficient de corrélation entre les deux images.
    :rtype: float
    :raises ValueError: Si les images sont incompatibles ou si l'une des deux
                        images possède un écart-type nul.
    """
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


class ResultatRegle:
    """
    Stocke les résultats statistiques d'une règle d'association.

    Cette classe regroupe les principales mesures calculées pour une règle :
    support, confiance et lift, ainsi que les effectifs nécessaires à leur
    interprétation.
    """
    def __init__(self, support, confiance, lift,
                 nb_A, nb_B, nb_AB, effectif):
        """
        Initialise les résultats d'une règle d'association.

        :param float support: Proportion de pixels vérifiant simultanément A et B.
        :param float confiance: Probabilité de B sachant A.
        :param float lift: Mesure d'association entre A et B.
        :param int nb_A: Nombre de pixels vérifiant la condition A.
        :param int nb_B: Nombre de pixels vérifiant la condition B.
        :param int nb_AB: Nombre de pixels vérifiant simultanément A et B.
        :param int effectif: Nombre total de pixels étudiés.
        """
        self.support = support
        self.confiance = confiance
        self.lift = lift

        self.nb_A = nb_A
        self.nb_B = nb_B
        self.nb_AB = nb_AB
        self.effectif = effectif


def verifierDeuxTableaux(tab1, tab2):
    """
    Vérifie que deux tableaux 2D peuvent être comparés pixel par pixel.

    Les tableaux doivent être non nuls, non vides et posséder les mêmes
    dimensions.

    :param float[][] tab1: Premier tableau 2D.
    :param float[][] tab2: Deuxième tableau 2D.
    :raises ValueError: Si un tableau est nul, vide ou possède des dimensions
                        différentes de l'autre.
    """
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
    """
    Calcule une règle d'association entre deux tableaux 2D.

    Chaque pixel du premier tableau définit l'antécédent A et chaque pixel
    correspondant du second tableau définit le conséquent B.

    Les trois indicateurs suivants sont calculés :

    - le support : proportion de pixels vérifiant A et B ;
    - la confiance : proportion des pixels vérifiant B parmi ceux vérifiant A ;
    - le lift : rapport entre la confiance et la probabilité de B.

    :param float[][] tab1: Premier tableau 2D utilisé pour définir A.
    :param float[][] tab2: Deuxième tableau 2D utilisé pour définir B.
    :param float seuil1: Seuil utilisé pour la condition A.
    :param float seuil2: Seuil utilisé pour la condition B.
    :param str operateur1: Opérateur de comparaison de A, ``"<"`` ou ``">"``.
    :param str operateur2: Opérateur de comparaison de B, ``"<"`` ou ``">"``.
    :returns: Objet contenant les résultats de la règle d'association.
    :rtype: ResultatRegle
    :raises ValueError: Si les tableaux sont incompatibles, si A ou B est
                        absent ou si un opérateur est invalide.
    """
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
    """
    Calcule les coefficients d'une régression linéaire entre deux tableaux 2D.

    Les valeurs des deux tableaux sont aplaties puis considérées comme des
    couples de données (X, Y). La droite obtenue est de la forme :

        Y = aX + b

    où ``a`` est le coefficient directeur et ``b`` l'ordonnée à l'origine.

    :param float[][] tabX: Tableau 2D contenant les variables explicatives X.
    :param float[][] tabY: Tableau 2D contenant les variables expliquées Y.
    :returns: Tuple contenant le coefficient directeur ``a`` et l'ordonnée à
              l'origine ``b``.
    :rtype: tuple[float, float]
    :raises ValueError: Si les tableaux sont incompatibles, contiennent moins
                        de deux valeurs ou si les valeurs de X sont constantes.
    """
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
    """
    Génère un graphique PNG représentant une régression linéaire.

    Les couples de valeurs sont représentés sous forme de nuage de points et
    la droite de régression linéaire est superposée.

    Le graphique est enregistré dans le dossier
    ``output/regression/``.

    Dans le contexte du projet, l'axe X représente le NDVI et l'axe Y la
    température de surface terrestre (LST).

    :param float[][] tabX: Tableau 2D contenant les valeurs du NDVI.
    :param float[][] tabY: Tableau 2D contenant les valeurs de LST.
    :param str fichier: Nom du fichier PNG à générer.
    :raises ValueError: Si les tableaux sont incompatibles ou si la régression
                        linéaire ne peut pas être calculée.
    """
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