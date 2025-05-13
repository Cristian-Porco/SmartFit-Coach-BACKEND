import base64
import json

from django.db import transaction
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
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage

# === LLM configuration ===
llm = ChatOpenAI(
    temperature=0,
    model="gpt-3.5-turbo",
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


# === Prompt per analisi pasti testuale (FoodParsing) ===
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
    model="gpt-4o-mini",
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


# === Prompt per analisi pasti immagine (FoodParsing) ===
vision_prompt_text = """
L'immagine che ti fornisco mostra uno o più alimenti o pasti.

Analizza il contenuto visivo e restituisci un array JSON con oggetti aventi i seguenti campi:
- "meal": nome sintetico del pasto (es. "Pasta al sugo")
- "keywords": parole chiave attinenti al pasto, includendo sia forma singolare che plurale (es. "patata", "patate")
- "quantity": quantità stimata in grammi, come numero intero

Restituisci solo l'array JSON. Nessuna spiegazione.
"""

vision_prompt_llm = ChatOpenAI(
    model="gpt-4o-mini",  # o "gpt-4o" se hai accesso
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

def encode_image(file) -> str:
    """Converte un file in stringa base64"""
    import io
    buffer = io.BytesIO()
    file.seek(0)
    buffer.write(file.read())
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def generate_food_analysis_from_image_file(file) -> list:
    try:
        base64_img = encode_image(file)

        message = HumanMessage(content=[
            {"type": "text", "text": vision_prompt_text},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_img}"
                }
            }
        ])

        result = vision_prompt_llm.invoke([message])
        content = result.content.strip()

        # Estraggo l'array JSON dalla risposta
        start = content.find("[")
        end = content.rfind("]") + 1
        if start == -1 or end == -1:
            raise ValueError("La risposta non contiene un JSON valido.")
        return json.loads(content[start:end])

    except Exception as e:
        print(f"Errore LangChain Vision: {e}")
        return []


# === Prompt per ottimizzare le quantità ===
foodplan_optimization_prompt = PromptTemplate.from_template("""
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


foodplan_optimization_llm = ChatOpenAI(
    temperature=0.5,
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY")
)

foodplan_chain = foodplan_optimization_prompt | foodplan_optimization_llm

def generate_foodplan_adjustment(food_plan) -> str:
    """
    Genera un prompt per ottimizzare le quantità degli alimenti nel piano alimentare.

    :param food_plan: istanza FoodPlan
    :param min_fiber: fibra minima richiesta
    :param min_sugars: zuccheri minimi desiderati
    :param max_sugars: zuccheri massimi tollerati
    :return: JSON con quantità ottimizzate (come stringa)
    """
    try:
        items = food_plan.foodplanitem_set.select_related("food_item")
        food_items_str = "\n".join([
            f"- ID {item.id} - {item.food_item.name}: {item.quantity_in_grams}g "
            f"(kcal: {item.food_item.kcal_per_100g}, pro: {item.food_item.protein_per_100g}, "
            f"carb: {item.food_item.carbs_per_100g}, zuccheri: {item.food_item.sugars_per_100g or 0}, "
            f"grassi: {item.food_item.fats_per_100g}, fibre: {item.food_item.fiber_per_100g})"
            for item in items
        ])

        result = foodplan_chain.invoke({
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
    Applica gli aggiornamenti di quantità ai FoodPlanItem **solo se la quantità è effettivamente cambiata**.

    :param data: lista di dict come:
        [{ "id": 1, "adjusted_quantity_in_grams": 110 }, ...]
    :return: lista di ID realmente aggiornati
    """
    from .models import FoodPlanItem
    updated_ids = []

    with transaction.atomic():
        for entry in data:
            item_id = entry.get("id")
            new_qty = entry.get("adjusted_quantity_in_grams")

            if item_id is None or new_qty is None or new_qty < 10:
                continue

            try:
                item = FoodPlanItem.objects.get(id=item_id)
                if abs(item.quantity_in_grams - new_qty) >= 0.01:  # evita cambi irrilevanti
                    item.quantity_in_grams = new_qty
                    item.save()
                    updated_ids.append(item_id)
            except FoodPlanItem.DoesNotExist:
                continue

    return updated_ids


# === Prompt per creare una scheda alimentare ===
personalized_food_plan_prompt = PromptTemplate.from_template("""
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


food_plan_llm = ChatOpenAI(
    model="gpt-4o",  # o "gpt-4-vision-preview" se disponibile
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

food_plan_chain = personalized_food_plan_prompt | food_plan_llm

def generate_food_plan_from_context(goal: str, weights: list, measurements: list, prev_macros: dict) -> list:
    """
    :param goal: es. "massa"
    :param weights: lista di tuple (data, peso)
    :param measurements: lista di dict {"date": "...", "chest": ..., ...}
    :param prev_macros: dict con max_protein, max_carbs, max_fats, max_kcal
    :return: lista di pasti (dict) generati dall'AI
    """
    def format_weights(w):
        return "\n".join(f"{d}: {v} kg" for d, v in w)

    def format_measurements(m):
        lines = []
        for row in m:
            parts = [f"{row['date']}:"]
            for k, v in row.items():
                if k != "date" and v is not None:
                    parts.append(f"{k.capitalize()} {v} cm")
            lines.append(" ".join(parts))
        return "\n".join(lines)

    try:
        response = food_plan_chain.invoke({
            "goal": goal,
            "weights": format_weights(weights),
            "measurements": format_measurements(measurements),
            "prev_protein": prev_macros["max_protein"],
            "prev_carbs": prev_macros["max_carbs"],
            "prev_fats": prev_macros["max_fats"],
            "prev_kcal": prev_macros["max_kcal"]
        })

        content = response.content.strip()
        start = content.find("[")
        end = content.rfind("]") + 1

        if start == -1 or end == -1:
            raise ValueError("Risposta non contiene JSON valido")

        return json.loads(content[start:end])
    except Exception as e:
        print(f"Errore generazione piano: {e}")
        return []



#
generate_food_item_prompt = PromptTemplate.from_template("""
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

generate_food_item_chain = generate_food_item_prompt | ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_food_item(name: str, user) -> "FoodItem | None":
    try:
        result = generate_food_item_chain.invoke({"name": name})
        content = result.content.strip()
        start = content.find("{")
        end = content.rfind("}") + 1
        if start == -1 or end == -1:
            raise ValueError("JSON non trovato nella risposta.")

        data = json.loads(content[start:end])

        from data.models import FoodItem
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


#
generate_macros_prompt = PromptTemplate.from_template("""
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

generate_macros_chain = generate_macros_prompt | ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_new_macros(goal: str, weights: list, measurements: list, prev_macros: dict) -> dict:
    """
    :param goal: stringa es. "massa", "definizione"
    :param weights: lista di tuple (data, peso)
    :param measurements: lista di dict con date e misure
    :param prev_macros: dict con "max_protein", "max_carbs", "max_fats"
    :return: dict con nuovi macro e reason
    """

    def format_weights(w):
        return "\n".join(f"{d}: {v} kg" for d, v in w)

    def format_measurements(m):
        lines = []
        for row in m:
            parts = [f"{row['date']}:"]
            for k, v in row.items():
                if k != "date" and v is not None:
                    parts.append(f"{k.capitalize()} {v} cm")
            lines.append(" ".join(parts))
        return "\n".join(lines)

    try:
        result = generate_macros_chain.invoke({
            "goal": goal,
            "weights": format_weights(weights),
            "measurements": format_measurements(measurements),
            "prev_protein": prev_macros["max_protein"],
            "prev_carbs": prev_macros["max_carbs"],
            "prev_fats": prev_macros["max_fats"]
        })
        content = result.content.strip()
        start = content.find("{")
        end = content.rfind("}") + 1
        return json.loads(content[start:end])
    except Exception as e:
        print(f"Errore nella generazione dei macro: {e}")
        return {}


#
alternative_meals_prompt = PromptTemplate.from_template("""
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

alternative_chain = alternative_meals_prompt | ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.6,
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_alternative_meals(section, user) -> list[dict]:
    from django.db.models import Sum, F, FloatField, ExpressionWrapper

    from data.models import FoodPlanItem
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

    section_name = section.name

    result = alternative_chain.invoke({
        "section_name": section_name,
        "total_protein": round(macros["total_protein"] or 0),
        "total_carbs": round(macros["total_carbs"] or 0),
        "total_fats": round(macros["total_fats"] or 0)
    })

    content = result.content.strip()
    start = content.find("[")
    end = content.rfind("]") + 1
    if start == -1 or end == -1:
        raise ValueError("JSON non valido nella risposta.")

    parsed = json.loads(content[start:end])  # un singolo array

    enriched = []
    for item in parsed:
        name = item["meal"]
        quantity = item["quantity"]
        keywords = item.get("keywords", [])

        # Ricerca alimento esistente
        candidates = find_matching_food_items(keywords)
        best_match = select_best_food_item(name, candidates)

        if best_match["id"]:
            from data.models import FoodItem
            food_item = FoodItem.objects.get(id=best_match["id"])
        else:
            food_item = generate_food_item(name, user)
            if not food_item:
                continue

        enriched.append({
            "meal": name,
            "food_item_id": food_item.id,
            "quantity": quantity,
            "section": section.name
        })

    return [enriched]  # compatibilità con view