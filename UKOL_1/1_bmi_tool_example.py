"""
BMI Kalkulačka s Anthropic Tool Use
===================================
Ukázkový skript pro kurz AI agentů.

Demonstruje základní "smyčku" tool use:
1. Uživatel položí dotaz
2. LLM se rozhodne použít nástroj
3. My nástroj zavoláme
4. Výsledek vrátíme LLM
5. LLM vygeneruje finální odpověď
"""

from dotenv import load_dotenv
load_dotenv()  # Načte .env soubor ze stejného adresáře

import anthropic
import json

# ============================================================
# 1. SETUP - inicializace klienta
# ============================================================
# API klíč se načte automaticky z ANTHROPIC_API_KEY env proměnné
# Alternativně: client = anthropic.Anthropic(api_key="sk-ant-...")
client = anthropic.Anthropic()

# ============================================================
# 2. DEFINICE NÁSTROJE (pro LLM)
# ============================================================
# Toto říká LLM, jaký nástroj má k dispozici a jak ho použít
tools = [
    {
        "name": "calculate_bmi",
        "description": "Vypočítá BMI (Body Mass Index) na základě váhy a výšky. Použij tento nástroj, když uživatel chce znát své BMI.",
        "input_schema": {
            "type": "object",
            "properties": {
                "weight_kg": {
                    "type": "number",
                    "description": "Váha v kilogramech"
                },
                "height_cm": {
                    "type": "number",
                    "description": "Výška v centimetrech"
                }
            },
            "required": ["weight_kg", "height_cm"]
        }
    }
]

# ============================================================
# 3. IMPLEMENTACE NÁSTROJE (skutečná Python funkce)
# ============================================================
def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    """Vypočítá BMI a vrátí výsledek s kategorií."""
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    bmi = round(bmi, 1)
    
    # Určení kategorie
    if bmi < 18.5:
        category = "podváha"
    elif bmi < 25:
        category = "normální váha"
    elif bmi < 30:
        category = "nadváha"
    else:
        category = "obezita"
    
    return {
        "bmi": bmi,
        "category": category,
        "weight_kg": weight_kg,
        "height_cm": height_cm
    }

# ============================================================
# 4. HLAVNÍ FUNKCE - zpracování dotazu
# ============================================================
def process_query(user_message: str) -> str:
    """Zpracuje uživatelův dotaz pomocí LLM s tool use."""
    
    print(f"\n{'='*60}")
    print(f"UŽIVATEL: {user_message}")
    print('='*60)
    
    # --- PRVNÍ VOLÁNÍ API ---
    print("\n[1] Odesílám dotaz do LLM...")
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=tools,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    print(f"[2] Stop reason: {response.stop_reason}")
    
    # --- KONTROLA, ZDA LLM CHCE POUŽÍT NÁSTROJ ---
    if response.stop_reason == "tool_use":
        # Najdeme tool_use blok v odpovědi
        tool_use_block = None
        for block in response.content:
            if block.type == "tool_use":
                tool_use_block = block
                break
        
        if tool_use_block:
            tool_name = tool_use_block.name
            tool_input = tool_use_block.input
            tool_use_id = tool_use_block.id
            
            print(f"[3] LLM chce zavolat: {tool_name}")
            print(f"    Parametry: {json.dumps(tool_input, indent=2)}")
            
            # --- ZAVOLÁNÍ PYTHON FUNKCE ---
            if tool_name == "calculate_bmi":
                result = calculate_bmi(
                    weight_kg=tool_input["weight_kg"],
                    height_cm=tool_input["height_cm"]
                )
                print(f"[4] Výsledek nástroje: {result}")
            else:
                result = {"error": f"Neznámý nástroj: {tool_name}"}
            
            # --- DRUHÉ VOLÁNÍ API - vrácení výsledku ---
            print("[5] Odesílám výsledek zpět do LLM...")
            
            final_response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                tools=tools,
                messages=[
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": response.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": json.dumps(result)
                            }
                        ]
                    }
                ]
            )
            
            # Extrahujeme textovou odpověď
            final_text = ""
            for block in final_response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            
            print(f"\n[6] FINÁLNÍ ODPOVĚĎ LLM:")
            print("-" * 40)
            print(final_text)
            return final_text
    
    # Pokud LLM nepoužil nástroj, vrátíme přímo odpověď
    text_response = ""
    for block in response.content:
        if hasattr(block, "text"):
            text_response += block.text
    
    print(f"\nODPOVĚĎ (bez nástroje): {text_response}")
    return text_response

# ============================================================
# 5. SPUŠTĚNÍ
# ============================================================
if __name__ == "__main__":
    # Testovací dotazy
    queries = [
        "Vážím 75 kg a měřím 180 cm. Jaké je moje BMI?",
        # "Mám 92 kilo a 175 centimetrů, jsem v normě?",
        # "Co je to BMI?"  # Tento dotaz nevyžaduje nástroj
    ]
    
    for query in queries:
        process_query(query)
        print("\n")
