#!/usr/bin/env python3
"""
generate_mocs.py — Obsidian MOC (Map of Content) 索引页自动生成器

扫描论文笔记和概念库目录，为每个目录生成带 [[wikilink]] 的 _Index.md 索引页。
幂等：仅在内容变化时才写入文件。

Usage:
    python generate_mocs.py --mode all        # 扫描全部（默认）
    python generate_mocs.py --mode concepts   # 仅概念库
    python generate_mocs.py --mode papers     # 仅论文笔记
    python generate_mocs.py --dry-run         # 预览，不写入
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR.parent / "_shared" / "scholar-config.json"

INDEX_FILENAME = "_Index.md"

# Directories to always skip
SKIP_DIRS = {".obsidian", ".trash", ".git", "templates", "模板"}


def load_config() -> dict:
    """Load scholar-config.json and return paths dict."""
    if not CONFIG_PATH.exists():
        print(f"[ERROR] Config not found: {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg


def expand_path(raw: str) -> Path:
    """Expand ~ and resolve to absolute path."""
    return Path(raw).expanduser().resolve()


# ---------------------------------------------------------------------------
# Scanning & Index Generation
# ---------------------------------------------------------------------------

def collect_notes(directory: Path) -> tuple[list[Path], list[Path]]:
    """
    Collect immediate child .md files (excluding _Index.md) and child
    directories (excluding SKIP_DIRS) in *directory*.

    Returns (subdirs, notes) both sorted by name.
    """
    subdirs = []
    notes = []

    if not directory.is_dir():
        return subdirs, notes

    for child in sorted(directory.iterdir(), key=lambda p: p.name.lower()):
        if child.name.startswith("."):
            continue
        if child.is_dir() and child.name not in SKIP_DIRS:
            subdirs.append(child)
        elif child.is_file() and child.suffix.lower() == ".md" and child.name != INDEX_FILENAME:
            notes.append(child)

    return subdirs, notes


def count_notes_recursive(directory: Path) -> int:
    """Count all .md files (excluding _Index.md) recursively under directory."""
    count = 0
    if not directory.is_dir():
        return 0
    for p in directory.rglob("*.md"):
        if p.name != INDEX_FILENAME and not any(part in SKIP_DIRS for part in p.parts):
            count += 1
    return count


def build_index_content(directory: Path, subdirs: list[Path], notes: list[Path]) -> str:
    """Build the markdown content for an _Index.md file."""
    dir_name = directory.name
    total_notes = count_notes_recursive(directory)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# {dir_name}",
        "",
        f"> Auto-generated MOC · 共 {total_notes} 篇笔记 · 更新于 {timestamp}",
        "",
    ]

    # Subdirectory links
    if subdirs:
        lines.append("## 子目录")
        lines.append("")
        for sd in subdirs:
            n = count_notes_recursive(sd)
            # Use relative wikilink: [[subdir/_Index|subdir]]
            lines.append(f"- [[{sd.name}/{INDEX_FILENAME[:-3]}|{sd.name}]] ({n} 篇)")
        lines.append("")

    # Note links
    if notes:
        lines.append("## 笔记")
        lines.append("")
        for note in notes:
            stem = note.stem
            lines.append(f"- [[{stem}]]")
        lines.append("")

    # If directory is empty
    if not subdirs and not notes:
        lines.append("*（此目录暂无笔记）*")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core: process a directory tree
# ---------------------------------------------------------------------------

def process_directory(
    directory: Path,
    stats: dict,
    dry_run: bool = False,
) -> None:
    """
    Recursively process *directory*: generate _Index.md for it and all
    sub-directories that contain .md files or sub-directories.
    """
    if not directory.is_dir():
        return
    if directory.name in SKIP_DIRS:
        return

    subdirs, notes = collect_notes(directory)

    # Recurse into subdirs first (bottom-up ensures counts are ready)
    for sd in subdirs:
        process_directory(sd, stats, dry_run=dry_run)

    # Re-collect after recursion (subdirs may now have _Index.md, but we
    # don't count those as notes)
    subdirs, notes = collect_notes(directory)

    # Skip if nothing to index
    if not subdirs and not notes:
        return

    stats["dirs_scanned"] += 1

    content = build_index_content(directory, subdirs, notes)
    index_path = directory / INDEX_FILENAME

    # Idempotency: compare with existing content (ignore timestamp line)
    if index_path.exists():
        existing = index_path.read_text(encoding="utf-8")
        # Strip the timestamp line for comparison (line starting with "> Auto-generated")
        def strip_timestamp(text: str) -> str:
            lines = text.splitlines()
            return "\n".join(
                line for line in lines
                if not line.startswith("> Auto-generated MOC")
            )

        if strip_timestamp(existing) == strip_timestamp(content):
            stats["skipped"] += 1
            return

        # Content changed
        if not dry_run:
            index_path.write_text(content, encoding="utf-8")
        stats["updated"] += 1
        print(f"  [UPDATED] {index_path}")
    else:
        # New index
        if not dry_run:
            index_path.write_text(content, encoding="utf-8")
        stats["created"] += 1
        print(f"  [CREATED] {index_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate Obsidian MOC index pages")
    parser.add_argument(
        "--mode",
        choices=["concepts", "papers", "all"],
        default="all",
        help="Which directories to scan (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )
    args = parser.parse_args()

    cfg = load_config()
    paths = cfg.get("paths", {})

    vault_root = expand_path(paths.get("obsidian_vault", "~/ObsidianVault"))
    papers_folder = paths.get("paper_notes_folder", "论文笔记")
    concepts_folder = paths.get("concepts_folder", "_概念")

    papers_dir = vault_root / papers_folder
    concepts_dir = vault_root / papers_folder / concepts_folder

    if not vault_root.is_dir():
        print(f"[ERROR] Vault not found: {vault_root}")
        sys.exit(1)

    stats = {"dirs_scanned": 0, "created": 0, "updated": 0, "skipped": 0}

    if args.dry_run:
        print("[DRY RUN] No files will be written.\n")

    # --- Concepts ---
    if args.mode in ("concepts", "all"):
        print(f"=== Scanning concepts: {concepts_dir} ===")
        if concepts_dir.is_dir():
            process_directory(concepts_dir, stats, dry_run=args.dry_run)
        else:
            print(f"  [WARN] Concepts directory not found: {concepts_dir}")

    # --- Papers (excluding _概念 subdirectory) ---
    if args.mode in ("papers", "all"):
        print(f"\n=== Scanning papers: {papers_dir} ===")
        if papers_dir.is_dir():
            # Process sub-directories of papers_dir, skipping the concepts folder
            subdirs, notes = collect_notes(papers_dir)
            for sd in subdirs:
                if sd.name == concepts_folder:
                    continue  # skip concepts dir in papers mode
                process_directory(sd, stats, dry_run=args.dry_run)
            # Now generate the top-level papers index
            # (re-collect to include all subdirs for the top-level index)
            stats["dirs_scanned"] += 1
            all_subdirs, all_notes = collect_notes(papers_dir)
            content = build_index_content(papers_dir, all_subdirs, all_notes)
            index_path = papers_dir / INDEX_FILENAME

            def strip_ts(text: str) -> str:
                return "\n".join(
                    l for l in text.splitlines()
                    if not l.startswith("> Auto-generated MOC")
                )

            if index_path.exists():
                existing = index_path.read_text(encoding="utf-8")
                if strip_ts(existing) == strip_ts(content):
                    stats["skipped"] += 1
                else:
                    if not args.dry_run:
                        index_path.write_text(content, encoding="utf-8")
                    stats["updated"] += 1
                    print(f"  [UPDATED] {index_path}")
            else:
                if not args.dry_run:
                    index_path.write_text(content, encoding="utf-8")
                stats["created"] += 1
                print(f"  [CREATED] {index_path}")
        else:
            print(f"  [WARN] Papers directory not found: {papers_dir}")

    # --- Summary ---
    print(f"\n{'='*50}")
    print(f"扫描目录: {stats['dirs_scanned']}")
    print(f"新建索引: {stats['created']}")
    print(f"更新索引: {stats['updated']}")
    print(f"跳过(无变化): {stats['skipped']}")
    if args.dry_run:
        print("\n[DRY RUN] 以上为预览，未实际写入任何文件。")


if __name__ == "__main__":
    main()
