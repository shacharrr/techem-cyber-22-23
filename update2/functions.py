import socket
import random
import os
import shutil
import datetime
import subprocess
import pyautogui

def u_where():
    return (socket.gethostname(), 1)

def u_rand(n1, n2):
    return (str(random.randint(int(n1), int(n2))), 1)

def u_lsdir(dirpath):
    return (str(os.listdir(dirpath)), 1)

def u_delete(filepath):
    try:
        os.remove(filepath)
        return ("File deleted", 1)
    except:
        return ("Couldnt delete file", 1)

def u_copy(filepath1, filepath2):
    try:
        shutil.copy(filepath1, filepath2)
        return (f"{filepath1} copied to {filepath2}", 1)
    except:
        return ("Couldnt copy file", 1)

def u_time():
    return (str(datetime.datetime.now().strftime("%H:%M:%S")), 1)

def u_execute(filepath):
    # try:
    #     subprocess.call(filepath, shell=True)
    #     return ("File opened", 1)
    # except:
    #     return ("Couldnt open file", 1)
    try:
        os.startfile(filepath)
        return ("File opened", 1)
    except:
        return ("Couldnt open file", 1)

def u_screenshot():
    pyautogui.screenshot("scrnsht.png")
    return ("scrnsht.png", 2)

# Just for the list
def u_exit():
    pass

def u_list_functions():
    pass

def u_update():
    pass