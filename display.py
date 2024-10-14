import sys
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import ttk, filedialog

from compressor import CODE_BASE_PATH
from main import run_file_compressor, default_args
from tkinter import Tk
from tkinter.ttk import Label
from typing import Optional, Any
from tkinter.ttk import Entry
from typing import Union


class FileCompressorGUI:
    """
    this class manages the program GUI.
    """

    def __init__(self, root):
        # type: (Tk) -> None
        """
        the GUI init recieves a tk.root, and creates the tabs and GUI buttons& features
        on it.
        :param root:
        """
        # set the main window
        self.root = root
        self.root.title("IDO Compressor")
        # Create the main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)
        # set theme
        root.tk.call("source",  CODE_BASE_PATH / "azure.tcl")
        root.tk.call("set_theme", "dark")

        # Init params

        self.is_password = tk.BooleanVar()
        self.replace = tk.BooleanVar()
        self.replace.set(False)
        self.is_password.set(False)
        # compress params
        self.compress_file_path:list[str] = []
        self.compress_folder_path:Any = None
        self.compress_archive_path:Any = None

        # inflate params
        self.inflate_archive_path:Any = None
        self.inflate_save_path:Any = None
        # inspect params
        self.examine_archive_path:Any = None
        self.delete_indices_entry_val = tk.StringVar()
        self.delete_indices_entry_val.set("")

        # Create tabs for different functionalities
        self.create_compress_tab()
        self.create_inflate_tab()
        self.create_examine_tab()
        self.create_settings_tab()

    # Creating the FileCompressorGUI class

    def create_compress_tab(self):
        # type: () -> None
        """
        this function creates the compress tab
        :return: none
        """
        compress_tab = ttk.Frame(self.notebook)
        self.notebook.add(compress_tab, text="Compress")

        # File Select
        ttk.Label(compress_tab, text="File Select:").grid(row=0, column=0, sticky="w")
        self.compress_file_path_label = ttk.Label(compress_tab, text="No file selected")
        self.compress_file_path_label.grid(row=0, column=1)
        self.compress_file_button = ttk.Button(compress_tab, text="Select Files",
                                               command=lambda: self.select_files(self.compress_file_path_label))
        self.compress_file_button.grid(row=0, column=2)

        # Folder Select
        ttk.Label(compress_tab, text="Folder Select:").grid(row=1, column=0, sticky="w")
        self.compress_folder_path_label = ttk.Label(compress_tab, text="No folder selected")
        self.compress_folder_path_label.grid(row=1, column=1)
        self.compress_folder_path_button = ttk.Button(compress_tab, text="Select Folders",
                                                      command=lambda: self.select_folders(
                                                          self.compress_folder_path_label))
        self.compress_folder_path_button.grid(row=1, column=2)

        # Archive Save Path
        ttk.Label(compress_tab, text="Archive Save Path:").grid(row=2, column=0, sticky="w")
        self.compress_archive_path_label = ttk.Label(compress_tab, text="No path selected")
        self.compress_archive_path_label.grid(row=2, column=1)
        ttk.Button(compress_tab, text="Select Save Path",
                   command=lambda: self.save_archive(self.compress_archive_path_label)).grid(row=2, column=2)

        # Encrypt Password
        ttk.Label(compress_tab, text="Encrypt Password:").grid(row=3, column=0, sticky="w")
        self.compress_password_entry = ttk.Entry(compress_tab, show="*")
        self.compress_password_entry.grid(row=3, column=1)

        ttk.Checkbutton(compress_tab, text="Encrypt File", command=self.hide_password_entry,
                        variable=self.is_password).grid(
            row=3, column=2)

        hide_button(self.compress_password_entry)

        ttk.Checkbutton(compress_tab, text="Replace File",
                        variable=self.replace).grid(
            row=4, column=2)

        # Compress Button
        ttk.Button(compress_tab, text="Compress", command=self.compress).grid(row=4, column=0, columnspan=3)

    def create_inflate_tab(self):
        # type: () -> None
        """
        this function creates the inflate tab
        :return: none
        """
        inflate_tab = ttk.Frame(self.notebook)
        self.notebook.add(inflate_tab, text="Inflate")

        # Archive Select
        ttk.Label(inflate_tab, text="Archive Select:").grid(row=0, column=0, sticky="w")
        self.inflate_file_path_label = ttk.Label(inflate_tab, text="No file selected")
        self.inflate_file_path_label.grid(row=0, column=1)
        ttk.Button(inflate_tab, text="Select Archive",
                   command=lambda: self.select_archive(self.inflate_file_path_label)).grid(row=0, column=2)

        # Destination Path
        ttk.Label(inflate_tab, text="Destination Path:").grid(row=1, column=0, sticky="w")
        self.inflate_archive_path_label = ttk.Label(inflate_tab, text="No Path selected")
        self.inflate_archive_path_label.grid(row=1, column=1)
        ttk.Button(inflate_tab, text="Select Destination",
                   command=lambda: self.save_files(self.inflate_archive_path_label)).grid(row=1, column=2)

        # Decrypt Password
        ttk.Label(inflate_tab, text="Decrypt Password:").grid(row=2, column=0, sticky="w")
        self.inflate_password_entry = ttk.Entry(inflate_tab, show="*")
        self.inflate_password_entry.grid(row=2, column=1)

        # Inflate Button
        ttk.Button(inflate_tab, text="Inflate", command=self.inflate).grid(row=3, column=0, columnspan=3)

    def create_examine_tab(self):
        # type: () -> None
        """
        this function creates the inspect tab
        :return:
        """
        examine_tab = ttk.Frame(self.notebook)
        self.notebook.add(examine_tab, text="Examine")

        # Archive Select
        ttk.Label(examine_tab, text="Archive Select:").grid(row=0, column=0, sticky="w")
        self.examine_file_path_label = ttk.Label(examine_tab, text="No Archive selected")
        self.examine_file_path_label.grid(row=0, column=1)
        ttk.Button(examine_tab, text="Select Archive",
                   command=lambda: self.select_archive(self.examine_file_path_label, False)).grid(row=0, column=2)

        # Decrypt Password
        ttk.Label(examine_tab, text="Decrypt Password:").grid(row=2, column=0, sticky="w")
        self.examine_password_entry = ttk.Entry(examine_tab, show="*")
        self.examine_password_entry.grid(row=2, column=1)

        # File Delete Indices
        ttk.Label(examine_tab, text="File Delete Indices:").grid(row=3, column=0, sticky="w")
        self.delete_indices_entry = ttk.Entry(examine_tab, textvariable=self.delete_indices_entry_val)
        self.delete_indices_entry.grid(row=3, column=1)
        self.delete_indices_entry_val.trace_add('write', self.delete_indices_change)

        # Examine Button
        ttk.Button(examine_tab, text="Inspect Content", command=self.inspect).grid(row=4, column=0, sticky="s")
        ttk.Button(examine_tab, text="Delete From Archive", command=self.delete).grid(row=4, column=1)
        ttk.Button(examine_tab, text="Validate Archive", command=self.validate).grid(row=4, column=2)

    def create_settings_tab(self):
        # type: () -> None
        """
        this function creates the settings tab
        :return: none
        """
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")

        # Compressor
        self.combo_var = tk.StringVar()
        ttk.Label(self.settings_tab, text="Compressor:").grid(row=0, column=0, sticky="w")
        self.compressor_combo = ttk.Combobox(self.settings_tab, textvariable=self.combo_var, values=["RLE", "LZW"],
                                             state="readonly")
        self.compressor_combo.current(0)
        self.compressor_combo.grid(row=0, column=1)
        self.combo_var.set("RLE")
        self.combo_var.trace_add('write', self.compressor_change)

        # Byte Size

        self.byte_size_label = ttk.Label(self.settings_tab, text="Byte Size:")
        self.byte_size_label.grid(row=1, column=0, sticky="w")
        self.byte_size_entry = ttk.Entry(self.settings_tab)

        self.byte_size_entry.insert(tk.END, "5")
        self.byte_size_entry.grid(row=1, column=1)

        # Cap Size
        self.cap_size_label = ttk.Label(self.settings_tab, text="Cap Size:")
        self.cap_size_label.grid(row=2, column=0, sticky="w")

        self.cap_size_entry = ttk.Entry(self.settings_tab)
        self.cap_size_entry.insert(tk.END, "99")
        self.cap_size_entry.grid(row=2, column=1)

        # About Project Link
        link1 = ttk.Label(self.settings_tab, text="About Project", cursor="hand2")
        link1.grid(row=8, column=0)
        link1.bind("<Button-1>", lambda e: open_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))

    def select_files(self, label: Optional[Label] = None) -> None:
        """
        this opens a dialogue for file selection,
        and changes relevant variables and labels
        :param label: the label to change
        :return:none
        """
        file_paths = filedialog.askopenfilenames()
        file_names_str = ""
        if file_paths != "":
            self.compress_file_path = [x for x in file_paths]

        for file in file_paths:
            file_names_str += Path(file).name + ", "

        file_names_str = file_names_str[:-2]
        if file_paths:
            if label is not None:
                label.config(text=file_names_str)

    # Function to handle file selection for compression

    def select_folders(self, label:Any="")-> None:

        """
        this opens a dialogue for folder selection,
        and changes relevant variables and labels
        :param label:
        :return: none
        """
        file_paths = filedialog.askdirectory()

        if file_paths != "":
            self.compress_folder_path = file_paths

        if file_paths:
            if label != "":
                label.config(text=file_paths)

    # Function to handle folder selection for compression

    def save_archive(self, label=None):
        # type: (Optional[Label]) -> None
        """
        this opens a dialogue for ".ido" archive save,
        and changes relevant variables and labels
        :param label:
        :return: none
        """
        file_path = filedialog.asksaveasfilename(filetypes=[("IDO files", "*.ido")], defaultextension=".ido")
        if label is not None:
            label.config(text=file_path)
        if file_path != "":
            self.compress_archive_path = file_path

    # Function to handle saving the compressed archive

    def save_files(self, label:Any=None) -> None:
        file_path = filedialog.askdirectory()
        if file_path != "":
            self.inflate_save_path = file_path

        if label is not None:
            label.config(text=file_path)

    # Function to handle selecting the destination path for inflated files

    def select_archive(self, label=None, inflate_flag=True):
        # type: (Any, bool) -> None
        """
        this opens a dialogue for ".ido" archive select,
        and changes relevant variables and labels
        :param label:
        :return: none
        """
        file_path = filedialog.askopenfilename(filetypes=[("IDO files", "*.ido")])
        if label is not None:
            label.config(text=file_path)

        if file_path != "":
            if inflate_flag:
                self.inflate_archive_path = file_path
            else:
                self.examine_archive_path = file_path

    # Function to handle selecting the archive file for inflation or inspection

    def hide_password_entry(self):
        # type: () -> None
        """
        this function hides/shows the password entry, based on the is_password value
        :return:
        """
        if not self.is_password.get():
            hide_button(self.compress_password_entry)
        else:
            show_button(self.compress_password_entry)

    # Function to handle hiding the password entry field

    def compressor_change(self, *args):
        # type: (*str) -> None
        """
        this function manages the change of compressor in the settings tab
        it shows/hides relevant buttons.
        :param args:  none
        :return: none
        """
        if self.compressor_combo.get() == "LZW":
            self.combo_var.set("LZW")
            hide_button(self.cap_size_entry)
            hide_button(self.byte_size_entry)
            hide_button(self.cap_size_label)
            hide_button(self.byte_size_label)
        else:
            self.combo_var.set("RLE")
            show_button(self.cap_size_entry, 2, 1)
            show_button(self.byte_size_entry, 1, 1)
            show_button(self.byte_size_label, 1, 0)
            show_button(self.cap_size_label, 2, 0)

    def delete_indices_change(self, *args: Any) -> None:
        # Function to handle changes in the deleted indices entry field
        self.delete_indices_entry_val.set(self.delete_indices_entry.get())

    def compress(self):
        # type: () -> None
        """
        this function redirects the input from the GUI,
        and calls the compress command in the main program file.
        :return:
        """
        # create default args for main
        args = default_args()
        # get file and folder paths.
        file_paths = []
        if self.compress_file_path is not None:
            file_paths = [x for x in self.compress_file_path]
        folder_path = None
        if self.compress_folder_path is not None:
            args.file_path = file_paths + [self.compress_folder_path]
        else:
            args.file_path = file_paths
        # get save path
        args.save_path = self.compress_archive_path
        # get password if entered.
        if self.is_password.get():
            args.password = self.compress_password_entry.get()
        # get data from settings tab.
        if self.combo_var.get() == "RLE":
            try:
                args.byte_size = int(self.byte_size_entry.get())
            except ValueError:
                print("Invalid byte size Value")
            try:
                args.cap_size = int(self.cap_size_entry.get())
            except ValueError:
                print("Invalid cap size Value")
            args.compressor = 0
        else:
            args.compressor = 1

        args.replace = self.replace.get()
        # set action to archive and run
        args.archive = True
        run_file_compressor(args)

    def inflate(self):
        # type: () -> None
        """
        this function redirects the input from the GUI,
        and calls the inflate command in the main program file.
        :return:
        """
        # set args as default
        args = default_args()
        # get args from gui
        args.file_path = self.inflate_archive_path
        args.save_path = self.inflate_save_path
        args.password = self.inflate_password_entry.get()
        args.open = True
        # call open command
        run_file_compressor(args)

    def inspect(self):
        # type: () -> None
        """
        redirect GUI input to main inspect function
        :return: none
        """
        # get default args
        args = default_args()
        # get args from gui
        args.file_path = self.examine_archive_path
        args.password = self.examine_password_entry.get()
        args.inspect = True
        # run command
        run_file_compressor(args)

    def delete(self):
        # type: () -> None
        """
        redirect GUI input to main delete function
        :return:
        """
        # set default args
        args = default_args()
        # get data from gui
        args.file_path = self.examine_archive_path
        args.password = self.examine_password_entry.get()
        args.delete = self.delete_indices_entry_val.get()
        # run main command.
        run_file_compressor(args)

    def validate(self):
        # type: () -> None
        # get default args
        args = default_args()
        # get args from gui
        args.file_path = self.examine_archive_path
        args.password = self.examine_password_entry.get()
        args.validate = True
        # run command
        run_file_compressor(args)


def hide_button(widget):
    # type: (Union[Entry, Label]) -> None
    # hides a widget
    widget.grid_forget()


def show_button(widget, row=3, column=1):
    # type: (Union[Entry, Label], int, int) -> None
    # places a widget on given coordinates in the grid
    widget.grid(row=row, column=column)


def open_url(url:str)-> None:
    # Function to open a URL in the default web browser
    webbrowser.open_new(url)


# Function to set default arguments


class PrintRedirector():
    """
    this function redirects the print from the command line to a new window
    that opens and closes after a few seconds
    """

    # init new output window
    def __init__(self, root):
        # type: (Tk) -> None
        self.root = root
        self.text_widget: Any = None
        self.output_window: Any = None



    def write(self, text):
        # type: (str) -> None
        """
        this function overwrites the text command from stdout.
        it recieves the original text, and outputs it via a window in tkinter.
        :param text: text to be printed
        :return: none
        """
        # Create a new output window if it's not already open
        if not self.output_window or not self.output_window.winfo_exists():
            self.create_output_window()

        # Write the text to the Text widget
        self.text_widget.insert("end", text)
        self.text_widget.see("end")

    def create_output_window(self) -> None:

        """
        creates an output window for the message
        :return: none
        """
        # create tk window
        self.output_window = tk.Toplevel(self.root)
        self.output_window.title("Message")
        self.output_window.geometry("300x220")
        # create text widget in it
        self.text_widget = tk.Text(self.output_window, wrap="word")
        self.text_widget.pack(fill="y", expand=True)

        # Schedule closing the window after 2 seconds
        self.output_window.after(2500, self.close_output_window)

    def close_output_window(self):
        # type: () -> None
        # close the output window
        if self.output_window and self.output_window.winfo_exists():
            self.output_window.destroy()

    def flush(self)-> None:
        pass


def run_program_gui():
    # type: () -> None
    """
    this function runs the GUI.
    :return: none
    """
    # create new root
    root = tk.Tk()
    # switch between the normal stdout and print redirector class.
    old_out = sys.stdout
    redirect:Any = PrintRedirector(root)
    sys.stdout = redirect

    # set icon
    try:
        root.iconbitmap(CODE_BASE_PATH / "theme/IDO_file_compressor.ico")
    except tk.TclError:
        pass

    # call GUI init
    app = FileCompressorGUI(root)
    # run GUI
    root.mainloop()
    # when finished - reset the stdout.
    sys.stdout = old_out


if __name__ == "__main__":
    run_program_gui()
