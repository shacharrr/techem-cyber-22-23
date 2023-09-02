import socket
from threading import Lock
from packet import HexBytesToInt, IntToHexBytes, Packet, PacketType
from game import TickTackToe
import os

BUFFER = 1024

class Client:
    def __init__(self, name=""):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = name
        self.lock = Lock()

        self.game = None

    def connect(self, addr: tuple):
        connected = False
        while not connected:
            try:
                self.client.connect(addr)
                connected = True
            except:
                pass

    def recv(self):
        while True:
            try:
                data_length = self.client.recv(10)

                packet_size = HexBytesToInt(data_length)
                current_size = 0
                packet_data = b""
                while current_size < packet_size:
                    packet_data += self.client.recv(BUFFER)
                    current_size += BUFFER
            except:
                print("Lost connection to the server, closing (You may reopen the game to check if the server up again)")
                self.crash_safely()

            pkt = Packet.Deserialize(packet_data)

            match pkt.Type:
                case PacketType.CreateServerResponse:
                    if int(pkt.Data) == -1:
                        continue

                    self.game = TickTackToe(pkt.Data, True)

                case PacketType.JoinServerResponse:
                    if int(pkt.Data) == -1:
                        continue

                    self.game = TickTackToe(pkt.Data, False)

                case PacketType.JoinServerRequest:
                    self.game.is_startable = True

                case PacketType.GameSendState:
                    self.game.is_over = pkt.Data.is_over
                    self.game.board = pkt.Data.board
                    self.game.won = pkt.Data.won
                    self.game.is_turn = True

                case PacketType.GameResetState:
                    self.game.reset(self.name)
                    self.game.is_over = False

                case PacketType.LeaveServerRequest:
                    self.game.is_over = True
                    self.game.is_startable = False
                    self.game.is_game_owner = True
                    self.game.reset(self.name)

                case PacketType.LeaveServerResponse:
                    self.game = None

                case PacketType.GameChatMessage:
                    self.game.game_chat.append(pkt.Data)

                case _:
                    raise Exception("Oops, you did something wrong!")

            ## Continue

    def crash_safely(self):
        if self.game != None:
            self.send(Packet(Type=PacketType.LeaveServerRequest, Data=self.game.game_code))
        os._exit(0)

    def send(self, packet: Packet):
        self.lock.acquire()
        sp = packet.Serialize()
        self.client.sendall(IntToHexBytes(len(sp)))
        self.client.sendall(sp)
        self.lock.release()
