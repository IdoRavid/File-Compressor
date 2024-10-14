import filecmp
import pytest

# Import necessary classes and functions from other modules
from archive import Archive, write_archive, read_archive, hash_password
from encoded_file import Encoded_File
from file_handler import files_to_encoded_files_list
from compressor import RLE_Compressor, TEST_BASE_PATH
from pathlib import Path

# Define base paths for testing
ARCHIVE_TEST_PATH = TEST_BASE_PATH / "archive tests"


# Fixture to set up an archive for testing
@pytest.fixture
def setup_archive():
    # Creating an instance of the Archive class with some data
    encoded_file = Encoded_File(b"Sample encoded data", binary_flag=False, byte_length=8)
    archive = Archive([encoded_file])

    # Define the file path to save the archive
    save_path = ARCHIVE_TEST_PATH / "test_archive.ido"

    # Save the archive to a file
    write_archive(save_path, archive)

    return save_path, encoded_file


# Fixture to provide a temporary file path
@pytest.fixture
def temp_file_path(tmp_path):
    return tmp_path / "temp_file"


# Test to check the correct number of encoded files in the archive
def test_correct_number_of_encoded_files(setup_archive):
    _, _ = setup_archive

    new_archive = read_archive(ARCHIVE_TEST_PATH / "test_archive.ido")
    assert len(new_archive.get_encoded_files_list()) == 1


# Test to check the correctness of encoded file data in the archive
def test_correct_encoded_file_data(setup_archive):
    _, encoded_file = setup_archive
    new_archive = read_archive(ARCHIVE_TEST_PATH / "test_archive.ido")
    new_encoded_files = new_archive.get_encoded_files_list()
    assert new_encoded_files[0].get_data() == encoded_file.get_data()


# Test to check the correctness of binary flags in the encoded files
def test_correct_binary_flag(setup_archive):
    _, encoded_file = setup_archive
    new_archive = read_archive(ARCHIVE_TEST_PATH / "test_archive.ido")
    new_encoded_files = new_archive.get_encoded_files_list()
    assert new_encoded_files[0].is_binary() == encoded_file.is_binary()


# Test to check the correctness of byte lengths in the encoded files
def test_correct_byte_length(setup_archive):
    _, encoded_file = setup_archive
    new_archive = read_archive(ARCHIVE_TEST_PATH / "test_archive.ido")
    new_encoded_files = new_archive.get_encoded_files_list()
    assert new_encoded_files[0].get_byte_len() == encoded_file.get_byte_len()


# Test to archive and dearchive a single text file
def test_single_text_file_archive_dearchive(temp_file_path):
    comp = RLE_Compressor()
    file_path = ARCHIVE_TEST_PATH / "text_file.txt"
    file_content = file_path.read_text()

    temp_path = ARCHIVE_TEST_PATH / "temp.txt"
    with open(temp_path, 'w') as temp_file:
        temp_file.write(file_content)

    encode_file = comp.encode(file_content, "text_file.txt", 5, 99)
    archive = Archive([encode_file])
    encoded_file_list = archive.get_encoded_files_list()
    decoded_file = comp.decode(encoded_file_list[0])
    new_file = temp_file_path
    new_file.write_text(decoded_file)
    assert filecmp.cmp(temp_path, new_file)


# Test to archive and dearchive a single binary file
def test_single_binary_file_archive_dearchive(temp_file_path):
    comp = RLE_Compressor()
    file_path = ARCHIVE_TEST_PATH / "bin_file.xlsx"
    file_content = file_path.read_bytes()
    encode_file = comp.encode(file_content, "bin_file.xlsx", 5, 99)
    archive = Archive([encode_file])
    encoded_file_list = archive.get_encoded_files_list()
    decoded_file = comp.decode(encoded_file_list[0])
    new_file = temp_file_path
    new_file.write_bytes(decoded_file)
    assert filecmp.cmp(file_path, new_file)


# Test to archive and dearchive a single string
def test_single_string_archive_dearchive():
    text_1 = b'asdasdasd;ljkm'
    assert_archive_dearchive([text_1])

    text_2 = 'asdasdasd;ljkm'
    assert_archive_dearchive([text_2])


# Test to archive and dearchive multiple strings
def test_multi_string_archive_dearchive():
    text_1 = b'aaaa'
    text_2 = b'bbbbcdddddddd'
    assert_archive_dearchive([text_1, text_2])

    text_3 = 'cccccc'
    text_4 = 'dddddd'
    assert_archive_dearchive([text_3, text_4])

    text_5 = 'eeeee'
    text_6 = b'fffff'
    assert_archive_dearchive([text_5, text_6])


# Helper function to assert archive and dearchive results
def assert_archive_dearchive(text_list):
    rle_compressor = RLE_Compressor()
    encoded_files = []
    for text in text_list:
        encoded_files.append(rle_compressor.encode(text, "name", 5, 99))
    original_archive, new_archive = setup_archive_dearchive(encoded_files, (ARCHIVE_TEST_PATH / "arc.ido"))
    decoded_text = []
    for file in new_archive.get_encoded_files_list():
        decoded_text.append(rle_compressor.decode(file))
    assert text_list == decoded_text


# Helper function to set up archive for testing
def setup_archive_dearchive(encoded_files_list, path):
    archive = Archive(encoded_files_list)
    write_archive(path, archive)
    new_archive = read_archive(path)
    return archive, new_archive


# Test to check empty archive
def test_empty_archive():
    archive, new_archive = setup_archive_dearchive([], (ARCHIVE_TEST_PATH / "empty_archive.ido"))
    assert len(new_archive.get_encoded_files_list()) == 0


# Test to check archiving and dearchiving large text
def test_large_text():
    large_text = "a" * 1000000  # 1 MB of 'a's
    assert_archive_dearchive([large_text])


# Test to check the contents of the archive
def test_archive_contents():
    file_path = ARCHIVE_TEST_PATH / "folder_scheme"
    comp = RLE_Compressor()
    encoded_list = files_to_encoded_files_list([file_path], 5, comp, 99)
    archive = Archive(encoded_list)
    content_string = archive.get_archive_contents()

    assert r"1 - folder_scheme\folder\another_bin_file.pub" in content_string or r"1 - folder_scheme/folder/another_bin_file.pub" in content_string
    assert r"2 - folder_scheme\folder\inside folder\bin_file.pptx" in content_string or r"2 - folder_scheme/folder/inside folder/bin_file.pptx" in content_string
    assert r"3 - folder_scheme\folder\inside folder\text file.txt" in content_string or r"3 - folder_scheme/folder/inside folder/text file.txt" in content_string
    assert r"4 - folder_scheme\folder\text file.txt" in content_string or r"4 - folder_scheme/folder/text file.txt" in content_string
    assert r"5 - folder_scheme\some_file.accdb" in content_string or r"5 - folder_scheme/some_file.accdb" in content_string
    assert r"6 - folder_scheme\text file.txt" in content_string or r"6 - folder_scheme/text file.txt" in content_string


# Test to delete files from the archive
def test_delete_files_from_archive():
    file_path = ARCHIVE_TEST_PATH / "folder_scheme"
    comp = RLE_Compressor()
    encoded_list = files_to_encoded_files_list([file_path], 5, comp, 99)
    archive = Archive(encoded_list)
    assert archive.delete_files_from_archive([1, 2])
    content_string = archive.get_archive_contents()
    assert r"1 - folder_scheme\folder\inside folder\text file.txt" in content_string or r"1 - folder_scheme/folder/inside folder/text file.txt" in content_string
    assert r"2 - folder_scheme\folder\text file.txt" in content_string or r"2 - folder_scheme/folder/text file.txt" in content_string
    assert r"3 - folder_scheme\some_file.accdb" in content_string or r"3 - folder_scheme/some_file.accdb" in content_string
    assert r"4 - folder_scheme\text file.txt" in content_string or r"4 - folder_scheme/text file.txt" in content_string


# Test to delete files with bad numbers from the archive
def test_delete_bad_number():
    file_path = ARCHIVE_TEST_PATH / "folder_scheme"
    comp = RLE_Compressor()
    encoded_list = files_to_encoded_files_list([file_path], 5, comp, 99)
    archive = Archive(encoded_list)
    assert not archive.delete_files_from_archive([0, 2])
    content_string = archive.get_archive_contents()
    assert r"1 - folder_scheme\folder\another_bin_file.pub" in content_string or r"1 - folder_scheme/folder/another_bin_file.pub" in content_string
    assert r"2 - folder_scheme\folder\inside folder\bin_file.pptx" in content_string or r"2 - folder_scheme/folder/inside folder/bin_file.pptx" in content_string
    assert r"3 - folder_scheme\folder\inside folder\text file.txt" in content_string or r"3 - folder_scheme/folder/inside folder/text file.txt" in content_string
    assert r"4 - folder_scheme\folder\text file.txt" in content_string or r"4 - folder_scheme/folder/text file.txt" in content_string
    assert r"5 - folder_scheme\some_file.accdb" in content_string or r"5 - folder_scheme/some_file.accdb" in content_string
    assert r"6 - folder_scheme\text file.txt" in content_string or r"6 - folder_scheme/text file.txt" in content_string


# Test hashing password when None is provided
def test_hash_none():
    assert hash_password(None) is None


# Test to get the size of the archive
def test_get_size():
    archive = Archive([])
    assert archive.get_size() > 0


# Test equality of archive instances
def test_archive_eq():
    archive_1 = Archive([])
    assert archive_1 != 2


# Test when non-list files are provided
def test_non_list_files():
    with pytest.raises(TypeError):
        archive1 = Archive("file")


# Entry point for running the tests
if __name__ == "__main__":
    pytest.main()
