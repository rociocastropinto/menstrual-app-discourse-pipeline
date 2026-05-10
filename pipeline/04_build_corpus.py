import pandas as pd

# =============================================================
# SCRIPT 05: VALIDACIÓN FINAL Y EXPORTACIÓN DEL CORPUS
# =============================================================
# Este es el paso final. Lee los resultados de la IA (Script 04),
# elimina falsos positivos mediante palabras clave de dominio
# y genera el archivo Excel definitivo para la tesis.

def run_final_validation(input_csv, output_excel):
    print(f"--- Iniciando Validación Final desde {input_csv} ---")

    # 1. CARGAR RESULTADOS DE LA IA
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo {input_csv}. ¿Corriste el Script 04?")
        return

    # 2. FILTRAR POR RELEVANCIA DE LA IA
    # Identificamos la columna de la IA (BART)
    # Si el Script 04 generó 'is_relevant_binary.1', la usamos. Si no, usamos 'is_relevant_binary'
    col_ia = 'is_relevant_binary.1' if 'is_relevant_binary.1' in df.columns else 'is_relevant_binary'

    df_ia = df[df[col_ia] == 1].copy()
    conteo_ia = len(df_ia)
    print(f"-> Artículos aprobados por la IA: {conteo_ia}")

    # 3. FILTRO DE SEGURIDAD (Validación de Dominio Menstrual/Reproductivo)
    # Esto asegura que no se cuelen artículos de tecnología general o deportes
    keywords_dominio = [
        'period', 'menstrual', 'fertility', 'ovulation', 'cycle',
        'pregnancy', 'contraception', 'abortion', 'reproductive',
        'menopause', 'pcos', 'endometriosis', 'clue', 'flo', 'natural cycles'
    ]

    def es_dominio_correcto(text):
        text_lower = str(text).lower()
        return any(word in text_lower for word in keywords_dominio)

    print("-> Aplicando validación final de palabras clave...")
    df_final = df_ia[df_ia['body_text'].apply(es_dominio_correcto)].copy()
    conteo_final = len(df_final)
    descartados = conteo_ia - conteo_final

    # 4. EXPORTAR RESULTADOS
    # Ordenar por fecha para facilitar la lectura en la tesis
    if 'date' in df_final.columns:
        df_final = df_final.sort_values(by='date', ascending=False)

    df_final.to_excel(output_excel, index=False)

    # 5. RESUMEN METODOLÓGICO (Para tu capítulo de Metodología)
    print("\n" + "="*30)
    print("      RESULTADOS FINALES")
    print("="*30)
    print(f"Aprobados por IA:          {conteo_ia}")
    print(f"Descartados por validación: {descartados}")
    print(f"CORPUS FINAL (Excel):      {conteo_final}")
    print(f"\nArchivo guardado: {output_excel}")
    print("="*30)

if __name__ == "__main__":
    # Conexión con el Script 04
    ARCHIVO_IA = 'results_transformers_v12.csv'
    ARCHIVO_FINAL = '05_CORPUS_FINAL_TESIS.xlsx'

    run_final_validation(ARCHIVO_IA, ARCHIVO_FINAL)