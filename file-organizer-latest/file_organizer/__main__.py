#!/usr/bin/env python3
"""File Organizer
Organize files by extension or by date (YYYY/MM), with dry-run and undo.
Usage:
  python -m file_organizer --source <dir> --mode [ext|date] [--dry-run]
  python -m file_organizer --source <dir> --undo --undo-log <log.json>
"""
from __future__ import annotations
import argparse, shutil, sys, json
from pathlib import Path
from datetime import datetime

def plan_moves(source: Path, target: Path, mode: str):
    ops = []
    for p in source.iterdir():
        if p.is_dir():
            continue
        if mode == "ext":
            ext = p.suffix.lower().lstrip(".") or "no_ext"
            dest = target / ext / p.name
        elif mode == "date":
            ts = datetime.fromtimestamp(p.stat().st_mtime)
            dest = target / f"{ts.year:04d}" / f"{ts.month:02d}" / p.name
        else:
            raise ValueError("mode must be 'ext' or 'date'")
        if p.resolve() == dest.resolve():
            continue
        ops.append((p, dest))
    return ops

def do_moves(ops, dry_run: bool, undo_log: Path|None):
    performed = []
    for src, dst in ops:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dry_run:
            print(f"[DRY] {src} -> {dst}")
        else:
            # dedupe if exists
            if dst.exists():
                i, stem, suf = 1, dst.stem, dst.suffix
                while True:
                    cand = dst.with_name(f"{stem} ({i}){suf}")
                    if not cand.exists():
                        dst = cand
                        break
                    i += 1
            shutil.move(str(src), str(dst))
            performed.append((str(src), str(dst)))
            print(f"[MOVE] {src} -> {dst}")
    if not dry_run and undo_log and performed:
        undo_log.write_text(json.dumps(performed, indent=2), encoding="utf-8")
        print(f"[LOG] Undo log written to {undo_log}")

def undo(undo_log: Path, dry_run: bool):
    if not undo_log.exists():
        print("No undo log found.")
        return
    moves = json.loads(undo_log.read_text(encoding="utf-8"))
    for dst, src in reversed(moves):
        dst_p, src_p = Path(dst), Path(src)
        if dry_run:
            print(f"[DRY-UNDO] {dst_p} -> {src_p}")
        else:
            src_p.parent.mkdir(parents=True, exist_ok=True)
            if dst_p.exists():
                shutil.move(str(dst_p), str(src_p))
                print(f"[UNDO] {dst_p} -> {src_p}")
            else:
                print(f"[SKIP] Missing {dst_p}, cannot undo.")

def main(argv=None):
    ap = argparse.ArgumentParser(description="Organize files by extension or date.")
    ap.add_argument("--source", required=True, help="Directory to organize")
    ap.add_argument("--target", help="Target directory (default: source)")
    ap.add_argument("--mode", choices=["ext","date"], default="ext")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--undo-log", default="undo_moves.json")
    ap.add_argument("--undo", action="store_true")
    args = ap.parse_args(argv)

    source = Path(args.source).expanduser().resolve()
    target = Path(args.target).expanduser().resolve() if args.target else source

    if args.undo:
        undo(Path(args.undo_log).resolve(), args.dry_run)
        return 0

    if not source.exists() or not source.is_dir():
        print("Source must be an existing directory", file=sys.stderr)
        return 1

    ops = plan_moves(source, target, args.mode)
    if not ops:
        print("Nothing to do.")
        return 0
    do_moves(ops, args.dry_run, Path(args.undo_log).resolve())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
