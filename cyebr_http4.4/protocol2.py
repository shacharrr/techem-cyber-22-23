import socket
import functions

class HTTPServer:
    def __init__(self, addr, hompage) -> None:
        self.conn           = socket.socket() # Temporery assignment 

        self.homepage       = hompage
        self.headline       = ""
        self.selectors      = {}
        self.body           = b""

        self.server_socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server_socket.bind(addr)
        self.server_socket.listen()


    def recv(self, buff):
        self.conn, _ = self.server_socket.accept()
        
        request_data = b""
        cdata = b""
        
        while b"\r\n\r\n" not in cdata:
            cdata = self.conn.recv(buff)
            request_data += cdata

        self.headline = request_data.split(b"\r\n")[0].decode() # Headline assignment

        for s in request_data.split(b"\r\n\r\n")[0].split(b"\r\n")[1:]: # Selectors assignment
            k, v = s.decode().split(": ")
            self.selectors[k] = v

        if "Content-Length" in self.selectors:
            size = int(self.selectors["Content-Length"])
            csize = 0
            
            while csize < size:
                cdata = self.conn.recv(buff)
                request_data += cdata
                csize += len(cdata)

            self.body = request_data.split(b"\r\n\r\n")[-1] # Body assignment


    def handle(self):
        is_function = "?" in self.headline.split()[1].split("/")[-1]
        try:
            if is_function:
                rbody = self.handle_function()
            else:
                path_access = self.headline.split()[1]  
                if path_access == "/":
                    path_access = self.homepage

                f = open(f"./{path_access}", "rb")
                rbody = f.read()
                f.close()

            self.response(rbody, 200)
        except Exception as e:
            print("Response Error:", e)
            self.response(status=404)


    def handle_function(self):
        function_call = self.headline.split()[1].split("/")[-1]
        function_name = function_call.split("?")[0]
        function_args = function_call.split("?")[-1].replace("&", " ").replace("=", " ").encode().split()[1::2]
        if self.body:
            function_args.append(self.body)

        function_args = tuple(function_args)
        return functions.function_dict[function_name](*function_args)


    def response(self, rbody=b"", status=404):
        f = open("404.html", "rb")
        response_data = b"HTTP/1.1 404 Not Found\r\n\r\n" + f.read()
        f.close()

        if status == 200:
            response_data = b"HTTP/1.1 200 OK\r\n\r\n" + rbody
        self.conn.send(response_data)


    def flush(self):
        self.headline   = ""
        self.selectors  = {}
        self.body       = b""

        self.conn.close()
        self.conn       = socket.socket()
