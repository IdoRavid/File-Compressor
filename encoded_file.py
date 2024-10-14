from pathlib import Path
from typing import Any


class Encoded_File:
    def __init__(self, data: bytes, binary_flag: bool, byte_length: int, file_path: Path = Path(""),
                 encoder: str = "RLE", cap_size: int = 99) -> None:
        """
        Initialize an Encoded_File object with the provided data, binary flag, byte length, file path, and encoder.

        Args:
            data (bytes): The encoded data.
            binary_flag (bool): A flag indicating whether the data is binary or not.
            byte_length (int): The length of each byte in the encoding.
            file_path (Path, optional): The file path associated with the encoded data.
            encoder (str, optional): The encoder used to encode the data (default is "RLE").
        """
        if not isinstance(data, bytes):
            raise TypeError("data is not bytes")
        self.__data = data
        if not isinstance(binary_flag, bool):
            raise TypeError("binary flag is not bool")
        self.__binary = binary_flag
        if not isinstance(byte_length, int):
            raise TypeError("byte length is not int")
        if byte_length < 0:
            raise ValueError("byte length cannot be negative")
        self.__byte_length = byte_length
        if file_path is not None:
            if not isinstance(file_path, Path):
                raise TypeError("file path is not path type")
        self.__path = file_path
        if not isinstance(encoder, str):
            raise TypeError("encoder is not string")
        self.__encoder = encoder
        if not isinstance(cap_size, int):
            raise TypeError("cap_size should be int")
        self.__cap_size = cap_size

    def __eq__(self, other:Any) -> bool:
        """
        Compare if two Encoded_File objects are equal.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if equal, False otherwise.
        """
        if isinstance(other, Encoded_File):
            if self.__data == other.__data:
                if self.__binary == other.__binary:
                    if self.__byte_length == other.__byte_length:
                        if self.__path == other.__path:
                            return True
        return False

    def is_binary(self) -> bool:
        """
        Check if the encoded data is binary.

        Returns:
            bool: True if binary, False otherwise.
        """
        return self.__binary

    def get_data(self) -> bytes:
        """
        Get the encoded data.

        Returns:
            bytes: The encoded data.
        """
        return self.__data

    def get_byte_len(self) -> int:
        """
        Get the byte length of the encoding.

        Returns:
            int: The byte length of the encoding.
        """
        return self.__byte_length

    def get_path(self) -> Path:
        """
        Get the file path associated with the encoded data.

        Returns:
            Path: The file path.
        """
        return self.__path

    def set_path(self, path: Path) -> None:
        """
        Set the file path associated with the encoded data.

        Args:
            path (Path): The file path to set.
        """
        if path is not None:
            if not isinstance(path, Path):
                raise TypeError("path is not a Path object")
        self.__path = path

    def get_encoder(self) -> str:
        """
        Get the encoder used for encoding the data.

        Returns:
            str: The encoder name.
        """
        return self.__encoder

    def get_cap_size(self) -> int:
        return self.__cap_size
