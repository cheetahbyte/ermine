
from enum import Enum

class ConnectionType(Enum):
    """This enum is used to represent the connection type"""
    http: str = "http"
    ws: str = "websocket"