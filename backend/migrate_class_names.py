from pathlib import Path
from shutil import move

root = Path('dataset')
if not root.exists():
    print('No dataset folder found')
    raise SystemExit(1)

for p in list(root.iterdir()):
    if not p.is_dir():
        continue
    new_name = p.name.title()
    if new_name != p.name:
        new_path = root / new_name
        if new_path.exists():
            print(f"Target path {new_path} already exists; merging files from {p} into it.")
            for f in p.iterdir():
                target = new_path / f.name
                if not target.exists():
                    move(str(f), str(target))
            p.rmdir()
        else:
            print(f"Renaming {p} -> {new_path}")
            p.rename(new_path)
print('Migration complete')
