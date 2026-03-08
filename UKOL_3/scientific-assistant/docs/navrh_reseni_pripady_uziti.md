# Vědecký asistent – návrh řešení a případy užití

## Volba řešení

- Framework: LangGraph (LangChain)
- Typ agenta: ReAct (Reasoning + Acting)
- LLM backend: Anthropic Claude
- Databáze: SQLite
- Druhý nástroj: Wikipedia
- Rozhraní: CLI (příkazová řádka)

## Datový model

Projekt má svoje poznámky — kompozice ku N. Poznámka se nesmí narodit bez projektu, nemůže přeputovat k jinému projektu. Zánik projektu znamená zánik všech jeho poznámek.

Draft článku žije jako atribut projektu (draft_project_artefakt). Instančně v něm žije markdown. Není to samostatná entita, je to vlastnost majitele — projektu.

## Příběh použití

Vědecký asistent pomáhá uživateli při psaní odborného článku. Uživatel komunikuje s agentem přirozeným jazykem v příkazové řádce. Agent má k dispozici lokální databázi poznámek a přístup na Wikipedii. Výstupním artefaktem je draft článku v markdown formátu, který se postupně buduje a upravuje v rámci projektu.

### 1. Uživatel chce založit nový projekt

Uživatel zadá požadavek na založení projektu s názvem a popisem (např. "Založ nový projekt Kvantová mechanika a filosofie bodu v časoprostoru, článek do odborného časopisu o vztahu kvantové teorie a geometrie časoprostoru.")

Systém vytvoří projekt v databázi a potvrdí založení. Draft je prázdný. Od této chvíle se drží kontext tohoto projektu až do odvolání.

### 2. Uživatel chce pracovat na existujícím projektu

Uživatel zadá požadavek na zobrazení projektů (např. "Ukaž mi moje projekty" nebo "Na čem můžu pracovat?")

Systém zobrazí seznam existujících projektů. Uživatel vybere. Systém přepne kontext na vybraný projekt.

### 3. Uživatel chce uložit poznámku

Uživatel zadá požadavek na uložení poznámky (např. "Zapiš si poznámku — Heisenbergův princip neurčitosti implikuje, že pojem bodu v klasickém smyslu ztrácí v kvantové mechanice operační význam.")

Systém uloží poznámku do databáze pod aktuální projekt a potvrdí uložení.

### 4. Uživatel chce zjistit, co už má v poznámkách

Uživatel zadá dotaz na poznámky podle klíčového slova (např. "Co mám v poznámkách o Heisenbergovi?")

Systém prohledá poznámky aktuálního projektu a zobrazí nalezené záznamy.

### 5. Uživatel potřebuje doplnit informace z externího zdroje

Uživatel zadá požadavek na vyhledání na Wikipedii (např. "Najdi mi na Wikipedii něco o Planckově délce.")

Systém vyhledá na Wikipedii, vrátí shrnutí a nabídne, zda si má výsledek uložit jako poznámku.

### 6. Uživatel chce přehled všech poznámek projektu

Uživatel zadá požadavek na výpis poznámek (např. "Ukaž mi všechny poznámky k tomuto projektu.")

Systém zobrazí seznam všech poznámek seřazených podle data vytvoření.

### 7. Uživatel chce sestavit nebo rozšířit draft článku

Uživatel zadá požadavek na práci s draftem (např. "Na základě mých poznámek navrhni osnovu článku" nebo "Přidej do draftu kapitolu o Planckově délce.")

Systém si přečte poznámky z databáze, načte aktuální stav draftu, vygeneruje nový nebo rozšířený obsah a uloží aktualizovaný draft zpět do projektu.

### 8. Uživatel chce vidět aktuální stav draftu

Uživatel zadá požadavek na zobrazení draftu (např. "Ukaž mi draft" nebo "Jak vypadá článek?")

Systém načte draft z projektu a zobrazí jeho aktuální obsah.

### 9. Uživatel chce ručně upravit draft

Uživatel si vyžádá aktuální draft. Systém ho zobrazí v konzoli. Uživatel draft zkopíruje, upraví v externím editoru a vloží upravenou verzi zpět do chatu (např. "Tady je upravený draft: ...").

Systém přijme upravenou verzi a uloží ji jako nový stav draftu projektu. Při dalších úpravách agent pracuje s touto verzí. Pokud uživatel chce, aby agent měnil jen konkrétní část, řekne to slovně (např. "Přepiš jen druhou kapitolu, zbytek nech.")
