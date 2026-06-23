# Pipeline Multimodale Automatica per Backup

## Descrizione
Sistema automatizzato che monitora una directory di ingresso per nuovi file multimediali (immagini e audio), li elabora tramite script dedicati e registra le informazioni in un database SQLite per il backup e il catalogo.

## Architettura
- **Watcher**: script Python che utilizza `pyinotify` per monitorare la directory `data/` in tempo reale.
- **Script di elaborazione**: script shell presenti in `scripts/` che gestiscono le diverse tipologie di file (immagini, audio).
- **Database**: SQLite con schema definito in `scripts/schema.sql` e helper in `scripts/db_helper.py`.
- **Directory di lavoro**:
  - `data/` : file in ingresso da elaborare
  - `logs/` : log del watcher
  - `output/` : risultati dell'elaborazione (se prodotti dagli script)
  - `scripts/` : contiene watcher, helper DB, schema e script di elaborazione

## Installazione
1. Clonare il repository o copiare la struttura di progetto.
2. Installare le dipendenze Python necessarie:
   ```bash
   pip install --user pyinotify
   ```
3. Assicurarsi che gli script di elaborazione (`process_image.sh`, `process_audio.sh`) siano presenti e eseguibili in `scripts/`.
4. Copiare l'unità systemd `pipeline-watcher.service` in `~/.config/systemd/user/` e abilitarla:
   ```bash
   cp pipeline-watcher.service ~/.config/systemd/user/
   systemctl --user daemon-reload
   systemctl --user enable --now pipeline-watcher.service
   ```

## Uso
- Posizionare i file da elaborare nella directory `data/`.
- Il watcher rileverà automaticamente i nuovi file e li invierà allo script appropriato in base all'estensione.
- I log sono disponibili in `logs/watcher.log`.
- Le informazioni sui file elaborati sono salvate nel database SQLite (per impostazione predefinita creato in `data/media.db` oppure percorso configurabile negli helper).

## Esempi
```bash
# Avvio manuale del watcher (per test)
python3 scripts/watcher.py

# Inserimento di un file di prova
cp /path/to/immagine.jpg data/
# Osservare il log in logs/watcher.log
```

## Stato
✅ COMPLETATO — 2026-06-14
Tutte le fasi sono state implementate:
1. Struttura di progetto
2. Unità systemd per il watcher
3. Script watcher con pyinotify
4. Schema DB e helper di inserimento
5. (Facoltativo) Script di elaborazione esempio da aggiungere secondo le esigenze specifiche.
