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

# NDVI
URL_GET_IMAGE="https://sh.dataspace.copernicus.eu/api/v1/process"
evalscript = util.chargerEvalscript("ndvi")
NDVI_BODY={
    "input": {
        "bounds": {
        "bbox": [
            5.30,
            43.45,
            5.55,
            43.60
        ]
        },
        "data": [
        {
            "type": "sentinel-2-l2a",
            "dataFilter": {
            "timeRange": {
                "from": "2024-06-01T00:00:00Z",
                "to": "2024-06-10T23:59:59Z"
            },
            "mosaickingOrder":"leastCC"
            }
        }
        ]
    },
    "output": {
        "width": 1024,
        "height": 1024,
        "responses": [
        {
            "identifier": "default",
            "format": {
            "type": "image/tiff"
            }
        }
        ]
    },
    "evalscript": evalscript
}

etape("Récupération du TIF NDVI sur Aix")

response = session.post(
    URL_GET_IMAGE, 
    json=NDVI_BODY,
    timeout=20
)

if response.status_code != 200:
    erreur()
    print("Erreur: Code ", response.status_code)
    print(response.text)
    exit(response.status_code)

ndvi=response.content

ok()


# LST
evalscript=util.chargerEvalscript("lst")
LST_BODY = {
    "input": {
        "bounds": {
            "bbox": [
                5.30,
                43.45,
                5.55,
                43.60
            ]
        },
        "data": [
            {
                "type": "sentinel-3-slstr-l2",
                "dataFilter": {
                    "timeRange": {
                        "from": "2026-07-28T09:00:00Z",
                        "to": "2026-07-28T09:59:59Z"
                    }
                }
            }
        ]
    },
    "output": {
        "width": 1024,
        "height": 1024,
        "responses": [
            {
                "identifier": "default",
                "format": {
                    "type": "image/tiff"
                }
            }
        ]
    },
    "evalscript": evalscript
}

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

print(response.status_code)
print(hash(evalscript))
print(response.request.body.decode() if isinstance(response.request.body, bytes) else response.request.body)

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

ok()

name = "JasDeBouffan"
etape(f"Traitement des données NDVI à {name}")

x=420
y=450
width = 575-x
height = 562-y
jasDeBouffan = img.NDVI(ndvi, name, x, y, width, height)

data.append(jasDeBouffan)

ok()

name="ParcDeLaTorse"
etape(f"Traitement des données NDVI à {name}")

x=660
y=460
width=695-x
height=560-y
torse = img.NDVI(ndvi, name, x, y, width, height)

data.append(torse)

ok()

name="CentreHistorique"
etape(f"Traitement des données NDVI à {name}")

x=550
y=450
width=650-x
height=525-y
centreHistorique = img.NDVI(ndvi, name, x, y, width, height)

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

ok()

name = "JasDeBouffan"
etape(f"Traitement des données LST à {name}")

x=420
y=450
width = 575-x
height = 562-y
jasDeBouffan = img.LST(lst, name, x, y, width, height)

data.append(jasDeBouffan)

ok()

name="ParcDeLaTorse"
etape(f"Traitement des données LST à {name}")

x=660
y=460
width=695-x
height=560-y
torse = img.LST(lst, name, x, y, width, height)

data.append(torse)

ok()

name="CentreHistorique"
etape(f"Traitement des données LST à {name}")

x=550
y=450
width=650-x
height=525-y
centreHistorique = img.LST(lst, name, x, y, width, height)

data.append(centreHistorique)

ok()





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


with rasterio.open("image/LST.tif") as src:
    lst = src.read(1)

print(np.nanmax(lst))
print(np.nanmin(lst))

print("Exécution terminée, temps total: ", time.time()-debut, " secondes.")