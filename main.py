import os
import xml.sax.saxutils as saxutils

# --- Konfiguration ---
RECORDINGS_DIR = "/mnt/Medien/Videos/ts"  # Pfad zum Aufnahmeverzeichnis anpassen
DRY_RUN = False  # True = nur anzeigen, False = .nfo-Dateien tatsächlich schreiben
OVERWRITE = False  # True = bestehende .nfo-Dateien überschreiben


def make_nfo_for_meta(meta_path: str) -> None:
    base_path = os.path.splitext(os.path.splitext(meta_path)[0])[0]
    ts_path = base_path + ".ts"
    nfo_path = base_path + ".nfo"

    # Nur verarbeiten, wenn eine zugehörige .ts-Datei existiert
    if not os.path.exists(ts_path):
        print(f"[Übersprungen] Keine .ts-Datei gefunden für: {meta_path}")
        return

    if os.path.exists(nfo_path) and not OVERWRITE:
        print(f"[Vorhanden] .nfo existiert bereits: {nfo_path}")
        return

    # .meta-Datei mit Fallback-Encodings einlesen (Dreambox nutzt meist UTF-8 oder Latin-1)
    lines = None
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            with open(meta_path, "r", encoding=enc) as f:
                lines = [line.rstrip("\r\n") for line in f.readlines()]
            break
        except UnicodeDecodeError:
            continue

    if not lines:
        print(f"[Fehler] Konnte Datei nicht dekodieren: {meta_path}")
        return

    # Zeile 1 = Service-Ref, Zeile 2 = Titel, Zeile 3 = Beschreibung (optional)
    title = lines[1].strip() if len(lines) >= 2 and lines[1].strip() else os.path.basename(base_path)
    plot = lines[2].strip() if len(lines) >= 3 and lines[2].strip() else ""

    safe_title = saxutils.escape(title)
    safe_plot = saxutils.escape(plot)

    nfo_content = (
        '<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n'
        "<movie>\n"
        f"  <title>{safe_title}</title>\n"
    )
    if safe_plot:
        nfo_content += f"  <plot>{safe_plot}</plot>\n"
    nfo_content += "</movie>\n"

    if DRY_RUN:
        print(f"[DRY-RUN] Würde erstellen: {nfo_path}")
        print(f"          Titel: {title}")
        if plot:
            print(f"          Plot : {plot[:80]}{'...' if len(plot) > 80 else ''}")
    else:
        with open(nfo_path, "w", encoding="utf-8") as f:
            f.write(nfo_content)
        print(f"[Erstellt] {nfo_path} -> \"{title}\"")


def main() -> None:
    if not os.path.isdir(RECORDINGS_DIR):
        print(f"Verzeichnis nicht gefunden: {RECORDINGS_DIR}")
        return

    for root, _, files in os.walk(RECORDINGS_DIR):
        for filename in sorted(files):
            if filename.lower().endswith(".meta"):
                make_nfo_for_meta(os.path.join(root, filename))


if __name__ == "__main__":
    main()