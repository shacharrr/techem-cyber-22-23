import socket
import protocol
import os

IP = "localhost"
PORT = 8000
ADDR = (IP, PORT)

def client_run():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while 1:
        try:
            client_socket.connect(ADDR)
            break
        except:
            pass

    while 1:
        ret, e = protocol.recv(client_socket)
        print(ret)
        if e != -1:
            fexec = input("Choose function to exectue (name&args...)")
            protocol.send(socket=client_socket, message=fexec, data_size=len(fexec))

            if fexec == "u_exit":
                break

            fret, ferror = protocol.recv(client_socket)
            if ferror == 1:
                print(fret)
            elif ferror == 2:
                print(f"File: {fret} was recieved")

    client_socket.close()
    print("Connection was closed")
    

client_run()