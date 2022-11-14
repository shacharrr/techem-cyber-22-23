import socket
import protocol
import functions
import os
import importlib

IP = "localhost"
PORT = 8000
ADDR = (IP, PORT)

def server_run():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(ADDR)
    server_socket.listen()

    print("[SERVER]: Established connection")

    connection_socket, connection_addr = server_socket.accept()
    print(f"[SERVER]: New connection with {connection_addr[0]}:{connection_addr[1]}")

    while 1:
        func_list = list_functions()
        protocol.send(socket=connection_socket, message=func_list, data_size=len(func_list))

        ret, e = protocol.recv(connection_socket)
        if e == -1:
            print(f"[SERVER]: {ret}")
            print(f"[SERVER]: Client {connection_addr[0]}:{connection_addr[1]} disconnected")
            connection_socket.close()

            connection_socket, connection_addr = server_socket.accept()
            print(f"[SERVER]: New connection with {connection_addr[0]}:{connection_addr[1]}")

        elif e == 1:
            # Handle args an execute functions
            if len(ret.split("&")) > 1:
                rsplit = ret.split("&")
                args = tuple(rsplit[1:])
                try:
                    fret, ferror = getattr(functions, rsplit[0])(*args)
                except Exception as e:
                    fret, ferror = (f"Couldnt execute {rsplit[0]}, {e}", 1)
            else:
                if ret == "u_exit":
                    connection_socket.close()
                    continue
                elif ret == "u_update":
                    fret, ferror = update()
                else:
                    try:
                        fret, ferror = getattr(functions, ret)()
                    except Exception as e:
                        fret, ferror = (f"Couldnt execute {ret}, {e}", 1)

            # Handle return types
            if ferror == 1:
                protocol.send(socket=connection_socket, message=fret, data_size=len(fret))
            elif ferror == 2:
                filesize = os.path.getsize(fret)
                protocol.send(socket=connection_socket, file=fret, data_size=filesize)


def list_functions():
    s = ""
    for f in dir(functions):
        if f.startswith("u_"):
            s += f"\n{f}"

    return s

def update():
    importlib.reload(functions)
    importlib.reload(protocol)
    return ("Protocol && Functions has been reloaded", 1)

server_run()