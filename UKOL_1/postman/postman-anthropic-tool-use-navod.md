# Testování Anthropic Tool Use v Postmanu

## Úvod

Tento návod ukazuje, jak **ručně testovat tool use** (function calling) v Anthropic API pomocí aplikace Postman. Je to doplněk k Python skriptu s BMI kalkulačkou – zde uvidíš přesně, co se posílá "po drátech" na úrovni HTTP.

---

## Co je Postman a proč ho použít

Postman je desktopová aplikace (nebo webová verze), která umožňuje posílat HTTP requesty na libovolné API a zkoumat odpovědi. Pro vývojáře je užitečný, protože:

**Vidíš raw data** – přesnou strukturu JSON requestu i odpovědi, bez jakékoliv abstrakce.

**Rychle experimentuješ** – změníš parametr, pošleš request, vidíš výsledek. Žádné překompilovávání.

**Snadný debugging** – když ti nefunguje kód, můžeš v Postmanu ověřit, jestli je problém v API nebo ve tvé implementaci.

---

## Architektura testu

V Python skriptu se dějí **dvě HTTP volání** na Anthropic API. V Postmanu to budou dva samostatné requesty:

```
┌─────────────────────────────────────────────────────────────┐
│  REQUEST 1: "Uživatel se ptá na BMI"                        │
│                                                             │
│  POST https://api.anthropic.com/v1/messages                 │
│  Body: dotaz + definice nástroje                            │
│                                                             │
│  → Odpověď: LLM chce zavolat calculate_bmi(75, 180)         │
└─────────────────────────────────────────────────────────────┘
                              ↓
            (normálně bys zde zavolal funkci v kódu,
             v Postmanu výsledek "simuluješ" ručně)
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  REQUEST 2: "Tady máš výsledek nástroje"                    │
│                                                             │
│  POST https://api.anthropic.com/v1/messages                 │
│  Body: celá konverzace + tool_result s BMI hodnotou         │
│                                                             │
│  → Odpověď: "Vaše BMI je 23.1, což je normální váha..."     │
└─────────────────────────────────────────────────────────────┘
```

---

## Krok 1: Instalace a spuštění Postmanu

Pokud nemáš Postman nainstalovaný, stáhni ho z **https://www.postman.com/downloads/** a nainstaluj. Po spuštění se můžeš přihlásit nebo pokračovat bez účtu.

---

## Krok 2: Vytvoření Environment (prostředí)

Environment ti umožňuje uložit proměnné (např. API klíč), které pak použiješ ve více requestech.

**Postup:**

1. Vpravo nahoře klikni na ikonu **Environment** (ozubené kolečko nebo dropdown "No Environment")
2. Klikni **Create Environment** nebo **+ New**
3. Pojmenuj ho např. "Anthropic API"
4. Přidej proměnnou:
   - **Variable:** `ANTHROPIC_API_KEY`
   - **Type:** `secret`
   - **Initial value:** (nech prázdné)
   - **Current value:** `sk-ant-api03-xxxxx...` (tvůj skutečný klíč)
5. Ulož a vyber tento environment v dropdownu vpravo nahoře

---

## Krok 3: Nastavení Headers

Každý request na Anthropic API potřebuje tyto hlavičky:

| Header | Hodnota | Vysvětlení |
|--------|---------|------------|
| `x-api-key` | `{{ANTHROPIC_API_KEY}}` | Tvůj API klíč (načte se z environment) |
| `anthropic-version` | `2023-06-01` | Verze API protokolu |
| `content-type` | `application/json` | Říká API, že posíláme JSON |

Dvojité složené závorky `{{...}}` jsou Postman syntaxe pro proměnné.

---

## Krok 4: Request 1 – Dotaz s definicí nástroje

**Vytvoř nový request:**

1. Klikni **New** → **HTTP Request**
2. Nastav metodu na **POST**
3. URL: `https://api.anthropic.com/v1/messages`
4. Záložka **Headers** – přidej tři hlavičky z tabulky výše
5. Záložka **Body** → vyber **raw** → typ **JSON**

**Body (zkopíruj celé):**

```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 1024,
  "tools": [
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
  ],
  "messages": [
    {
      "role": "user",
      "content": "Vážím 75 kg a měřím 180 cm. Jaké je moje BMI?"
    }
  ]
}
```

**Co se děje v tomto JSON:**

- `model` – který Claude model použít
- `max_tokens` – maximální délka odpovědi
- `tools` – definice dostupných nástrojů (zde jen BMI kalkulačka)
- `messages` – konverzace, zatím jen uživatelův dotaz

**Klikni Send** a podívej se na odpověď.

---

## Krok 5: Analýza odpovědi na Request 1

Odpověď bude vypadat přibližně takto:

```json
{
  "id": "msg_xxxxx",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "tool_use",
      "id": "toolu_01ABC123xyz",
      "name": "calculate_bmi",
      "input": {
        "weight_kg": 75,
        "height_cm": 180
      }
    }
  ],
  "stop_reason": "tool_use",
  ...
}
```

**Důležité hodnoty:**

- `stop_reason: "tool_use"` – LLM chce použít nástroj (nezastavil se sám)
- `content[0].type: "tool_use"` – blok s požadavkem na nástroj
- `content[0].id` – **ZAPAMATUJ SI TOTO ID!** Budeš ho potřebovat v Request 2
- `content[0].input` – parametry, které LLM určil z dotazu (75 kg, 180 cm)

---

## Krok 6: Request 2 – Vrácení výsledku nástroje

Teď simuluješ, že jsi funkci `calculate_bmi(75, 180)` zavolal a dostal výsledek. V reálném kódu by to Python spočítal, v Postmanu výsledek napíšeš ručně.

**Vytvoř druhý request** se stejným URL a headers.

**Body (zkopíruj a UPRAV `id`):**

```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 1024,
  "tools": [
    {
      "name": "calculate_bmi",
      "description": "Vypočítá BMI (Body Mass Index) na základě váhy a výšky.",
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
  ],
  "messages": [
    {
      "role": "user",
      "content": "Vážím 75 kg a měřím 180 cm. Jaké je moje BMI?"
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "tool_use",
          "id": "toolu_01ABC123xyz",
          "name": "calculate_bmi",
          "input": {
            "weight_kg": 75,
            "height_cm": 180
          }
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "tool_result",
          "tool_use_id": "toolu_01ABC123xyz",
          "content": "{\"bmi\": 23.1, \"category\": \"normální váha\", \"weight_kg\": 75, \"height_cm\": 180}"
        }
      ]
    }
  ]
}
```

**DŮLEŽITÉ:** Nahraď `toolu_01ABC123xyz` skutečným ID z odpovědi na Request 1! Musí se shodovat na obou místech (`id` v assistant zprávě a `tool_use_id` v tool_result).

**Co se děje v tomto JSON:**

- Posíláš **celou konverzaci** – původní dotaz, odpověď LLM (s tool_use), a nově výsledek nástroje (tool_result)
- `tool_result` obsahuje JSON string s výsledkem výpočtu
- LLM teď má všechny informace k vytvoření finální odpovědi

**Klikni Send.**

---

## Krok 7: Finální odpověď

Odpověď bude vypadat přibližně takto:

```json
{
  "id": "msg_yyyyy",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Vaše BMI je 23.1, což spadá do kategorie \"normální váha\". To je skvělý výsledek! BMI mezi 18.5 a 25 je považováno za zdravé rozmezí."
    }
  ],
  "stop_reason": "end_turn",
  ...
}
```

Všimni si, že `stop_reason` je teď `"end_turn"` – LLM dokončil odpověď a nežádá další nástroj.

---

## Shrnutí workflow

1. **Vytvoř Environment** s API klíčem
2. **Request 1:** Pošli dotaz + definici nástroje → dostaneš `tool_use` s ID
3. **Zkopíruj ID** z odpovědi
4. **Request 2:** Pošli celou konverzaci + `tool_result` → dostaneš finální odpověď

---

## Tipy pro experimentování

**Zkus změnit dotaz** – např. "Měřím 165 cm a vážím 90 kg" – a sleduj, jak se změní parametry v tool_use.

**Zkus dotaz bez BMI** – např. "Co je hlavní město Francie?" – LLM nepoužije nástroj a vrátí přímo textovou odpověď (`stop_reason: "end_turn"`).

**Zkus špatné ID** – v Request 2 zadej jiné tool_use_id a uvidíš chybovou hlášku.

---

## Souvislost s Python kódem

Tento manuální proces je přesně to, co dělá Python skript automaticky:

| Postman (ruční) | Python (automatický) |
|-----------------|----------------------|
| Request 1 | `client.messages.create(...)` první volání |
| Kopírování ID | `tool_use_block.id` |
| Výpočet BMI | `calculate_bmi(weight, height)` |
| Request 2 | `client.messages.create(...)` druhé volání |

Postman je nástroj pro pochopení a debugging, Python pro produkční použití.
