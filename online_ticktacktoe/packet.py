import pickle
from enum import Enum


def IntToHexBytes(number: int) -> bytes:
    base = hex(number)
    return f"{base[:2]}{'0' * (10 - len(base))}{base[2:]}".encode()


def HexBytesToInt(hex_bytes: bytes) -> int:
    return int(hex_bytes.decode(), 16)


class PacketType(Enum):
    CreateServerRequest = 0
    CreateServerResponse = 1
    JoinServerRequest = 2
    JoinServerResponse = 3
    GameSendState = 4
    GameResetState = 5
    LeaveServerRequest = 6
    LeaveServerResponse = 7
    GameChatMessage = 8


class Packet:
    def __init__(
        self,
        Sender: str | None = None,
        SubPort: int | None = None,
        Type: PacketType | None = None,
        Data=None,
    ):
        self.Sender = Sender
        self.SubPort = SubPort
        self.Type = Type
        self.Data = Data

    def Serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def Deserialize(ByteStream):
        obj = pickle.loads(ByteStream)
        return obj

    # Debug
    def __str__(self) -> str:
        return f"Sender: {self.Sender}\nSubPort: {self.SubPort}\nType: {self.Type}\n Data: {self.Data}\n"
