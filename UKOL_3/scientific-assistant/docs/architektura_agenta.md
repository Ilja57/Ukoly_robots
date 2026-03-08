# Vědecký asistent – architektura agenta

## Dvě možné architektury

LangGraph nabízí dva přístupy k implementaci ReAct agenta. Oba jsou funkčně ekvivalentní — liší se mírou kontroly nad vnitřní strukturou.

### Předpřipravený ReAct agent (`create_react_agent`)

Tento přístup zapouzdřuje celý reasoning cyklus do jednoho volání. Vývojář definuje LLM a sadu nástrojů, framework sestaví graf automaticky. Přístup je vhodný pro rychlé prototypování, kdy vývojář nepotřebuje zasahovat do vnitřní logiky agenta. Nevýhodou je, že workflow zůstává skryté — nelze snadno přidat mezikroky, logování nebo vlastní rozhodovací logiku.

### Explicitní stavba grafu (`StateGraph`)

Vývojář ručně definuje uzly (agent, tools), hrany mezi nimi a rozhodovací funkci (`should_continue`), která po každém kroku vyhodnotí, zda agent potřebuje zavolat nástroj nebo vrátit odpověď uživateli. Workflow je viditelné ve zdrojovém kódu a lze ho libovolně rozšiřovat — přidávat uzly, měnit podmínky větvení, vkládat mezikroky.

## Zvolená architektura

Pro toto řešení je zvolen druhý přístup — explicitní stavba grafu. Explicitní graf lépe demonstruje princip ReAct cyklu (Reasoning → Acting → Observation) a umožňuje plnou kontrolu nad chováním agenta.

## Struktura grafu

Graf se skládá ze dvou uzlů a podmíněné hrany:

**Uzel `agent`** přijme aktuální stav konverzace (historii zpráv) a zavolá LLM (Claude). LLM na základě kontextu rozhodne, zda potřebuje zavolat některý z nástrojů, nebo zda může odpovědět přímo uživateli.

**Uzel `tools`** provede volání nástroje, který LLM zvolil. Výsledek nástroje se přidá do historie zpráv a řízení se vrátí zpět do uzlu `agent`.

**Rozhodovací funkce `should_continue`** po každém průchodu uzlem `agent` vyhodnotí odpověď LLM. Pokud odpověď obsahuje volání nástroje, graf pokračuje do uzlu `tools`. Pokud neobsahuje, graf končí a odpověď se vrátí uživateli.

Tento cyklus se opakuje, dokud LLM nevyhodnotí, že má dostatek informací pro odpověď.

**Omezení počtu cyklů.** Rozhodovací funkce `should_continue` obsahuje počítadlo kroků. Pokud agent překročí stanovený limit (např. 10 cyklů), graf skončí a vrátí uživateli dosavadní výsledek. Tím se zabrání nekonečnému zacyklení v případě, kdy LLM opakovaně volá nástroje, aniž by dospěl k závěru.

## Nástroje agenta

Agent má k dispozici dvě skupiny nástrojů:

**SQLite nástroje** pracují s lokální databází projektu. Umožňují vyhledávání v poznámkách podle klíčových slov, uložení nové poznámky, výpis všech poznámek projektu a čtení nebo zápis draftu článku.

**Wikipedia** slouží k dohledání informací z externího zdroje. Agent vyhledá článek na Wikipedii a vrátí shrnutí relevantního obsahu a odkaz na článek.
