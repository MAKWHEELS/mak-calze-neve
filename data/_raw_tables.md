# Tabelle taglie NPK - dati estratti

Generato da `data/build.py` il 2026-09-02; Light, RE Grip e The Original aggiornate il 2026-11-07. Riepilogo di servizio per la
verifica: i dati completi (misura -> taglia) sono in `data/socks.json` e inline in
`index.html`.

## Fonti

| Modello | Fonte | Note |
|---|---|---|
| The Original | `data/original-rev03.txt` | Estratta dal PDF REV 03 con pdfplumber, taglia per taglia. |
| Light | `data/light-regrip-rev05.txt` | Estratta dal PDF REV 05 del 05/11/2026 con pdfplumber, taglia per taglia. |
| Grip 3D | `data/grip3d-rev01.txt` | Digitalizzata, `NPK GRIP 3D TAGLIA XS..XXL`, con la 195/55R18 aggiunta dal PDF REV 01. |
| RE Grip | = Light | PDF ufficiale unico "RE-GRIP & MULTIGRIP LIGHT"; stesse taglie (confermato). |
| EZ Socks | `pdf/ez-socks.pdf` via `pdfplumber.extract_table()` | Griglia con bordi cella. Bande separate sulla 1a colonna (etichetta taglia verticale), mappate in ordine su XSMALL..XXXLARGE (7 bande, verificato). |

## Conteggi per taglia

### The Original (536 misure distinte)

| Taglia | n. misure |
|---|---|
| TG.69 | 14 |
| TG.71 | 16 |
| TG.73 | 17 |
| TG.74 | 22 |
| TG.76 | 22 |
| TG.77 | 28 |
| TG.79 | 28 |
| TG.80 | 24 |
| TG.81 | 29 |
| TG.83 | 34 |
| TG.85 | 24 |
| TG.87 | 37 |
| TG.89 | 56 |
| TG.93 | 57 |
| TG.95 | 56 |
| TG.96 | 43 |
| TG.97 | 29 |

### Light (493 misure distinte, REV 05)

| Taglia | n. misure |
|---|---|
| 1 | 14 |
| 2 | 30 |
| 3 | 42 |
| 4 | 53 |
| 5 | 52 |
| 6 | 60 |
| 7 | 92 |
| 8 | 73 |
| 9 | 77 |

### EZ Socks (560 misure distinte)

| Taglia | n. misure |
|---|---|
| XSMALL | 29 |
| SMALL | 54 |
| MEDIUM | 86 |
| LARGE | 106 |
| XLARGE | 122 |
| XXLARGE | 90 |
| XXXLARGE | 96 |

### Grip 3D (606 misure distinte)

| Taglia | n. misure |
|---|---|
| XS | 30 |
| S | 57 |
| M | 97 |
| L | 133 |
| XL | 158 |
| XXL | 131 |

### RE Grip (493 misure distinte, REV 05)

| Taglia | n. misure |
|---|---|
| 1 | 14 |
| 2 | 30 |
| 3 | 42 |
| 4 | 53 |
| 5 | 52 |
| 6 | 60 |
| 7 | 92 |
| 8 | 73 |
| 9 | 77 |

## Verifica

- **Light / RE Grip (2026-11-07)**: 493 misure nel finder = 493 nel PDF REV 05, taglia per taglia. Rispetto alla trascrizione di prima si aggiungono 145/70R13, 265/30R20, 275/30R20, 205/60R18, 315/30R20, 215/60R18, 215/65R17, 305/30R21, 275/35R23, 315/30R23; nessuna taglia esistente cambia.
- **The Original (2026-11-07)**: rifatta dal PDF. La vecchia lettura dell'Excel attribuiva l'etichetta di taglia a un numero fisso di righe e metteva le prime righe di una banda nella taglia precedente: 54 misure avevano la taglia sbagliata e 4 mancavano. Ora 533 misure coincidono con il configuratore del sito; le altre 3, da 17,5", lì non hanno il diametro nel dato. La 275/70R16 è in TG.96: compare una sola volta nel PDF, l'attribuzione anche a TG.97 era un errore di estrazione.
- **Grip 3D (2026-11-07)**: aggiunta la 195/55R18 in taglia L: nel PDF REV 01 sta a pagina 3, quella della taglia L.
- **Grip 3D, 2026-09-02**: verifica incrociata contro i rispettivi PDF
  (parser geometrico pdfplumber, solo in fase di controllo): 0 misure dichiarate
  risultano assenti dal PDF; 5-8 per modello compaiono nel testo PDF ma non nella
  tabella digitalizzata (artefatti multi-colonna o misure rare ai bordi).
- **EZ Socks**: 7 bande = 7 taglie, tutte le etichette verticali decodificate
  combaciano con la sequenza attesa. 560 misure metriche. ~23 misure compaiono in
  2 taglie adiacenti (XXLARGE/XXXLARGE): e' cosi' anche nel PDF originale, l'app
  mostra entrambe ("Taglie X o Y").
- **Non coperte**: le misure fuoristrada in formato flottante (es. `31X10.5 R15`,
  `33X12.5 R16`) presenti in EZ XXXLARGE non sono nel finder (formato non gestito
  dai 3 menu larghezza/serie/diametro) -> per quelle l'app rimanda al PDF.

## Spot-check

- Grip 3D `195/55 R16` -> M | Light `135/80 R13` -> 1 | The Original `135/80 R15` -> TG.76, `135/70 R15` -> TG.73
- EZ Socks: `135/70 R13`->XSMALL, `225/40 R16`->SMALL, `255/45 R15`->MEDIUM,
  `285/35 R19`->LARGE, `325/30 R20`->XLARGE, `235/65 R19`->XXLARGE o XXXLARGE, `225/90 R16`->XXXLARGE

## URL sito NPK (verificati HTTP 200 il 2026-09-02)

- The Original: https://noproblemkit.com/wp-content/uploads/2026/08/Snow-Socks-The-Original-updated-2020812.pdf
- Light: https://noproblemkit.com/wp-content/uploads/2026/11/Snow-Socks-Re-Grip-e-Light-2.0-20261105.pdf (indirizzo dalla copia del sito del 2026-11-07)
- EZ Socks: https://noproblemkit.com/wp-content/uploads/2026/08/EZ-Urban-updated-20260804.pdf
- Grip 3D: https://noproblemkit.com/wp-content/uploads/2026/08/Snow-Socks-Grip-3D-updated-20260812.pdf
- RE Grip: https://noproblemkit.com/wp-content/uploads/2026/11/Snow-Socks-Re-Grip-e-Light-2.0-20261105.pdf (indirizzo dalla copia del sito del 2026-11-07)
