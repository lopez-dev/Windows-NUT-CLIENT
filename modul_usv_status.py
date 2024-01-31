from datetime import datetime
# Aktuelle Zeit und Datum holen
now = datetime.now()
# Zeit und Datum als String formatieren
current_time = now.strftime("%Y-%m-%d %H:%M:%S")

# Hier können Sie Variablen und Funktionen für den USV-Status definieren
ups_data = {}  # Ein leeres Dictionary für die USV-Daten


def update_ups_data(data):
    """
    Aktualisiert die USV-Daten im Modul mit den neuen Daten.

    Args:
        data (dict): Ein Dictionary mit den aktuellen USV-Daten.
    """
    global ups_data
    ups_data = data
    # print(f"UPS Daten in modul_usv_status: {ups_data}")


def is_power_online(status_ups):
    """
    Überprüft, ob die USV online (ohne Stromausfall) ist.

    Args:
        status_ups (str): Der Wert von 'ups.status' aus den USV-Daten.

    Returns:
        bool: True, wenn die USV online ist, False, wenn ein Stromausfall vorliegt.
    OL = ONLINE
    OL CHRG = ONLINE AND CHARGING
    OB = ON BATTERY
    """
    # Wenn 'ups.status' den Wert 'OL' oder 'OL CHRG' hat, bedeutet dies, dass die USV online ist
    return 'OL' in status_ups


test = True


def get_ups_status():
    """
    Bestimmt den Status der USV basierend auf den aktuellen USV-Daten.

    Returns:
        str: "OK", wenn die USV online ist (kein Stromausfall), "Stromausfall" sonst.
    """
    global ups_data
    ups_status = ups_data.get('ups.status', 'Unknown')
    # print(f"Der aktuelle ups.status ist: {ups_status}")  # Zum Debuggen

    if is_power_online(ups_status):
        return "OK"
    else:
        print(f"Stromausfall - {current_time}")
        return "Stromausfall"


def process_usv_data():
    """
    Diese Funktion kann verwendet werden, um weitere Verarbeitung der USV-Daten hinzuzufügen, falls erforderlich.
    """
    global ups_data
