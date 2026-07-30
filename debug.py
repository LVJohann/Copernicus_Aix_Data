def etape(message):
    print(f"{message:.<60}", end="", flush=True)

def ok():
    print("[\033[1;32mOK\033[1;37m]")

def erreur():
    print("[\033[1;31mERREUR\033[1;37m]")