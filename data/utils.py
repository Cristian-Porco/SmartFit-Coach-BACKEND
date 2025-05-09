import json
from django.db.models import Q

import os
from dotenv import load_dotenv

# Carica variabili da .env (OPENAI_API_KEY)
load_dotenv()


def find_matching_food_items(keywords: list[str]):
    from data.models import FoodItem
    query = Q()
    for kw in keywords:
        query |= Q(name__icontains=kw)
    return list(FoodItem.objects.filter(query).distinct())


# Import aggiornati (LangChain 0.2+)
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# === LLM configuration ===
llm = ChatOpenAI(
    temperature=0,
    model_name="gpt-3.5-turbo",
    api_key=os.getenv("OPENAI_API_KEY")
)

# === Prompt per inferenza categoria ===
prompt = PromptTemplate.from_template("""
Dato il seguente obiettivo descritto da un utente, restituisci una sola parola tra:
fitness, bodybuilding, powerlifting, streetlifting.

Descrizione: "{description}"

Risposta:
""")

chain = prompt | llm

def infer_goal_target(description: str) -> str:
    try:
        result = chain.invoke({"description": description})
        return getattr(result, "content", "").strip().lower()
    except Exception as e:
        print(f"Errore LangChain/OpenAI: {e}")
        return ""

# === Prompt per spiegazione scelta IA ===
explain_prompt = PromptTemplate.from_template("""
Hai classificato l'obiettivo utente come "{category}".
Obiettivo dell'utente: "{description}"

Spiega brevemente (massimo 300 caratteri) perché questa categoria è la più adatta.
Risposta:
""")

explain_chain = explain_prompt | llm

def explain_goal_target(description: str, category: str) -> str:
    try:
        result = explain_chain.invoke({
            "description": description,
            "category": category
        })
        return getattr(result, "content", "").strip()
    except Exception as e:
        print(f"Errore nella spiegazione: {e}")
        return ""

# === Prompt per analisi peso utente ===
weight_analysis_prompt = PromptTemplate.from_template("""
L'utente ha come obiettivo "{goal}".
Ecco i suoi dati di peso nel tempo:

{weights}

Scrivi un'analisi sintetica (massimo 500 caratteri) sull'andamento del peso rispetto all'obiettivo.
Sii chiaro, professionale e conciso.
""")

weight_chain = weight_analysis_prompt | llm

def generate_weight_analysis(weights: list, goal: str) -> str:
    """
    :param weights: lista di tuple (data, peso), es. [("2025-04-01", 83.2), ...]
    :param goal: stringa, es. "bodybuilding"
    :return: stringa con analisi IA
    """
    weights_str = "\n".join(f"{date}: {weight}kg" for date, weight in weights)
    try:
        result = weight_chain.invoke({"goal": goal, "weights": weights_str})
        text = getattr(result, "content", "").strip()
        return text.strip()
    except Exception as e:
        print(f"Errore durante l'analisi IA: {e}")
        return "Errore durante l'analisi IA."


# === Prompt per analisi misure corporee (BodyMeasurement) ===
body_measurement_prompt = PromptTemplate.from_template("""
L'utente ha come obiettivo: "{goal}".
Questi sono i suoi dati di misurazione corporea nel tempo:

{measurements}

Scrivi un'analisi sintetica (massimo 500 caratteri) sull'andamento delle singole aree corporee rispetto all'obiettivo.
Sii chiaro, professionale e conciso.
""")

body_chain = body_measurement_prompt | llm

def generate_body_analysis(measurements: list, goal: str) -> str:
    """
    :param measurements: lista di dict {"date": "2025-05-01", "chest": 102.3, ...}
    :param goal: es. "bodybuilding"
    :return: stringa con analisi IA
    """
    def format_measure_row(entry):
        parts = [f"{entry['date']}:"]
        for key, value in entry.items():
            if key != "date" and value is not None:
                parts.append(f"{key.capitalize()} {value}cm")
        return " ".join(parts)

    formatted = "\n".join(format_measure_row(m) for m in measurements)

    try:
        result = body_chain.invoke({"goal": goal, "measurements": formatted})
        text = getattr(result, "content", "").strip()
        return text.strip()
    except Exception as e:
        print(f"Errore nell'analisi delle misure: {e}")
        return "Errore durante l'analisi delle misure."


# === Prompt per analisi pasti (FoodParsing) ===
food_parsing_prompt = PromptTemplate.from_template("""
Dalla seguente frase in linguaggio naturale:

"{input_text}"

1. Identifica ogni pasto o alimento menzionato.
2. Per ciascuno, genera un oggetto JSON con i seguenti campi:
    - "meal": nome sintetico del pasto o alimento (es. "Pasta al sugo")
    - "keywords": elenco di parole strettamente legate al pasto (ingredienti, alimenti, termini specifici).  
      Per ogni parola chiave, includi **sia la forma singolare che quella plurale**, se rilevante (es. "patata", "patate").
    - "quantity": stima della quantità in grammi, espressa come numero intero (es. 150).  
      Se nella frase ci sono termini qualitativi (es. "abbondante", "qualche", "una porzione"), interpreta e traduci in un valore numerico coerente.

Restituisci esclusivamente un array JSON. Nessuna spiegazione o testo fuori dal JSON.
""")

food_chain = food_parsing_prompt | ChatOpenAI(temperature=0)

def generate_food_analysis(input_text: str) -> list:
    """
    :param input_text: Frase in linguaggio naturale (es. "Ho mangiato una pasta al sugo con delle patate fritte")
    :return: Lista di dizionari JSON con campi "pasto", "parole_chiave" e "quantità"
    """
    try:
        result = food_chain.invoke({"input_text": input_text})
        content = getattr(result, "content", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Errore nell'analisi del pasto: {e}")
        return []


# === Prompt per selezione miglior alimento ===
food_item_selection_prompt = PromptTemplate.from_template("""
Tra i seguenti alimenti candidati, scegli quello che corrisponde meglio al pasto descritto:

Nome del pasto: "{meal}"

Candidati disponibili:
{candidates}

Restituisci esclusivamente il nome dell'alimento selezionato (nessuna spiegazione, solo testo).
""")

# Usa un modello diverso solo per questa chain
food_item_selector_llm = ChatOpenAI(
    temperature=0,
    model_name="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

food_item_selector_chain = food_item_selection_prompt | food_item_selector_llm

def select_best_food_item(meal: str, food_items: list["FoodItem"]) -> dict:
    if not food_items:
        return {"name": None, "id": None}

    formatted_candidates = "\n".join(f"- {item.name}" for item in food_items)

    try:
        result = food_item_selector_chain.invoke({
            "meal": meal,
            "candidates": formatted_candidates
        })
        name = getattr(result, "content", "").strip()

        # Cerca l'oggetto originale con quel nome
        matching = next((item for item in food_items if item.name == name), None)

        return {
            "name": name,
            "id": matching.id if matching else None
        }

    except Exception as e:
        print(f"Errore nella selezione dell'alimento: {e}")
        return {"name": None, "id": None}