# Vědecký asistent

ReAct agent pro podporu psaní odborných článků. Postavený na LangGraph s explicitním stavovým grafem, Anthropic Claude jako LLM backendem, SQLite databází a přístupem na Wikipedii.

## Co agent umí

- Založit a spravovat projekty (odborné články)
- Ukládat a prohledávat poznámky v rámci projektu
- Vyhledávat informace na Wikipedii
- Sestavovat a upravovat draft článku v markdown formátu

## Architektura

Agent je postaven jako explicitní `StateGraph` se dvěma uzly:

- **agent** — volá LLM (Claude), který rozhodne, zda použít nástroj nebo odpovědět
- **tools** — provede zvolený nástroj a vrátí výsledek zpět do agent uzlu

Rozhodovací funkce `should_continue` řídí cyklus s omezením na max. 10 kroků.

## Nástroje

| Nástroj | Popis |
|---------|-------|
| `create_project` | Založení nového projektu |
| `list_projects` | Seznam všech projektů |
| `save_note` | Uložení poznámky do projektu |
| `list_notes` | Výpis všech poznámek projektu |
| `search_notes` | Hledání v poznámkách podle klíčového slova |
| `read_draft` | Čtení aktuálního draftu článku |
| `save_draft` | Uložení nebo přepsání draftu |
| `search_wikipedia` | Vyhledání informací na Wikipedii |

## Instalace a spuštění

### 1. Klonování repozitáře

```bash
git clone https://github.com/<uzivatel>/scientific-assistant.git
cd scientific-assistant
```

### 2. Vytvoření virtuálního prostředí

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Instalace závislostí

```bash
pip install -r requirements.txt
```

### 4. Nastavení API klíče

```bash
cp .env.example .env
```

Otevři soubor `.env` a doplň svůj Anthropic API klíč.

### 5. Spuštění

```bash
python agent.py
```

## Struktura projektu

```
scientific-assistant/
├── agent.py              # hlavní soubor — graf, CLI smyčka
├── tools.py              # definice nástrojů (SQLite, Wikipedia)
├── schema.sql            # DDL schéma databáze
├── requirements.txt      # závislosti
├── .env.example          # vzor pro API klíč
├── README.md             # tento soubor
└── docs/
    ├── navrh_reseni_pripady_uziti.md
    ├── architektura_agenta.md
    └── langgraph_workflow.svg
```

## Dokumentace

Podrobnější popis návrhu řešení, architektury agenta a diagram workflow je v adresáři `docs/`.

## Příklady použití

```
Ty: Založ nový projekt Kvantová mechanika, článek o vztahu kvantové teorie a geometrie.
Asistent: Projekt vytvořen s ID 1.

Ty: Zapiš si poznámku — Heisenbergův princip neurčitosti implikuje ztrátu pojmu bodu.
Asistent: Poznámka uložena.

Ty: Najdi mi na Wikipedii něco o Planckově délce.
Asistent: (shrnutí z Wikipedie) Chceš si výsledek uložit jako poznámku?

Ty: Na základě mých poznámek navrhni osnovu článku.
Asistent: (návrh osnovy, uložení do draftu)
```
