import builtins
import contextlib
import io
import os

import pytest
from unittest.mock import MagicMock, patch, Mock
from stats import runtime_length, compare_size, get_total_files_size, get_directory_size


@pytest.fixture
def output_loc(tmp_path):
    # Use tmp_path for relative output location
    return tmp_path / "output_file.txt"


def test_runtime_length():
    # Define a simple function to be decorated
    @runtime_length
    def some_function():
        pass

    # Call the decorated function
    some_function()

    # No assertions needed, just checking if it runs without errors


def test_compare_size_with_inflate_archive(tmp_path, output_loc):
    # Create some mock files and directories
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    dir1 = tmp_path / "dir1"
    dir1_file = dir1 / "file3.txt"
    file1.write_text("File 1 content")
    file2.write_text("File 2 content")
    dir1.mkdir()
    dir1_file.write_text("File 3 content")

    mock = Mock()
    mock.side_effect = print  # ensure actual print is called to capture its txt
    print_original = print
    builtins.print = mock

    try:
        str_io = io.StringIO()
        with contextlib.redirect_stdout(str_io):
            with patch('stats.get_total_files_size', return_value=10):
                # Define a simple function to be decorated
                @compare_size
                def inflate_archive_to_files(file_path, save_path):
                    return file_path

                # Call the decorated function with the list of files
                result = inflate_archive_to_files([file1, file2, dir1], output_loc)

        output = str_io.getvalue()

        assert print.called  # `called` is a Mock attribute
        assert output.startswith(f"\nArchive size:")
    finally:
        builtins.print = print_original  # ensure print is "unmocked"


def test_compare_size_with_add_files_to_archive(tmp_path, output_loc):
    # Create some mock files and directories
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    dir1 = tmp_path / "dir1"
    dir1_file = dir1 / "file3.txt"
    file1.write_text("File 1 content")
    file2.write_text("File 2 content")
    dir1.mkdir()
    dir1_file.write_text("File 3 content")

    mock = Mock()
    mock.side_effect = print  # ensure actual print is called to capture its txt
    print_original = print
    builtins.print = mock

    try:
        str_io = io.StringIO()
        with contextlib.redirect_stdout(str_io):
            with patch('stats.get_total_files_size', return_value=10):
                # Define a simple function to be decorated
                @compare_size
                def add_files_to_archive(file_path, output_loc):
                    return file_path

                # Call the decorated function with the list of files
                result = add_files_to_archive([file1, file2, dir1], output_loc)

        output = str_io.getvalue()

        assert print.called  # `called` is a Mock attribute
        assert output.startswith(f"\nEncoding completed")
    finally:
        builtins.print = print_original  # ensure print is "unmocked"


def test_get_total_files_size(tmp_path):
    # Create some mock files and directories
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    dir1 = tmp_path / "dir1"
    dir1_file = dir1 / "file3.txt"
    file1.write_text("File 1 content")
    file2.write_text("File 2 content")
    dir1.mkdir()
    dir1_file.write_text("File 3 content")

    # Calculate the total size of the files and directories
    expected_size = file1.stat().st_size + file2.stat().st_size + dir1_file.stat().st_size

    # Call the function to get the total size
    total_size = get_total_files_size([file1, file2, dir1])

    # Check if the function returns the correct total size
    assert total_size == expected_size


def test_get_directory_size(tmp_path):
    # Create some mock files and directories
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    dir1 = tmp_path / "dir1"
    dir1_file = dir1 / "file3.txt"
    file1.write_text("File 1 content")
    file2.write_text("File 2 content")
    dir1.mkdir()
    dir1_file.write_text("File 3 content")

    # Calculate the total size of the directory
    expected_size = file1.stat().st_size + file2.stat().st_size + dir1_file.stat().st_size

    # Call the function to get the directory size
    total_size = get_directory_size(tmp_path)

    # Check if the function returns the correct directory size
    assert total_size == expected_size


def test_get_total_files_size_empty_list(tmp_path):
    # Test with an empty list of files/directories
    total_size = get_total_files_size([])
    assert total_size == 0


def test_get_total_files_size_nested_directories(tmp_path):
    # Test with nested directories
    dir1 = tmp_path / "dir1"
    dir1.mkdir()
    dir2 = dir1 / "dir2"
    dir2.mkdir()
    file1 = dir2 / "file1.txt"
    file1.write_text("File content")

    # Calculate the expected total size
    expected_size = file1.stat().st_size

    # Call the function to get the total size
    total_size = get_total_files_size([dir1])

    # Check if the function returns the correct total size
    assert total_size == expected_size


def test_get_total_files_size_files_of_different_sizes(tmp_path):
    # Test with files of different sizes
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    file3 = tmp_path / "file3.txt"

    # Write different content to each file to ensure different sizes
    file1.write_text("Small file")
    file2.write_text("Medium file" * 1000)  # Large file
    file3.write_text("Large file" * 10000)  # Very large file

    # Calculate the expected total size
    expected_size = sum([file1.stat().st_size, file2.stat().st_size, file3.stat().st_size])

    # Call the function to get the total size
    total_size = get_total_files_size([file1, file2, file3])

    # Check if the function returns the correct total size
    assert total_size == expected_size


def test_get_total_files_size_non_existent_files(tmp_path):
    # Test how the function handles non-existent files/directories
    non_existent_file = tmp_path / "non_existent_file.txt"
    non_existent_dir = tmp_path / "non_existent_dir"

    # Call the function with non-existent paths
    total_size1 = get_total_files_size([non_existent_file])
    total_size2 = get_total_files_size([non_existent_dir])

    # Check if the function returns 0 for non-existent paths
    assert total_size1 == 0
    assert total_size2 == 0




def test_compare_size_with_exception_raised(tmp_path, output_loc):
    # Define a function that raises an exception
    def function_with_exception(arg):
        raise ValueError("Something went wrong")

    # Call the decorated function with the function that raises an exception
    with pytest.raises(ValueError):
        compare_size(function_with_exception)(output_loc)


if __name__ == "__main__":
    pytest.main([__file__])
