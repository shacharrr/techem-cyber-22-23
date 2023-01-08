def calculate_next(n):
    n = int(n.decode())
    return str(n+1).encode()

def calculate_area(h, w):
    h, w = int(h.decode()), int(w.decode())
    return str((h*w)/2).encode()

def upload(filename, filecontent):
    f = open(f"./{filename.decode()}", "wb")
    f.write(filecontent)
    f.close()
    return b""

def image(name):
    # Change path if add folder
    f = open(f"./{name.decode()}", "rb")
    image_str = f.read()
    f.close()
    return image_str

function_dict = {
    "calculate-next":   calculate_next,
    "calculate-area":   calculate_area,
    "image":            image,
    "upload":           upload,
}
