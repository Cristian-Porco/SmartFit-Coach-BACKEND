import os
from dotenv import load_dotenv

# Carica variabili da .env (OPENAI_API_KEY)
load_dotenv()

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