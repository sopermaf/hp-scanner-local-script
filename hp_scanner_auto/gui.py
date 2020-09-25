import os
import tkinter as tk
from functools import partial

from . import scanner
from .templates import folders, files



class ScannerGUI(tk.Frame):
    def __init__(self, master=None, folder_temps=None, file_temps=None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.create_widgets(
            folder_temps or [],
            file_temps or [],
        )

        self.folder_temps = folder_temps
        self.file_temps = file_temps
        self.t_folder = None
        self.t_file = None

    def create_widgets(self, folder_temps, file_temps):
        # show templates
        self.setup_template_listbox('folders', folder_temps)
        self.setup_template_listbox('files', file_temps)

        # show chosen option
        self.filepath_str = tk.StringVar(self, value='')
        self.filepath_label = tk.Entry(self, textvariable=self.filepath_str, width=100, bg="yellow")
        self.filepath_label.pack()

        # activate button
        self.scan = tk.Button(self, text="Start Scan", command=self.scan_document)
        self.scan.pack(side="left")

        self.add_folders = tk.Button(
            self,
            text="Add Folder Template",
            command=partial(self.extend_template, "folder"),
        )
        self.add_folders.pack(side="right")

        self.add_files = tk.Button(
            self,
            text="Add File Template",
            command=partial(self.extend_template, "file"),
        )
        self.add_files.pack(side="right")

        # show status
        self.status_text = tk.StringVar(self, value='')
        self.status = tk.Label(self, textvariable=self.status_text)
        self.status.pack(side="bottom")


    def scan_document(self):
        # reset warnings
        self.status_text.set('')
        self.status.config(fg='green')

        # get filepath and validate
        save_filepath = self.filepath_str.get().strip()
        if not save_filepath:
            self.status.config(fg='red')
            self.status_text.set('Set filepath first')
            return
        if not save_filepath.endswith('.pdf'):
            save_filepath += '.pdf'
            self.filepath_str.set(save_filepath)

        # attempt scan
        self.status_text.set(f'Attempting scan: {save_filepath}')
        scanner.automate_scan_process(
            printer_ip=os.environ['PRINTER_IP'],
            filepath=save_filepath
        )
        self.status_text.set(f'Scanned successfully.\nSaved as {save_filepath}')

    def extend_template(self, temp_type):
        if temp_type not in {'folder', 'file'}:
            raise ValueError('Invalid template type')

        widget = self.__dict__[f'{temp_type}s']
        temps = self.__dict__[f'{temp_type}_temps']

        # add new val to widget and templates
        val = self.filepath_str.get()
        temps.append(val)
        widget.insert(tk.END, val)


    def on_select(self, evt):
        new_t_folder = self._get_selected(self.folders)
        if new_t_folder:
            self.t_folder = new_t_folder

        new_t_file = self._get_selected(self.files)
        if new_t_file:
            self.t_file = new_t_file

        t_full = f'{self.t_folder}/{self.t_file}' if self.t_file else self.t_folder

        self.filepath_str.set(t_full)

    @classmethod
    def _get_selected(cls, widget):
        try:
            index = widget.curselection()[0]
            seleted = widget.get(index)
        except IndexError:
            seleted = ""

        return seleted

    def setup_template_listbox(self, name, vals):
        self.__dict__[name] = tk.Listbox(self, selectmode=tk.EXTENDED)

        template_widget = self.__dict__[name]

        for template in vals:
            template_widget.insert(tk.END, template)
        template_widget.bind('<<ListboxSelect>>', self.on_select)
        template_widget.pack(fill=tk.BOTH, expand=1)


def launch_gui():
    root = tk.Tk()
    root.title("HP Scanner Helper")
    root.geometry("2000x1200")

    app = ScannerGUI(
        master=root,
        folder_temps=folders,
        file_temps=files,
    )
    app.mainloop()
