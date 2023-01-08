from protocol2 import HTTPServer

if __name__ == "__main__":
    h = HTTPServer(("localhost", 8800), "index.html")
    while True:
        h.recv(2048)
        h.handle()
        h.flush()
