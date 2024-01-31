import tkinter as tk
from tkinter import messagebox
import configparser
import modul_livedata


# Funktion zum Laden der Konfigurationsdatei
def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


# Funktion zum Speichern der Konfigurationsdatei
def save_config(config):
    user_response = messagebox.askyesno("Bestätigung", "Möchten Sie diese Einstellungen Speichern?")
    if user_response:
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        messagebox.showinfo("Info", "Einstellungen gespeichert.")


# Funktion zum Erstellen der GUI
def create_gui(parent_frame=None):  # Fügen Sie live_data_module als Argument hinzu
    root = tk.Frame(parent_frame) if parent_frame else tk.Tk()
    root.pack(fill=tk.BOTH, expand=1)
    config = load_config()

    if not parent_frame:
        root.master.title("Kommunikation")

    # Eingabefelder und Labels
    tk.Label(root, text="NUT Host:").grid(row=0, column=0)
    nut_host_entry = tk.Entry(root)
    nut_host_entry.grid(row=0, column=1)
    nut_host_entry.insert(0, config.get('nut', 'nut_host'))

    tk.Label(root, text="NUT Port:").grid(row=1, column=0)
    nut_port_entry = tk.Entry(root)
    nut_port_entry.grid(row=1, column=1)
    nut_port_entry.insert(0, config.get('nut', 'nut_port'))

    tk.Label(root, text="UPS Name:").grid(row=2, column=0)
    ups_name_entry = tk.Entry(root)
    ups_name_entry.grid(row=2, column=1)
    ups_name_entry.insert(0, config.get('nut', 'ups_name'))

    tk.Label(root, text="Polling interval:").grid(row=3, column=0)
    polling_interval_entry = tk.Entry(root)
    polling_interval_entry.grid(row=3, column=1)
    polling_interval_entry.insert(0, config.get('nut', 'polling_interval'))

    tk.Label(root, text="Username:").grid(row=4, column=0)
    username_entry = tk.Entry(root)
    username_entry.grid(row=4, column=1)
    username_entry.insert(0, config.get('nut', 'username'))

    tk.Label(root, text="Password:").grid(row=5, column=0)
    password_entry = tk.Entry(root)
    password_entry.grid(row=5, column=1)
    password_entry.insert(0, config.get('nut', 'password'))

    # Buttons
    def apply_changes():
        config.set('nut', 'nut_host', nut_host_entry.get())
        config.set('nut', 'nut_port', nut_port_entry.get())
        config.set('nut', 'ups_name', ups_name_entry.get())
        config.set('nut', 'polling_interval', polling_interval_entry.get())
        config.set('nut', 'username', username_entry.get())
        config.set('nut', 'password', password_entry.get())
        # ... Fügen Sie hier weitere Parameter hinzu ...
        save_config(config)
        # new_config = load_config()  # Lade die aktualisierte Konfiguration
        # live_data_module.update_gui(tree, new_config)  # Aktualisiere die GUI mit der neuen Konfiguration
        # Aufruf der load_config Funktion aus dem modul_livedata Modul
        modul_livedata.load_config()

    tk.Button(root, text="Speichern", command=lambda: apply_changes()).grid(row=7, column=1, pady=10)  # Ändern Sie hier

    if not parent_frame:
        root.mainloop()


# Hauptprogramm
if __name__ == "__main__":
    module.create_gui(parent_frame=None, tree=module.tree, live_data_module=module)
