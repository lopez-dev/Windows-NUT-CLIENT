import tkinter as tk
from tkinter import ttk
import modul_livedata
import modul_shutdown
import modul_communication
import sys  # Für sys.exit()


def main():
    global root
    root = tk.Tk()
    root.title("Windows NUT Client")

    # Erstellen des Notebook (Tabs)
    notebook = ttk.Notebook(root)

    # LiveData-Tab
    livedata_frame = ttk.Frame(notebook)
    notebook.add(livedata_frame, text="Live Daten")
    modul_livedata.create_gui(livedata_frame)

    # Shutdown-Tab
    shutdown_frame = ttk.Frame(notebook)
    notebook.add(shutdown_frame, text="Shutdown")
    modul_shutdown.create_gui(shutdown_frame)

    # Kommunikation-Tab
    communication_frame = ttk.Frame(notebook)
    notebook.add(communication_frame, text="Kommunikation")
    modul_communication.create_gui(communication_frame)

    notebook.pack(expand=1, fill="both")

    # Starten Sie den Event-Loop der GUI
    root.mainloop()


if __name__ == "__main__":
    main()
