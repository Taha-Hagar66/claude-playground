"""Read-only summary of your Desktop: file types, biggest files, newest files.
Run:  python desktop_report.py   ->  writes desktop_report.md next to this script.
"""
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # the Desktop folder
OUT = Path(__file__).resolve().parent / "desktop_report.md"

files = []
for p in ROOT.rglob("*"):
    try:
        if p.is_file():
            st = p.stat()
            files.append((p, st.st_size, st.st_mtime))
    except OSError:
        pass  # skip files we can't read (e.g. cloud-only OneDrive placeholders)

def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"

types = Counter((p.suffix.lower() or "(none)") for p, _, _ in files)
total = sum(s for _, s, _ in files)
rel = lambda p: p.relative_to(ROOT)

lines = [
    f"# Desktop report — {datetime.now():%Y-%m-%d %H:%M}",
    f"**{len(files)} files**, {human(total)} total, in `{ROOT}`\n",
    "## Most common file types",
    *[f"- `{ext}` — {n}" for ext, n in types.most_common(8)],
    "\n## Largest files",
    *[f"- {human(s)} — `{rel(p)}`" for p, s, _ in sorted(files, key=lambda f: -f[1])[:5]],
    "\n## Most recently changed",
    *[f"- {datetime.fromtimestamp(m):%Y-%m-%d} — `{rel(p)}`" for p, _, m in sorted(files, key=lambda f: -f[2])[:5]],
]
OUT.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
