import sys
from pathlib import Path
from typing import Any, Optional, Union
from bcrypt import checkpw, hashpw, gensalt
from encoded_file import Encoded_File


class Archive:
    def __init__(self, encoded_files: list[Encoded_File], password: Any = None):
        """
        Initialize an Archive object with a list of encoded files and an optional password.

        Args:
            encoded_files (list[Encoded_File]): A list of encoded files.
            password (Any, optional): An optional password for the archive.
        """
        # set values to instance
        self.__hashed_password = b"0"
        self.__encoded_file_list = encoded_files
        if isinstance(password, bytes):
            self.__hashed_password = password
        else:
            if password is not None and password != "":
                # if there is a password - hash it, and store it
                self.__hashed_password = hash_password(password)
        self.__password_protected = bool(password is not None)
        if not isinstance(encoded_files, list):
            raise TypeError("files should be in a list")

    def __eq__(self, other: Any) -> bool:
        """
        Compare if two Archive objects are equal.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if equal, False otherwise.
        """
        if not isinstance(other, Archive):
            return False
        equal_bool = True
        # check each file in the other archive is the same
        for file in enumerate(self.__encoded_file_list):
            if file[1] != other.__encoded_file_list[file[0]]:
                equal_bool = False
                break
        # check passwords are the same
        if equal_bool:
            if self.__hashed_password == other.__hashed_password:
                return True
        return False

    def is_protected(self) -> bool:
        """
        Check if the archive is password protected.

        Returns:
            bool: True if protected, False otherwise.
        """
        return self.__password_protected

    def check_password(self, password_try: Any) -> bool:
        """
        Check if the provided password is correct.

        Args:
            password_try (str): The password to check.

        Returns:
            bool: True if the password is correct, False otherwise.
        """
        if password_try is None and self.is_protected():
            return False
        elif password_try is None and not self.is_protected():
            return True
        pwd_bytes = password_try.encode("utf-8")
        return checkpw(pwd_bytes, self.__hashed_password)

    def get_encoded_files_list(self) -> list[Encoded_File]:
        """
        Get the list of encoded files in the archive.

        Returns:
            list[Encoded_File]: A list of Encoded_File objects.
        """
        return self.__encoded_file_list

    def get_hashed_password(self) -> Any:
        """
        Get the hashed password of the archive.

        Returns:
            Optional[bytes]: The hashed password or None if not password protected.
        """
        return self.__hashed_password

    def add_to_archive(self, new_file: Union[list[Encoded_File], Encoded_File]) -> None:
        """
        Add one or more files to the archive.

        Args:
            file (Union[list[Encoded_File], Encoded_File]): The file or list of files to add to the archive.
            :param new_file:
        """
        current_file_paths = []
        # create a file paths list
        for file in self.get_encoded_files_list():
            current_file_paths.append(file.get_path())
        # check each item in the list is encoded
        if isinstance(new_file, Encoded_File):
            # if the file is already in the archive, delete the current one and replace it
            if new_file.get_path() in current_file_paths:
                for current_file in self.get_encoded_files_list():
                    if current_file.get_path() == new_file.get_path():
                        self.__encoded_file_list.remove(current_file)
            # add new file to list
            self.__encoded_file_list.append(new_file)
        # if the args is a list, do the same for each item.
        elif isinstance(new_file, list):
            for sub_file in new_file:
                if isinstance(sub_file, Encoded_File):
                    if sub_file.get_path() in current_file_paths:
                        for current_file in self.get_encoded_files_list():
                            if current_file.get_path() == sub_file.get_path():
                                self.__encoded_file_list.remove(current_file)
                    self.__encoded_file_list.append(sub_file)

    def get_archive_contents(self) -> str:
        files = self.get_encoded_files_list()
        paths = []
        for file in files:
            paths.append(file.get_path())
        sorted_paths = sorted(paths)

        numbered_paths = []
        counter = 1
        for path in sorted_paths:
            numbered_paths.append(str(counter) + str(" - ") + str(path))
            counter += 1

        path_string = ''.join(str(x) + '\n' for x in numbered_paths)
        return '\n' + path_string

    def delete_files_from_archive(self, file_numbers: Union[list[str], list[int]]) -> bool:
        for file_number in file_numbers:
            if int(file_number) > len(self.get_encoded_files_list()) or int(file_number) < 1:
                return False
        else:
            paths = []
            paths_to_delete = []
            for file in self.get_encoded_files_list():
                paths.append(file.get_path())
            sorted_paths = sorted(paths)
            for file_number in file_numbers:
                paths_to_delete.append(sorted_paths[int(file_number) - 1])

            new_encoded_files = [file for file in self.get_encoded_files_list() if
                                 file.get_path() not in paths_to_delete]
            self.__encoded_file_list = new_encoded_files
            return True

    def get_size(self) -> int:
        """
        Get the size of the encoded file.

        Returns:
            int: The size of the encoded file in bytes.
        """
        return sys.getsizeof(self)


def hash_password(password: Any) -> Any:
    """
    Hash a password using bcrypt.

    Args:
        password: The password to hash.

    Returns:
        bytes: The hashed password.
    """
    if password is None:
        return
    else:
        pwd_bytes = password.encode("utf-8")
        salt = gensalt()
        return hashpw(pwd_bytes, salt)


def write_archive(path: Path, archive: Archive) -> None:
    """
    this function writes the archive instance to a file, using a predefined structure
    :param path: the new file path to write to
    :param archive:  the archive file
    :return: None
    """
    with open(path, 'wb') as file:
        # Write hashed password if exists
        if archive.is_protected():
            file.write((archive.get_hashed_password()))
        else:
            file.write(b'\x00' * 60)  # Write 60 null bytes to indicate no password

        # Write encoded files data, binary flags, byte lengths and path
        # after each data type - add a delimiter
        for encoded_file in archive.get_encoded_files_list():
            data = encoded_file.get_data()
            file.write(data + b'x\\\\x')  # Write encoded file data
            file.write(str(int(encoded_file.is_binary())).encode('utf-8') + b'x\\\\x')  # Write binary flag
            file.write(str(encoded_file.get_byte_len()).encode('utf-8') + b'x\\\\x')  # Write byte length
            file.write(str(encoded_file.get_path()).encode('utf-8') + b'x\\\\x')  # Write path
            file.write(encoded_file.get_encoder().encode('utf-8') + b'x\\\\x')  # Write encoder
            file.write(str(encoded_file.get_cap_size()).encode('utf-8') + b'x\\\\x')  # Write cap_size


def read_archive(path: Path) -> Archive:
    """
    this function reads an .ido file from a path, and returns an archive instance
    :param path: archive_file path
    :return: archive
    """
    encoded_files = []
    password_protected = False
    # read file in binary
    with open(path, 'rb') as file:
        # Read hashed password if exists
        hashed_password = file.read(60)  # Assuming password hash length is 64 bytes
        if hashed_password != b'\x00' * 60:  # Check if a hashed password exists
            password_protected = True

        # Read encoded files data, binary flags, byte lengths, and paths
        combined_line = b''.join(file.readlines())
        encoded_file_chunks = combined_line.split(b'x\\\\x')[:-1]  # Remove last empty element

        # Split the combined line using the delimiter b'x\\\\x'
        for i in range(0, len(encoded_file_chunks), 6):  # Each encoded file consists of 5 parts
            encoded_file_data = encoded_file_chunks[i]
            binary_flag_data = encoded_file_chunks[i + 1]
            byte_length_data = encoded_file_chunks[i + 2]
            path_data = encoded_file_chunks[i + 3]
            encoder_data = encoded_file_chunks[i + 4]
            cap_size_data = encoded_file_chunks[i + 5]
            # Convert data to appropriate types
            binary_flag = bool(int(binary_flag_data.decode('utf-8')))
            byte_length = int(byte_length_data.decode('utf-8'))
            path = Path(path_data.decode('utf-8'))
            encoder = encoder_data.decode('utf-8')
            cap_size = int(cap_size_data.decode('utf-8'))
            # Append the encoded file
            encoded_files.append(Encoded_File(encoded_file_data, binary_flag, byte_length, path, encoder, cap_size))
    # Return the archive, with or without the password
    if password_protected:
        return Archive(encoded_files, hashed_password)
    else:
        return Archive(encoded_files, None)


class DecryptError(Exception):
    def __init__(self, message: str = "WRONG PASSWORD") -> None:
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
