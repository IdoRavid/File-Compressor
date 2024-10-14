import pathlib
import shutil
from unittest.mock import patch
import pytest
from flaky import flaky

from compressor import TEST_BASE_PATH, CODE_BASE_PATH
from main import *
import tempfile

# Define the base path for the code
MAIN_TEST_BASE_PATH = TEST_BASE_PATH / "Main Tests"


# Fixture for providing mock arguments
@pytest.fixture
def mock_args():
    return Namespace(
        archive=False,
        open=False,
        validate=False,
        inspect=False,
        password=None,
        byte_size=5,
        compressor=0,
        file_path="something",
        save_path=os.path.expanduser("~"),
        cap_size=99,
        delete=None,
        replace=False
    )


# Fixture for setting up temporary directories
@pytest.fixture
def temp_dirs():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_run_file_compressor():
    with patch('main.run_file_compressor') as mock:
        yield mock


@pytest.fixture
def mock_parse_args():
    with patch('main.parse_args') as mock:
        yield mock


@pytest.fixture
def mock_print():
    with patch('builtins.print') as mock:
        yield mock


@pytest.fixture
def mock_path():
    with patch('main.Path') as mock:
        yield mock


# Test for parsing command line arguments
def test_parse_args():
    # Test with valid arguments
    args = parse_args(['-f', '/path/to/files', '-a', '-s', '/path/to/save', '-p', 'password', '-b', '10', '-c', '1'])
    assert args.file_path == '/path/to/files'
    assert args.archive == True
    assert args.save_path == '/path/to/save'
    assert args.password == 'password'
    assert args.byte_size == 10
    assert args.compressor == 1

    # Test with missing arguments
    with pytest.raises(SystemExit):
        parse_args(['-f', '/path/to/files', '-a', '-s', '/path/to/save', '-p', 'password', '-b'])


# Test for handling archive command
def test_command_handler_archive(mock_args, temp_dirs):
    with patch('main.add_files_to_archive') as mock_add_files_to_archive:
        mock_args.archive = True
        mock_args.file_path = str(temp_dirs)
        command_handler(mock_args)
        assert validate_args(mock_args)
        assert mock_add_files_to_archive.called


# Test for handling open command
def test_command_handler_open(mock_args, temp_dirs):
    mock_args.open = True
    with patch('main.inflate_archive_to_files') as mock_inflate_archive_to_files:
        mock_args.file_path = str(temp_dirs)
        command_handler(mock_args)
        assert mock_inflate_archive_to_files.called


# Test for handling validate command
def test_command_handler_validate(mock_args, temp_dirs):
    mock_args.validate = True
    with patch('main.is_valid_archive') as mock_is_valid_archive:
        mock_args.validate = True
        mock_args.file_path = str(temp_dirs)
        command_handler(mock_args)
        assert mock_is_valid_archive.called


# Test for handling inspect command
def test_command_handler_inspect(mock_args, temp_dirs):
    mock_args.inspect = True
    with patch('main.is_valid_archive') as mock_is_valid_archive, \
            patch('main.open_archive_from_file') as mock_open_archive_from_file:
        mock_is_valid_archive.return_value = True
        mock_open_archive_from_file.return_value.is_protected.return_value = False
        mock_args.file_path = str(temp_dirs)
        command_handler(mock_args)
        assert mock_open_archive_from_file.called


# Test for validating command line arguments
def test_validate_args(mock_args, temp_dirs):
    mock_args.file_path = None
    assert not validate_args(mock_args)  # No file path provided

    mock_args.file_path = '/path/to/file'
    assert not validate_args(mock_args)  # File path does not exist

    mock_args.file_path = '/path/to/existing_file'
    mock_args.save_path = '/path/to/folder'
    assert not validate_args(mock_args)  # Save path is a directory and doesn't exist

    mock_args.file_path = MAIN_TEST_BASE_PATH / "File.txt"
    mock_args.save_path = temp_dirs
    assert validate_args(mock_args) == True  # Valid arguments provided

    # opened file is not with archive extension
    mock_args.open = True
    mock_args.file_path = str(CODE_BASE_PATH / "file.txt")
    assert not validate_args(mock_args)

    # invalid byte size
    mock_args.byte_size = -2
    assert not validate_args(mock_args)

    mock_args.file_path = "_random_place"
    assert not validate_args(mock_args)


# Test for running the file compressor
def test_run_file_compressor(mock_args):
    with patch('main.parse_args', return_value=mock_args), \
            patch('main.validate_args', return_value=True), \
            patch('main.command_handler') as mock_command_handler:
        run_file_compressor()
        assert mock_command_handler.called


# Test for archiving files with a folder target
def test_archive_files_with_folder_target(mock_args, temp_dirs):
    save_path = temp_dirs
    target_path = Path(save_path) / "Archive.ido"
    if target_path.exists():
        target_path.unlink()

    mock_args.file_path = str(MAIN_TEST_BASE_PATH / "folder_scheme")
    mock_args.save_path = save_path
    mock_args.archive = True
    command_handler(mock_args)

    assert (Path(save_path) / "Archive.ido").exists()


# Test for archiving files with a file target
def test_archive_files_with_file_target(mock_args, temp_dirs):
    save_path = temp_dirs / "New Archive.ido"
    mock_args.file_path = str(MAIN_TEST_BASE_PATH / "Final Project.pdf")
    if Path(save_path).exists():
        Path(save_path).unlink()
    mock_args.save_path = save_path
    mock_args.archive = True
    command_handler(mock_args)

    assert (Path(save_path)).exists()


# Test for inflating files from an archive
def test_inflate_files_from_archive(mock_args, temp_dirs):
    try:
        save_folder = Path(TEST_BASE_PATH / "temp_test_folder")
        save_folder.mkdir()
    except FileExistsError:
        pass

    save_path = save_folder / "New_location"
    files_path = str(MAIN_TEST_BASE_PATH / "compressed_folder_scheme.ido")
    mock_args.save_path = save_path
    mock_args.file_path = files_path
    mock_args.open = True
    command_handler(mock_args)
    assert Path(save_folder / "New_location/folder_scheme").exists() or Path(
        save_folder / "New_location" /"folder_scheme").exists()


# Test for inspecting an archive
def test_inspect_archive(mock_args, temp_dirs, capsys):
    mock_args.file_path = str(MAIN_TEST_BASE_PATH / "compressed_folder_scheme.ido")
    mock_args.inspect = True
    command_handler(mock_args)
    captured = capsys.readouterr().out

    assert r"1 - folder_scheme\folder\another_bin_file.pub" in captured
    assert r"2 - folder_scheme\folder\inside folder\bin_file.pptx" in captured
    assert r"3 - folder_scheme\folder\inside folder\text file.txt" in captured
    assert r"4 - folder_scheme\folder\text file.txt" in captured
    assert r"5 - folder_scheme\some_file.accdb" in captured
    assert r"6 - folder_scheme\text file.txt" in captured


def test_command_handler_delete(mock_args, temp_dirs, capsys):
    mock_args.delete = "1,2"
    original_file = pathlib.Path(MAIN_TEST_BASE_PATH / "Copy_location/Test_Archive.ido")
    copy_file = pathlib.Path(temp_dirs / "Test_Archive.ido")
    shutil.copy(original_file, copy_file)

    mock_args.file_path = str(copy_file)
    command_handler(mock_args)
    mock_args.delete = None
    mock_args.inspect = True
    command_handler(mock_args)
    captured = capsys.readouterr().out

    assert ("1 - folder_scheme/folder/inside folder/text file.txt" in captured
            or "1 - folder_scheme\\folder\\inside folder\\text file.txt" in captured)
    assert ("2 - folder_scheme/folder/text file.txt" in captured
            or "2 - folder_scheme\\folder\\text file.txt" in captured)
    assert ("3 - folder_scheme/some_file.accdb" in captured
            or "3 - folder_scheme\\some_file.accdb" in captured)
    assert ("4 - folder_scheme/text file.txt" in captured
            or "4 - folder_scheme\\text file.txt" in captured)


# Test for creating password protection
def test_create_password_protection(mock_args, temp_dirs):
    mock_args.file_path = str(MAIN_TEST_BASE_PATH / "Final Project.pdf")
    mock_args.password = "123123"
    save_path = temp_dirs / "Protected.ido"
    if Path(save_path).exists():
        Path(save_path).unlink()
    mock_args.save_path = save_path
    mock_args.archive = True
    command_handler(mock_args)
    assert Path(save_path).exists()
    assert open_archive_from_file(Path(save_path)).is_protected()


# Test for refusing to open an encrypted file without a password
def test_refuse_to_open_encrypted_file(mock_args, temp_dirs, capsys):
    file_path = str(MAIN_TEST_BASE_PATH / "Protected.ido")
    mock_args.file_path = file_path
    mock_args.open = True
    command_handler(mock_args)
    captured = capsys.readouterr()
    assert "INCORRECT Password" in captured.out


# Test for opening a file with correct password
def test_open_file_with_correct_password(mock_args, temp_dirs):
    file_path = str(MAIN_TEST_BASE_PATH / "Protected.ido")
    mock_args.file_path = file_path
    save_path = temp_dirs / "Decrypted"
    if Path(save_path).exists():
        try:
            Path(save_path).unlink()
        except PermissionError:
            pass
    mock_args.save_path = save_path
    mock_args.open = True
    mock_args.password = "123123"
    command_handler(mock_args)
    assert Path(save_path).exists()


# Test for displaying help message
def test_help(mock_args, capsys):
    argv = ['--help']

    with pytest.raises(SystemExit):
        args = parse_args(argv)
    captured = capsys.readouterr()
    assert "**************************************************************** Welcome to" in captured.out


# Test for parsing arguments with missing file path
def test_parse_args_missing_file_path():
    argv = ['-a']
    args = parse_args(argv)
    assert not validate_args(args)  # Should return False because file path is missing


# Test for parsing arguments with invalid file path
def test_parse_args_invalid_file_path():
    argv = ['-a', '-f', 'nonexistent_file.txt']
    args = parse_args(argv)
    assert not validate_args(args)  # Should return False because file path is invalid


# Test for parsing arguments with invalid save path
def test_parse_args_invalid_save_path():
    argv = ['-a', '-f', 'existing_file.txt', '-s', 'nonexistent_folder/']
    args = parse_args(argv)
    assert not validate_args(args)  # Should return False because save path is invalid


# Test for parsing arguments with invalid byte size
def test_parse_args_invalid_byte_size():
    argv = ['-a', '-f', 'existing_file.txt', '-b', '-5']
    args = parse_args(argv)
    assert not validate_args(args)  # Should return False because byte size is invalid


# Test for parsing arguments with invalid cap size
def test_parse_args_invalid_cap_size():
    argv = ['-a', '-f', 'existing_file.txt', '-q', '-5']
    args = parse_args(argv)
    assert not validate_args(args)  # Should return False because cap size is invalid


# Test for handling missing arguments
def test_missing_arguments(capsys):
    # Simulate running the script without any arguments
    sys.argv = ['main.py']
    run_file_compressor()
    captured = capsys.readouterr()
    assert "Please enter File path." in captured.out


# Test for handling invalid argument combination
def test_invalid_argument_combination(capsys):
    # Simulate providing incompatible options together
    sys.argv = ['main.py', '-a', '-o']
    run_file_compressor()
    captured = capsys.readouterr()
    assert "Incorrect Arguments Entered." in captured.out


# Test for handling invalid file path format
def test_invalid_file_path_format(capsys):
    # Simulate providing a file path with invalid characters
    sys.argv = ['main.py', '-f', 'path_with_!@#_special_characters']
    run_file_compressor()
    captured = capsys.readouterr()
    assert "File Doesn't exist" in captured.out



# Test for handling nonexistent save path
def test_nonexistent_save_path(tmp_path, capsys, temp_dirs):
    # Simulate providing a nonexistent save path
    file_path = str(MAIN_TEST_BASE_PATH / "File.txt")
    sys.argv = ['main.py', '-s', str(tmp_path / 'nonexistent_folder/another_folder'), '-f', file_path]
    run_file_compressor()
    captured = capsys.readouterr()
    assert "Folder doesn't Exist" in captured.out


# Test for handling negative integer values
def test_negative_integer_values(capsys, temp_dirs):
    # Simulate providing negative values for integer options
    file_path = str(MAIN_TEST_BASE_PATH / "File.txt")
    sys.argv = ['main.py', '-b', '-5', '-f', file_path]
    run_file_compressor()
    captured = capsys.readouterr()
    assert "Invalid byte size" in captured.out


# Test for handling non-integer values for integer options
def test_non_integer_values_for_integer_options(capsys, temp_dirs):
    # Simulate providing non-integer values for integer options
    file_path = str(MAIN_TEST_BASE_PATH / "File.txt")
    sys.argv = ['main.py', '-b', 'byte_size_is_not_integer', '-f', file_path]
    run_file_compressor()
    captured = capsys.readouterr()
    assert "Incorrect Arguments Entered" in captured.out


# Test for handling missing password for a protected archive
def test_missing_password_for_protected_archive(capsys, temp_dirs):
    # Simulate trying to inspect or inflate a password-protected archive without providing the password
    protected_path = str(MAIN_TEST_BASE_PATH / "Protected.ido")
    sys.argv = ['main.py', '-i', '-f', protected_path]
    run_file_compressor()
    captured = capsys.readouterr()
    assert "Protected Archive. Enter Password." in captured.out  # Assuming the password is correct


# Test for handling incorrect password for a protected archive
def test_incorrect_password_for_protected_archive(capsys, temp_dirs):
    # Simulate providing an incorrect password for a password-protected archive
    protected_path = str(MAIN_TEST_BASE_PATH / "Protected.ido")
    sys.argv = ['main.py', '-i', '-f', protected_path, '-p', 'incorrect_password']
    run_file_compressor()
    captured = capsys.readouterr()
    assert "INCORRECT Password" in captured.out


# Test for handling invalid compression algorithm number
def test_invalid_compression_algorithm_number(capsys, temp_dirs):
    # Simulate providing an invalid compression algorithm number
    file_path = str(MAIN_TEST_BASE_PATH / "File.txt")
    sys.argv = ['main.py', '-c', '2', '-f', file_path]
    run_file_compressor()
    captured = capsys.readouterr()
    assert "Invalid Compressor Number. see -Help" in captured.out


# Test for general functionality
def test_invalid_input_for_delete(capsys, temp_dirs):
    file_path = str(MAIN_TEST_BASE_PATH / "File.txt")
    sys.argv = ['main.py', '-d', '-2', '-f', file_path]
    run_file_compressor()
    captured = capsys.readouterr()
    assert "Invalid Index for delete." in captured.out

    sys.argv = ['main.py', '-d', 'i,2', '-f', file_path]
    run_file_compressor()
    captured = capsys.readouterr()
    assert "Invalid Index for delete." in captured.out


def test_open_non_archive_file(mock_run_file_compressor, mock_print):
    args = default_args()
    args.open = True
    args.file_path = str(MAIN_TEST_BASE_PATH / "File.txt")

    run_file_compressor(args)
    mock_print.assert_called_once_with("\nCannot Open - not an archive file.")
    mock_run_file_compressor.assert_not_called()


def test_handle_list_of_file_paths(mock_run_file_compressor, capsys):
    args = default_args()
    args.open = True
    args.file_path = [str(MAIN_TEST_BASE_PATH / "File.txt"), str(MAIN_TEST_BASE_PATH / "folder_scheme/some_file.accdb")]

    run_file_compressor(args)
    captured = capsys.readouterr()
    assert "Cannot Open - not an archive file." in captured.out


def test_handle_nonexistent_directory(mock_run_file_compressor, mock_print):
    args = default_args()
    args.file_path = str(MAIN_TEST_BASE_PATH / "File.txt")
    args.save_path = str(MAIN_TEST_BASE_PATH / "non_existent/non_existent_folder")

    run_file_compressor(args)
    mock_print.assert_called_once_with("Folder doesn't Exist")
    mock_run_file_compressor.assert_not_called()


def test_handle_delete_existing_archive_failure(mock_run_file_compressor, mock_path, capsys):
    mock_path.return_value.unlink.side_effect = OSError
    args = default_args()
    args.replace = True
    args.archive = True
    args.file_path = str(MAIN_TEST_BASE_PATH / "File.txt")
    args.save_path = str(MAIN_TEST_BASE_PATH / "Archive.ido")
    command_handler(args)
    captured = capsys.readouterr()
    assert "Unable to delete archive" in captured.out


def test_handle_unknown_error(mock_parse_args, capsys):
    sys.argv = [CODE_BASE_PATH / 'main.py', "-g"]
    mock_parse_args.side_effect = SystemExit
    run_file_compressor()
    captured = capsys.readouterr()
    assert "Incorrect Arguments Entered." in captured.out


def test_command_handler_type_error(capsys):
    args = default_args()
    args.file_path = Exception
    args.archive = True
    command_handler(args)
    captured = capsys.readouterr()
    assert "Incorrect Type inserted." in captured.out

    args.archive = False
    args.open = True
    command_handler(args)
    captured = capsys.readouterr()
    assert "Incorrect Type inserted." in captured.out


def test_invalid_archive(capsys):
    args = default_args()
    args.file_path = MAIN_TEST_BASE_PATH / "Invalid Archive.ido"
    args.validate = True
    command_handler(args)
    captured = capsys.readouterr()
    assert "Invalid Archive." in captured.out

    args.validate = False
    args.inspect = True
    command_handler(args)
    captured = capsys.readouterr()
    assert "Invalid Archive" in captured.out


# Entry point for running tests if the script is executed directly
if __name__ == "__main__":
    pytest.main([__file__])
