import socket
    

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverAdress = ("localhost", 6004)

clientSocket.connect(serverAdress)

print("Me he conectado al servidor {} en el puerto {}".format(*serverAdress))

try:
    while True:
        messageRecived = clientSocket.recv(1024)
        messageRecived = messageRecived.decode()

        if messageRecived == "End":
            break

        a = input(messageRecived)
        if a == "":
            a = "x"
        a = a.encode()
        clientSocket.sendall(a)

        
finally:
    clientSocket.close()