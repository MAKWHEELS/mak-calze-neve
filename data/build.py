#!/usr/bin/env python3
"""
Costruisce data/socks.json e rigenera index.html per la web app
"Calze da neve NPK - scelta taglia".

    python3 data/build.py

Fonti dati:
  - Light / RE Grip : data/light-regrip-rev05.txt, dal PDF REV 05 del 05/11/2026       (TAGLIA 1..9)
  - Grip 3D         : data/grip3d-rev01.txt, trascrizione controllata sul PDF REV 01  (XS..XXL)
  - The Original    : data/original-rev03.txt, dal PDF REV 03 sul sito NPK               (TG.69..TG.97)
  - EZ Socks        : pdf/ez-socks.pdf, estratto con pdfplumber (XSMALL..XXXLARGE)

RE Grip usa la stessa tabella di Light (il PDF ufficiale e' un unico documento
"RE-GRIP & MULTIGRIP LIGHT", confermato: stesse taglie 1/2/3...).

Per Grip 3D i dati vengono dalla trascrizione controllata sul PDF,
non dal PDF direttamente: il loro layout (etichette taglia ruotate 90 gradi,
blocchi che continuano tra pagine) non si estrae bene. EZ Socks non ha trascrizione,
ma il suo PDF ha una griglia con bordi cella leggibili da pdfplumber.extract_table():
si separano le bande sulla prima colonna (etichetta taglia verticale) e si mappano
in ordine su XSMALL..XXXLARGE.

Dipendenze: pip3 install pdfplumber
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MAK = os.path.dirname(REPO)

TXT_LIGHT = os.path.join(HERE, "light-regrip-rev05.txt")
TXT_GRIP3D = os.path.join(HERE, "grip3d-rev01.txt")
TXT_ORIGINAL = os.path.join(HERE, "original-rev03.txt")
PDF_EZ = os.path.join(REPO, "pdf", "ez-socks.pdf")

# ---------------------------------------------------------------- normalizzazione misure
# accetta: 135/70R13 | 135/70 R13 | 135/80/13 | 215/75R17,5 | 215/75 R 17.5
TIRE_RE = re.compile(r"(\d{2,3})\s*/\s*(\d{2})\s*[R/]\s*(\d{2}(?:[.,]\d)?)")


def norm_tire(w, s, d):
    d = d.replace(",", ".")
    return f"{w}/{s}R{d}"


def find_tires(text):
    return [norm_tire(*m) for m in TIRE_RE.findall(text)]


def split_key(key):
    """195/55R16 -> (195, 55, '16')  |  215/75R17.5 -> (215, 75, '17.5')"""
    m = re.match(r"^(\d{2,3})/(\d{2})R(\d{2}(?:\.\d)?)$", key)
    w, s, d = m.group(1), m.group(2), m.group(3)
    return int(w), int(s), d


# ---------------------------------------------------------------- parser tabelle .txt
def parse_txt(path, header_re):
    """File con blocchi:  '<header> <TAGLIA>' seguito da una misura per riga."""
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    blocks = {}
    cur = None
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        m = header_re.match(line)
        if m:
            cur = m.group(1).strip()
            blocks.setdefault(cur, set())
            continue
        if cur is None:
            continue
        for t in find_tires(line):
            blocks[cur].add(t)
    return {k: v for k, v in blocks.items() if v}


def parse_light():
    hdr = re.compile(r"^NPK\s+LIGHT\s+TAGLIA\s+(.+)$", re.I)
    return parse_txt(TXT_LIGHT, hdr)


def parse_grip3d():
    hdr = re.compile(r"^NPK\s+GRIP\s*3D\s+TAGLIA\s+(.+)$", re.I)
    return parse_txt(TXT_GRIP3D, hdr)


def parse_original():
    hdr = re.compile(r"^NPK\s+ORIGINAL\s+TAGLIA\s+(.+)$", re.I)
    return parse_txt(TXT_ORIGINAL, hdr)


# ---------------------------------------------------------------- parser EZ Socks (PDF)
EZ_SEQ = ["XSMALL", "SMALL", "MEDIUM", "LARGE", "XLARGE", "XXLARGE", "XXXLARGE"]
_EZ_TIRE = re.compile(r"^(\d{2,3})/(\d{2})\s*R\s*(\d{2})(?:[.,](\d))?$")


def parse_ez():
    """
    Il PDF EZ Urban e' una griglia (diametri in colonna, una banda per taglia).
    L'etichetta taglia e' testo verticale nella prima colonna, presente solo sulla
    riga d'inizio di ogni banda. pdfplumber.extract_table() rende la griglia:
    si spezza in bande dove la col. 0 non e' vuota e si mappano in ordine su EZ_SEQ.
    """
    try:
        import pdfplumber
    except ImportError:
        sys.exit("Manca pdfplumber: pip3 install pdfplumber")
    import warnings

    bands = []  # [ [label_raw, set(misure)], ... ]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with pdfplumber.open(PDF_EZ) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if not table:
                    continue
                for row in table[1:]:  # salta la riga d'intestazione diametri
                    label = re.sub(r"[^A-Z]", "", (row[0] or "").upper())
                    row_tires = set()
                    for cell in row[1:]:
                        if not cell:
                            continue
                        m = _EZ_TIRE.match(cell.replace(" ", ""))
                        if m:
                            w, s, d, dec = m.groups()
                            row_tires.add(f"{w}/{s}R{d}" + (f".{dec}" if dec else ""))
                    if label:
                        bands.append([label, set()])
                    if bands:
                        bands[-1][1].update(row_tires)

    if len(bands) != len(EZ_SEQ):
        sys.exit(
            f"parse_ez: trovate {len(bands)} bande, attese {len(EZ_SEQ)} "
            f"({EZ_SEQ}). Il PDF EZ e' cambiato: verificare data/_raw_tables.md."
        )

    table = {}
    for i, (label_raw, tires) in enumerate(bands):
        size = EZ_SEQ[i]
        # cross-check: l'etichetta verticale (letta al contrario) contiene la taglia?
        decoded = label_raw[::-1]
        if not all(ch in decoded for ch in size):
            print(f"  [avviso] EZ banda {i} '{decoded}' non combacia con {size}")
        table[size] = tires
    return table


# ---------------------------------------------------------------- modelli
MODELS = [
    {
        "slug": "the-original",
        "name": "The Original",
        "subtitle": "NPK Multigrip - The Original Snow Socks",
        "image": "assets/the-original.png",
        "pdf": "pdf/the-original.pdf",
        "site": "https://noproblemkit.com/wp-content/uploads/2026/08/Snow-Socks-The-Original-updated-2020812.pdf",
        "source": "original",
    },
    {
        "slug": "light",
        "name": "Light",
        "subtitle": "NPK Multigrip Light 2.0 Snow Socks",
        "image": "assets/light.png",
        "pdf": "pdf/light.pdf",
        "site": "https://noproblemkit.com/wp-content/uploads/2026/11/Snow-Socks-Re-Grip-e-Light-2.0-20261105.pdf",
        "source": "light",
    },
    {
        "slug": "ez-socks",
        "name": "EZ Socks",
        "subtitle": "NPK EZ Urban Snow Socks",
        "image": "assets/ez-socks.png",
        "pdf": "pdf/ez-socks.pdf",
        "site": "https://noproblemkit.com/wp-content/uploads/2026/08/EZ-Urban-updated-20260804.pdf",
        "source": "ez",
    },
    {
        "slug": "grip-3d",
        "name": "Grip 3D",
        "subtitle": "NPK Grip 3D Snow Socks",
        "image": "assets/grip-3d.png",
        "pdf": "pdf/grip-3d.pdf",
        "site": "https://noproblemkit.com/wp-content/uploads/2026/08/Snow-Socks-Grip-3D-updated-20260812.pdf",
        "source": "grip3d",
    },
    {
        "slug": "re-grip",
        "name": "RE Grip",
        "subtitle": "NPK RE-Grip Snow Socks",
        "image": "assets/re-grip.png",
        "pdf": "pdf/re-grip.pdf",
        "site": "https://noproblemkit.com/wp-content/uploads/2026/11/Snow-Socks-Re-Grip-e-Light-2.0-20261105.pdf",
        "source": "light",  # stessa tabella di Light
    },
]

# ordine di visualizzazione delle taglie per modello
SIZE_ORDER = {
    "light": ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
    "grip3d": ["XS", "S", "M", "L", "XL", "XXL"],
    "original": [f"TG.{n}" for n in
                 (69, 71, 73, 74, 76, 77, 79, 80, 81, 83, 85, 87, 89, 93, 95, 96, 97)],
    "ez": EZ_SEQ,
}


def order_sizes(source, keys):
    pref = SIZE_ORDER.get(source, [])
    known = [k for k in pref if k in keys]
    rest = sorted(k for k in keys if k not in pref)
    return known + rest


# ---------------------------------------------------------------- assemblaggio
def build_dataset():
    tables = {
        "light": parse_light(),
        "grip3d": parse_grip3d(),
        "original": parse_original(),
        "ez": parse_ez(),
    }

    out_models = []
    for m in MODELS:
        entry = {
            "slug": m["slug"],
            "name": m["name"],
            "subtitle": m["subtitle"],
            "image": m["image"],
            "pdf": m["pdf"],
            "site": m["site"],
            "pdf_only": m["source"] is None,
        }
        if m["source"]:
            table = tables[m["source"]]
            sizes = order_sizes(m["source"], set(table))
            fit = {}
            for size in sizes:
                for tire in table[size]:
                    fit.setdefault(tire, [])
                    if size not in fit[tire]:
                        fit[tire].append(size)
            # ordina i valori di fit secondo l'ordine taglie
            rank = {s: i for i, s in enumerate(sizes)}
            for tire in fit:
                fit[tire].sort(key=lambda s: rank.get(s, 99))
            entry["sizes"] = sizes
            entry["fit"] = fit
        out_models.append(entry)

    import datetime
    return {
        "models": out_models,
        "generated": datetime.date.today().isoformat(),
    }


TEMPLATE = os.path.join(REPO, "index.template.html")
INDEX = os.path.join(REPO, "index.html")
JSON_OUT = os.path.join(HERE, "socks.json")


def main():
    data = build_dataset()

    with open(JSON_OUT, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)

    with open(TEMPLATE, encoding="utf-8") as fh:
        tpl = fh.read()
    payload = "var DB = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"
    if "/*SOCKS_JSON*/" not in tpl:
        sys.exit("Segnaposto /*SOCKS_JSON*/ non trovato in index.template.html")
    html = tpl.replace("/*SOCKS_JSON*/", payload)
    with open(INDEX, "w", encoding="utf-8") as fh:
        fh.write(html)

    # ---- riepilogo
    print("Generati:")
    print("  " + os.path.relpath(JSON_OUT, MAK))
    print("  " + os.path.relpath(INDEX, MAK))
    print()
    for m in data["models"]:
        if m["pdf_only"]:
            print(f"  {m['name']:14s}  solo PDF")
        else:
            n_mis = len(m["fit"])
            print(f"  {m['name']:14s}  {len(m['sizes']):2d} taglie  {n_mis:4d} misure")


if __name__ == "__main__":
    main()
