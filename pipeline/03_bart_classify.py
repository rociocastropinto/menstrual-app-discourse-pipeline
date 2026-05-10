import pandas as pd
from transformers import pipeline
from tqdm import tqdm

def run_transformer_pipeline(input_csv, output_csv):
    print("Cargando corpus...")
    df = pd.read_csv(input_csv, engine='python')

    if 'tier_200' in df.columns:
        df = df[df['tier_200'] == True].copy().reset_index(drop=True)

    total_articles = len(df)
    print(f"--- Iniciando clasificación Dual (Semántica + Heurística) de {total_articles} artículos ---")

    classifier = pipeline("zero-shot-classification",
                          model="facebook/bart-large-mnli",
                          device=-1)

    candidate_labels = [
        "socio-technical analysis of fertility and period tracking apps",
        "privacy risks, data surveillance and legal accountability of apps",
        "biological research, menstrual synchrony and scientific myths",
        "personal finance, medical insurance and crowdfunding for treatments",
        "general artificial intelligence news and computing trends",
        "commercial list of health apps and consumer recommendations",
        "bicycle theft, sports tracking and GPS security",
        "local economic forecasts and real estate market"
    ]

    results = []

    for i, row in tqdm(df.iterrows(), total=total_articles, desc="Procesando", unit="art"):
        text = f"{row['headline']}. {str(row['body_text'])[:700]}" # Aumentamos a 700 para ver más contexto

        try:
            output = classifier(text, candidate_labels, multi_label=False)
            top_label = output['labels'][0]
            score = output['scores'][0]

            is_relevant = 0
            tag = "IRRELEVANT"

            # --- FILTRO HEURÍSTICO (Para detectar Listas Comerciales/Catálogos) ---
            # Buscamos patrones de precios, rangos de edad de catálogo y términos de descarga
            patrones_lista = ["£", "free:", "aged 0-9", "aged 10-19", "aged 20-29", "free in apple", "app store", "download for"]
            es_lista_comercial = any(patron in text.lower() for patron in patrones_lista)

            # --- LÓGICA DE DECISIÓN REFINADA ---
            # Bajamos el umbral a 0.45 para no perder artículos descriptivos como el de Glow
            if score > 0.45:
                if top_label == "socio-technical analysis of fertility and period tracking apps":
                    if not es_lista_comercial:
                        is_relevant = 1
                        tag = "apps_as_main_topic"
                    else:
                        tag = "DISCARDED_COMMERCIAL_LIST"

                elif top_label == "privacy risks, data surveillance and legal accountability of apps":
                    is_relevant = 1
                    tag = "apps_and_data_privacy_practices"

            results.append({
                'is_relevant_binary': is_relevant,
                'thesis_tag': tag,
                'ai_confidence': score,
                'ai_topic': top_label
            })
        except Exception as e:
            results.append({'is_relevant_binary': 0, 'thesis_tag': "ERROR", 'ai_confidence': 0, 'ai_topic': "ERROR"})

    df_results = pd.DataFrame(results)
    df_final = pd.concat([df, df_results], axis=1)
    df_final.to_csv(output_csv, index=False)
    print(f"\n--- Proceso completado. Resultados en: {output_csv} ---")

if __name__ == "__main__":
    run_transformer_pipeline('corpus_final_procesado_v12.csv', 'results_transformers_v12.csv')