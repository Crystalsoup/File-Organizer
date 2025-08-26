# File Organizer 

Organize files by **extension** or by **date (YYYY/MM)** with **dry-run** and **undo**.

## Usage
```bash
python -m file_organizer --source ~/Downloads --mode ext --dry-run
python -m file_organizer --source ~/Downloads --mode date --undo-log moves.json
# later...
python -m file_organizer --source ~/Downloads --undo --undo-log moves.json
```

## Tests
```bash
python -m pytest -q
```
