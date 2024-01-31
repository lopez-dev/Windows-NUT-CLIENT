import tkinter as tk
from tkinter import ttk
from nut2 import PyNUTClient, PyNUTError
import configparser
import time
import modul_usv_status
import sys

current_config = None
nut_client = None


def load_config():
    global current_config
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
        if config.sections():
            current_config = config
            return config
        else:
            print("Konfigurationsdatei konnte nicht geladen werden.")
            return None
    except Exception as e:
        print(f"Fehler beim Laden der Konfigurationsdatei: {e}")
        return None


def disconnect_usv():
    global nut_client
    if nut_client:
        try:
            nut_client.disconnect()
            print("Verbindung zur USV wurde getrennt.")
        except Exception as e:
            print(f"Fehler beim Trennen der Verbindung zur USV: {e}")
        nut_client = None


def fetch_ups_data(tree, status_label):
    global current_config, nut_client

    if current_config:
        nut_host = current_config.get('nut', 'nut_host')
        nut_port = current_config.get('nut', 'nut_port')
        ups_name = current_config.get('nut', 'ups_name')
        username = current_config.get('nut', 'username', fallback=None)
        password = current_config.get('nut', 'password', fallback=None)

        try:
            if nut_client is None:
                nut_client = PyNUTClient(host=nut_host, port=int(nut_port), login=username, password=password)
            # nut_client.connect()  # Diese Zeile entfernen

            ups_data = nut_client.list_vars(ups_name)
            modul_usv_status.update_ups_data(ups_data)

            status_label.config(text="Verbindung OK", fg="green")

            tree.delete(*tree.get_children())
            for key, value in ups_data.items():
                tree.insert("", tk.END, values=(key, value))

        except Exception as e:
            print(f"Fehler beim Abrufen der UPS-Daten: {e}")
            status_label.config(text=f"Verbindung fehlgeschlagen: {e}", fg="red")

    polling_interval = int(current_config.get('general', 'polling_interval', fallback=10000))
    root.after(polling_interval, lambda: fetch_ups_data(tree, status_label))


def create_gui(parent_frame=None):
    global current_config, root
    root = parent_frame if parent_frame else tk.Tk()
    current_config = load_config()

    if not current_config:
        print("Keine gültige Konfiguration gefunden.")
        return

    tree = ttk.Treeview(root, columns=("Variable", "Wert"), show="headings")
    tree.heading("#1", text="Variable")
    tree.heading("#2", text="Wert")
    tree.pack()

    status_label = tk.Label(root, text="Verbindungsstatus wird überprüft...", fg="blue")
    status_label.pack()

    reload_button = tk.Button(root, text="Konfiguration neu laden",
                              command=lambda: fetch_ups_data(tree, status_label))
    reload_button.pack()

    fetch_ups_data(tree, status_label)
    root.after(10000, lambda: fetch_ups_data(tree, status_label))

    if not parent_frame:
        try:
            root.mainloop()
        finally:
            on_closing(root)


def on_closing(root):
    print("Closing event triggered in main.")
    disconnect_usv()
    sys.exit(0)


if __name__ == "__main__":
    try:
        create_gui()
    except Exception as e:
        print(f"Fehler beim Starten der GUI: {e}")
    finally:
        on_closing(root)
