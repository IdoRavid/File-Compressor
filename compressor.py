from pathlib import Path
from typing import Optional,  Union
from io import StringIO
from encoded_file import *

# get base path of project. needed for all tests.
CODE_BASE_PATH = Path(__file__).parent.resolve()
TEST_BASE_PATH = CODE_BASE_PATH / "tests"



# region Compressor Classes

class Compressor:
    """the compressor class is the base class for the compressing algorithms.
    it holds little functionality and is mainly used for inheriting method & decorators """

    def __init__(self, name: str) -> None:
        self.__name = name

    def get_name(self) -> str:
        return self.__name

    def encode(self, text: Union[str, bytes], file_name: str = "", byte_size: int = 5, cap_size: int = 99) -> Encoded_File:
        """ the Encode function manages basic type & value validation, and calls
        the relevant encoding function, based on params."""

        if not isinstance(text, str) and not isinstance(text, bytes):
            raise TypeError("Text is not String or bytes")
        if not isinstance(byte_size, int):
            raise TypeError("Byte Size is not a number")
        if byte_size <= 0:
            raise ValueError("Byte Size should be a positive integer")
        if cap_size <= 0:
            raise ValueError("Cap Size should be a positive integer")
        if not isinstance(file_name, str):
            raise TypeError
        if len(text) == 0:
            raise ValueError("Empty textfile")

        # if we're encoding binary files - call binary encode
        if isinstance(text, bytes):
            return self.binary_encode(text, byte_size, file_name, cap_size)
        else:  # else call string encode
            return self.string_encode(text, byte_size, file_name, cap_size)

    def decode(self, archive: Encoded_File) -> Union[Optional[str], Optional[None], Optional[int], Optional[bytes]]:
        """similar to the Encode function, the Decode function calls the relevant specific decode method."""
        if archive.is_binary():
            return self.binary_decode(archive)
        else:
            return self.string_decode(archive)

    # the four following functions are empty in this class, and used only for order's sake.
    # they are all overridden in the child classes
    def binary_encode(self, text: bytes, byte_size: int, file_name: str, cap_size: int = 99) -> Encoded_File:
        return Encoded_File(b"", False, 0, Path("-"))

    def string_encode(self, text: str, byte_size: int, file_name: str, cap_size: int = 99) -> Encoded_File:
        return Encoded_File(b"", False, 0, Path(""))

    def binary_decode(self, encoded_file: Encoded_File) -> Optional[bytes]:
        pass

    def string_decode(self, encoded_file: Encoded_File) -> Optional[str]:
        pass


class RLE_Compressor(Compressor):
    """The RLE compressor function is a type of Compressor, which uses the Run Length Encoding
    Algorithm.The class overrides the encoding & decoding of the parent class, and implements the
    algorithm."""

    def __init__(self) -> None:
        super().__init__("RLE")

    def binary_encode(self, text: bytes, byte_size: int, file_name: str, cap_size: int = 99) -> Encoded_File:
        """Method to encode bytes using binary encoding.
        The function iterates
        over the bytes, and finds lengths of recurring values,
        it stores the amount of recurrence, and then the value in a new string
        finally, it returns the new string"""
        encoding = b''  # bytes encoding
        i = 0
        while i < len(text):  # iterating over the text indices
            count = 1
            # find recurring characters
            while (i + count * byte_size < len(text) and (len(text) - (i + count * byte_size)) > byte_size and
                   text[i: i + byte_size] == text[i + count * byte_size: i + (count + 1) * byte_size]):
                count += 1
            # if we're over the given byte size, store data as the max byte,
            total_count = count
            while count > cap_size:
                encoding += str(cap_size).encode('utf-8') + (text[i:i + byte_size])
                count -= cap_size  # retry after removing n bytes from the counter
            padding = "0" * (len(str(cap_size)) - len(str(count)))
            byte_padding = padding.encode('utf-8')
            encoding += byte_padding + str(count).encode('utf-8') + (text[i:i + byte_size])
            i += byte_size * total_count
        # return the data encoded as an archive instance
        return Encoded_File(encoding, True, byte_size, Path(file_name), self.get_name(), cap_size)

    def string_encode(self, text: str, byte_size: int, file_name: str, cap_size: int = 99) -> Encoded_File:
        """the string encode is similar to the byte encode, only using strings"""
        encoding = ''
        i = 0
        # iterating over string indices
        while i < len(text):
            count = 1
            # as long as there are recurrences, add to counter
            while (i + count * byte_size < len(text) and (len(text) - (i + count * byte_size)) > byte_size and
                   text[i: i + byte_size] == text[i + count * byte_size: i + (count + 1) * byte_size]):
                count += 1
            # if we've reached the byte size limit, store in byte-size and remove from counter
            total_count = count
            while count >= cap_size:
                encoding += str(cap_size) + text[i: i + byte_size]
                count -= cap_size
            # add new data to encoded string
            run_length_size = len(str(cap_size))
            encoding += "0" * (run_length_size - len(str(count))) + str(count) + text[i:i + byte_size]
            i += byte_size * total_count
        # turn string to bytes:
        byte_string = encoding.encode('utf-8')
        # return the data encoded as an archive instance
        return Encoded_File(byte_string, False, byte_size, Path(file_name), self.get_name(), cap_size)

    def binary_decode(self, encoded_file: Encoded_File) -> Optional[bytes]:
        """the binary decoding is basically the opposite function of the binary encode.
        it receives an archive file, and it recreates the original bytes string
        using the byte_length stored in the archive instance."""
        i = 0
        # get the byte len & cap size from the encoded file
        byte_len = encoded_file.get_byte_len()
        cap_size = encoded_file.get_cap_size()
        # calculate it's size in the encoded string
        indicator_size = len(str(cap_size))
        decoded_text = b''
        # get encoded string
        text = encoded_file.get_data()
        # iterate on string indices
        while i < len(text):
            # get the current run-length count
            count = int((text[i:i + indicator_size]).decode('utf-8'))
            # get the current character_string
            char = text[i + indicator_size:i + indicator_size + byte_len]
            # add their product to the decoded text
            decoded_text += char * count
            # go to next run_length_count
            i += indicator_size + byte_len
        return decoded_text

    def string_decode(self, encoded_file: Encoded_File) -> Optional[str]:
        """the string decoding is basically the opposite function of the string encode.
               it receives an archive file, and it recreates the original string
               using the byte_length stored in the archive instance."""
        # get the byte len from the archive
        byte_len = encoded_file.get_byte_len()
        cap_size = encoded_file.get_cap_size()
        # calculate it's size in the encoded string
        indicator_size = len(str(cap_size))
        decoded_text = ''
        i = 0
        # get encoded bytes
        byte_text = encoded_file.get_data()
        # turn bytes to encoded string
        text = byte_text.decode('utf-8')
        # iterate on string indices
        while i < len(text):
            # get the current run-length count
            run_length = int(text[i:i + indicator_size])
            # add to decoded text the counter times the character
            decoded_text += str(
                (int(run_length)) * (text[i + int(indicator_size): i + int(indicator_size) + byte_len]))
            i += indicator_size + byte_len
        return decoded_text


# endregion

# region LZW compressor

class LZW_Compressor(Compressor):
    def __init__(self) -> None:
        super().__init__("LZW")

    def string_encode(self, text: str, byte_size: int, file_name: str, cap_size: int = 99) -> Encoded_File:
        """
        Encode a string into an encoded file using the standard LZW algorithm.

        Parameters:
        - text: The text to be encoded.
        - byte_size: Irrelevant - used only in RLE.
        - file_name: The name of the file.
        - cap_size: Irrelevant - used only in RLE.

        Returns:
        An instance of Encoded_File representing the encoded file.
        """

        # First, build the dictionary with keys ranging from 1 to 256,
        # each key representing a single character in the text.
        dict_size = 256
        dictionary = dict((chr(i), i) for i in range(dict_size))

        # Initialize parameters
        current_string = ""
        result = []

        # Iterate over the text
        for char in text:
            # Add the current char to the current string
            concat_string = current_string + char

            # Check if the concatenated string is already in the dictionary
            if concat_string in dictionary:
                # Set the current string to the concatenated string
                current_string = concat_string
            else:
                # Add the code for the current string to the result
                result.append(dictionary[current_string])

                # Add the concatenated string to the dictionary
                dictionary[concat_string] = dict_size
                dict_size += 1

                # Reset the current string to the current character
                current_string = char

        # If the current string is not empty, append its code to the result
        if current_string:
            result.append(dictionary[current_string])

        # Convert the result list to a string, separating values with '~'
        result_str = ""
        for item in result:
            result_str += str(item)
            result_str += '~'

        # Create an encoded file using UTF-8 encoding of the result
        return Encoded_File(result_str.encode('utf-8'), False, byte_size, Path(file_name), self.get_name(), cap_size)

    def string_decode(self, encoded_file: Encoded_File) -> Optional[str]:
        """
        Decode an encoded file using the standard LZW algorithm.

        Parameters:
        - encoded_file: The encoded file to be decoded.

        Returns:
        The decompressed content of the file as a string.
        """

        # Recreate the compressed list of integers from the encoded file data
        compressed_str = (encoded_file.get_data().decode('utf-8')).split("~")[:-1]
        compressed = [int(x) for x in compressed_str]

        # Create a dictionary
        dict_size = 256
        dictionary = dict((i, chr(i)) for i in range(dict_size))

        # StringIO is used for efficiency
        result = StringIO()

        current_string = chr(compressed.pop(0))
        result.write(current_string)

        # Iterate over the compressed list
        for char in compressed:
            # For each compressed character in the list
            if char in dictionary:
                # If it has a corresponding value in the dictionary, retrieve it
                entry = dictionary[char]
            elif char == dict_size:
                # If it doesn't have a value in the dictionary, create a new entry
                entry = current_string + current_string[0]
            else:
                # Raise an error for invalid compressed character
                raise ValueError('Bad compressed char: %s' % char)

            # Write the entry to the result
            result.write(entry)

            # Add the combination of current_string and entry[0] to the dictionary
            dictionary[dict_size] = current_string + entry[0]
            dict_size += 1

            # Set current_string to the entry for the next iteration
            current_string = entry

        # Get the decoded string from the result
        return result.getvalue()

    def binary_encode(self, text: bytes, byte_size: int, file_name: str, cap_size: int = 99) -> Encoded_File:
        """
        Encode a byte string into an encoded file using the standard LZW algorithm.

        Parameters:
        - text: The byte string to be encoded.
        - byte_size: The size of each byte.
        - file_name: The name of the file.
        - cap_size: Irrelevant - used only in RLE.

        Returns:
        An instance of Encoded_File representing the encoded file.
        """

        # Build the dictionary with keys ranging from 1 to 256,
        # each key representing a single byte in the text.
        dict_size = 256
        dictionary = {bytes([i]): i for i in range(dict_size)}

        # Initialize parameters
        current_bytes = b""
        result = []

        # Iterate over the bytes
        for byte in text:
            # Add the current byte to the current bytes
            concat_bytes = current_bytes + bytes([byte])

            # Check if the concatenated bytes are already in the dictionary
            if concat_bytes in dictionary:
                # Set the current bytes to the concatenated bytes
                current_bytes = concat_bytes
            else:
                # Add the code for the current bytes to the result
                result.append(dictionary[current_bytes])

                # Add the concatenated bytes to the dictionary
                dictionary[concat_bytes] = dict_size
                dict_size += 1

                # Reset the current bytes to the current byte
                current_bytes = bytes([byte])

        # If the current bytes are not empty, append their code to the result
        if current_bytes:
            result.append(dictionary[current_bytes])

        # Convert the result list to bytes and concatenate with '~' separator
        result_bytes = b"".join(str(item).encode('utf-8') + b"~" for item in result)

        # Create an encoded file using the result bytes
        return Encoded_File(result_bytes, True, byte_size, Path(file_name), self.get_name(), cap_size)

    def binary_decode(self, encoded_file):
        # type: (Encoded_File) -> bytes
        """
        Decode an encoded file with binary content, using the standard LZW algorithm.

        Parameters:
        - encoded_file: The encoded file to be decoded.

        Returns:
        The decompressed content of the file as a byte string.
        """

        # Recreate the compressed list of integers from the encoded file data
        compressed_str = encoded_file.get_data().split(b"~")[:-1]
        compressed = [int(x.decode('utf-8')) for x in compressed_str]

        # Build the dictionary with keys ranging from 1 to 256,
        # each key representing a single byte in the text.
        dict_size = 256
        dictionary = {i: bytes([i]) for i in range(dict_size)}

        # Initialize result as a byte string
        result = bytearray()

        # Initialize current_string as a byte
        current_string = bytes([compressed.pop(0)])
        result.extend(current_string)

        # Iterate through the compressed list
        for char in compressed:
            # For each compressed character in the list
            if char in dictionary:
                # If it has a corresponding value in the dictionary, retrieve it
                entry = dictionary[char]
            elif char == dict_size:
                # If it doesn't have a value in the dictionary, create a new entry
                entry = current_string + bytes([current_string[0]])
            else:
                # Raise an error for invalid compressed character
                raise ValueError('Bad compressed char: %s' % char)

            # Append entry to the result
            result.extend(entry)

            # Add the combination of current_string and entry[0] to the dictionary
            dictionary[dict_size] = current_string + bytes([entry[0]])
            dict_size += 1

            # Set current_string to the entry for the next iteration
            current_string = entry

        # Get the decoded byte string from the result
        return bytes(result)

# endregion
