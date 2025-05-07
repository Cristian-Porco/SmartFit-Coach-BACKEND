import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def infer_goal_target(description):
    prompt = f"""In base alla seguente descrizione dell'obiettivo, restituisci una sola parola tra: fitness, bodybuilding, powerlifting, streetlifting.
Descrizione: "{description}"
Risposta:"""

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=10,
        temperature=0
    )
    return response.choices[0].text.strip().lower()
