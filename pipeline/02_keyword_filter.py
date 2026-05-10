#(El Clasificador)
# Este es el segundo paso. Toma la base de datos limpia y aplica criterios de relevancia para tu investigación.
# Filtro Temático: Usa palabras clave para descartar ruido (como temas de ciclismo o economía)
# y confirmar que los artículos traten realmente sobre FemTech (apps de fertilidad, seguimiento menstrual, etc.).
# Análisis de Tesis: Clasifica los artículos relevantes en categorías específicas, como "Prácticas de Privacidad de Datos" o "Uso General".
# Cámara de Eco: Utiliza inteligencia (TF-IDF y similitud de coseno)
# para agrupar artículos que dicen casi lo mismo, detectando así la repetición mediática.
# Salida: Genera el archivo final corpus_final_procesado_v12.csv.

import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def run_pipeline(input_file, output_file):
    print(f"--- Iniciando procesamiento de {input_file} ---")
    df = pd.read_csv(input_file)

    # 1. DEFINICIÓN DE REGLAS DE RELEVANCIA
    def get_relevance_and_tag(row):
        # Combinamos titular y cuerpo para el análisis
        content = f"{str(row['headline'])} {str(row['body_text'])}".lower()

        # Filtro de Ruido (Binario 0)
        noise_terms = ['strava', 'bicycle', 'cycling', 'housing starts', 'unemployment rate', 'construction']
        if any(term in content for term in noise_terms):
            return 0, "IRRELEVANT"

        # Palabras clave de apps (Asegura que sea sobre FemTech)
        femtech_apps = r"(natural cycles|clue|flo|glow|period tracker|fertility app|menstrual tracking|ovia|period calendar)"
        if not re.search(femtech_apps, content):
            return 0, "IRRELEVANT"

        # Definición de Etiquetas de Tesis (Thesis Tags)
        # Prioridad B: Privacidad y Vigilancia
        privacy_keywords = r"(privacy|data sharing|surveillance|consent|monetization|gdpr|subpoena|policing|prosecution|data brokers|legal enforcement|third party)"

        if re.search(privacy_keywords, content):
            return 1, "apps_and_data_privacy_practices"
        else:
            # Si no es privacidad, es el tema médico/uso general (Tag A)
            return 1, "apps_as_main_topic"

    print("Step 1: Clasificando relevancia y etiquetas...")
    results = df.apply(get_relevance_and_tag, axis=1)
    df['is_relevant_binary'] = [r[0] for r in results]
    df['thesis_tag'] = [r[1] for r in results]

    # 2. DETECCIÓN DE CÁMARA DE ECO (Similitud Textual)
    print("Step 2: Detectando Cámaras de Eco (duplicados mediáticos)...")
    df['echo_chamber_id'] = "unique"

    # Solo comparamos los que pasaron el filtro de relevancia
    relevant_indices = df[df['is_relevant_binary'] == 1].index
    if len(relevant_indices) > 1:
        documents = df.loc[relevant_indices, 'body_text'].fillna("").tolist()

        # Convertimos texto a vectores (TF-IDF)
        tfidf = TfidfVectorizer(stop_words='english').fit_transform(documents)
        # Calculamos similitud entre todos los artículos
        pairwise_sim = cosine_similarity(tfidf)

        # Agrupamos si la similitud es > 85%
        group_counter = 1
        visited = set()

        for i in range(len(relevant_indices)):
            if i not in visited:
                # Encontrar artículos similares al artículo 'i'
                similar_indices = [j for j, sim in enumerate(pairwise_sim[i]) if sim > 0.85]
                if len(similar_indices) > 1:
                    ec_id = f"EC_GROUP_{group_counter:03d}"
                    for idx_in_list in similar_indices:
                        real_idx = relevant_indices[idx_in_list]
                        df.at[real_idx, 'echo_chamber_id'] = ec_id
                        visited.add(idx_in_list)
                    group_counter += 1

    # 3. GUARDAR Y RESUMIR
    df.to_csv(output_file, index=False)
    print(f"--- Proceso completado. Archivo guardado como: {output_file} ---")

    # Resumen estadístico
    print("\nRESUMEN DE RESULTADOS:")
    print(df['is_relevant_binary'].value_counts().rename({1: 'Relevantes', 0: 'Ruido/No Relevantes'}))
    print("\nDISTRIBUCIÓN DE TAGS (Solo Relevantes):")
    print(df[df['is_relevant_binary']==1]['thesis_tag'].value_counts())
    print(f"\nGrupos de Cámara de Eco detectados: {group_counter - 1}")

# Ejecutar
if __name__ == "__main__":
    run_pipeline('corpus_metadata_final_v9.csv', 'corpus_final_procesado_v12.csv')