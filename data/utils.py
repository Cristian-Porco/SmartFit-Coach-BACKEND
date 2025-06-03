import base64
import json
import re

from django.db import transaction
from django.db.models import Q

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage

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

# === Configurazione LLM ===
llm_3_5_turbo = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))

llm_4o_mini = ChatOpenAI(temperature=0, model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

llm_4o = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
llm_4o_semicreativa = ChatOpenAI(model="gpt-4o", temperature=0.5, api_key=os.getenv("OPENAI_API_KEY"))
llm_4o_creativa = ChatOpenAI(model="gpt-4o", temperature=0.9, api_key=os.getenv("OPENAI_API_KEY"))




goals_target_prompt = PromptTemplate.from_template("""
Dato il seguente obiettivo descritto da un utente, restituisci una sola parola tra:
fitness, bodybuilding, powerlifting, streetlifting.

Descrizione: "{description}"

Risposta:
""")

# Questa riga crea una catena LangChain combinando il prompt definito sopra con un modello linguistico (ad es. GPT-3.5).
# La catena si occupa di ricevere in input una descrizione testuale dell'obiettivo dell'utente
# (come ad esempio: "Voglio diventare più forte e migliorare la mia forma fisica") e produce in risposta 
# una classificazione automatica dell'obiettivo in una delle seguenti categorie predefinite: 
# 'fitness', 'bodybuilding', 'powerlifting', 'streetlifting'.
#
# L'inferenza viene fatta tramite intelligenza artificiale: il modello analizza semanticamente il contenuto 
# della descrizione e sceglie la categoria che meglio rappresenta l’intento espresso, anche quando l’utente 
# non usa esplicitamente le parole chiave di riferimento.
#
# Questo approccio consente di offrire una classificazione intelligente e flessibile, utile per personalizzare 
# programmi di allenamento, raccomandazioni nutrizionali o percorsi utente su piattaforme fitness.
goals_target_chain = goals_target_prompt | llm_3_5_turbo

def infer_goal_target(description: str) -> str:
    """
    Funzione che utilizza un modello linguistico (LLM) per determinare automaticamente
    la categoria di allenamento a cui appartiene un obiettivo descritto in linguaggio naturale.

    Parametri:
    - description (str): una frase o testo libero scritto dall’utente, che descrive il proprio obiettivo fisico o sportivo.

    Ritorna:
    - Una stringa contenente una sola parola tra: 'fitness', 'bodybuilding', 'powerlifting', 'streetlifting',
      scelta in base all’analisi semantica del testo.
    - In caso di errore nell'inferenza o nella comunicazione con il modello, restituisce una stringa vuota.

    Esempio:
        infer_goal_target("Voglio migliorare la mia forza massimale nello squat") --> "powerlifting"
    """
    try:
        result = goals_target_chain.invoke({"description": description})
        return getattr(result, "content", "").strip().lower()
    except Exception as e:
        print(f"Errore LangChain/OpenAI: {e}")
        return ""




goal_description_prompt = PromptTemplate.from_template("""
Hai classificato l'obiettivo utente come "{category}".
Obiettivo dell'utente: "{description}"

Spiega brevemente (massimo 300 caratteri) perché questa categoria è la più adatta.
Risposta:
""")

# Questa catena LangChain utilizza un modello linguistico (es. GPT-3.5) per generare una spiegazione sintetica
# della classificazione precedentemente assegnata all’obiettivo dell’utente.
# A partire dalla descrizione testuale dell’obiettivo e dalla categoria scelta (fitness, bodybuilding, ecc.),
# il modello motiva la propria scelta in modo conciso e comprensibile, facilitando la trasparenza
# e l'affidabilità percepita del sistema.
#
# Questo è utile per mostrare all’utente una giustificazione “umana” alla categorizzazione ricevuta,
# migliorando la fiducia nell’algoritmo e facilitando eventuali correzioni o interventi da parte di un trainer.
goal_description_chain = goal_description_prompt | llm_3_5_turbo

def explain_goal_target(description: str, category: str) -> str:
    """
    Funzione che fornisce una spiegazione sintetica (max 300 caratteri) per giustificare
    la classificazione di un obiettivo utente in una delle categorie predefinite.

    Parametri:
    - description (str): descrizione libera dell’obiettivo dell’utente, es. "Voglio aumentare la massa muscolare".
    - category (str): categoria scelta dal modello (fitness, bodybuilding, powerlifting, streetlifting).

    Ritorna:
    - Una breve frase generata dall’IA che spiega in modo chiaro e logico
      perché l’obiettivo rientra nella categoria indicata.
    - In caso di errore, restituisce una stringa vuota e stampa un messaggio di log.

    Esempio:
        explain_goal_target("Voglio un fisico scolpito e definito", "bodybuilding")
        --> "Perché l'obiettivo si concentra sull'estetica muscolare, tipico del bodybuilding."
    """
    try:
        result = goal_description_chain.invoke({
            "description": description,
            "category": category
        })
        return getattr(result, "content", "").strip()
    except Exception as e:
        print(f"Errore nella spiegazione: {e}")
        return ""
    

    

weight_analysis_prompt = PromptTemplate.from_template("""
L'utente ha come obiettivo "{goal}".
Ecco i suoi dati di peso nel tempo:

{weights}

Scrivi un'analisi sintetica (massimo 500 caratteri) sull'andamento del peso rispetto all'obiettivo.
Sii chiaro, professionale e conciso.
""")

# Questa catena LangChain prende in input:
# - l’obiettivo dell’utente (es. "bodybuilding", "fitness", ecc.)
# - una serie di misurazioni del peso nel tempo (date e valori in kg)
#
# Utilizza un modello linguistico (LLM) per generare un commento analitico e professionale sull'andamento del peso.
# L'analisi è pensata per essere utile come feedback automatico nei report utente, dashboard, o interfacce di coaching.
# Il modello valuta se il trend del peso è coerente con l’obiettivo indicato (es. aumento per bodybuilding, calo per fitness),
# e restituisce un testo sintetico, massimo 500 caratteri, che commenta in modo chiaro e oggettivo l’andamento registrato.
weight_analysis_chain = weight_analysis_prompt | llm_3_5_turbo

def generate_weight_analysis(weights: list, goal: str) -> str:
    """
    Analizza l'andamento del peso corporeo dell’utente in relazione al suo obiettivo di allenamento
    (es. dimagrimento, aumento massa, mantenimento), restituendo un commento professionale generato dall’IA.

    :param weights: lista di tuple (data, peso), es. [("2025-04-01", 83.2), ...]
                    Le date devono essere in formato stringa ISO (YYYY-MM-DD) e i pesi in float (kg).
    :param goal: stringa che rappresenta l'obiettivo dell’utente, es. "fitness", "bodybuilding", "powerlifting", "streetlifting"
    :return: stringa contenente un'analisi concisa dell’andamento del peso (massimo 500 caratteri).
             In caso di errore, restituisce un messaggio di fallback.

    Esempio:
        generate_weight_analysis([("2025-04-01", 80.0), ("2025-04-15", 81.2)], "bodybuilding")
        --> "Il peso è aumentato gradualmente, segnale positivo per un obiettivo di crescita muscolare."

    Questo tipo di feedback può essere integrato in app di monitoraggio o dashboard fitness per fornire
    valutazioni intelligenti e contestuali, migliorando l’interazione e la motivazione dell’utente.
    """
    weights_str = "\n".join(f"{date}: {weight}kg" for date, weight in weights)
    try:
        result = weight_analysis_chain.invoke({"goal": goal, "weights": weights_str})
        text = getattr(result, "content", "").strip()
        return text.strip()
    except Exception as e:
        print(f"Errore durante l'analisi IA: {e}")
        return "Errore durante l'analisi IA."
    



body_measurement_analysis_prompt = PromptTemplate.from_template("""
L'utente ha come obiettivo: "{goal}".
Questi sono i suoi dati di misurazione corporea nel tempo:

{measurements}

Scrivi un'analisi sintetica (massimo 500 caratteri) sull'andamento delle singole aree corporee rispetto all'obiettivo.
Sii chiaro, professionale e conciso.
""")

# Questa catena LangChain combina il prompt testuale con un modello LLM (es. GPT-3.5),
# per generare un’analisi intelligente dell’andamento delle misure corporee nel tempo,
# in funzione dell'obiettivo dichiarato dall’utente (es. "bodybuilding", "fitness", "powerlifting", ecc.).
#
# Il prompt fornisce al modello i dati grezzi delle misurazioni (formattati come testo leggibile)
# e chiede di produrre una breve analisi (max 500 caratteri), professionale e concisa,
# che valuti se le variazioni corporee osservate sono coerenti con il goal prefissato.
body_measurement_analysis_chain = body_measurement_analysis_prompt | llm_3_5_turbo

def generate_body_analysis(measurements: list, goal: str) -> str:
    """
    Analizza l’evoluzione delle misure corporee (torace, braccia, vita, ecc.) nel tempo,
    generando un commento professionale, sintetico e coerente con l’obiettivo fitness o sportivo dell’utente.

    :param measurements: lista di dizionari con data e misure, es.:
                         [
                             {"date": "2025-05-01", "chest": 102.3, "waist": 82.1, "arms": 35.2},
                             {"date": "2025-05-15", "chest": 104.0, "waist": 81.8, "arms": 36.0}
                         ]
                         Le chiavi rappresentano le aree corporee (in cm), e "date" deve essere in formato ISO.
                         I valori nulli o assenti vengono ignorati nella formattazione.
    :param goal: stringa che rappresenta l'obiettivo dell’utente, come "bodybuilding", "fitness", ecc.

    :return: stringa con una breve analisi generata dall'IA (max 500 caratteri) che descrive:
             - quali aree sono migliorate o stabili
             - se il trend è coerente con l’obiettivo
             - eventuali progressi significativi

    In caso di errore tecnico o di inferenza, restituisce un messaggio di fallback.
    """

    def format_measure_row(entry):
        # Converte ogni record di misure in una riga leggibile, es:
        # "2025-05-01: Chest 102.3cm Waist 82.1cm Arms 35.2cm"
        parts = [f"{entry['date']}:"]
        for key, value in entry.items():
            if key != "date" and value is not None:
                parts.append(f"{key.capitalize()} {value}cm")
        return " ".join(parts)

    # Costruisce la stringa completa da passare al modello, una riga per ogni data
    formatted = "\n".join(format_measure_row(m) for m in measurements)

    try:
        result = body_measurement_analysis_chain.invoke({"goal": goal, "measurements": formatted})
        text = getattr(result, "content", "").strip()
        return text
    except Exception as e:
        print(f"Errore nell'analisi delle misure: {e}")
        return "Errore durante l'analisi delle misure."
    



food_parsing_natural_language_prompt = PromptTemplate.from_template("""
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

# La catena food_chain unisce il prompt a un modello AI (GPT-4o mini in questo caso),
# che analizza frasi libere in linguaggio naturale e le trasforma in una struttura JSON utile per il tracciamento alimentare.
#
# Il modello è istruito a:
# - estrarre i singoli pasti o alimenti menzionati
# - generare una descrizione sintetica di ciascun alimento
# - identificare parole chiave rilevanti (sia in forma singolare che plurale)
# - stimare la quantità consumata, anche in assenza di numeri espliciti (es. "qualche patatina" → 50g)
#
# Questo output strutturato può essere poi utilizzato per popolare una food diary app, una dashboard nutrizionale o un backend per piani alimentari intelligenti.
food_parsing_natural_language_chain = food_parsing_natural_language_prompt | llm_4o_mini

def generate_food_analysis(input_text: str) -> list:
    """
    Analizza una frase libera dell’utente che descrive cosa ha mangiato,
    e restituisce una lista di pasti/alimenti in formato JSON strutturato.

    :param input_text: Frase in linguaggio naturale (es. "Ho mangiato una pasta al sugo con delle patate fritte")
    :return: Lista di dizionari, ciascuno con:
             - "meal": stringa sintetica (es. "Pasta al sugo")
             - "keywords": lista di parole chiave (es. ["patata", "patate", "olio", "frittura"])
             - "quantity": quantità stimata in grammi (int)

    L’output può essere usato per:
    - Alimentare un diario alimentare digitale
    - Popolare moduli di inserimento automatico dei pasti
    - Generare riepiloghi nutrizionali o analisi caloriche

    In caso di errore nella risposta del modello o nel parsing JSON, restituisce una lista vuota.
    """
    try:
        result = food_parsing_natural_language_chain.invoke({"input_text": input_text})
        content = getattr(result, "content", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Errore nell'analisi del pasto: {e}")
        return []
    



food_item_selection_prompt = PromptTemplate.from_template("""
Tra i seguenti alimenti candidati, scegli quello che corrisponde meglio al pasto descritto:

Nome del pasto: "{meal}"

Candidati disponibili:
{candidates}

Restituisci esclusivamente il nome dell'alimento selezionato (nessuna spiegazione, solo testo).
""")

# Questa catena LangChain utilizza un modello IA (GPT-4o mini) per confrontare il nome di un pasto
# con una lista di alimenti candidati (provenienti da un database o da un sistema utente) e selezionare
# quello che meglio corrisponde in base alla semantica del nome.
#
# Il prompt è progettato per restituire *esclusivamente* il nome dell’alimento più pertinente.
# Il modello si basa su comprensione semantica e similarità linguistica, anche in presenza di sinonimi,
# varianti ortografiche o nomi descrittivi vaghi (es. "riso con pollo" vs "piatto unico pollo e riso").
food_item_selector_chain = food_item_selection_prompt | llm_4o_mini

def select_best_food_item(meal: str, food_items: list["FoodItem"]) -> dict:
    """
    Dato il nome di un pasto e una lista di oggetti `FoodItem`, utilizza un modello IA per selezionare
    il candidato più coerente semanticamente con il nome del pasto.

    :param meal: stringa con il nome del pasto descritto dall’utente (es. "pasta al sugo con tonno")
    :param food_items: lista di oggetti `FoodItem`, ciascuno con almeno attributi `name` (str) e `id` (str|int)

    :return: dizionario con:
        - "name": nome dell’alimento selezionato
        - "id": ID corrispondente all’alimento nel database
        Se nessun alimento corrisponde, ritorna {"name": None, "id": None}

    Utilizzo tipico:
        - Abbinamento tra descrizione libera dell’utente e dati strutturati
        - Aiuto nella normalizzazione di input testuali in interfacce nutrizionali
        - Supporto alla compilazione automatica di pasti giornalieri

    Esempio:
        select_best_food_item("riso con pollo", [FoodItem("Riso basmati", 1), FoodItem("Pollo al curry", 2)])
        → {"name": "Pollo al curry", "id": 2}
    """

    if not food_items:
        return {"name": None, "id": None}

    # Costruiamo l’elenco leggibile dei candidati da fornire al modello
    formatted_candidates = "\n".join(f"- {item.name}" for item in food_items)

    try:
        # Invochiamo la catena AI per ottenere il nome selezionato
        result = food_item_selector_chain.invoke({
            "meal": meal,
            "candidates": formatted_candidates
        })
        name = getattr(result, "content", "").strip()

        # Cerchiamo l’alimento originale che ha quel nome
        matching = next((item for item in food_items if item.name == name), None)

        return {
            "name": name,
            "id": matching.id if matching else None
        }

    except Exception as e:
        print(f"Errore nella selezione dell'alimento: {e}")
        return {"name": None, "id": None}




food_parsing_vision_prompt = """
L'immagine che ti fornisco mostra uno o più alimenti o pasti.

Analizza il contenuto visivo e restituisci un array JSON con oggetti aventi i seguenti campi:
- "meal": nome sintetico del pasto (es. "Pasta al sugo")
- "keywords": parole chiave attinenti al pasto, includendo sia forma singolare che plurale (es. "patata", "patate")
- "quantity": quantità stimata in grammi, come numero intero

Restituisci solo l'array JSON. Nessuna spiegazione.
"""

def encode_image(file) -> str:
    """
    Converte un file immagine in una stringa codificata in Base64, 
    adatta per l'invio a un modello IA con supporto Vision (es. GPT-4o).
    """
    import io
    buffer = io.BytesIO()
    file.seek(0)
    buffer.write(file.read())
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def generate_food_analysis_from_image_file(file) -> list:
    """
    Analizza visivamente un'immagine contenente cibo e restituisce un array JSON
    con i dettagli identificati su ciascun alimento rilevato.

    :param file: oggetto file (es. caricato da utente via form) contenente un'immagine di uno o più pasti.
    :return: lista di dizionari, ciascuno con:
             - "meal": nome sintetico del pasto (es. "insalata con tonno")
             - "keywords": lista di parole chiave (es. ["tonno", "insalata", "pomodoro", "pomodori"])
             - "quantity": stima della quantità (int, in grammi)

    La funzione utilizza il modello GPT-4o con supporto multimodale (testo + immagine)
    per interpretare visivamente il contenuto del file, trasformandolo in dati strutturati.

    In caso di errore nel parsing o nella risposta del modello, restituisce una lista vuota.
    """

    try:
        # Codifica l'immagine come stringa base64 per inviarla al modello via URL data URI
        base64_img = encode_image(file)

        # Componiamo il messaggio multimodale da inviare: testo + immagine
        message = HumanMessage(content=[
            {"type": "text", "text": food_parsing_vision_prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_img}"
                }
            }
        ])

        # Invochiamo il modello GPT-4o Vision per ottenere una risposta testuale
        result = llm_4o.invoke([message])
        content = result.content.strip()

        # Estraiamo l'array JSON dalla risposta, isolando la sezione tra [ ... ]
        start = content.find("[")
        end = content.rfind("]") + 1
        if start == -1 or end == -1:
            raise ValueError("La risposta non contiene un JSON valido.")
        return json.loads(content[start:end])

    except Exception as e:
        print(f"Errore LangChain Vision: {e}")
        return []




food_plan_optimization_prompt = PromptTemplate.from_template("""
L'obiettivo è ottimizzare un piano alimentare in termini di nutrienti, considerando solo i valori nutrizionali degli alimenti, e ignorando il contenuto semantico o la varietà.

Il piano deve rispettare i seguenti vincoli nutrizionali totali:
- Calorie: massimo {max_kcal} kcal
- Proteine: minimo {min_protein} g, massimo {max_protein} g
- Carboidrati: minimo {min_carbs} g, massimo {max_carbs} g
- Grassi: minimo {min_fats} g, massimo {max_fats} g

L'obiettivo è avvicinarsi **quanto più possibile ai limiti massimi**, senza mai superarli, **e garantire il raggiungimento dei valori minimi** per ciascun macronutriente.

Ecco l'elenco degli alimenti disponibili nel piano (ogni alimento ha quantità iniziale e valori per 100g):

{food_items}

Regole da rispettare:
- Modifica le quantità (in grammi) per ogni alimento.
- Ogni quantità deve essere **compresa tra 10g e 200g**.
- **Non sono ammesse quantità pari a 0g.**
- **Non superare alcun valore massimo.**
- **Raggiungi almeno i valori minimi.**
- Ignora il tipo di alimento, lavora solo sui numeri.

Rispondi solo con un JSON **puro**, senza blocchi di codice, backtick o etichette. Il risultato deve essere solo l'array JSON, ad esempio:

[
  {{ "id": 1, "adjusted_quantity_in_grams": 100 }},
  {{ "id": 2, "adjusted_quantity_in_grams": 150 }}
]
""")

# Catena LangChain che utilizza il modello GPT-4o per ottimizzare le quantità degli alimenti
# in un piano alimentare, tenendo conto esclusivamente dei dati numerici nutrizionali
food_plan_optimization_chain = food_plan_optimization_prompt | llm_4o

def generate_foodplan_adjustment(food_plan) -> str:
    """
    Usa un modello IA per calcolare le quantità ottimali di ciascun alimento all’interno
    di un piano alimentare, in modo da avvicinarsi ai limiti massimi (senza mai superarli)
    e garantire almeno i minimi di ciascun macronutriente (proteine, carboidrati, grassi).

    :param food_plan: istanza del modello `FoodPlan`, contenente nutrienti target e gli alimenti associati
    :return: stringa JSON contenente le nuove quantità per ogni alimento

    L'output sarà un JSON tipo:
    [
        { "id": 1, "adjusted_quantity_in_grams": 100 },
        { "id": 3, "adjusted_quantity_in_grams": 150 }
    ]
    """

    try:
        # Estrae gli alimenti associati al piano, con i dati nutrizionali per 100g
        items = food_plan.foodplanitem_set.select_related("food_item")

        # Costruisce la stringa leggibile per il prompt IA, uno per riga
        food_items_str = "\n".join([
            f"- ID {item.id} - {item.food_item.name}: {item.quantity_in_grams}g "
            f"(kcal: {item.food_item.kcal_per_100g}, pro: {item.food_item.protein_per_100g}, "
            f"carb: {item.food_item.carbs_per_100g}, zuccheri: {item.food_item.sugars_per_100g or 0}, "
            f"grassi: {item.food_item.fats_per_100g}, fibre: {item.food_item.fiber_per_100g})"
            for item in items
        ])

        # Invoca la catena IA con i limiti target e i dati formattati
        result = food_plan_optimization_chain.invoke({
            "max_protein": food_plan.max_protein,
            "max_carbs": food_plan.max_carbs,
            "max_fats": food_plan.max_fats,
            "min_protein": round(food_plan.max_protein * 0.95, 1),
            "min_carbs": round(food_plan.max_carbs * 0.95, 1),
            "min_fats": round(food_plan.max_fats * 0.95, 1),
            "max_kcal": food_plan.max_kcal,
            "food_items": food_items_str
        })

        return getattr(result, "content", "").strip()

    except Exception as e:
        print(f"Errore durante l’ottimizzazione IA: {e}")
        return "Errore durante l’ottimizzazione IA."

def apply_foodplan_adjustment(data: list[dict]) -> list[int]:
    """
    Applica le nuove quantità agli oggetti `FoodPlanItem`, ma **solo se la quantità è cambiata** rispetto a quella originale.

    :param data: lista di dizionari con id alimento e nuova quantità:
                 es. [{ "id": 2, "adjusted_quantity_in_grams": 130 }, ...]
    :return: lista di ID degli alimenti effettivamente aggiornati

    Il salvataggio avviene in transazione atomica per garantire coerenza,
    ed evita aggiornamenti ridondanti se la quantità è praticamente invariata.
    """
    from .models import FoodPlanItem
    from django.db import transaction

    updated_ids = []

    with transaction.atomic():
        for entry in data:
            item_id = entry.get("id")
            new_qty = entry.get("adjusted_quantity_in_grams")

            if item_id is None or new_qty is None or new_qty < 10:
                continue

            try:
                item = FoodPlanItem.objects.get(id=item_id)
                # Evita aggiornamenti irrilevanti (differenza inferiore a 0.01g)
                if abs(item.quantity_in_grams - new_qty) >= 0.01:
                    item.quantity_in_grams = new_qty
                    item.save()
                    updated_ids.append(item_id)
            except FoodPlanItem.DoesNotExist:
                continue

    return updated_ids




food_plan_personalized_prompt = PromptTemplate.from_template("""
L'utente ha come obiettivo nutrizionale: "{goal}".

Ecco i suoi dati recenti:
- Peso nell'ultimo mese:
{weights}

- Misure corporee principali dell'ultimo mese:
{measurements}

Nella precedente scheda alimentare seguiva questi macro:
- Proteine: {prev_protein} g
- Carboidrati: {prev_carbs} g
- Grassi: {prev_fats} g
- Calorie: {prev_kcal} kcal

Genera un piano alimentare giornaliero completo, suddiviso in 4-6 pasti.

Ogni alimento deve essere un oggetto separato. Es. "Yogurt con miele e mandorle" → 3 oggetti distinti.

Per ogni alimento, restituisci un oggetto JSON con:
- "meal": nome sintetico
- "keywords": parole chiave (singolare/plurale + componenti del nome)
- "quantity": quantità stimata in grammi (intero)
- "matched_food_item": oggetto con "name"
- "section": nome della sezione (es. Colazione)
- "section_keywords": parole chiave legate al momento della giornata (es. mattina, colazione)

Rispondi solo con un array JSON valido. Nessuna spiegazione, nessun blocco ```json.
""")

# Catena LangChain con GPT-4o che genera un piano alimentare completo e strutturato
# basandosi su: obiettivo nutrizionale, andamento peso e misure, e macro precedenti
food_plan_personalized_chain = food_plan_personalized_prompt | llm_4o

def generate_food_plan_from_context(goal: str, weights: list, measurements: list, prev_macros: dict) -> list:
    """
    Genera automaticamente un piano alimentare giornaliero strutturato in 4-6 pasti,
    utilizzando un modello IA multimodale e i dati dell’utente (peso, misure e macro precedenti).

    :param goal: stringa descrittiva (es. "massa", "definizione", "ricomposizione")
    :param weights: lista di tuple (data, peso), es. [("2025-05-01", 78.4), ...]
    :param measurements: lista di dict, es. [{"date": "2025-05-01", "chest": 102.3, "waist": 80.0}]
    :param prev_macros: dict con macro seguiti prima, es:
        {
            "max_protein": 160,
            "max_carbs": 300,
            "max_fats": 70,
            "max_kcal": 2600
        }

    :return: lista di dizionari JSON, uno per alimento, con i seguenti campi:
        - meal: nome sintetico (es. "Fesa di tacchino")
        - keywords: parole chiave (singolare/plurale) dell’alimento
        - quantity: quantità suggerita in grammi (int)
        - matched_food_item: oggetto con nome (es. {"name": "Fesa di tacchino"})
        - section: sezione del pasto (es. "Spuntino post workout")
        - section_keywords: parole associate alla fascia oraria (es. ["pomeriggio", "post allenamento"])

    Il risultato è un piano alimentare utilizzabile per popolare interfacce utente,
    moduli nutrizionali, o piani AI-driven di meal planning.

    Se la risposta del modello non contiene un JSON valido, ritorna una lista vuota.
    """

    def format_weights(w):
        # Converte il peso in formato testo leggibile per il modello
        return "\n".join(f"{d}: {v} kg" for d, v in w)

    def format_measurements(m):
        # Converte le misure corporee in formato testo leggibile per il modello
        lines = []
        for row in m:
            parts = [f"{row['date']}:"]
            for k, v in row.items():
                if k != "date" and v is not None:
                    parts.append(f"{k.capitalize()} {v} cm")
            lines.append(" ".join(parts))
        return "\n".join(lines)

    try:
        # Invoca la catena AI fornendo tutti i dati utente formattati
        response = food_plan_personalized_chain.invoke({
            "goal": goal,
            "weights": format_weights(weights),
            "measurements": format_measurements(measurements),
            "prev_protein": prev_macros["max_protein"],
            "prev_carbs": prev_macros["max_carbs"],
            "prev_fats": prev_macros["max_fats"],
            "prev_kcal": prev_macros["max_kcal"]
        })

        content = response.content.strip()

        # Estrae il blocco JSON delimitato da [ ... ]
        start = content.find("[")
        end = content.rfind("]") + 1

        if start == -1 or end == -1:
            raise ValueError("Risposta non contiene JSON valido")

        return json.loads(content[start:end])

    except Exception as e:
        print(f"Errore generazione piano: {e}")
        return []




food_item_generate_macros_prompt = PromptTemplate.from_template("""
Inventa un alimento realistico con il nome "{name}" e genera i suoi valori nutrizionali per 100g. 

Restituisci solo un JSON con i seguenti campi (nessun testo extra):
- "name": nome dell'alimento
- "kcal_per_100g"
- "protein_per_100g"
- "carbs_per_100g"
- "sugars_per_100g"
- "fats_per_100g"
- "saturated_fats_per_100g"
- "fiber_per_100g"

Non includere barcode o brand. Scrivi solo il JSON.
""")

# Catena LangChain che usa GPT-4o per creare un alimento plausibile a partire da un nome utente.
# Il modello genera direttamente i valori nutrizionali realistici per 100g.
food_item_generate_macros_chain = food_item_generate_macros_prompt | llm_4o

def generate_food_item(name: str, user) -> "FoodItem | None":
    """
    Genera un nuovo alimento fittizio ma nutrizionalmente realistico a partire da un nome,
    e lo salva nel database associandolo all’utente che lo ha richiesto.

    :param name: Nome dell’alimento inventato (es. "Pane di quinoa integrale")
    :param user: Utente Django a cui associare l'alimento (campo author)
    :return: istanza salvata di FoodItem o None in caso di errore
    """

    try:
        # Invochiamo la catena IA per ottenere i dati nutrizionali dell’alimento generato
        result = food_item_generate_macros_chain.invoke({"name": name})
        content = result.content.strip()

        # Estraiamo il blocco JSON dalla risposta (isolando la prima e ultima graffa)
        start = content.find("{")
        end = content.rfind("}") + 1
        if start == -1 or end == -1:
            raise ValueError("JSON non trovato nella risposta.")

        data = json.loads(content[start:end])

        # Importiamo il modello solo se necessario (lazy load per evitare circolarità)
        from data.models import FoodItem

        # Creiamo il nuovo oggetto `FoodItem` nel database
        food = FoodItem.objects.create(
            author=user,
            name=data["name"],
            kcal_per_100g=data["kcal_per_100g"],
            protein_per_100g=data["protein_per_100g"],
            carbs_per_100g=data["carbs_per_100g"],
            sugars_per_100g=data.get("sugars_per_100g"),
            fats_per_100g=data["fats_per_100g"],
            saturated_fats_per_100g=data.get("saturated_fats_per_100g"),
            fiber_per_100g=data["fiber_per_100g"]
        )

        return food

    except Exception as e:
        print(f"Errore generazione alimento: {e}")
        return None




food_plan_generate_macros_prompt = PromptTemplate.from_template("""
L'utente ha il seguente obiettivo: "{goal}".

Andamento del peso nell'ultimo mese:
{weights}

Andamento delle misure corporee nell'ultimo mese:
{measurements}

Nella precedente scheda alimentare ha seguito questi macronutrienti giornalieri:
- Proteine: {prev_protein} g
- Carboidrati: {prev_carbs} g
- Grassi: {prev_fats} g

In base a queste informazioni, proponi una nuova impostazione per i macronutrienti giornalieri, coerente con l'obiettivo e l'evoluzione fisica.

Restituisci esclusivamente un JSON con i seguenti campi:
- "max_protein": grammi di proteine consigliati (intero)
- "max_carbs": grammi di carboidrati consigliati (intero)
- "max_fats": grammi di grassi consigliati (intero)
- "reason": spiegazione dettagliata **in formato HTML**, che illustri il motivo delle modifiche o conferme per ogni macronutriente. Usa tag HTML e metti in <b>grassetto</b> le parole chiave (es. proteine, aumento, riduzione, ecc.)

Rispondi solo con un oggetto JSON valido. Nessun testo introduttivo, nessun blocco ```json.
""")

# Catena LangChain che usa GPT-4o per ricalcolare i fabbisogni nutrizionali dell’utente
# in funzione del suo obiettivo (es. massa, definizione) e dell’evoluzione fisica recente.
food_plan_generate_macros_chain = food_plan_generate_macros_prompt | llm_4o

def generate_new_macros(goal: str, weights: list, measurements: list, prev_macros: dict) -> dict:
    """
    Analizza l’evoluzione fisica dell’utente e propone nuovi valori ottimizzati per i macronutrienti giornalieri.

    :param goal: Obiettivo dichiarato dell’utente (es. "massa", "definizione", "mantenimento")
    :param weights: Lista di tuple (data, peso), es. [("2025-05-01", 78.5), ...]
    :param measurements: Lista di dict con le misure corporee storiche,
                         es. [{"date": "2025-05-01", "waist": 82.0, "chest": 102.5}, ...]
    :param prev_macros: Dizionario con i valori precedenti dei macro:
                        {
                          "max_protein": 160,
                          "max_carbs": 280,
                          "max_fats": 70
                        }

    :return: Dizionario JSON con:
        {
            "max_protein": 165,
            "max_carbs": 290,
            "max_fats": 72,
            "reason": "<p>Spiegazione HTML con <b>parole chiave</b> evidenziate...</p>"
        }

    L’output include sia i nuovi target macro, sia una spiegazione HTML dettagliata e leggibile direttamente
    in interfacce frontend o pannelli di analisi (renderizzata come testo HTML).
    """

    def format_weights(w):
        # Converte il peso in una stringa leggibile per il modello
        return "\n".join(f"{d}: {v} kg" for d, v in w)

    def format_measurements(m):
        # Formatta le misurazioni per il modello in linguaggio leggibile
        lines = []
        for row in m:
            parts = [f"{row['date']}:"]
            for k, v in row.items():
                if k != "date" and v is not None:
                    parts.append(f"{k.capitalize()} {v} cm")
            lines.append(" ".join(parts))
        return "\n".join(lines)

    try:
        # Invio dei dati al modello LLM tramite prompt personalizzato
        result = food_plan_generate_macros_chain.invoke({
            "goal": goal,
            "weights": format_weights(weights),
            "measurements": format_measurements(measurements),
            "prev_protein": prev_macros["max_protein"],
            "prev_carbs": prev_macros["max_carbs"],
            "prev_fats": prev_macros["max_fats"]
        })

        content = result.content.strip()

        # Estrazione del JSON dalla risposta del modello (ignorando eventuale formattazione anomala)
        start = content.find("{")
        end = content.rfind("}") + 1
        return json.loads(content[start:end])

    except Exception as e:
        print(f"Errore nella generazione dei macro: {e}")
        return {}




food_plan_alternative_meals_prompt = PromptTemplate.from_template("""
Ecco la composizione nutrizionale di un pasto della sezione "{section_name}".

Macro totali da rispettare (±10%):
- Proteine: {total_protein} g
- Carboidrati: {total_carbs} g
- Grassi: {total_fats} g

Genera un'alternativa composta da 2-4 alimenti semplici.

Requisiti:
- Ogni alimento è un oggetto JSON con:
  - "meal": nome sintetico (es. "Pane integrale")
  - "quantity": quantità in grammi (es. 60)
  - "section": "{section_name}"
  - "keywords": parole chiave rilevanti per il meal, includendo:
    - le parole componenti il nome (sia singolare che plurale)
    - ingredienti o sinonimi alimentari se rilevanti

Restituisci un singolo array JSON, senza testo extra.

Esempio:
[
  {{ "meal": "Pane integrale", "quantity": 60, "section": "Spuntino", "keywords": ["pane", "pani", "integrale"] }},
  {{ "meal": "Tonno al naturale", "quantity": 100, "section": "Spuntino", "keywords": ["tonno", "tonni", "naturale"] }}
]
""")

# Catena LangChain che utilizza GPT-4o mini per suggerire un'alternativa realistica
# a un pasto esistente, rispettando i macro target della sezione (±10%)
food_plan_alternative_meals_chain = food_plan_alternative_meals_prompt | llm_4o_mini

def generate_alternative_meals(section, user) -> list[dict]:
    """
    Genera un'alternativa realistica e bilanciata (in termini di macro) per una sezione di pasto,
    mantenendo lo stesso apporto nutrizionale ±10% e restituendo alimenti riconoscibili o creati automaticamente.

    :param section: istanza `FoodSection` (es. "Colazione", "Cena", ecc.)
    :param user: utente attivo, utilizzato per creare alimenti custom se mancanti
    :return: lista (singola) contenente un array di dict, ognuno con:
             - "meal": nome alimento
             - "food_item_id": id DB collegato (esistente o generato)
             - "quantity": quantità in grammi
             - "section": nome della sezione (es. "Pranzo")
    """

    from django.db.models import Sum, F, FloatField, ExpressionWrapper
    from data.models import FoodPlanItem

    # Calcolo dei macronutrienti totali della sezione corrente
    items = FoodPlanItem.objects.filter(food_section=section)

    def macro_expr(field):
        return ExpressionWrapper(
            F(f"food_item__{field}") * F("quantity_in_grams") / 100,
            output_field=FloatField()
        )

    macros = items.aggregate(
        total_protein=Sum(macro_expr("protein_per_100g")),
        total_carbs=Sum(macro_expr("carbs_per_100g")),
        total_fats=Sum(macro_expr("fats_per_100g"))
    )

    # Invio del prompt al modello AI per ottenere alternative valide
    result = food_plan_alternative_meals_chain.invoke({
        "section_name": section.name,
        "total_protein": round(macros["total_protein"] or 0),
        "total_carbs": round(macros["total_carbs"] or 0),
        "total_fats": round(macros["total_fats"] or 0)
    })

    content = result.content.strip()
    start = content.find("[")
    end = content.rfind("]") + 1
    if start == -1 or end == -1:
        raise ValueError("JSON non valido nella risposta.")

    parsed = json.loads(content[start:end])  # Array di alimenti suggeriti

    enriched = []

    for item in parsed:
        name = item["meal"]
        quantity = item["quantity"]
        keywords = item.get("keywords", [])

        # Ricerca semantica tra alimenti esistenti nel DB
        candidates = find_matching_food_items(keywords)
        best_match = select_best_food_item(name, candidates)

        if best_match["id"]:
            from data.models import FoodItem
            food_item = FoodItem.objects.get(id=best_match["id"])
        else:
            # Se non trovato, genera alimento realistico tramite IA
            food_item = generate_food_item(name, user)
            if not food_item:
                continue  # fallback: ignora se fallisce la generazione

        enriched.append({
            "meal": name,
            "food_item_id": food_item.id,
            "quantity": quantity,
            "section": section.name
        })

    # Ritorna un solo array dentro una lista (per compatibilità view)
    return [enriched]




# === Prompt per classificazione gruppo muscolare ===
food_plan_section_type_prompt = PromptTemplate.from_template("""
Sei un esperto di allenamento in palestra. 
Dato l'elenco degli esercizi e dettagli sulle serie, indica quale gruppo muscolare viene allenato maggiormente nella giornata.

Restituisci **una sola categoria breve**, come: "Petto", "Schiena", "Gambe", "Full Body", "Push", "Pull", "Spalle", ecc.

Dati della giornata:
{section_data}

Risposta (solo una parola o breve frase, senza punteggiatura):
""")

# Catena LangChain che usa un modello GPT-3.5 per classificare la giornata di allenamento
# in base al gruppo muscolare primario, sulla base dei dati delle serie ed esercizi.
food_plan_section_type_chain = food_plan_section_type_prompt | llm_3_5_turbo

def build_section_data(section) -> str:
    """
    Converte una sezione `GymPlanSection` in un formato testuale leggibile e ricco di contesto,
    per aiutare l'intelligenza artificiale a classificare il gruppo muscolare allenato.

    :param section: istanza GymPlanSection con esercizi e set associati
    :return: stringa dettagliata contenente esercizi, ripetizioni, carichi, tecniche, tempo, RIR, ecc.
    """

    items = section.gymplanitem_set.prefetch_related("sets", "sets__exercise")

    lines = []

    for item in items:
        if item.intensity_techniques:
            lines.append(f"Tecniche d'intensità: {', '.join(item.intensity_techniques)}")
        for s in item.sets.all():
            lines.append(
                f"- {s.exercise.name} | {s.prescribed_reps_1}-{s.prescribed_reps_2} reps | "
                f"{s.weight}kg | tempo {s.tempo_fcr} | RIR {s.rir} | riposo {s.rest_seconds}s"
            )

    return "\n".join(lines)

def classify_section_type(section) -> str:
    """
    Classifica automaticamente la sezione di allenamento (GymPlanSection)
    in base al gruppo muscolare o pattern di movimento predominante.

    Esempi possibili di classificazione:
    - "Petto", "Schiena", "Gambe", "Spalle", "Push", "Pull", "Full Body", "Braccia"

    :param section: istanza `GymPlanSection` con item e set collegati
    :return: categoria stimata come stringa breve (senza punteggiatura), es. "Push"

    Se la classificazione riesce, aggiorna anche il campo `section.type` nel database.
    In caso di errore o risposta vuota, ritorna una stringa vuota.
    """

    try:
        section_text = build_section_data(section)
        result = food_plan_section_type_chain.invoke({"section_data": section_text})
        category = getattr(result, "content", "").strip()

        if category:
            section.type = category.capitalize()
            section.save()

        return category

    except Exception as e:
        print(f"Errore nella classificazione: {e}")
        return ""




food_plan_section_note_prompt = PromptTemplate.from_template("""
Sei un esperto di allenamento. Ricevi un elenco di esercizi, dettagli sulle serie e sulle tecniche usate per una giornata di allenamento.

Scrivi una **nota sintetica (massimo 300 caratteri)** che spieghi **perché sono stati scelti questi esercizi**, includendo logica dell’allenamento (es. focus muscolare, intensità, varietà, controllo tecnico, recuperi).

Non usare emoji.

Dati della giornata:
{section_data}

Nota:
""")

# Catena LangChain che usa un LLM (es. GPT-3.5) per generare una breve nota tecnica e motivazionale,
# utile a spiegare la logica dietro la selezione degli esercizi di una giornata di allenamento.
food_plan_section_note_chain = food_plan_section_note_prompt | llm_3_5_turbo

def generate_section_note(section) -> str:
    """
    Genera e assegna una nota descrittiva per una `GymPlanSection`,
    spiegando la logica dell’allenamento del giorno (focus, tecniche, intensità, ecc.).

    :param section: istanza `GymPlanSection`, che contiene esercizi, serie e tecniche
    :return: stringa con la nota generata (max 300 caratteri)

    Se la generazione è valida, aggiorna automaticamente il campo `section.note`.
    In caso di errore o nota vuota, ritorna stringa vuota.
    """

    try:
        # Usa la funzione build_section_data per ottenere una descrizione leggibile e informativa
        section_text = build_section_data(section)

        # Invoca il modello LLM con il prompt formattato
        result = food_plan_section_note_chain.invoke({"section_data": section_text})
        note = getattr(result, "content", "").strip()

        # Se viene generata una nota valida, la salva nel campo della sezione
        if note:
            section.note = note
            section.save()

        return note

    except Exception as e:
        print(f"Errore nella generazione della nota: {e}")
        return ""




# === Prompt per descrizione completa della GymPlan ===
food_plan_note_prompt = PromptTemplate.from_template("""
Sei un esperto di programmazione dell’allenamento.

Dato un riepilogo dettagliato dei giorni (tipologia, tecniche usate, esercizi), scrivi una **breve descrizione (max 400 caratteri)** che riassuma:
- da quanti giorni è composta la scheda
- che tipologie di allenamento prevede
- su cosa si focalizza (volume, intensità, tecnica, forza, ecc.)
- eventuale varietà o logica strutturata (es. split upper/lower, push/pull, full body alternati)
- tecniche speciali usate
- nessuna emoji

Dati della scheda:
{plan_data}

Nota:
""")

# Catena LangChain che utilizza un modello GPT-3.5 per generare una descrizione sintetica e professionale
# della GymPlan (scheda settimanale di allenamento), partendo dal riepilogo strutturato dei giorni.
food_plan_note_chain = food_plan_note_prompt | llm_3_5_turbo

def build_plan_data(gym_plan) -> str:
    """
    Costruisce una stringa testuale che riassume, in linguaggio leggibile, il contenuto
    di ogni giornata della GymPlan, includendo esercizi, ripetizioni, pesi e tecniche usate.

    :param gym_plan: istanza GymPlan con sezioni e item associati
    :return: stringa da usare nel prompt per la generazione della descrizione finale
    """

    sections = gym_plan.gymplansection_set.prefetch_related(
        "gymplanitem_set__sets", "gymplanitem_set__sets__exercise"
    )

    lines = []

    for section in sections:
        # Intestazione della giornata con tipo (es. Push, Pull, Gambe, Full Body)
        lines.append(f"Giorno {section.day.upper()} ({section.type}):")

        for item in section.gymplanitem_set.all():
            if item.intensity_techniques:
                lines.append(f"  - Tecniche: {', '.join(item.intensity_techniques)}")

            for s in item.sets.all():
                lines.append(
                    f"  - {s.exercise.name} | {s.prescribed_reps_1}-{s.prescribed_reps_2} reps | "
                    f"{s.weight}kg | tempo {s.tempo_fcr}"
                )

    return "\n".join(lines)

def generate_gymplan_note(gym_plan) -> str:
    """
    Genera automaticamente una nota descrittiva e sintetica per una GymPlan settimanale,
    fornendo una panoramica utile su struttura, focus e logica del piano.

    :param gym_plan: istanza `GymPlan` con sezioni ed esercizi
    :return: stringa con descrizione generata (max 400 caratteri)

    Se la generazione è valida, salva la nota direttamente nel campo `gym_plan.note`.
    In caso di errore o risposta vuota, restituisce stringa vuota.
    """

    try:
        # Genera il contesto testuale completo da passare al modello
        plan_text = build_plan_data(gym_plan)

        # Invoca il modello per ottenere la nota sintetica
        result = food_plan_note_chain.invoke({"plan_data": plan_text})
        note = getattr(result, "content", "").strip()

        # Salva la nota nella GymPlan solo se presente
        if note:
            gym_plan.note = note
            gym_plan.save()

        return note

    except Exception as e:
        print(f"Errore nella generazione nota GymPlan: {e}")
        return ""




# === Prompt per generare GymPlanItem.notes ===
food_plan_item_note_prompt = PromptTemplate.from_template("""
Ricevi i dettagli di un esercizio inserito in una scheda di allenamento.

Scrivi una **nota sintetica (massimo 8 parole)** che descriva brevemente il focus dell'esercizio (tecnica, forza, stimolo metabolico, controllo, velocità, esplosività, intensità, resistenza, volume, ecc.).

Non usare emoji.

Dati esercizio:
{item_data}

Nota:
""")

# Catena LangChain che usa GPT-3.5 per generare una descrizione sintetica e informativa
# del focus allenante di un esercizio specifico, sulla base di parametri tecnici.
food_plan_item_note_chain = food_plan_item_note_prompt | llm_3_5_turbo

def build_item_data(item) -> str:
    """
    Costruisce una stringa leggibile contenente i dettagli di un singolo esercizio
    inserito in una GymPlan, utile per fornire contesto al modello AI.

    :param item: istanza `GymPlanItem` con set e tecniche d’intensità
    :return: stringa descrittiva dei set, carichi, RIR, tempo, riposi, ecc.
    """
    sets = item.sets.select_related("exercise")

    lines = []
    if item.intensity_techniques:
        lines.append(f"Tecniche d’intensità: {', '.join(item.intensity_techniques)}")

    for s in sets:
        lines.append(
            f"{s.exercise.name} | {s.prescribed_reps_1}-{s.prescribed_reps_2} reps | "
            f"{s.weight}kg | tempo {s.tempo_fcr} | RIR {s.rir} | riposo {s.rest_seconds}s"
        )

    return "\n".join(lines)

def generate_item_note(item) -> str:
    """
    Genera una breve nota (max 8 parole) per descrivere il focus dell’esercizio corrente
    in una scheda di allenamento, utile per comprendere l'intento programmativo (es. forza, tecnica, volume...).

    :param item: istanza `GymPlanItem` contenente set, esercizio e tecniche
    :return: stringa sintetica (es. "Focalizzato sul tempo sotto tensione")

    Se la generazione ha successo, la nota viene salvata nel campo `item.notes`.
    In caso di errore o risposta vuota, restituisce stringa vuota.
    """

    try:
        # Costruisce la descrizione tecnica per l'esercizio
        item_text = build_item_data(item)

        # Invia i dati al modello e ottiene la nota sintetica
        result = food_plan_item_note_chain.invoke({"item_data": item_text})
        note = getattr(result, "content", "").strip()

        # Salva la nota solo se presente
        if note:
            item.notes = note
            item.save()

        return note

    except Exception as e:
        print(f"Errore nella generazione nota GymPlanItem: {e}")
        return ""




# === PROMPT PER GENERARE LA SCHEDA ===
generate_plan_prompt = PromptTemplate.from_template("""
Sei un coach esperto. Devi creare una scheda di allenamento settimanale per un utente, in base ai giorni in cui si allena e alle sue misure recenti.

Obiettivo dell’utente: {goal}

Dati recenti (ultimi 30 giorni):
- Misure corporee: {body_measurements}
- Peso corporeo: {weights}

Per ciascun giorno, genera una lista di esercizi in inglese, con:
- nome esercizio
- ordine
- numero di serie (tra 3 e 6)
- tecnica d’intensità (tra: bilateral, unilateral, tempo-based)
- prescribed_reps_1 (massime ripetizioni per arto sinistro)
- prescribed_reps_2 (massime ripetizioni per arto destro)
- tempo_fcr (formato "eccentrica-pausa-concentrica", es. "3-1-2")
- rir (Reps in reserve, es. 1 o 2)
- weight (carico indicativo in kg, es. 50)
- rest_seconds (tempo di recupero in secondi, es. 90)
- notes (una **breve nota in italiano** che spiega il focus dell’esercizio, **massimo 10 parole**, **prima lettera maiuscola**, **niente emoji**)

Le ripetizioni sono da intendersi per arto.
Se la tecnica è `"tempo-based"`, allora devi generare solo **una serie** (`sets: 1`) per quell'esercizio.

Restituisci il risultato in **formato JSON valido**, strutturato come nell’esempio qui sotto.
Non usare blocchi di codice come ```json o simili. Restituisci solo il puro JSON.

Esempio di struttura:

{{ 
  "lun": [
    {{
      "name": "Barbell Squat",
      "order": 1,
      "sets": 4,
      "technique": "tempo-based",
      "prescribed_reps_1": 6,
      "prescribed_reps_2": 8,
      "tempo_fcr": "3-1-1",
      "rir": 1,
      "weight": 60,
      "rest_seconds": 90
    }}
  ]
}}

Giorni selezionati: {days}
""")

# Catena GPT-4o che genera un piano di allenamento completo settimanale
# in formato JSON, in base a: giorni attivi, obiettivo, peso e misure recenti.
generate_plan_chain = generate_plan_prompt | llm_4o

# === PROMPT PER PARSING NOMI ESERCIZI ===
name_parser_prompt = PromptTemplate.from_template("""
Dato il nome dell’esercizio: "{input_name}"

Trova il nome più simile tra questi presenti nel database (case insensitive):

{db_names}

Risposta: (solo uno dei nomi indicati)
""")

# Catena GPT-4o mini per normalizzare un nome di esercizio libero
# confrontandolo con l'elenco degli esercizi nel database.
parser_chain = name_parser_prompt | llm_4o_mini

def get_matching_gymitems_by_keywords(input_name: str, all_exercises: list[str]) -> list[str]:
    """
    Estrae parole chiave dal nome libero dell’esercizio inserito,
    e filtra i nomi degli esercizi del database che contengono almeno una parola chiave.

    :param input_name: Nome dell’esercizio generato dall’IA (es. "Barbell Bulgarian Split Squat")
    :param all_exercises: Lista completa dei nomi di esercizi esistenti nel database
    :return: Lista ridotta di candidati plausibili per il parsing
    """
    keywords = re.findall(r'\w+', input_name.lower())
    matched = [
        ex_name for ex_name in all_exercises
        if any(k in ex_name.lower() for k in keywords)
    ]
    return matched

def parse_exercise_name(input_name: str, all_exercises: list[str]) -> str:
    """
    Confronta un nome di esercizio generato dall’IA con quelli presenti nel database,
    e restituisce il nome più simile (normalizzazione tramite IA).

    :param input_name: Nome esercizio generato (es. "Bulgarian split squat")
    :param all_exercises: Tutti i nomi presenti nel database
    :return: Nome normalizzato presente nel DB, oppure stringa vuota in caso di errore
    """
    try:
        filtered = get_matching_gymitems_by_keywords(input_name, all_exercises)
        if not filtered:
            filtered = all_exercises[:15]  # fallback se nessuna parola chiave matcha
        result = parser_chain.invoke({
            "input_name": input_name,
            "db_names": ", ".join(filtered)
        })
        return getattr(result, "content", "").strip()
    except Exception as e:
        print(f"Errore parsing nome: {e}")
        return ""




gym_item_generate_alternative_prompt = PromptTemplate.from_template("""
Sei un coach esperto. Ti fornirò un esercizio attuale in una scheda di allenamento.

Genera un esercizio alternativo che alleni gli **stessi gruppi muscolari**, ma in modo diverso (con attrezzo differente o schema diverso).  
L’alternativa deve includere:
- name (nome in inglese)
- sets (numero serie)
- prescribed_reps_1 (ripetizioni minime per arto)
- prescribed_reps_2 (ripetizioni massime per arto)
- tempo_fcr (formato "eccentrica-pausa-concentrica")
- rir (Reps in reserve)
- weight (carico in kg)
- rest_seconds (recupero in secondi)
- notes (breve nota in italiano, max 10 parole, prima lettera maiuscola)

Se la tecnica dell’esercizio attuale è "tempo-based", imposta sempre sets: 1.

Non usare blocchi di codice come ```json o simili. Restituisci solo il puro JSON.

Esercizio attuale:
- Nome: {current_name}
- Tecnica: {technique}
""")

gym_item_generate_alternative_chain = gym_item_generate_alternative_prompt | llm_4o

def replace_gymplan_item_with_alternative(item_id):
    """
    Sostituisce un esercizio all’interno di una GymPlan con un’alternativa generata dall’IA,
    mantenendo lo stesso gruppo muscolare ma cambiando stimolo (attrezzo, esecuzione, schema).

    :param item_id: ID dell’oggetto GymPlanItem da sostituire
    :return: dict con stato dell’operazione, nomi e numero set generati
    """

    from data.models import GymPlanItem, GymItem, GymPlanSetDetail

    try:
        # Recupera l’item e i suoi set originali
        item = GymPlanItem.objects.get(id=item_id)
        sets = item.sets.all()
        if not sets.exists():
            return {"error": "Questo GymPlanItem non ha set associati."}

        s = sets.first()
        original_name = s.exercise.name
        technique = item.intensity_techniques[0] if item.intensity_techniques else "null"

        # === INVOCAZIONE GPT PER GENERARE UN ESERCIZIO ALTERNATIVO ===
        result = gym_item_generate_alternative_chain.invoke({
            "current_name": original_name,
            "technique": technique
        })
        content = getattr(result, "content", "").strip()
        new_data = json.loads(content)  # Deve contenere: name, sets, reps, ecc.

        # === PARSING NOME ESERCIZIO PER MATCH NEL DATABASE ===
        all_names = list(GymItem.objects.values_list("name", flat=True))
        possible_names = get_matching_gymitems_by_keywords(new_data["name"], all_names)

        # Catena di parsing (es. da "Incline Barbell Press" → "Barbell Incline Bench Press")
        parser_result = parser_chain.invoke({
            "input_name": new_data["name"],
            "db_names": ", ".join(possible_names or all_names[:15])
        })
        parsed_name = getattr(parser_result, "content", "").strip()

        try:
            gym_item = GymItem.objects.get(name__iexact=parsed_name)
        except GymItem.DoesNotExist:
            return {"error": f"Esercizio '{parsed_name}' non trovato nel database."}

        # === AGGIORNA GymPlanItem ===
        item.notes = new_data.get("notes", "")
        item.intensity_techniques = [technique]
        item.save()

        # === CANCELLA I SET PRECEDENTI ===
        item.sets.all().delete()

        # === CREA I NUOVI SET CON I DATI GENERATI ===
        total_sets = new_data.get("sets", 3)
        for i in range(1, total_sets + 1):
            GymPlanSetDetail.objects.create(
                plan_item=item,
                exercise=gym_item,
                order=i,
                set_number=i,
                prescribed_reps_1=new_data.get("prescribed_reps_1", 8),
                prescribed_reps_2=new_data.get("prescribed_reps_2", 10),
                tempo_fcr=new_data.get("tempo_fcr", "2-0-2"),
                rir=new_data.get("rir", 2),
                weight=new_data.get("weight", 0),
                rest_seconds=new_data.get("rest_seconds", 90)
            )

        return {
            "status": "Esercizio sostituito con successo.",
            "original_name": original_name,
            "new_name": gym_item.name,
            "sets": total_sets,
            "notes": item.notes
        }

    except GymPlanItem.DoesNotExist:
        return {"error": "GymPlanItem non trovato."}
    except json.JSONDecodeError:
        return {"error": "Risposta GPT non è un JSON valido."}
    except Exception as e:
        return {"error": str(e)}




generate_warmup_prompt = PromptTemplate.from_template("""
Sei un coach esperto. Ti fornirò i dettagli di un esercizio principale (con i suoi set) e devi creare una o più serie di **riscaldamento** per lo stesso esercizio.

Le serie di riscaldamento devono:
- usare lo stesso esercizio principale
- avere `set_number = 0`
- avere `order` incrementale da 1 in poi
- usare carichi e ripetizioni inferiori rispetto alle serie reali
- essere utili a preparare gradualmente il corpo all’esercizio target

Per ogni serie di riscaldamento restituisci:
- order (1, 2, 3...)
- prescribed_reps_1 e 2 (ripetizioni min/max per arto)
- tempo_fcr (formato "3-1-1")
- rir
- weight (in kg, inferiore rispetto a quello reale)
- rest_seconds

Restituisci **esattamente** un array JSON valido, **senza oggetti wrapper** e **senza blocchi di codice tipo ```json**.
""")

generate_warmup_chain = generate_warmup_prompt | llm_4o

def generate_warmup_sets(item: "GymPlanItem") -> dict:
    """
    Genera automaticamente serie di riscaldamento per un esercizio in una GymPlan.

    :param item: GymPlanItem di riferimento
    :return: dict con esito dell’operazione e ID dei set creati
    """

    try:
        # Recupera i set principali associati all’esercizio
        sets = item.sets.order_by("set_number")
        if not sets.exists():
            return {"error": "Questo esercizio non ha serie."}

        exercise = sets.first().exercise

        # Calcola il carico massimo usato tra i set target
        main_weight = max([s.weight for s in sets if s.weight], default=0)

        # Costruisce un riepilogo delle serie target (es. "8-10 reps @ 60kg; ...")
        series_summary = "; ".join(
            f"{s.prescribed_reps_1}-{s.prescribed_reps_2} reps @ {s.weight}kg"
            for s in sets
        )

        # === Chiamata al modello GPT-4o per generare warm-up ===
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        chain = generate_warmup_prompt | llm

        result = chain.invoke({
            "exercise_name": exercise.name,
            "series_summary": series_summary,
            "main_weight": main_weight
        })
        content = getattr(result, "content", "").strip()
        warmup_data = json.loads(content)  # Array JSON delle serie generate

        # === Creazione delle serie di riscaldamento nel DB ===
        created = []
        for w in warmup_data:
            from data.models import GymPlanSetDetail
            new_set = GymPlanSetDetail.objects.create(
                plan_item=item,
                exercise=exercise,
                set_number=0,  # distingue serie di warm-up
                order=w["order"],  # posizione nel warm-up
                prescribed_reps_1=w["prescribed_reps_1"],
                prescribed_reps_2=w["prescribed_reps_2"],
                tempo_fcr=w["tempo_fcr"],
                rir=w["rir"],
                weight=w["weight"],
                rest_seconds=w["rest_seconds"]
            )
            created.append(new_set.id)

        return {
            "status": f"{len(created)} serie di riscaldamento generate con successo.",
            "set_ids": created
        }

    except json.JSONDecodeError:
        return {"error": "Risposta GPT non è un JSON valido."}
    except Exception as e:
        return {"error": str(e)}




suggest_weight_prompt = PromptTemplate.from_template("""
Sei un coach esperto. Ti fornirò una serie di set eseguiti da un utente per un determinato esercizio.

Set (JSON):
{sets_summary}

In base a questi dati, suggerisci un **peso ideale** (in kg) da usare oggi, coerente con l’andamento.

Restituisci **solo il numero**, senza testo aggiuntivo, note o simboli. Nessuna unità di misura. Nessun blocco di codice.
""")

def get_suggested_weight(sets_data: list) -> float:
    """
    Calcola un peso suggerito da utilizzare per un esercizio, basato su performance recenti.

    :param sets_data: lista di dizionari, ciascuno rappresenta un set con chiavi come:
                      - reps (ripetizioni fatte)
                      - weight (peso usato)
                      - rir (Reps in Reserve)
                      - tempo, ecc.
    :return: peso consigliato come float (es. 52.5), oppure 0.0 se fallisce il parsing
    """
    # Serializza i set in formato JSON, da inserire nel prompt
    sets_summary = json.dumps(sets_data)

    # Costruisce e invoca la catena con modello GPT-4o-mini
    result = suggest_weight_prompt | llm_4o_mini
    response = result.invoke({"sets_summary": sets_summary})
    
    try:
        # Estrae e converte il contenuto in float, assicurandosi che sia un numero puro
        return float(response.content.strip())
    except Exception:
        # Se la risposta non è un numero valido, restituisce 0.0 come fallback
        return 0.0