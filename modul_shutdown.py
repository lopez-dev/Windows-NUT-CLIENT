import tkinter as tk
from tkinter import filedialog, messagebox
import configparser
import os
import time
import threading
import modul_livedata
import modul_usv_status
import subprocess
import os
import queue
from datetime import datetime
# Aktuelle Zeit und Datum holen
now = datetime.now()
# Zeit und Datum als String formatieren
current_time = now.strftime("%Y-%m-%d %H:%M:%S")


# Globale Variablen
test_ups_status = "OK"
ups_status = "OK"
shutdown_time = 0.0
remaining_time_shutdown = None
remaining_time_batch = None
batch_time = 0.0
batch_file_started = False
config = None

# Queue für GUI-Aktualisierung
gui_update_queue = queue.Queue()

# Mutex-Sperre für den Zugriff auf die GUI
gui_lock = threading.Lock()


def load_config():
    config_datei = configparser.ConfigParser()
    config_datei.read('config.ini')
    return config_datei


def save_config(config_datei):
    user_response = messagebox.askyesno("Bestätigung", "Möchten Sie diese Einstellungen speichern?")
    if user_response:
        with open('config.ini', 'w') as configfile:
            config_datei.write(configfile)
        messagebox.showinfo("Info", "Einstellungen gespeichert.")


def shutdown_system():
    user_response = messagebox.askyesno("Bestätigung", "Möchten Sie den Computer wirklich herunterfahren?")
    if user_response:
        os.system('shutdown /s /t 1')


def run_batch_file(batch_file_path):
    try:
        subprocess.Popen(f"cmd.exe /c {batch_file_path}", creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
        print(f"Fehler beim Ausführen der Batch-Datei: {e}")


def monitor_ups(conf, status_label, timer_label_shutdown, timer_label_batch):
    global test_ups_status, shutdown_time, remaining_time_shutdown, batch_time, \
        remaining_time_batch, batch_file_started
    while True:
        # Verwenden Sie den Status aus modul_usv_status
        real_ups_status = modul_usv_status.get_ups_status()
        # print(f"test_ups_status = {test_ups_status}")
        # print(f"ups_status = {real_ups_status}")
        if (test_ups_status == "Stromausfall" or real_ups_status == "Stromausfall") and allow_discharge.get():
            # Für Shutdown
            if remaining_time_shutdown is None:
                remaining_time_shutdown = shutdown_time

            # Für Batch-Datei
            if remaining_time_batch is None:
                remaining_time_batch = batch_time

            # Timer für Shutdown aktualisieren
            if remaining_time_shutdown is not None:
                minutes, seconds = divmod(remaining_time_shutdown, 60)
                hours, minutes = divmod(minutes, 60)
                timer_label_shutdown.config(
                    text=f"Verbleibende Zeit (Shutdown): {hours:02d}:{minutes:02d}:{seconds:02d}")
                remaining_time_shutdown -= 1

            # Timer für Batch-Datei aktualisieren
            if remaining_time_batch is not None:
                minutes, seconds = divmod(remaining_time_batch, 60)
                hours, minutes = divmod(minutes, 60)
                timer_label_batch.config(
                    text=f"Verbleibende Zeit (Batch): {hours:02d}:{minutes:02d}:{seconds:02d}")
                remaining_time_batch -= 1

            # Shutdown ausführen
            if remaining_time_shutdown <= 0:
                os.system('shutdown /s /t 1')

            # Batch-Datei ausführen # Überprüfen, ob die Batch-Datei bereits gestartet wurde
            if remaining_time_batch <= 0 and not batch_file_started and run_batch.get():
                batch_file_path = conf.get('batch', 'file_path', fallback='')
                run_batch_file(batch_file_path)
                batch_file_started = True  # Setzen Sie die Variable auf True, nachdem die Batch-Datei gestartet wurde

        else:
            remaining_time_shutdown = None
            remaining_time_batch = None
            batch_file_started = False  # Zurücksetzen der Variable
            timer_label_shutdown.config(text="Verbleibende Zeit (Shutdown): --:--:--")
            timer_label_batch.config(text="Verbleibende Zeit (Batch): --:--:--")

        status_label.config(text=f"USV Status: (TEST)={test_ups_status}  (REAL)=({real_ups_status})")
        time.sleep(1)


def toggle_ups_status():
    global test_ups_status
    if test_ups_status == "OK":
        test_ups_status = "Stromausfall"
        print(f"Test Stromausfall - {current_time}")
    else:
        test_ups_status = "OK"


def update_gui_from_queue(status_label, timer_label_shutdown, timer_label_batch):
    try:
        test_ups_status, real_ups_status = gui_update_queue.get_nowait()
        # Aktualisieren Sie die GUI-Elemente mit den erhaltenen Daten
        with gui_lock:
            status_label.config(text=f"USV Status: (TEST)={test_ups_status}  (REAL)=({real_ups_status})")
            # Weitere GUI-Aktualisierungen hier...
    except queue.Empty:
        pass

    # Planen Sie die nächste Aktualisierung nach einer Verzögerung
    status_label.after(100, update_gui_from_queue, status_label, timer_label_shutdown, timer_label_batch)


def create_gui(parent_frame=None, tree=None):
    global config
    config = load_config()
    global shutdown_time, batch_time, allow_discharge, run_batch
    root = parent_frame if parent_frame else tk.Tk()

    # Für Shutdown
    shutdown_time = int(float(config.get('shutdown', 'shutdown_time', fallback=0))) * 60

    # Für Batch-Datei
    batch_time = int(float(config.get('batch', 'batch_time', fallback=0)))
    batch_file_path = config.get('batch', 'file_path', fallback='')

    # Hinzugefügt: Eingabe- und Ausgabefeld für Batch-Dateipfad
    batch_file_path_entry = tk.Entry(root, width=50)
    batch_file_path_entry.grid(row=2, column=1)
    batch_file_path_entry.insert(0, config.get('batch', 'file_path', fallback=''))

    run_batch = tk.BooleanVar()
    run_batch.set(config.getboolean('batch', 'run_batch', fallback=False))

    if not parent_frame:
        root.title("Shutdown")

    allow_discharge = tk.BooleanVar()
    allow_discharge.set(config.getboolean('shutdown', 'allow_discharge', fallback=False))
    tk.Checkbutton(root, text="Entladung der Batterie erlauben für:", variable=allow_discharge).grid(row=0, column=0)

    shutdown_time_entry = tk.Entry(root)
    shutdown_time_entry.grid(row=0, column=1)
    shutdown_time_entry.insert(0, config.get('shutdown', 'shutdown_time', fallback=''))

    tk.Label(root, text="Minuten").grid(row=0, column=2)

    # Batch-Datei Optionen
    batch_time_entry = tk.Entry(root)
    batch_time_entry.grid(row=1, column=1)
    batch_time_entry.insert(0, config.get('batch', 'batch_time', fallback=''))

    tk.Checkbutton(root, text="Batch-Datei ausführen nach:", variable=run_batch).grid(row=1, column=0)
    tk.Label(root, text="Sekunden").grid(row=1, column=2)

    def browse_file():
        filepath = filedialog.askopenfilename()
        if filepath:
            batch_file_path_entry.delete(0, tk.END)
            batch_file_path_entry.insert(0, filepath)
            config.set('batch', 'file_path', filepath)
            save_config(config)

    tk.Button(root, text="Durchsuchen...", command=browse_file).grid(row=2, column=2)

    # ...

    def apply_changes():
        global shutdown_time, batch_time

        shutdown_time_str = shutdown_time_entry.get().strip()
        batch_time_str = batch_time_entry.get().strip()

        # Überprüfung und Hinzufügung fehlender Sektionen
        if not config.has_section('shutdown'):
            config.add_section('shutdown')
        if not config.has_section('batch'):
            config.add_section('batch')

        if shutdown_time_str:
            shutdown_time = int(float(shutdown_time_str)) * 60

        if batch_time_str:
            batch_time = int(float(batch_time_str))

        if shutdown_time_str:
            config.set('shutdown', 'shutdown_time', str(shutdown_time // 60))
        if batch_time_str:
            config.set('batch', 'batch_time', str(batch_time))

        # Hinzugefügt: Pfad der Batch-Datei speichern
        batch_path = batch_file_path_entry.get().strip()
        if batch_path:
            config.set('batch', 'file_path', batch_path)

        config.set('shutdown', 'allow_discharge', str(allow_discharge.get()))
        config.set('batch', 'run_batch', str(run_batch.get()))
        save_config(config)

    tk.Button(root, text="Speichern", command=apply_changes).grid(row=4, column=2)

    # Status Labels
    status_label = tk.Label(root, text=f"USV Status: {test_ups_status}")
    status_label.grid(row=5, column=0)

    countdown_label_shutdown = tk.Label(root, text="Verbleibende Zeit (Shutdown): --:--:--")
    countdown_label_shutdown.grid(row=6, column=0)

    countdown_label_batch = tk.Label(root, text="Verbleibende Zeit (Batch): --:--:--")
    countdown_label_batch.grid(row=7, column=0)

    tk.Button(root, text="Jetzt Herunterfahren", command=shutdown_system).grid(row=7, column=1)
    tk.Button(root, text="Toggle USV Status", command=toggle_ups_status).grid(row=8, column=1)

    ups_thread = threading.Thread(target=monitor_ups, args=(config, status_label, countdown_label_shutdown,
                                                            countdown_label_batch))
    ups_thread.daemon = True  # Markieren Sie den Thread als Hintergrundthread
    ups_thread.start()

    # Erstellen Sie einen Thread, um die GUI aus der Queue zu aktualisieren
    gui_update_thread = threading.Thread(target=update_gui_from_queue,
                                         args=(status_label, countdown_label_shutdown, countdown_label_batch))
    gui_update_thread.daemon = True
    gui_update_thread.start()

    if not parent_frame:
        root.mainloop()


if __name__ == "__main__":
    create_gui()
