def etape(message: str):
    """
        Affiche le message entré en paramètre puis une suite de points. \n
        Laisse de la place a la fin de la chaine pour entrer le status de ceette étape.\n
        :param str message: mesage à envoyer
    """
    print(f"{message:.<60}", end="", flush=True)

def ok():
    """
        Affiche OK en vert.
    """
    print("[\033[1;32mOK\033[1;37m]")

def erreur():
    """
        Affiche ERREUR en rouge.
    """
    print("[\033[1;31mERREUR\033[1;37m]")