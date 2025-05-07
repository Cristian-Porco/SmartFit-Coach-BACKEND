import os
from dotenv import load_dotenv

# Carica il file .env
load_dotenv()

# Import aggiornati
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

# Istanzia il modello
llm = ChatOpenAI(
    temperature=0,
    model_name="gpt-3.5-turbo",  # o "gpt-4"
    api_key=os.getenv("OPENAI_API_KEY")
)

# Template per il prompt
prompt = PromptTemplate.from_template("""
Dato il seguente obiettivo descritto da un utente, restituisci una sola parola tra:
fitness, bodybuilding, powerlifting, streetlifting.

Descrizione: "{description}"

Risposta:
""")

# Catena moderna usando pipe
chain = prompt | llm

def infer_goal_target(description: str) -> str:
    try:
        result = chain.invoke({"description": description})
        return result.content.strip().lower()
    except Exception as e:
        print(f"Errore LangChain/OpenAI: {e}")
        return ""
