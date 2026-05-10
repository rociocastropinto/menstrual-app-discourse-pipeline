# Este script extrae metadatos específicos (fecha, autor, titular)
# y limpia el cuerpo del texto de tus archivos RTF de Nexis Uni.
# Además, elimina duplicados inteligentes y clasifica cada artículo por su extensión (Tiers)
# para asegurar que solo analices contenido de calidad en tu tesis.

#Este es el primer paso. Su función es transformar tus archivos brutos de Nexis Uni en una base de datos organizada.
# Qué hace: Extrae metadatos específicos como fecha, autor, titular y sección, separándolos del cuerpo del texto.
# Limpieza: Elimina duplicados exactos usando una "huella digital" del texto y
# clasifica los artículos por su extensión en niveles o Tiers (150, 200 o 300 palabras) para asegurar la calidad del análisis.
# Salida: Genera el archivo corpus_metadata_final_v9.csv.


import re
import hashlib
from pathlib import Path
import pandas as pd
from striprtf.striprtf import rtf_to_text

# Rutas
ROOT = Path(r"C:\Users\ASUS\Documents\ALEMANIA 2024\MASTER DIGITAL HUMANITIES\WiSe 26\Tesis\nexis_downloads\geminis")
OUT_CSV = Path("corpus_metadata_final_v9.csv")

def extract_comprehensive_metadata(full_text):
    lines = [l.strip() for l in full_text.split('\n') if l.strip()]

    # 1. Extracción de Fecha (Formato: Month Day, Year)
    # Si no la encuentra, devuelve una cadena vacía "" en lugar de "Unknown"
    date_match = re.search(r"([A-Z][a-z]+ \d{1,2}, \d{4})", full_text)
    pub_date = date_match.group(1) if date_match else ""

    # 2. Otros Metadatos (Si no existen, quedan vacíos)
    publication = lines[0] if lines else ""

    def quick_regex(pattern, text):
        m = re.search(pattern, text, re.I | re.M)
        return m.group(1).strip() if m and m.group(1) else ""

    section = quick_regex(r"Section:\s*(.*?)(?:;|\n|$)", full_text)
    page_number = quick_regex(r"Pg\.\s*(\d+.*)", full_text)
    byline = quick_regex(r"Byline:\s*(.*)", full_text)
    copyright_val = quick_regex(r"Copyright\s*(.*)", full_text)
    headline = lines[0] if lines else ""

    # 3. Métricas Numéricas
    header_str = quick_regex(r"Length:\s+(\d+)", full_text)
    length_words_header = int(header_str) if header_str.isdigit() else 0

    # 4. Cuerpo del Texto
    parts = re.split(r"\bBody\b", full_text, maxsplit=1, flags=re.IGNORECASE)
    raw_body = parts[1] if len(parts) > 1 else full_text
    body_clean = re.split(r"Load-Date:|End of Document|Copyright", raw_body, flags=re.IGNORECASE)[0].strip()
    body_text = re.sub(r"\s+", " ", body_clean)
    body_word_count = len(body_text.split())

    return {
        "date": pub_date,
        "publication": publication,
        "section": section,
        "page_number": page_number,
        "byline": byline,
        "headline": headline,
        "body_text": body_text,
        "body_word_count": body_word_count,
        "length_words_header": length_words_header,
        "word_count_computed": len(re.sub(r"\s+", " ", full_text).split()),
        "length_diff_vs_header": body_word_count - length_words_header,
        "copyright": copyright_val
    }

# --- PROCESAMIENTO ---
rows = []
for fpath in sorted(ROOT.rglob("*.rtf")):
    try:
        content = fpath.read_text(encoding="utf-8", errors="replace")
        raw_txt = rtf_to_text(content)
        data = extract_comprehensive_metadata(raw_txt)
        h = hashlib.md5(data["body_text"].lower().encode("utf-8", errors="replace")).hexdigest()
        rows.append({"folder": fpath.parent.name, "filename": fpath.name, "content_hash": h, **data})
    except:
        continue

# --- CREACIÓN DEL DATAFRAME ---
df = pd.DataFrame(rows)

if not df.empty:
    df = df.drop_duplicates(subset=["content_hash"], keep="first").copy()

    # ESTA ES LA CLAVE: Forzamos a que 'date' sea tratada como Texto puro
    # Usamos errors='ignore' para que no intente convertir nada a fecha
    df['date'] = df['date'].astype(str)

    # Tiers
    df["tier_150"] = df["body_word_count"] >= 150
    df["tier_200"] = df["body_word_count"] >= 200
    df["tier_300"] = df["body_word_count"] >= 300

    df = df.reset_index(drop=True)
    df.insert(0, "article_id", df.index.map(lambda i: f"NU_{i+1:06d}"))

    final_cols = ["article_id", "date", "publication", "section", "page_number",
                  "byline", "headline", "body_word_count", "length_words_header",
                  "word_count_computed", "length_diff_vs_header", "tier_150",
                  "tier_200", "tier_300", "body_text", "folder", "filename", "copyright"]

    # Al guardar con utf-8-sig, Excel lo abrirá perfecto y no habrá error de tipos
    df[final_cols].to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"✅ ¡Proceso finalizado! Los campos vacíos ahora son celdas en blanco en el CSV.")