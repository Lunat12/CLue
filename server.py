from curses.ascii import isdigit
from random import choices
import socket 

#region dictionaries:

characters = {"1": "Srta. Amapola", "2": "Sra. Celeste", "3": "Profesor Mora", "4": "Coronel Rubio" , "5": "Padre Prado", "6" : "Dra. Orquídea"}
rooms = {"1": "Entrada", "2": "Sala de estar", "3": "Biblioteca", "4": "Cocina" , "5": "Estudio", "6" : "Billar"}
weapons = {"1": "Daga", "2": "Candelabro", "3": "Revolver", "4": "Cuerda" , "5": "Tuberia ardiendo", "6" : "Llave inglesa"}

#end region


#region functions:

def reset():
    global guilty, player1, player2, turn, message

    turn = False
    guilty = []
    player1 = []
    player2 = []
    message = None

def GetGuilty():
    global guilty

    num = choices(list(characters), k=1)[0]
    guilty.append(characters[num])
    
    
    num2 = choices(list(rooms), k=1)[0]
    guilty.append(rooms[num2])
    

    num3 = choices(list(weapons), k=1)[0]
    guilty.append(weapons[num3])

def DealCards():

    counter = 0
    for i in characters.values():
        if i not in guilty:
            counter += 1
            if counter % 2 == 0:
                player2.append(i)
                continue
            player1.append(i)

    for i in rooms.values():
        if i not in guilty:
            counter += 1
            if counter % 2 == 0:
                player2.append(i)
                continue
            player1.append(i)

    for i in weapons.values():
        if i not in guilty:
            counter += 1
            if counter % 2 == 0:
                player2.append(i)
                continue
            player1.append(i)
        
    print("\nTus cartas son: " + ', '.join(player1))

    send = ', '.join(player2)
    send = "\nTus cartas son: " + send + "\nPress enter to continue."
    return send.encode()



def Play():
    send = "\n¿Deseas 1-preguntar o 2-acusar?"

    if turn:
        send = input(send + " ")
        if send.isnumeric():
            return send == "1"
        return Play()
    return send.encode()
    
def Ask():
    global asking
    asking = []
    
    asking.append(characters[str(AskCharacter())])
    asking.append(rooms[str(AskRoom())])
    asking.append(weapons[str(AskWeapon())])


def AskCharacter():
    send = "\n¿Por cual personaje deseas preguntar? "

    for key, val in characters.items():
        send += f"\n\t{key}-{val}"
    send += "\n\tTú elección: "

    if turn:
        c = input(send)
        if c in characters.keys():
            return c
        print("\nOpción no valida")
        return AskCharacter()

    connection.sendall(send.encode())
    c = connection.recv(1024).decode()
    if c in characters.keys():
        return c
    connection.sendall("\nOpción no valida\nPress enter to continue.".encode())
    connection.recv(1024)
    return AskCharacter()


def AskRoom():
    send = "\n¿Por cual sala deseas preguntar? "

    for key, val in rooms.items():
        send += f"\n\t{key}-{val}"
    send += "\n\tTú elección: "

    if turn:
        r = input(send)
        if r in rooms.keys():
            return r
        print("\nOpción no valida")
        return AskRoom()

    connection.sendall(send.encode())
    r = connection.recv(1024).decode()
    if r in rooms.keys():
        return r
    connection.sendall("\nOpción no valida\nPress enter to continue.".encode())
    connection.recv(1024)
    return AskRoom()


def AskWeapon():
    send = "\n¿Por cual arma deseas preguntar? "

    for key, val in weapons.items():
        send += f"\n\t{key}-{val}"
    send += "\n\tTú elección: "

    if turn:
        w = input(send)
        if w in weapons.keys():
            return w
        print("\nOpción no valida")
        return AskWeapon()

    connection.sendall(send.encode())
    w = connection.recv(1024).decode()
    if w in weapons.keys():
        return w
    connection.sendall("\nOpción no valida\nPress enter to continue.".encode())
    connection.recv(1024)
    return AskWeapon()


def Answer():
    send = f"\nTu rival ha solicitado ver estas cartas de tu baraja: "
    global currentCoincidence
    currentCoincidence = []

    counter = 0
    if not turn:
        for i in asking:
            if i in player1:
                send += f"\n\t{counter}-{i}"
                currentCoincidence.append(i)
                counter += 1
        
        if len(currentCoincidence) <= 0:
            print("\nNinguna carta coincide.")
            return ""

        res = input(send+"\n\tElige una carta para mostrarle: ")

        if res.isdigit():
            if int(res) in range(0, len(currentCoincidence)):
                return res

        print("\nOpción no válida.")
        return Answer()

    for i in asking:
            if i in player2:
                send += f"\n\t{counter}-{i}"
                currentCoincidence.append(i)
                counter += 1
    
    if len(currentCoincidence) <= 0:
            send = "\nNinguna carta coincide.\nPulsa enter para continuar".encode()
            connection.sendall(send.encode())
            connection.recv(1024)
            return ""

    send += "\n\tElige una carta para mostrarle: "
    connection.sendall(send.encode())
    res = connection.recv(1024).decode()

    if res.isdigit():
            if int(res) in range(0, len(currentCoincidence)):
                return res

    connection.sendall("\nOpción no válida\nPulsa enter para continuar.".encode())
    connection.recv(1024)
    return Answer()


def EndTurn(_mesage):
    global turn

    if turn:

        if _mesage== "": print("\nTu rival dice: No tengo ninguna carta de esas.")
        else: print("\nJugador 2 dice: Tengo la carta " + currentCoincidence[int(_mesage)])
        
        turn= False
        return("\nTu turno\nPulsa enter para continuar.").encode()

    if _mesage== "": send = "\nTu rival dice: No tengo ninguna carta de esas."
    else: send = "\nJugador 1 dice: Tengo la carta " + currentCoincidence[int(_mesage)]
    turn = True
    print("Tu turno")
    send += "\nPulsa enter para continuar."
    return send.encode()


def Acuse():
    player = ""

    if turn:
        print("\nHas elegido acusar, llego el momento de jugarsela.")
        player = "1"
    else:
        connection.sendall("\nHas elegido acusar, llego el momento de jugarsela.\nPulsa enter para continuar.".encode())
        connection.recv(1024)
        player = "2"

    Ask()

    if asking == guilty: send = f"\nEl jugador {player} ha ganado. El assesino es {guilty[0]}, en la habitación {guilty[1]}, con el arma {guilty[2]}."
    else: send = f"\nEl jugador {player} ha perdido. El assesino es {guilty[0]}, en la habitación {guilty[1]}, con el arma {guilty[2]}."

    print(send)
    send +="\nPulsa enter para finalizar."
    connection.sendall(send.encode())

    connection.recv(1024)
    connection.sendall("End".encode())
    
    
    


#end region

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverAdress = ("localhost", 6004)

serverSocket.bind(serverAdress)

serverSocket.listen()

print("Se a conectado el servidor {} en el puerto {}".format(*serverAdress))

while True:
    print("Esperando cliente nuevo...")
    connection, clientAdress = serverSocket.accept()
    try:
        print("Se ha conectado el cliente ", clientAdress)
        reset()
        GetGuilty()
        connection.sendall(DealCards())
        
    
        while True:


            message = connection.recv(1024)
            message = message.decode()

            if turn:
                if Play(): Ask()
                else: 
                    Acuse()
                    break
            else:
                
                connection.sendall(Play())
                message = connection.recv(1024).decode()
                if message == "1": Ask()
                else: 
                    Acuse()
                    break
            connection.sendall(EndTurn(Answer()))

    finally:
        connection.close()