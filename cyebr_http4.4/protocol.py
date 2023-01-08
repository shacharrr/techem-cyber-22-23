##### Use protocol2 for better codebase #####
import socket
import functions

class HTTPServer:
    def __init__(self, addr: tuple, homepage: str) -> None:
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server_socket.bind(addr)
        self.server_socket.listen()

        self.request_data = b""
        self.conn = socket.socket()
        self.homepage = homepage
        self.selectors = {}

    def recv_request(self):
        self.conn, _ = self.server_socket.accept()
        self.request_data = b""
        self.selectors = {}

        BUFF = 2048 
        cdata = self.conn.recv(BUFF)
        while cdata:
            if b"\r\n\r\n" in cdata:
                self.request_data += cdata
                break
            self.request_data += cdata
            cdata = self.conn.recv(BUFF)

        for s in self.request_data.split(b"\r\n\r\n")[0].split(b"\r\n")[1:]:
            k,v = s.split(b": ")
            self.selectors[k] = v

        if b"Content-Length" in self.selectors:
            fsize = int(self.selectors[b"Content-Length"])
            csize = 0
            while csize < fsize:
                cdata = self.conn.recv(BUFF)
                self.request_data += cdata 
                csize += len(cdata)

    def handle_request(self):
        headline = self.request_data.split(b"\r\n")[0].decode()
        
        # <Method> <URL> <HTTP Version>
        print(headline)
        
        type_of_request = headline.split()[0]
         
        if type_of_request == "GET":
            self.handle_get(headline)
        elif type_of_request == "POST":
            self.handle_post(headline, self.request_data.split(b"\r\n\r\n")[-1])
        else:
            # Handle later
            pass

    def handle_get(self, headline):
        path_access = headline.split()[1]
        if path_access == "/":
            self.send_response(self.homepage)
            return

        if "?" in path_access.split("/")[-1]:
            function_call = path_access.split("/")[-1]
            function_name = function_call.split("?")[0]
            function_args = tuple(function_call.split("?")[-1].replace("&", " ").replace("=", " ").split()[1::2])

            self.send_response(function_name, True, tuple(function_args))
            return

        self.send_response(path_access)

    def handle_post(self, headline, content):
        path_access = headline.split()[1]

        function_call = path_access.split("/")[-1]
        function_name = function_call.split("?")[0]
        function_head_args = tuple(function_call.split("?")[-1].replace("&", " ").replace("=", " ").split()[1::2])

        functions.function_dict[function_name](*function_head_args, content)
        self.send_response(post=True)

    def send_response(self, path_access="", get_function=False, function_args=None, post=False):
        f = open("404.html", "rb")
        body = f.read()
        response_data = b"HTTP/1.1 404 Not Found\r\n\r\n" + body 
        f.close()

        if post:
            response_data = b"HTTP/1.1 200 OK\r\n\r\n"
        else:   
            try:
                if get_function:
                    body = functions.function_dict[path_access](*function_args)
                else:
                    f = open(f"./{path_access}", "rb")
                    body = f.read()
                    f.close()

                response_data = b"HTTP/1.1 200 OK\r\n\r\n" + body
            except Exception as e:
                    print("Response Error: ", e)

        self.conn.send(response_data)

    def close_request(self):
        self.conn.close()


