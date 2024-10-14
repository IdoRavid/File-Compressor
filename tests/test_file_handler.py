import filecmp
import pytest
import compressor
from file_handler import *
import tempfile

# Base paths for testing
FILE_HANDLER_TEST_PATH = compressor.TEST_BASE_PATH / "File_Handler_Tests"
COMPRESSING_TESTS_PATH = FILE_HANDLER_TEST_PATH / "compressing tests"


# Fixture to create a temporary folder for testing
@pytest.fixture
def temp_folder():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


# Test function to check if a file is a text file
def test_is_text_file():
    assert is_text_file(FILE_HANDLER_TEST_PATH / "some text file.txt")
    assert not is_text_file(FILE_HANDLER_TEST_PATH / "test.xlsx")


# Test function for converting files to encoded files list
def test_files_to_encoded_files_list(temp_folder):
    file_path = FILE_HANDLER_TEST_PATH / "folder_scheme"
    comp = compressor.RLE_Compressor()
    encoded_list = files_to_encoded_files_list([file_path], 5, comp, 99)

    print(encoded_list)


# Test function for checking the validity of an archive file
def test_validity_check(temp_folder):
    rle_comp = compressor.RLE_Compressor()
    encoded_files = [rle_comp.encode("something"), rle_comp.encode("another thing")]
    archive = Archive(encoded_files)
    write_archive(temp_folder / "correct_format.ido", archive)

    # Write an invalid file with incorrect format
    with open(temp_folder / "incorrect_format.ido", 'wb') as file:
        file.write(b"Invalid data\n")
        file.write(b"0\n")  # Incorrect binary flag
        file.write(b"10\n")  # Incorrect byte length

    # Write another invalid file with binary content
    with open(temp_folder / "binary_content.ido", 'wb') as file:
        file.write(b"\x00\x01\x02\x03\x04")  # Binary content

    assert is_valid_archive(temp_folder / "correct_format.ido")
    assert not is_valid_archive(temp_folder / "incorrect_format.ido")
    assert not is_valid_archive(temp_folder / "binary_content.ido")


# Test function for adding a single file to an archive
def test_single_file_to_archive(temp_folder):
    comp = compressor.RLE_Compressor()
    file_path = FILE_HANDLER_TEST_PATH / "bin_file.xlsx"
    save_path = temp_folder / "text_compress.ido"
    if save_path.exists():
        save_path.unlink()
    add_files_to_archive([file_path], save_path, 5, comp)
    assert is_valid_archive(save_path)

    new_archive = open_archive_from_file(save_path)
    archive_files = new_archive.get_encoded_files_list()
    decoded_file = comp.decode(archive_files[0])

    new_file = temp_folder / "new_test.xlsx"
    if new_file.exists():
        new_file.unlink()

    open_type = 'wb'
    if isinstance(decoded_file, str):
        open_type = 'w'
    with open(new_file, open_type) as file:
        file.write(decoded_file)
    assert filecmp.cmp(file_path, new_file)


# Test function for adding multiple files to an archive
def test_multi_file_to_archive(temp_folder):
    comp = compressor.RLE_Compressor()
    files_path = FILE_HANDLER_TEST_PATH / "folder_scheme"
    save_path = temp_folder / "folder_compress.ido"
    if save_path.exists():
        save_path.unlink()
    add_files_to_archive([files_path], save_path, 5, comp)
    assert is_valid_archive(save_path)


# Test function for saving an archive to a file
def test_save_archive_to_file(temp_folder):
    comp = compressor.RLE_Compressor()
    encoded_files = [comp.encode(b"some data", "path1", 5, 99), comp.encode(b"more data", "path2", 5, 99)]
    archive = Archive(encoded_files)
    save_path = temp_folder / "test_archive.ido"
    save_archive_to_file(archive, save_path)
    assert save_path.exists()

    saved_archive = open_archive_from_file(save_path)
    assert saved_archive == archive
    assert is_valid_archive(save_path)


# Test function for opening an archive from a file
def test_open_archive_from_file(temp_folder):
    comp = compressor.RLE_Compressor()
    encoded_files = [comp.encode("some data", "path1", 5, 99), comp.encode("more data", "path2", 5, 99)]
    archive = Archive(encoded_files)

    save_path = temp_folder / "test_archive.ido"
    save_archive_to_file(archive, save_path)
    opened_archive = open_archive_from_file(save_path)
    assert archive == opened_archive


# Test function for adding files to an existing archive
def test_add_files_to_archive_existing(temp_folder):
    comp = compressor.RLE_Compressor()
    encoded_files = [comp.encode("existing data")]
    archive = Archive(encoded_files)

    save_path = temp_folder / "existing_archive.ido"

    save_archive_to_file(archive, save_path)
    temp_archive = open_archive_from_file(save_path)
    assert len(temp_archive.get_encoded_files_list()) == 1
    new_files_paths = [FILE_HANDLER_TEST_PATH / "new_data.txt"]
    add_files_to_archive(new_files_paths, save_path, 5, comp)
    opened_archive = open_archive_from_file(save_path)
    assert len(opened_archive.get_encoded_files_list()) == 2


# Test function for adding files to a new archive
def test_add_files_to_archive_non_existing(temp_folder):
    comp = compressor.RLE_Compressor()
    new_files_paths = [FILE_HANDLER_TEST_PATH / "new_data.txt"]
    save_path = temp_folder / "new_archive.ido"
    if save_path.exists():
        save_path.unlink()
    add_files_to_archive(new_files_paths, save_path, 5, comp)
    opened_archive = open_archive_from_file(save_path)
    assert len(opened_archive.get_encoded_files_list()) == 1


# Test function for deflating an archive to files
def test_deflate_archive_to_files(temp_folder):
    comp = compressor.RLE_Compressor()
    encoded_files = [comp.encode("some data", "file1"), comp.encode("more data", "file2")]
    archive = Archive(encoded_files)
    save_path = temp_folder / "test_archive.ido"
    save_archive_to_file(archive, save_path)
    deflate_path = temp_folder / "deflated"
    inflate_archive_to_files(save_path, deflate_path)
    assert (deflate_path / "file1").exists()
    assert (deflate_path / "file2").exists()


# Test function for storing multiple files in an archive and inflating them
def test_multi_files_store_and_inflate(temp_folder):
    comp = compressor.RLE_Compressor()
    files_path = FILE_HANDLER_TEST_PATH / "folder_scheme"
    save_path = temp_folder / "folder_compress2.ido"
    if save_path.exists():
        save_path.unlink()
    add_files_to_archive([files_path], save_path, 5, comp)
    assert is_valid_archive(save_path)

    new_path = temp_folder / "results"

    inflate_archive_to_files(save_path, new_path)
    _, mismatch, error = filecmp.cmpfiles(files_path, new_path / 'folder_scheme', ['text file.txt', 'some_file.accdb'])
    assert len(mismatch) == 0
    assert len(error) == 0
    _, mismatch, error = filecmp.cmpfiles(files_path / 'folder', new_path / "folder_scheme/folder",
                                          ['text file.txt', 'another_bin_file.pub'])
    assert len(mismatch) == 0
    assert len(error) == 0


if __name__ == "__main__":
    pytest.main([__file__])
