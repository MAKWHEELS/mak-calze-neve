# Calze da neve NPK - scelta taglia

Web app single-file per i clienti: si sceglie il modello di calza da neve NPK
(The Original, Light, EZ Socks, Grip 3D, RE Grip), si inserisce la misura del
pneumatico e l'app dice quale taglia ordinare. Ogni modello linka il PDF taglie
ufficiale (locale, quindi consultabile offline) e la versione aggiornata sul sito
NPK.

Nessuna dipendenza esterna, tutto inline, funziona offline salvo i link uscenti a
`noproblemkit.com`. Stesso pattern di `../mak-tpms-relearn/`.

**Online:** https://makwheels.github.io/mak-calze-neve/

## Struttura

| File | Ruolo |
|---|---|
| `index.html` | L'app completa, dati inline. **Generato** - non modificare a mano. |
| `index.template.html` | Sorgente di markup/CSS/JS. Il segnaposto `/*SOCKS_JSON*/` viene sostituito col JSON. |
| `data/build.py` | Legge le tabelle applicative, assembla `data/socks.json` e rigenera `index.html`. |
| `data/socks.json` | Dataset leggibile (copia di servizio; l'app usa quello inline). |
| `data/_raw_tables.md` | Riepilogo di provenienza dati + verifica incrociata contro i PDF (snapshot). |
| `assets/` | Loghi (`mak.png`, `npk.png`) e le 5 immagini modello. |
| `pdf/` | I 5 PDF taglie ufficiali NPK. `light.pdf` e `re-grip.pdf` sono lo stesso documento. |

## Fonte dati

Tutti e 5 i modelli hanno il finder misura -> taglia:

- **Light / RE Grip**: `data/light-regrip-rev05.txt`, estratto dal PDF ufficiale REV 05 del 05/11/2026 (taglie 1..9, 493 misure). RE Grip usa la stessa tabella (PDF ufficiale unico).
- **Grip 3D**: `data/grip3d-rev01.txt` (XS..XXL), la trascrizione di `../NotebookLM/` con la 195/55R18 aggiunta in taglia L dal PDF REV 01.
- **The Original**: `data/original-rev03.txt`, estratto dal PDF ufficiale REV 03 (TG.69..TG.97, 536 misure). Prima veniva dall'Excel in `../NotebookLM/`, letto male ai bordi delle taglie.
- **EZ Socks**: estratto da `pdf/ez-socks.pdf` con `pdfplumber.extract_table()` — la
  griglia ha bordi cella leggibili; le bande si separano sulla prima colonna
  (etichetta taglia verticale) e si mappano in ordine su XSMALL..XXXLARGE.
  Le misure fuoristrada in formato flottante (`31X10.5 R15`) non sono nel finder.

Per Grip 3D i dati vengono dalla trascrizione, non dal PDF: il loro layout (etichette ruotate 90°, blocchi che continuano tra
pagine) non si estrae bene. Verifica incrociata contro i PDF in `data/_raw_tables.md`.

## Rigenerare dopo una modifica

Serve: `pip3 install pdfplumber`

1. Aggiorna la fonte: i `.txt` in `data/`, il `pdf/ez-socks.pdf`,
   oppure la mappa `MODELS` / `SIZE_ORDER` in `data/build.py`.
2. `python3 data/build.py`
3. Commit di `index.html` + `data/socks.json`.

## Aggiornare un PDF taglie

Quando NPK pubblica una revisione: sostituisci il file in `pdf/<slug>.pdf`,
aggiorna se serve la fonte dati corrispondente, rigenera e committa. Il link
"Versione aggiornata sul sito NPK" nell'app copre l'intervallo tra la revisione
NPK e la ripubblicazione.

## Deploy (GitHub Pages)

Repo pubblico - nessun dato sensibile, sono tabelle prodotto pubbliche.

```
git init && git add -A && git commit -m "Prima versione"
git branch -M main
gh repo create MAKWHEELS/mak-calze-neve --public --source=. --push
```

Poi su GitHub: **Settings > Pages > Source: `main` / root**. Aprire il link da
iPhone e provare la ricerca taglia + l'apertura dei PDF.
