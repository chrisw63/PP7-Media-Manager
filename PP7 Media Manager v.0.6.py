import re
import os
import shutil
import tkinter as tk
from tkinter import filedialog

# === CONFIGURE THESE PATHS IF YOUR PP7 INSTALL IS NON-STANDARD ===
library_folder = os.path.expandvars(r"%USERPROFILE%\Documents\ProPresenter\Libraries")
media_folder = os.path.expandvars(r"%USERPROFILE%\Documents\ProPresenter\Media")
backup_folder = os.path.expandvars(r"%USERPROFILE%\Documents\ProPresenter\UnusedMediaBackup")

move_unused = True  # Set to False to disable moving files

# Windows-style file paths (with or without extension)
media_path_pattern = re.compile(
    rb'[a-zA-Z]:\\(?:[^\\\x00-\x1F]+\\)*[^\\\x00-\x1F]+(?:\.[^\\\x00-\x1F.]+)?',
    re.IGNORECASE)


found_media = set()

# Scan *.pro files for media files
for root, _, files in os.walk(library_folder):
    for filename in files:
        if filename.lower().endswith('.pro'):
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                matches = media_path_pattern.findall(content)
                for match in matches:
                    decoded = os.path.normcase(match.decode('utf-8', errors='replace'))
                    found_media.add(decoded)
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

# Collect actual media files list
actual_media = set()
for root, _, files in os.walk(media_folder):
    for filename in files:
        full_path = os.path.normcase(os.path.join(root, filename))
        actual_media.add(full_path)

# Unused files
unused_media = sorted(actual_media - found_media)

# Moving paid content might upset people...
unused_media = [
    path for path in unused_media
    if "procontent" not in [part.lower() for part in os.path.normpath(path).split(os.path.sep)]]

print(f"\n=== Total {len(unused_media)} Unused Media Files ===")
print("(in Media folder but not used in a presentation)\n")

# File dialog - Cancel to not save
root = tk.Tk()
root.withdraw()  # Hide root window
save_path = filedialog.asksaveasfilename(
    title="Save Unused Media List",
    defaultextension=".txt",
    filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])

if save_path:
    with open(save_path, "w", encoding="utf-8") as out:
        for path in unused_media:
            out.write(path + "\n")
    print(f"\nUnused media list saved to: {save_path}")
else:
    print("\nSave canceled. No file written.")

# Move unused to backup folder
if move_unused and unused_media:
    confirm = input("Move unused files to backup folder? (y/n): ").strip().lower()
    if confirm == 'y':
        for file_path in unused_media:
            rel_path = os.path.relpath(file_path, media_folder)
            dest_path = os.path.join(backup_folder, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            try:
                shutil.move(file_path, dest_path)
            except Exception as e:
                print(f"Failed to move {file_path}: {e}")
        print("Move succeeded.")
    else:
        print("Move canceled by user.")
