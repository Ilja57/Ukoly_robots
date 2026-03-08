import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from tools import (
    init_db,
    create_project,
    list_projects,
    save_note,
    list_notes,
    search_notes,
    read_draft,
    save_draft,
    search_wikipedia,
)

# --- Načtení API klíče z .env ---
load_dotenv()

# --- System prompt pro agenta ---
SYSTEM_PROMPT = """Jsi vědecký asistent. Pomáháš uživateli při psaní odborného článku.

Máš k dispozici tyto nástroje:
- create_project: založení nového projektu (název, popis)
- list_projects: zobrazení seznamu projektů
- save_note: uložení poznámky do projektu (vyžaduje project_id)
- list_notes: výpis všech poznámek projektu (vyžaduje project_id)
- search_notes: hledání v poznámkách podle klíčového slova (vyžaduje project_id)
- read_draft: čtení aktuálního draftu článku (vyžaduje project_id)
- save_draft: uložení nebo přepsání draftu článku (vyžaduje project_id)
- search_wikipedia: vyhledání informací na Wikipedii

Pravidla:
- Vždy komunikuj česky.
- Pokud uživatel pracuje s poznámkami, draftem nebo ukládá data, potřebuješ znát project_id. 
  Pokud ho neznáš, zeptej se uživatele nebo mu nabídni seznam projektů.
- Při vyhledání na Wikipedii nabídni uživateli, zda si má výsledek uložit jako poznámku.
- Při sestavování draftu si nejdřív přečti existující poznámky a aktuální draft.
- Odpovídej stručně a věcně.
"""

# --- Definice stavu grafu ---
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# --- Seznam nástrojů ---
tools = [
    create_project,
    list_projects,
    save_note,
    list_notes,
    search_notes,
    read_draft,
    save_draft,
    search_wikipedia,
]

# --- LLM s nástroji ---
llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
)
llm_with_tools = llm.bind_tools(tools)

# --- Mapování názvů nástrojů na funkce ---
tool_map = {t.name: t for t in tools}

# --- Počítadlo kroků pro omezení cyklů ---
MAX_STEPS = 10
step_counter = 0


# ==========================================================
# Uzly grafu
# ==========================================================

def agent_node(state: AgentState) -> AgentState:
    """Uzel agent — zavolá LLM s historií zpráv."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def tools_node(state: AgentState) -> AgentState:
    """Uzel tools — provede nástroje, které LLM zvolil."""
    last_message = state["messages"][-1]
    results = []
    for tool_call in last_message.tool_calls:
        tool_fn = tool_map[tool_call["name"]]
        result = tool_fn.invoke(tool_call["args"])
        # vytvoříme ToolMessage s výsledkem
        from langchain_core.messages import ToolMessage
        results.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )
    return {"messages": results}


# ==========================================================
# Rozhodovací funkce
# ==========================================================

def should_continue(state: AgentState) -> str:
    """Rozhodne, zda pokračovat do tools nebo ukončit."""
    global step_counter
    step_counter += 1
    # omezení počtu cyklů
    if step_counter >= MAX_STEPS:
        return "end"
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"


# ==========================================================
# Sestavení grafu
# ==========================================================

graph_builder = StateGraph(AgentState)

# přidání uzlů
graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tools", tools_node)

# vstupní bod
graph_builder.set_entry_point("agent")

# podmíněná hrana z agent
graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": END,
    }
)

# hrana z tools zpět do agent
graph_builder.add_edge("tools", "agent")

# kompilace grafu
graph = graph_builder.compile()


# ==========================================================
# CLI smyčka
# ==========================================================

def main():
    """Hlavní smyčka — čte vstup od uživatele, volá graf, vypisuje odpověď."""
    global step_counter

    # inicializace databáze
    init_db()

    print("=== Vědecký asistent ===")
    print("Zadej dotaz nebo napiš 'exit' pro ukončení.\n")

    # historie konverzace
    messages = []

    while True:
        user_input = input("Ty: ").strip()
        if user_input.lower() in ("exit", "quit", "konec"):
            print("Ukončuji. Nashledanou!")
            break
        if not user_input:
            continue

        # reset počítadla kroků pro každý dotaz
        step_counter = 0

        # přidání uživatelovy zprávy
        messages.append(HumanMessage(content=user_input))

        # spuštění grafu
        result = graph.invoke({"messages": messages})

        # poslední zpráva od agenta
        assistant_message = result["messages"][-1]
        print(f"\nAsistent: {assistant_message.content}\n")

        # aktualizace historie
        messages = result["messages"]


if __name__ == "__main__":
    main()
