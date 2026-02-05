"""
NetDebug.cs translation

Static class for defining your own LiteNetLib logger instead of Console.WriteLine
or Debug.Log if compiled with UNITY flag
"""

import threading
from enum import IntEnum
from typing import Callable, Optional, Any


class NetLogLevel(IntEnum):
    """
    Log levels

    C# enum: NetLogLevel
    """

    Warning = 0
    Error = 1
    Trace = 2
    Info = 3


class InvalidPacketException(Exception):
    """
    Exception for invalid packets

    C# class: public class InvalidPacketException : ArgumentException
    """

    pass


class TooBigPacketException(InvalidPacketException):
    """
    Exception for packets that are too large

    C# class: public class TooBigPacketException : InvalidPacketException
    """

    pass


class INetLogger:
    """
    Interface to implement for your own logger

    C# interface: public interface INetLogger
    """

    def write_net(self, level: NetLogLevel, message: str, *args: Any) -> None:
        """
        Write log message

        C# method: void WriteNet(NetLogLevel level, string str, params object[] args)
        """
        raise NotImplementedError


class NetDebug:
    """
    Static class for debug logging

    C# class: public static class NetDebug
    """

    Logger: Optional[INetLogger] = None
    _debug_log_lock = threading.Lock()
    _debug_messages_enabled: bool = False  # Set via environment or compile-time flag

    @classmethod
    def enable_debug_messages(cls, enabled: bool = True):
        """Enable or disable debug messages"""
        cls._debug_messages_enabled = enabled

    @classmethod
    def _write_logic(cls, log_level: NetLogLevel, message: str, *args: Any) -> None:
        """
        Internal write logic with thread safety

        C# method: private static void WriteLogic(NetLogLevel logLevel, string str, params object[] args)
        """
        with cls._debug_log_lock:
            if cls.Logger is None:
                # Default to print (equivalent to Console.WriteLine)
                if args:
                    print(message % args)
                else:
                    print(message)
            else:
                cls.Logger.write_net(log_level, message, *args)

    @classmethod
    def write(cls, message: str, *args: Any) -> None:
        """
        Write trace message (only if DEBUG_MESSAGES is enabled)

        C# method: [Conditional("DEBUG_MESSAGES")] internal static void Write(string str, params object[] args)
        """
        if cls._debug_messages_enabled:
            cls._write_logic(NetLogLevel.Trace, message, *args)

    @classmethod
    def write_with_level(cls, level: NetLogLevel, message: str, *args: Any) -> None:
        """
        Write message with specific level (only if DEBUG_MESSAGES is enabled)

        C# method: [Conditional("DEBUG_MESSAGES")] internal static void Write(NetLogLevel level, string str, params object[] args)
        """
        if cls._debug_messages_enabled:
            cls._write_logic(level, message, *args)

    @classmethod
    def write_force(cls, message: str, *args: Any) -> None:
        """
        Write trace message forcefully (only if DEBUG or DEBUG_MESSAGES is enabled)

        C# method: [Conditional("DEBUG_MESSAGES"), Conditional("DEBUG")] internal static void WriteForce(string str, params object[] args)
        """
        if cls._debug_messages_enabled:
            cls._write_logic(NetLogLevel.Trace, message, *args)

    @classmethod
    def write_force_with_level(cls, level: NetLogLevel, message: str, *args: Any) -> None:
        """
        Write message with level forcefully (only if DEBUG or DEBUG_MESSAGES is enabled)

        C# method: [Conditional("DEBUG_MESSAGES"), Conditional("DEBUG")] internal static void WriteForce(NetLogLevel level, string str, params object[] args)
        """
        if cls._debug_messages_enabled:
            cls._write_logic(level, message, *args)

    @classmethod
    def write_error(cls, message: str, *args: Any) -> None:
        """
        Write error message (always written)

        C# method: internal static void WriteError(string str, params object[] args)
        """
        cls._write_logic(NetLogLevel.Error, message, *args)


__all__ = [
    "NetLogLevel",
    "InvalidPacketException",
    "TooBigPacketException",
    "INetLogger",
    "NetDebug",
]
