import os
from pathlib import Path
from typing import Union, Any
from archive import *
from compressor import Compressor, RLE_Compressor, LZW_Compressor
from stats import runtime_length, compare_size
from encoded_file import Encoded_File


def save_archive_to_file(archive: Archive, save_path: Path) -> None:
    """
    Save an Archive object to a file.

    Args:
        archive (Archive): The Archive object to save.
        save_path (Path): The path to save the archive file.
    """
    write_archive(save_path, archive)


def open_archive_from_file(archive_path: Path) -> Archive:
    """
    Open an Archive object from a file.

    Args:
        archive_path (Path): The path to the archive file.

    Returns:
        Archive: The opened Archive object.
    """
    if not is_valid_archive(archive_path):
        raise IOError("Corrupted Archive File, Unable to read")
    return read_archive(archive_path)


@runtime_length
@compare_size
def add_files_to_archive(new_files_paths: Union[list[Path], Path], save_path: Path, byte_len: int, compress: Compressor,
                         password: Any = None, cap_size: int = 99) -> None:
    """
    Add files to an existing archive or create a new archive.

    Args:
        save_path (Path): The path to save the archive.
        new_files_paths (Union[list[Path], Path]): The paths to the files to add to the archive.
        byte_len (int): The byte length for encoding the files.
        compress (Compressor): The compressor object to use for encoding.

    Raises:
        ValueError: If the path is not a recognized archive file.
        IOError: If the archive file is corrupted.
        :param byte_len: size of byte for RLE compress
        :param cap_size: size of cap for RLE compress
        :param new_files_paths: parent folder of files / list of all files
        :param compress: comppressor type to use
        :param save_path: path to save file
        :param password: archive password
    """
    if save_path.exists():
        # if the save path is a directory - add a default 'Archive.ido' suffix to the path
        if save_path.is_dir():
            save_path = save_path / 'Archive.ido'
            encoded_files = files_to_encoded_files_list(new_files_paths, byte_len, compress, cap_size)
            # add the files to a new archive instance
            archive = Archive(encoded_files, password)
            # save the archive in a .ido file.
            save_archive_to_file(archive, save_path)

        # if the save path is not .ido type - raise error
        elif save_path.is_file():
            if save_path.suffix != ".ido":
                raise ValueError("Invalid Path - Not a recognized Archive file")
            else:
                # if it is a .ido archive - check validity
                if not is_valid_archive(save_path):
                    raise IOError("Corrupted Archive File, Unable to read")
                else:  # if the file is valid
                    # create archive instance
                    archive = open_archive_from_file(save_path)
                    # encode files in the path given
                    encoded_files = files_to_encoded_files_list(new_files_paths, byte_len, compress, cap_size)
                    # add the files to the archive
                    archive.add_to_archive(encoded_files)
                    # save archive as .ido file
                    save_archive_to_file(archive, save_path)
    else:
        # if file doesn't exist - check suffix
        if save_path.suffix != ".ido":
            raise ValueError("Invalid Path - Not a recognized Archive file")
        # encode files given
        encoded_files = files_to_encoded_files_list(new_files_paths, byte_len, compress, cap_size)
        # add the files to a new archive instance
        archive = Archive(encoded_files, password)
        # save the archive in a .ido file.
        save_archive_to_file(archive, save_path)


def files_to_encoded_files_list(files_paths: Union[list[Path], Path], byte_len: int, comp: Compressor, cap_size: int) \
        -> list[Encoded_File]:
    """
    Convert a list of file paths to a list of Encoded_File objects.
    This function Uses recursion.

    Args:
        files_paths (list[Path]): The paths to the files.
        byte_len (int): The byte length for encoding the files.
        comp (Compressor): The compressor object to use for encoding.

    Returns:
        list[Encoded_File]: A list of Encoded_File objects.
    """
    # create new list
    encoded_files_list = []
    # for each file in the path
    if not isinstance(files_paths, list):
        new_files_list = [files_paths]
        files_paths = new_files_list
    for file_path in files_paths:
        # if it's a folder - recursively call the function on the contents of the folder
        if file_path.is_dir():
            folder_name = file_path.name
            # get files in folder
            files_in_dir = list(file_path.iterdir())
            # recursively call function
            encoded_files_in_dir = files_to_encoded_files_list(files_in_dir, byte_len, comp, cap_size)
            # add the parent folder path as prefix
            for file in encoded_files_in_dir:
                new_path = folder_name + '/' + str(file.get_path())
                file.set_path(Path(new_path))
                encoded_files_list.append(file)
        # if it's a file
        else:
            # select open type - r or rb
            file_name = file_path.name
            if not is_text_file(file_path):
                opened_file = open(file_path, 'rb')
                file_content = opened_file.read()
                # encode file and add to the encoded files list
                encoded_files_list.append(comp.encode(file_content, file_name, byte_len, cap_size))
            else:
                opened_file_var = open(file_path, 'r')
                string_file_content = ''
                for line in opened_file_var.readlines():
                    string_file_content += line
                # encode file and add to the encoded files list

                encoded_files_list.append(comp.encode(string_file_content, file_name, byte_len, cap_size))

    return encoded_files_list



@runtime_length
@compare_size
def inflate_archive_to_files(archive_path: Path, save_path: Path, password: Any= None)  -> None:
    """
    Extract files from an archive and save them to disk.

    Args:
        archive_path (Path): The path to the archive file.
        save_path (Path): The directory where files will be extracted.
        :param save_path:
        :param archive_path:
        :param password:
    """
    rle_comp = RLE_Compressor()
    lzw_comp = LZW_Compressor()
    archive = open_archive_from_file(archive_path)
    if archive.is_protected():
        if archive.check_password(password):
            print("Correct Password")
        else:
            raise DecryptError

    for encoded_file in archive.get_encoded_files_list():
        if os.name == 'nt':
            correct_file_path = str(encoded_file.get_path()).replace('/','\\')

        else:
            correct_file_path = str(encoded_file.get_path()).replace('\\','/')

        new_file_path = save_path / correct_file_path
        if encoded_file.get_encoder() == 'RLE':
            file_content = rle_comp.decode(encoded_file)
        else:
            file_content = lzw_comp.decode(encoded_file)
        # select write type
        if encoded_file.is_binary():
            open_type = 'wb'
        else:
            open_type = 'w'
        new_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(new_file_path, open_type) as file:
            file.write(file_content)


def is_text_file(path: Path) -> bool:
    """
    Check if a file is a text file based on its extension.

    Args:
        path (Path): The path to the file.

    Returns:
        bool: True if the file is a text file, False otherwise.
    """
    return path.suffix == ".txt"


def is_valid_archive(path: Path) -> bool:
    """
    Check if an archive file is valid.

    Args:
        path (Path): The path to the archive file.

    Returns:
        bool: True if the archive file is valid, False otherwise.
    """
    try:
        with open(path, 'rb') as file:
            # Read hashed password if exists
            hashed_password = file.read(64)
            # Check if the hashed password is valid
            if hashed_password != b'\x00' * 64 and len(hashed_password) != 64:
                return False

            # Read encoded files data, binary flags, byte lengths, and paths
            combined_line = b''.join(file.readlines())
            encoded_file_chunks = combined_line.split(b'x\\\\x')[:-1]  # Remove last empty element

            # Validate each encoded file data, binary flag, byte length, and path
            for i in range(0, len(encoded_file_chunks), 6):  # Each encoded file consists of 5 parts
                encoded_file_data = encoded_file_chunks[i]
                binary_flag_data = encoded_file_chunks[i + 1]
                byte_length_data = encoded_file_chunks[i + 2]
                path_data = encoded_file_chunks[i + 3]
                encode_data = encoded_file_chunks[i + 4]
                cap_data = encoded_file_chunks[i + 5]
                # Ensure all required data exists
                if not encoded_file_data or not binary_flag_data or not byte_length_data or not path_data or not encode_data or not cap_data:
                    print("Debugging Info:")
                    print("encoded_file_data:", encoded_file_data)
                    print("binary_flag_data:", binary_flag_data)
                    print("byte_length_data:", byte_length_data)
                    print("cap_data:", cap_data)
                    return False
    except FileNotFoundError:
        return False
    return True
