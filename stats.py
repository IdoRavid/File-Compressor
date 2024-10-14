import datetime
import os
from functools import wraps
from pathlib import Path
from typing import Callable, Any, Union
from archive import Archive
from pathlib import WindowsPath


def runtime_length(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator function that measures the time it took for a function to perform."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Wrapper function that measures the execution time of the decorated function."""
        start_time = datetime.datetime.now()  # Record the start time
        result = func(*args, **kwargs)  # Call the decorated function
        end_time = datetime.datetime.now()  # Record the end time
        # Calculate and print the execution time
        print(f"\nExecution time: {end_time - start_time} \n")
        return result

    return wrapper


def compare_size(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator function for comparing input and output sizes of a compress/decompress process."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Wrapper function wrapped around the compress/decompress function."""
        input_size = 0

        # Check if any arguments are passed
        if not args:
            print("Invalid input to function.")
            return

        # Extract the first positional argument
        input_data = args[0]
        if isinstance(input_data, Path):
            input_data = [input_data]

        # Calculate input size based on the type of input data
        if isinstance(input_data, Archive):
            input_size = input_data.get_size()
        elif isinstance(input_data, list):
            input_size = get_total_files_size(input_data)
        else:
            # Handle unsupported input data type
            print("Unsupported input data type.")
            return

        func_name = func.__name__
        # Call the wrapped function
        result = func(*args, **kwargs)
        output_path = args[1]

        # Calculate output size based on the result
        output_size = 0
        if isinstance(output_path, Path):
            output_path = [output_path]

        if isinstance(output_path, Archive):
            output_size = output_path.get_size()
        elif isinstance(output_path, list):
            output_size = get_total_files_size(output_path)
        else:
            # Handle unsupported output data type
            print("Unsupported output data type.")
            return

        # Print size comparison
        if func_name == 'add_files_to_archive':
            space_saved = input_size - output_size
            print(
                f"\nEncoding completed.\nOriginal File(s) size: {input_size} bytes\nArchive size: {output_size} bytes"
                f"\nSpace saved: {int(100 * (round(space_saved / input_size, 2)))}%\n")
        else:
            print(f"\nArchive size: {input_size} bytes\nInflated File(s) size: {output_size} bytes\n")

        if output_size >= input_size and func_name == "add_files_to_archive":
            print("\nWarning: Output size is greater than or equal to input size.\n")
        return result

    return wrapper


def get_total_files_size(path_list: list[Path]) -> int:
    """Calculate the total size of files in the given list of paths."""
    try:
        total_size = 0
        for path in path_list:
            if path.is_file():
                total_size += path.stat().st_size
            else:
                total_size += get_directory_size(str(path))
        return total_size
    except FileNotFoundError:
        return 0


def get_directory_size(directory):
    # type: (Union[WindowsPath, str]) -> int
    """Returns the size of the directory in bytes."""
    total = 0
    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_directory_size(entry.path)
    except NotADirectoryError:
        return os.path.getsize(directory)
    except PermissionError:
        return 0
    return total
