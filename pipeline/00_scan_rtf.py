# Dice cuántos archivos encontró y te imprime la ubicación de los primeros cinco
#RTF files found: 3980
from pathlib import Path

ROOT = Path(r"C:\Users\ASUS\Documents\ALEMANIA 2024\MASTER DIGITAL HUMANITIES\WiSe 26\Tesis\nexis_downloads\geminis")

print("Folder exists:", ROOT.exists())

rtf_files = list(ROOT.rglob("*.rtf"))
print("RTF files found:", len(rtf_files))

# show a few example files
for f in rtf_files[:5]:
    print(f)
