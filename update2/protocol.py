import os
import time

BUFF = 1024

# Message sent/recieved - 1
# File sent/recieved - 2

def send(**kwargs):
    sender_socket = None
    message = ""
    file_path = ""
    data_size = 0

    for k, d in kwargs.items():
        if k == "socket":
            sender_socket = d
        elif k == "message":
            message = d
        elif k == "file":
            file_path = d
        elif k == "data_size":
            data_size = d


    if sender_socket == None:
        return ("Socket was not specified" -1)
    
    if message != "" and file_path != "":
        return ("Cannot send both file and a message at the same time", -1)

    if data_size == 0:
        return ("Data's size was not specified", -1)

    
    # File
    if file_path != "":
        # Check if file exists
        if not os.path.exists(file_path):
            return ("File path does not exists", -1)

        # First send if file
        try:
            sender_socket.send(str(len("protocol_send_file")).rjust(10, "0").encode())
        except Exception as e:
            return (f"Connection lost at file start, {e}", -1)

        sender_socket.send("protocol_send_file".encode())

        # File extension
        file_extension = os.path.splitext(file_path)[1]
        sender_socket.send(str(len(file_extension)).rjust(10, "0").encode())
        sender_socket.send(file_extension.encode())

        sender_socket.send(str(data_size).rjust(10, "0").encode())
        with open(file_path, "rb") as f:
            size = 0
            while size < data_size:
                current_file_data = f.read(BUFF)
                sender_socket.send(current_file_data)
                size += BUFF
        
        return (f"File: {file_path}, was successfuly sent", 2)

    # Message

    # First send if message
    try:
        sender_socket.send(str(len("protocol_send_message")).rjust(10, "0").encode())
    except Exception as e:
        return (f"Connection lost at start of message, {e}", -1)

    sender_socket.send("protocol_send_message".encode())
    sender_socket.send(str(data_size).rjust(10, "0").encode())
    sender_socket.send(message.encode())

    return (f"Message: {message}, was successfuly sent", 1)


def recv(socket, **kwargs):
    directory = "."

    for k, d in kwargs.items():
        if k == "dir":
            directory = d


    try:
        size_of_type_of_recv = int(socket.recv(10).decode())
    except Exception as e:
         return (f"Size of Type of recieve failed, {e}", -1)

    try:
        type_of_recv = socket.recv(size_of_type_of_recv).decode()
    except Exception as e:
        return (f"Type of recieve failed, {e}", -1)

    if type_of_recv == "protocol_send_file":
        try:
            extension_size = int(socket.recv(10).decode())
            extension_name = socket.recv(extension_size).decode()
        except Exception as e:
            return (f"Failed to retrieve file extension, {e}", -1)

        try:
            data_size = int(socket.recv(10).decode())
        except Exception as e:
            return (f"Data size of file failed, {e}", -1)

        file_name = f"{directory}/file_{int(time.time())}{extension_name}"
        with open(file_name, "wb") as f:
            size = 0
            while size < data_size:
                try:
                    current_file_data = socket.recv(BUFF)
                except Exception as e:
                    return ("Current File Data failed", -1)

                f.write(current_file_data)
                size += BUFF
        
        return (file_name, 2)

    elif type_of_recv == "protocol_send_message":
        try:
            data_size = int(socket.recv(10).decode())
        except Exception as e:
            return (f"Data size of message failed, {e}", -1)

        try:
            message = socket.recv(data_size).decode()
        except Exception as e:
            return (f"Message failed, {e}", -1)

        return (message, 1)
    
    else:
        print(type_of_recv)
        return ("Something unexpected happened :(", -1)