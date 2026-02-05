"""
INetSerializable.cs translation

Interface for serializable objects
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .net_data_reader import NetDataReader
    from .net_data_writer import NetDataWriter


class INetSerializable(ABC):
    """
    Interface for objects that can be serialized/deserialized

    C# interface: public interface INetSerializable
    """

    @abstractmethod
    def serialize(self, writer: "NetDataWriter") -> None:
        """
        Serialize object to binary data

        C# method: void Serialize(NetDataWriter writer)
        """
        pass

    @abstractmethod
    def deserialize(self, reader: "NetDataReader") -> None:
        """
        Deserialize object from binary data

        C# method: void Deserialize(NetDataReader reader)
        """
        pass


__all__ = ["INetSerializable"]
