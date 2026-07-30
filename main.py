#==========IMPORTATION DES LIBRAIRIES=========
import numpy as np
import json
import rasterio
import os
import Image as img
import requests
import time
import util
from debug import *
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
#==========INITIALISATION==========
debut = time.time()
clear = lambda: os.system('cls')
clear()
load_dotenv()


DOSSIER = "./image"

util.supprimer_tif(DOSSIER)

#==========VARIABLES==========
source = "NDVI.tif"
session = requests.Session()

CLIENT_ID=os.getenv("COPERNICUS_CLIENT_ID")
CLIENT_SECRET=os.getenv("COPERNICUS_CLIENT_SECRET")




#==========RECUPERATION DU TOKEN==========
# VARIABLES
URL_GET_TOKEN="https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
PAYLOAD_TOKEN= {
    "grant_type" : "client_credentials",
    "client_id" : CLIENT_ID,
    "client_secret" : CLIENT_SECRET
}
TOKEN_FILE="token.json"
etape("Récupération du Token")

 # Vérifier si un token existe déjà
if os.path.exists(TOKEN_FILE):
    newToken = False
    with open(TOKEN_FILE, "r") as f:
        data = json.load(f)

    # marge de sécurité de 60 secondes
    if data["expires_at"] > time.time() + 60:
        TOKEN = data["access_token"]
    else:
        newToken = True

    # Sinon créer un nouveau token
if newToken or not os.path.exists(TOKEN_FILE):
    newToken = True
    response = session.post(URL_GET_TOKEN, data=PAYLOAD_TOKEN)
    response.raise_for_status()

    token_data = response.json()

    TOKEN = token_data["access_token"]

    # Sauvegarde
    with open(TOKEN_FILE, "w") as f:
        json.dump({
            "access_token": TOKEN,
            "expires_at": time.time() + token_data["expires_in"]
        }, f)

if newToken and response.status_code != 200:
    erreur()
    print("Erreur: Code ", response.status_code)
    print(response.text)
    exit(response.status_code)

ok()




#==========RECUPERATION DES TIF==========
# VARIABLES
HEADER={
    "Authorization" : f"Bearer {TOKEN}",
    "Content-Type" : "application/json",
    "Accept" : "image/tiff"
}
session.headers.update(HEADER)
URL_GET_IMAGE="https://sh.dataspace.copernicus.eu/api/v1/process"

# NDVI
SCRIPT_NAME = "ndviSent3"
evalscript = util.chargerEvalscript(SCRIPT_NAME)
REQUEST_NAME = "ndviSent3"
NDVI_BODY=util.chargerRequete(REQUEST_NAME)
NDVI_BODY["evalscript"] = evalscript

etape("Récupération du TIF NDVI sur Aix")

response = session.post(
    URL_GET_IMAGE, 
    json=NDVI_BODY,
    timeout=300
)

if response.status_code != 200:
    erreur()
    print("Erreur: Code ", response.status_code)
    print(response.text)
    exit(response.status_code)

ndvi=response.content

ok()


# LST
SCRIPT_NAME = "lstSent3"
evalscript=util.chargerEvalscript(SCRIPT_NAME)
REQUEST_NAME = "lstSent3"
LST_BODY = util.chargerRequete(REQUEST_NAME)
LST_BODY["evalscript"] = evalscript

etape("Récupération du TIF LST sur Aix")

response = session.post(
    URL_GET_IMAGE, 
    json=LST_BODY,
    timeout=20
)
if response.status_code != 200:
    erreur()
    print("Erreur: Code ", response.status_code)
    print(response.text)
    exit(response.status_code)

lst=response.content

ok()




#==========TELECHARGEMENT IMAGE RESULTAT==========
etape("Téléchargement des images")

if not os.path.exists("image/NDVI.tif"):
    util.telechargerImage(ndvi, "NDVI")
if not os.path.exists("image/LST.tif"):
    util.telechargerImage(lst, "LST")

ok()




#==========TRAITEMENT DE LA DONNEE==========
data = []
etape("Récupération de l'image NDVI")

with rasterio.open("image/NDVI.tif") as src:
    ndvi = src.read(1)

ok()

name = "AIX"
etape(f"Traitement des données NDVI à {name}")

x = 400
y = 400
width = 750-x
height = 670-y
aixGlobal = img.NDVI(ndvi, name, x, y, width, height)
data.append(aixGlobal)
AIX = [aixGlobal]

ok()

name = "JasDeBouffan"
etape(f"Traitement des données NDVI à {name}")

x=420
y=450
width = 575-x
height = 562-y
jasDeBouffan = img.NDVI(ndvi, name, x, y, width, height)
JAS = [jasDeBouffan]

data.append(jasDeBouffan)

ok()

name="ParcDeLaTorse"
etape(f"Traitement des données NDVI à {name}")

x=660
y=460
width=695-x
height=560-y
torse = img.NDVI(ndvi, name, x, y, width, height)
TORSE = [torse]

data.append(torse)

ok()

name="CentreHistorique"
etape(f"Traitement des données NDVI à {name}")

x=550
y=450
width=650-x
height=525-y
centreHistorique = img.NDVI(ndvi, name, x, y, width, height)
CENTRE = [centreHistorique]

data.append(centreHistorique)

ok()


etape("Récupération de l'image LST...")

with rasterio.open("image/LST.tif") as src:
    lst = src.read(1)

ok()

name = "AIX"
etape(f"Traitement des données LST à {name}")

x = 400
y = 400
width = 750-x
height = 670-y
aixGlobal = img.LST(lst, name, x, y, width, height)
data.append(aixGlobal)
AIX.append(aixGlobal)

ok()

name = "JasDeBouffan"
etape(f"Traitement des données LST à {name}")

x=420
y=450
width = 575-x
height = 562-y
jasDeBouffan = img.LST(lst, name, x, y, width, height)
JAS.append(jasDeBouffan)

data.append(jasDeBouffan)

ok()

name="ParcDeLaTorse"
etape(f"Traitement des données LST à {name}")

x=660
y=460
width=695-x
height=560-y
torse = img.LST(lst, name, x, y, width, height)
TORSE.append(torse)

data.append(torse)

ok()

name="CentreHistorique"
etape(f"Traitement des données LST à {name}")

x=550
y=450
width=650-x
height=525-y
centreHistorique = img.LST(lst, name, x, y, width, height)
CENTRE.append(centreHistorique)

data.append(centreHistorique)

ok()


DATA = {
    "Aix_Global" : AIX,
    "Torse" : TORSE,
    "Jas de Bouffan" : JAS,
    "Centre historique" : CENTRE
}



#==========AFFICHAGE DES RESULTATS==========
reponse = input("Voulez-vous afficher les résultats des statistiques ? [Y/n]")
if reponse.upper() == "Y":
    for elt in data:
        elt.toString()




#==========VISUALISATION DES DONNEES==========
reponse = ""
reponse = input("Voulez-vous générer des images des différentes données ? [Y/n]")
if reponse.upper() == "Y":
    for elt in data:
        etape("Génération de l'image " + elt.nom + "...")
        elt.genererPNG(elt.nom)
        ok()


#==========CORRELATION==========
reponse = ""
reponse = input("Voulez-vous afficher les données de corrélation ? [Y/n]")
if reponse.upper() == "Y":
    SEUILS_NDVI = [
        0.32,
        0.35,
        0.38,
        0.40
    ]
    SEUILS_LST = [30, 32, 34, 36, 38, 40, 42]

    for seuil_ndvi in SEUILS_NDVI:

        for seuil_lst in SEUILS_LST:

            print(
                f"\n===== NDVI < {seuil_ndvi} => LST > {seuil_lst}°C =====\n"
            )


            for name, tab in DATA.items():

                try:

                    correlation = util.correlation(
                        tab[0],
                        tab[1]
                    )

                    resultat = util.calculerRegle(
                        tab[0].tab2D,
                        tab[1].tab2D,
                        seuil_ndvi,
                        seuil_lst
                    )


                    print(
                        f"{name:<22}"
                        f"Corr={correlation:6.3f} "
                        f"Conf={resultat.confiance:6.3f} "
                        f"Lift={resultat.lift:6.3f} "
                        f"Support={resultat.support:6.3f}"
                    )


                except ValueError as e:

                    print(
                        f"{name:<22}"
                        f"Impossible ({e})"
                    )


reponse = ""
reponse = input("Voulez-vous générer des courbes de tendance ? [Y/n]")
if reponse.upper() == "Y":
    for (name, tab) in DATA.items():
        etape(f"Génération de la courbe de tendance de {name}")
        util.genererRegressionPNG(
            tab[0].tab2D,
            tab[1].tab2D,
            f"{name}_regression.png"
        )

        ok()

reponse = ""
reponse = input("Voulez-vous afficher le nuage de points global ? [Y/n]")
if reponse.upper() == "Y":
    etape("Affichage du nuage de points global")
    ndvi = img.NDVI(ndvi, "GLOBAL NDVI", 0, 0, 1024, 1024)
    lst = img.LST(lst, "GLOBAL LST", 0, 0, 1024, 1024)

    plt.xlim(
        min(ndvi.tab1D),
        max(ndvi.tab1D)
    )

    plt.scatter(
        ndvi.tab1D,
        lst.tab1D
    )

    plt.xlabel("NDVI")
    plt.ylabel("LST °C")

    plt.grid()
    plt.show()

    ok()


print("Exécution terminée, temps total: ", time.time()-debut, " secondes.")