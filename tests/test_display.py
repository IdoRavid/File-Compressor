import pytest
from tkinter import Tk
from unittest.mock import patch
from display import FileCompressorGUI, PrintRedirector, run_program_gui
from flaky import flaky
from main import default_args


@pytest.fixture
def root():
    root = Tk()
    yield root
    root.destroy()


@pytest.fixture
def gui(root):
    return FileCompressorGUI(root)


@flaky(10)
def test_compressor_change():
    root = Tk()
    gui = FileCompressorGUI(root)
    # Testing compressor change
    gui.root.update()
    gui.notebook.select(gui.settings_tab)
    gui.root.update()
    gui.compressor_combo.set("LZW")
    gui.root.update()

    assert not gui.cap_size_entry.winfo_viewable()
    assert not gui.byte_size_entry.winfo_viewable()

    gui.compressor_combo.set("RLE")
    gui.root.update()
    assert gui.cap_size_entry.winfo_viewable()
    assert gui.byte_size_entry.winfo_viewable()


@flaky(5)
def test_validation_invalid_files(gui):
    with patch('tkinter.filedialog.askopenfilenames', return_value=""):
        gui.select_files()
        assert gui.compress_file_path_label.cget("text") == "No file selected"


@flaky(5)
def test_print_redirector_write(gui):
    redirector = PrintRedirector(gui.root)
    redirector.create_output_window()  # Ensure output window is created
    with patch.object(redirector.text_widget, 'insert') as mock_insert:
        redirector.write("Test message")
        mock_insert.assert_called_once_with("end", "Test message")
    redirector.close_output_window()


@flaky(5)
def test_validation_invalid_archive_path(gui):
    with patch('tkinter.filedialog.asksaveasfilename', return_value=""):
        gui.save_archive()
        assert gui.compress_archive_path_label.cget("text") == "No path selected"


@flaky(5)
def test_validation_invalid_input(gui):
    gui.byte_size_entry.insert(0, "invalid")
    gui.compress()
    assert gui.compress_archive_path_label.cget("text") == "No path selected"


@flaky(5)
def test_interaction_select_files(gui):
    with patch('tkinter.filedialog.askopenfilenames', return_value=["file1", "file2"]):
        gui.select_files(gui.compress_file_path_label)
        assert gui.compress_file_path_label.cget("text") == "file1, file2"


@flaky(5)
def test_interaction_select_folders(gui):
    with patch('tkinter.filedialog.askdirectory', return_value="/path/to/folder"):
        gui.select_folders(gui.compress_folder_path_label)
        assert gui.compress_folder_path_label.cget("text") == "/path/to/folder"


@flaky(5)
def test_run_program_gui():
    # Testing the run_program_gui function
    with patch('tkinter.Tk.mainloop') as mock_mainloop:
        run_program_gui()
        mock_mainloop.assert_called_once()


@flaky(5)
@patch('display.run_file_compressor')
def test_compress_with_password(mock_run_file_compressor, gui):
    # Testing the compress method with a password given
    # Set up initial state
    gui.compress_password_entry.insert(0, "password123")
    gui.is_password.set(True)
    # Call the compress method
    gui.compress()

    # Assert that run_file_compressor was called with the correct arguments
    expected_args = default_args()
    expected_args.password = "password123"
    expected_args.archive = True
    mock_run_file_compressor.assert_called_once_with(expected_args)


@flaky(5)
def test_invalid_cap_size_value(gui):
    # Testing invalid cap size value
    gui.compressor_combo.set("RLE")
    gui.cap_size_entry.delete(0, 'end')
    gui.cap_size_entry.insert(0, "invalid")
    gui.byte_size_entry.insert(0, "5")
    gui.compress()
    assert gui.compress_archive_path_label.cget("text") == "No path selected"


@flaky(5)
def test_select_archive(gui):
    # Testing select archive
    with patch('tkinter.filedialog.askopenfilename', return_value="selected_archive.ido"):
        gui.select_archive(gui.inflate_file_path_label)
        assert gui.inflate_archive_path == "selected_archive.ido"
        assert gui.inflate_file_path_label.cget("text") == "selected_archive.ido"


@flaky(5)
def test_save_archive(gui):
    # Testing save archive
    with patch('tkinter.filedialog.asksaveasfilename', return_value="saved_archive.ido"):
        gui.save_archive(gui.compress_archive_path_label)
        assert gui.compress_archive_path == "saved_archive.ido"
        assert gui.compress_archive_path_label.cget("text") == "saved_archive.ido"

@flaky(5)
def test_hide_and_show_password_entry():
    root = Tk()
    gui = FileCompressorGUI(root)
    # Testing compressor change
    gui.root.update()
    # Test hiding password entry
    assert not gui.compress_password_entry.winfo_viewable()
    gui.root.update()
    gui.is_password.set(True)
    gui.hide_password_entry()
    gui.root.update()
    assert gui.compress_password_entry.winfo_viewable()
    # Test showing password entry
    gui.is_password.set(False)
    gui.hide_password_entry()  # Hide it again to simulate user action
    gui.root.update()
    assert not gui.compress_password_entry.winfo_viewable()
    gui.root.update()

def test_inflate_command(gui):
    gui.inflate_archive_path = "/path/to/archive.ido"
    gui.inflate_save_path = "/path/to/save/location"
    gui.inflate_password_entry.insert(0, "password123")

    with patch("display.run_file_compressor") as mock_run_file_compressor:
        # Run inflate command
        gui.inflate()

        # Extract and verify the arguments passed to run_file_compressor
        args = mock_run_file_compressor.call_args[0][0]  # Extract arguments from the first call
        expected_args = default_args()
        expected_args.file_path = "/path/to/archive.ido"
        expected_args.save_path = "/path/to/save/location"
        expected_args.password = "password123"
        expected_args.open = True

        assert args == expected_args, "Arguments passed to run_file_compressor do not match expected arguments"





def test_inspect_command(gui):
    # Fill basic params for inspect command
    gui.examine_archive_path = "/path/to/archive.ido"
    gui.examine_password_entry.insert(0, "password123")

    with patch("display.run_file_compressor") as mock_run_file_compressor:
        # Run inspect command
        gui.inspect()

    args = mock_run_file_compressor.call_args[0][0]  # Extract arguments from the first call
    expected_args = default_args()
    expected_args.file_path = "/path/to/archive.ido"
    expected_args.password = "password123"
    expected_args.inspect = True

    assert args == expected_args, "Arguments passed to run_file_compressor do not match expected arguments"

@flaky(5)
def test_delete_command(gui):

    # Fill basic params for delete command
    gui.examine_archive_path = "/path/to/archive.ido"
    gui.examine_password_entry.insert(0, "password123")
    gui.delete_indices_entry.insert(0, "1,2,3")  # Assuming you need to specify indices to delete
    # Run delete command
    gui.delete_indices_change()
    with patch("display.run_file_compressor") as mock_run_file_compressor:
        # Run inspect command
        gui.delete()

    args = mock_run_file_compressor.call_args[0][0]  # Extract arguments from the first call
    expected_args = default_args()
    expected_args.file_path = "/path/to/archive.ido"
    expected_args.password = "password123"
    expected_args.delete = "1,2,3"

    assert args == expected_args, "Arguments passed to run_file_compressor do not match expected arguments"


def test_validate_command(gui):
    # Fill basic params for inspect command
    gui.examine_archive_path = "/path/to/archive.ido"
    gui.examine_password_entry.insert(0, "password123")

    with patch("display.run_file_compressor") as mock_run_file_compressor:
        # Run inspect command
        gui.validate()

    args = mock_run_file_compressor.call_args[0][0]  # Extract arguments from the first call
    expected_args = default_args()
    expected_args.file_path = "/path/to/archive.ido"
    expected_args.password = "password123"
    expected_args.validate = True

    assert args == expected_args, "Arguments passed to run_file_compressor do not match expected arguments"



if __name__ == "__main__":
    pytest.main([__file__])
