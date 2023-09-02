import socket
from threading import Thread
from packet import HexBytesToInt, IntToHexBytes, Packet, PacketType

BUFFER = 1024


def UniqueGameCode(game_codes, MAXID):
    if len(game_codes) < 1:
        return 0

    i = 0
    while i <= MAXID:
        if i not in game_codes:
            return i
        i += 1
    return -1


class Server:
    def __init__(self, addr: tuple):
        self.addr = addr
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.addr)
        self.server.listen()

        self.games = {}

        # Control Panel
        self.run = True

    def accept_loop(self):
        while self.run:
            client, _ = self.server.accept()
            Thread(target=self.client_loop, args=(client,)).start()

    def client_loop(self, client: socket.socket):
        while self.run:
            try:
                data_length = client.recv(10)

                packet_size = HexBytesToInt(data_length)
                current_size = 0
                packet_data = b""
                while current_size < packet_size:
                    packet_data += client.recv(BUFFER)
                    current_size += BUFFER
            except:
                print(f"Client: {client} has disconnected/lost connection")
                client.close()
                break

            pkt: Packet = Packet.Deserialize(packet_data)

            match pkt.Type:
                case PacketType.CreateServerRequest:
                    game_code = str(UniqueGameCode([int(k) for k in self.games], 64))
                    game_code = f"{'0'*(4-len(game_code))}{game_code}"
                    if int(game_code) != -1:
                        self.games[f"{'0'*(4-len(game_code))}{game_code}"] = [client]

                    rpkt = Packet(Type=PacketType.CreateServerResponse, Data=game_code).Serialize()

                    client.sendall(IntToHexBytes(len(rpkt)))
                    client.sendall(rpkt)

                case PacketType.JoinServerRequest:
                    rgc = pkt.Data
                    if rgc not in self.games or len(self.games[rgc]) > 1:
                        rpkt = Packet(Type=PacketType.JoinServerResponse, Data=-1).Serialize()
                    else:
                        self.games[rgc].append(client)
                        tpkt = Packet(Type=PacketType.JoinServerRequest).Serialize()
                        self.games[rgc][0].sendall(IntToHexBytes(len(tpkt)))
                        self.games[rgc][0].sendall(tpkt)

                        rpkt = Packet(Type=PacketType.JoinServerResponse, Data=rgc).Serialize()

                        client.sendall(IntToHexBytes(len(rpkt)))
                        client.sendall(rpkt)
                
                case PacketType.GameSendState | PacketType.GameResetState | PacketType.GameChatMessage:
                    rpkt = pkt.Serialize()

                    for c in self.games[pkt.SubPort]:
                        if c == client:
                            continue
                        c.sendall(IntToHexBytes(len(rpkt)))
                        c.sendall(rpkt)

                case PacketType.LeaveServerRequest:
                    rgc = pkt.Data

                    if len(self.games[rgc]) > 1:    
                        self.games[rgc].remove(client)
                        tpkt = Packet(Type=PacketType.LeaveServerRequest).Serialize()
                        self.games[rgc][0].sendall(IntToHexBytes(len(tpkt)))
                        self.games[rgc][0].sendall(tpkt)
                    else:
                        del self.games[rgc]

                    rpkt = Packet(Type=PacketType.LeaveServerResponse).Serialize()
                    client.sendall(IntToHexBytes(len(rpkt)))
                    client.sendall(rpkt)


                case _:
                    raise Exception("Oops, you did something wrong!")


# server = Server(("localhost", 9999))
server = Server(("localhost", 9999))
server.accept_loop()
