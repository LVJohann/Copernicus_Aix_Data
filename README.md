# Copernicus Aix Data

Analyse de données satellitaires de la ville d'**Aix-en-Provence** à partir des données du **Copernicus Data Space Ecosystem**.

Le projet récupère des données raster au format GeoTIFF, les découpe sur plusieurs zones d'Aix-en-Provence, calcule des statistiques spatiales et étudie la relation entre **végétation (NDVI)** et **température de surface (LST)**.

## Fonctionnalités

- Authentification auprès de l'API Copernicus Data Space avec un `client_id` et un `client_secret`.
- Récupération de données via l'API **Process**.
- Téléchargement de rasters GeoTIFF.
- Analyse du **NDVI**.
- Analyse de la **LST** (Land Surface Temperature).
- Découpage des données sur plusieurs zones :
  - Aix global
  - Jas de Bouffan
  - Parc de la Torse
  - Centre historique
- Calcul de statistiques :
  - moyenne
  - écart-type
  - quartiles
  - minimum / maximum
  - nombre de valeurs différentes
  - indice d'hétérogénéité spatiale
  - taux de répétition
- Analyse de la végétation à partir de seuils NDVI.
- Calcul de la corrélation entre NDVI et LST.
- Calcul de règles d'association avec :
  - support
  - confiance
  - lift
- Régression linéaire entre NDVI et LST.
- Génération d'images PNG et de graphiques.

## Structure du projet

```text
Copernicus_Aix_Data/
├── evalscript/
│   ├── lstSent3.js
│   ├── ndviSent2.js
│   └── ndviSent3.js
│
├── requetes/
│   ├── lstSent3.json
│   ├── ndviSent2.json
│   └── ndviSent3.json
│
├── image/
│   └── .keep
│
├── output/
│   ├── image/
│   │   ├── lst/
│   │   └── ndvi/
│   └── regression/
│
├── ImageCop.py
├── debug.py
├── main.py
├── util.py
├── .gitignore
└── README.md
```

Les fichiers `.tif`, les images générées et le token d'authentification sont ignorés par Git afin d'éviter de transformer le dépôt en musée de fichiers lourds.

## Prérequis

- Python **3.10+** recommandé
- Un compte **Copernicus Data Space Ecosystem**
- Des identifiants API :
  - `COPERNICUS_CLIENT_ID`
  - `COPERNICUS_CLIENT_SECRET`

### Dépendances Python

Installer les dépendances avec :

```bash
pip install numpy rasterio matplotlib requests python-dotenv
```

## Configuration

Créer un fichier `.env` à la racine du projet :

```env
COPERNICUS_CLIENT_ID=votre_client_id
COPERNICUS_CLIENT_SECRET=votre_client_secret
```

Le fichier `.env` est ignoré par Git et ne doit jamais être publié.

Le programme utilise le flux OAuth2 `client_credentials` de Copernicus Data Space pour obtenir un token d'accès. Le token est ensuite conservé localement dans `token.json` jusqu'à son expiration.

## Utilisation

Lancer le programme depuis la racine du dépôt :

```bash
python main.py
```

Le programme effectue successivement les opérations suivantes :

1. Nettoyage des anciens GeoTIFF présents dans `image/`.
2. Récupération ou renouvellement du token Copernicus.
3. Requête du raster NDVI.
4. Requête du raster LST.
5. Sauvegarde des données dans :
   - `image/NDVI.tif`
   - `image/LST.tif`
6. Découpage des rasters sur les différentes zones étudiées.
7. Calcul des statistiques.
8. Proposition de générer les images.
9. Proposition de calculer les corrélations et règles d'association.
10. Génération éventuelle des graphiques de régression.

Le programme demande plusieurs fois si les résultats doivent être affichés ou si des images doivent être générées.

## Données utilisées

### NDVI

Le NDVI, ou **Normalized Difference Vegetation Index**, permet d'estimer la présence et la densité de végétation.

Pour Sentinel-2, le projet contient également un evalscript permettant de calculer directement :

```text
NDVI = (B08 - B04) / (B08 + B04)
```

avec :

- `B04` : bande rouge
- `B08` : proche infrarouge

Le fichier `evalscript/ndviSent3.js` utilise quant à lui directement la variable NDVI fournie par le produit Sentinel-3.

### LST

La LST, ou **Land Surface Temperature**, représente la température de surface.

Le produit Sentinel-3 fournit la température en Kelvin. Le projet la convertit en degrés Celsius :

```text
LST(°C) = LST(K) - 273.15
```

## Requêtes Copernicus

Les paramètres des requêtes sont stockés dans `requetes/`.

Exemple de structure :

```json
{
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
                        "from": "...",
                        "to": "..."
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
    }
}
```

Le `bbox` utilisé couvre la zone d'étude autour d'Aix-en-Provence.

Les dates présentes dans les fichiers JSON correspondent aux acquisitions utilisées lors des analyses et peuvent être modifiées pour effectuer de nouvelles études.

## EvalScripts

Les EvalScripts permettent de définir le traitement effectué par l'API Copernicus avant le téléchargement du raster.

### `ndviSent2.js`

Calcule le NDVI à partir des bandes Sentinel-2 B04 et B08.

### `ndviSent3.js`

Récupère la valeur NDVI du produit Sentinel-3.

### `lstSent3.js`

Récupère la LST Sentinel-3 et convertit les valeurs de Kelvin en Celsius.

## Zones étudiées

Les rasters sont découpés à l'aide de coordonnées en pixels correspondant à l'image téléchargée.

Les zones actuellement étudiées sont :

| Zone | Description |
|---|---|
| Aix global | Zone principale d'étude |
| Jas de Bouffan | Quartier de l'ouest d'Aix |
| Parc de la Torse | Secteur comprenant le parc de la Torse |
| Centre historique | Centre historique d'Aix-en-Provence |

Les coordonnées `x`, `y`, `width` et `height` sont définies dans `main.py`.

> **Attention :** ces coordonnées sont liées à la taille et à la résolution du raster demandé. Si la résolution (`width` / `height`) ou le `bbox` de la requête change, les coordonnées de découpage doivent être recalculées.

## Statistiques

Pour chaque zone, la classe `ImageDonnee` calcule notamment :

- moyenne
- écart-type
- Q1
- médiane (Q2)
- Q3
- minimum
- maximum
- nombre de valeurs différentes
- indice d'hétérogénéité spatiale
- taux de répétition

Pour le NDVI, des indicateurs supplémentaires sont calculés :

- proportion de pixels avec `NDVI >= 0.5`
- proportion de pixels avec `0.2 <= NDVI < 0.5`

Ces seuils peuvent être adaptés selon les objectifs de l'étude.

## Corrélation NDVI / LST

Le projet calcule une corrélation de Pearson entre les valeurs NDVI et LST correspondant aux mêmes pixels.

Conceptuellement :

```text
r = covariance(NDVI, LST) / (écart-type(NDVI) × écart-type(LST))
```

Les deux images doivent avoir exactement les mêmes dimensions.

Une valeur :

- proche de `1` indique une relation linéaire positive ;
- proche de `-1` indique une relation linéaire négative ;
- proche de `0` indique une faible relation linéaire.

La corrélation ne permet toutefois pas, à elle seule, de conclure à une relation de causalité.

## Règles d'association

Le projet teste également des relations de la forme :

```text
NDVI < seuil_NDVI  →  LST > seuil_LST
```

Pour chaque combinaison de seuils, trois indicateurs sont calculés.

### Support

Proportion de pixels satisfaisant simultanément les deux conditions :

```text
support = P(A ∩ B)
```

### Confiance

Proportion des pixels satisfaisant `B` parmi ceux qui satisfont `A` :

```text
confiance = P(B | A)
```

### Lift

Mesure le rapport entre la confiance de la règle et la fréquence naturelle du conséquent :

```text
lift = P(B | A) / P(B)
```

Un lift supérieur à `1` indique que `B` est plus fréquent lorsque `A` est vrai que dans l'ensemble des pixels.

## Régression linéaire

Le projet peut générer une régression linéaire de la LST en fonction du NDVI :

```text
LST = a × NDVI + b
```

Le graphique est enregistré dans :

```text
output/regression/
```

Cette représentation permet notamment d'observer la tendance générale entre végétation et température de surface.

## Fichiers générés

Les fichiers temporaires suivants peuvent être générés pendant l'exécution :

```text
image/
├── NDVI.tif
├── LST.tif
├── AIX_NDVI.tif
├── AIX_LST.tif
├── JasDeBouffan_NDVI.tif
├── JasDeBouffan_LST.tif
├── ParcDeLaTorse_NDVI.tif
├── ParcDeLaTorse_LST.tif
├── CentreHistorique_NDVI.tif
└── CentreHistorique_LST.tif
```

Les images de visualisation sont placées dans :

```text
output/image/ndvi/
output/image/lst/
```

Les graphiques de régression sont placés dans :

```text
output/regression/
```

Ces fichiers sont volontairement exclus du dépôt Git via `.gitignore`.

## Modules principaux

### `main.py`

Point d'entrée du programme.

Il gère :

- l'authentification ;
- les requêtes API ;
- le téléchargement des rasters ;
- le traitement des différentes zones ;
- l'affichage des résultats ;
- les analyses de corrélation ;
- la génération des graphiques.

### `ImageCop.py`

Contient les classes :

- `ImageDonnee`
- `NDVI`
- `LST`

Ces classes regroupent les données raster et les statistiques associées.

### `util.py`

Contient les fonctions utilitaires :

- manipulation des tableaux 1D/2D ;
- découpage des images ;
- création de GeoTIFF ;
- chargement des requêtes et EvalScripts ;
- calcul de corrélation ;
- calcul de support, confiance et lift ;
- régression linéaire ;
- génération des graphiques.

### `debug.py`

Fournit les fonctions simples d'affichage de l'état des étapes :

```text
[OK]
[ERREUR]
```

## Sécurité

Ne jamais publier :

```text
.env
token.json
```

Les identifiants Copernicus ne doivent pas être écrits directement dans le code.

Le dépôt contient un `.gitignore` configuré pour exclure les secrets et les fichiers de données générés.

Si un secret a été accidentellement commité, il faut le considérer comme compromis et le révoquer ou le renouveler.

## Limites et points d'attention

- Les résultats dépendent fortement de la date d'acquisition des données.
- La résolution spatiale diffère selon les produits Sentinel utilisés.
- Les zones sont actuellement définies par des rectangles en pixels et non par des polygones géographiques.
- Une comparaison NDVI/LST nécessite des rasters spatialement compatibles.
- Les nuages et autres artefacts peuvent influencer les statistiques.
- Une corrélation statistique ne constitue pas une preuve de causalité.
- Les seuils NDVI et LST utilisés dans les règles d'association sont des paramètres d'analyse et non des vérités universelles.
- Les données raster générées peuvent être volumineuses et ne sont donc pas versionnées dans Git.

## Objectif scientifique

L'objectif principal du projet est d'étudier spatialement la relation entre la **végétation urbaine** et la **température de surface** à Aix-en-Provence.

L'hypothèse étudiée est notamment qu'une présence plus importante de végétation peut être associée à des températures de surface plus faibles.

Le projet permet ainsi de combiner :

```text
Données satellitaires
        ↓
Traitement raster
        ↓
NDVI + LST
        ↓
Découpage par zones
        ↓
Statistiques spatiales
        ↓
Corrélation / règles d'association
        ↓
Régression et visualisation
```

## Licence

Projet à vocation pédagogique et scientifique.

Les données satellitaires restent soumises aux conditions d'utilisation et aux licences applicables du **Copernicus Data Space Ecosystem**.
