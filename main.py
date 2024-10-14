from argparse import Namespace, ArgumentParser
import os
import pathvalidate
from compressor import Compressor, RLE_Compressor, LZW_Compressor, CODE_BASE_PATH
from typing import Union
from file_handler import *
from pathlib import Path
import sys


# Help string for command-line interface
HELP_STRING = ("\n"
               "**************************************************************** \n"
               "Welcome to The File compressor App. Enter Some of the following arguments:\n -f: File Path- paths of "
               "the files to archive, or path of archive to inflate.\n -s: File save Path- path of new archive of "
               "or path of new files. \n  -a - Create archive from files. \n -o - "
               "Inflate files from archive. \n -v: Validate: make sure archive format is correct. \n -i: Inspect "
               "- show files in archive. \n -p: Password. enter password of existing file or enter new password "
               "for new file. \n -c: Compressor - change compression type. 0-RLE, 1-LZW \n -q: Cap size: change encoder"
               "cap size \n -d: Delete. delete files from Archive. Get index from inspect command. add ',' between "
               "indices.  \n -r: Replace. Replace current archive file with a new one. \n -h: Help - this help "
               "message.\n OR- just run the 'display.py' file directly to open the GUI.\n"
               "****************************************************************\n"
               )


def parse_args(argv: list[str]) -> Namespace:
    """Parse command-line arguments and return a namespace."""
    # Define argument parser
    parser = ArgumentParser(
        prog='main.py',
        description='Runs File Compressor',
        add_help=True,  # Enable default help message
        epilog=HELP_STRING,
        exit_on_error=True  # Exit if errors occur during parsing
    )
    group = parser.add_mutually_exclusive_group()

    # Add command line arguments
    parser.add_argument('-f', '--file_path', type=str, default=None,
                        help='Path of files to archive/Path to unpack archive')

    parser.add_argument('-s', '--save_path', type=str, default=os.path.expanduser("~"),
                        help='Path for archive save/load')

    # Add mutually exclusive group for different operations
    group.add_argument('-a', '--archive', action='store_true',
                       help='create archive from files')

    group.add_argument('-o', '--open', action='store_true',
                       help='inflate archive to files')

    group.add_argument('-v', '--validate', action='store_true',
                       help='validate .ido archive format')

    group.add_argument('-i', '--inspect', action='store_true',
                       help='inspect contents of an archive')

    group.add_argument('-d', '--delete', type=str, default=None,
                       help='delete files from archive')

    # Add optional arguments
    parser.add_argument('-p', '--password', type=str, default=None,
                        help='archive password')
    parser.add_argument('-b', '--byte_size', type=int, default=5,
                        help='change RLE encoder byte size')
    parser.add_argument('-c', '--compressor', type=int, default=0,
                        help='change compression algorithm 0-RLE, 1-LZW')
    parser.add_argument('-q', '--cap_size', default=99, help="change RLE encoder cap size")
    parser.add_argument('-r', '--replace', action='store_true',
                        help='replace current archive with a new one.')

    # Parse arguments
    return parser.parse_args(argv)


def command_handler(args: Namespace) -> None:
    """
    Handle command-line arguments and execute corresponding actions.

    :param args: Parsed command-line arguments
    :return: None
    """
    # Handle different command line options
    if args.archive:
        try:
            if args.replace:
                try:
                    Path(args.save_path).unlink()
                except OSError:
                    print("Unable to delete archive. Adding to existing archive instead.")

            # Create archive from files
            if isinstance(args.file_path, str):
                add_files_to_archive(Path(args.file_path), Path(args.save_path), args.byte_size,
                                     match_relevant_compressor(args.compressor), args.password)
            else:
                file_paths_list = [Path(x) for x in args.file_path]
                add_files_to_archive(file_paths_list, Path(args.save_path), args.byte_size,
                                     match_relevant_compressor(args.compressor), args.password, args.cap_size)

        except TypeError:
            print("\nIncorrect Type inserted.")
            return

    elif args.open:
        try:
            # Inflate archive to files
            inflate_archive_to_files(Path(args.file_path), Path(args.save_path), args.password)
        except ValueError:
            print("\nOne of the values inserted is Incorrect")
            return
        except TypeError:
            print("\nIncorrect Type inserted.")
        except DecryptError:
            print("\nINCORRECT Password. Unable to Open archive. Try again")
            return

    elif args.validate:
        # Validate Archive
        if is_valid_archive(Path(args.file_path)):
            print("\nArchive Valid.")
            return
        else:
            print("\nInvalid Archive.")
            return

    elif args.inspect or args.delete:
        # Inspect Files in archive
        if not is_valid_archive(Path(args.file_path)):
            print("\nInvalid Archive, Unable to Inspect")
            return
        else:
            archive = open_archive_from_file(Path(args.file_path))
            if archive.is_protected():
                if args.password is None:
                    print("Protected Archive. Enter Password.")
                if archive.check_password(args.password):
                    print("Password Correct")
                else:
                    print("INCORRECT Password. Unable to Inspect archive. Try again")
                    return
            if args.inspect:
                print(archive.get_archive_contents())
            else:  # if delete file
                delete_indices = args.delete.split(',')
                archive.delete_files_from_archive(delete_indices)  # delete relevant files
                save_archive_to_file(archive, Path(args.file_path))  # replace archive with new one.
            return

    return


def validate_args(args: Namespace) -> bool:
    """
    Validate command-line arguments.

    :param args: Parsed command-line arguments
    :return: True if args are valid, False otherwise
    """
    # Validate command line arguments
    if args.file_path is None or args.file_path == "" or args.file_path == []:  # no file path
        print("\nPlease enter File path.")
        return False
    if isinstance(args.file_path, str):
        file_path = Path(args.file_path)
        if not file_path.exists():  # file path doesn't exist
            print("\nFile Doesn't exist")
            return False
        if args.open and Path(args.file_path).suffix != ".ido":
            print("\nCannot Open - not an archive file.")
            return False
    elif isinstance(args.file_path, list):
        for current_file_path in args.file_path:
            file_path = Path(current_file_path)
            if not file_path.exists():  # file path doesn't exist
                print("\nFile Doesn't exist")
                return False
            if args.open and file_path.suffix != ".ido":
                print("\nCannot Open - not an archive file.")
                return False

    if args.save_path is not None:  # if save path entered

        save_path = Path(args.save_path)
        # if it's a directory - check existence.
        if save_path.suffix == "":
            if not save_path.exists():
                print("Folder doesn't Exist")
                return False

        # if it's a file - check parent exists.
        else:
            if not save_path.parent.exists():
                print("Parent Folder doesn't Exist")

            # if wrong suffix entered.
            if save_path.suffix != ".ido" and save_path.suffix != '':
                print("Invalid File name - File should end with .ido")
                return False
    if args.byte_size <= 0:
        print("Invalid byte size - should be positive integer.")
        return False
    if args.cap_size <= 0:
        print("Invalid cap size - should be positive integer")
        return False
    if not match_relevant_compressor(args.compressor):
        print("Invalid Compressor Number. see -Help")
        return False
    if args.delete is not None:
        delete_indices = args.delete.split(',')
        for index in delete_indices:
            try:
                index_num = int(index)
            except ValueError:
                print("Invalid Index for delete.")
                return False
            if int(index_num) < 0:
                print("Invalid Index for delete.")
                return False

    return True


def match_relevant_compressor(comp_number: int) -> Union[Compressor, bool]:
    """
    Match compression algorithm number to corresponding compressor object
    :param comp_number:
    :return: Compressor name if exists, false otherwise
    """
    if comp_number == 0:
        return RLE_Compressor()
    elif comp_number == 1:
        return LZW_Compressor()
    else:
        return False


def run_file_compressor(args: Union[Namespace, None] = None) -> None:
    """
     Main function to run the file compressor
    :return: None
    """
    if args is None:
        args = None
        try:  # try to parse args
            args = parse_args(sys.argv[1:])
        except SystemExit:  # if error - print and exit
            if "--help" in sys.argv or "-h" in sys.argv:
                return
            else:
                print("Incorrect Arguments Entered.")
                return

    # validate args
    if validate_args(args):
        command_handler(args)  # if validated - run command handler.
    else:
        return


def default_args() -> Namespace:
    """
    function that creates a default namespace for command parsing in main
    :return: args namespace
    """
    return Namespace(
        archive=False,
        open=False,
        validate=False,
        inspect=False,
        password=None,
        byte_size=5,
        compressor=0,
        file_path=[],
        save_path=None,
        cap_size=99,
        delete=None,
        replace=False
    )


if __name__ == '__main__':
    run_file_compressor()
