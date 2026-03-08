import sqlite3
from pathlib import Path
from langchain_core.tools import tool

# --- Cesta k databázi ---
DB_PATH = Path(__file__).parent / "assistant.db"


def get_connection():
    """Vrátí připojení k SQLite databázi."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializace databáze ze schema.sql."""
    schema_path = Path(__file__).parent / "schema.sql"
    conn = get_connection()
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    conn.commit()
    conn.close()


# ==========================================================
# SQLite nástroje
# ==========================================================

@tool
def create_project(name: str, description: str) -> str:
    """Založí nový projekt s názvem a popisem. Vrátí ID založeného projektu."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO projects (name, description) VALUES (?, ?)",
        (name, description)
    )
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return f"Projekt vytvořen s ID {project_id}."


@tool
def list_projects() -> str:
    """Zobrazí seznam všech projektů. Vrátí ID, název, popis a datum vytvoření."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, description, created_at FROM projects ORDER BY id"
    ).fetchall()
    conn.close()
    if not rows:
        return "Žádné projekty neexistují."
    lines = []
    for r in rows:
        lines.append(f"[{r['id']}] {r['name']} — {r['description']} (vytvořeno: {r['created_at']})")
    return "\n".join(lines)


@tool
def save_note(project_id: int, name: str, content: str) -> str:
    """Uloží novou poznámku do projektu. Vyžaduje project_id, název a obsah poznámky."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO documents (project_id, name, content) VALUES (?, ?, ?)",
        (project_id, name, content)
    )
    conn.commit()
    conn.close()
    return f"Poznámka '{name}' uložena do projektu {project_id}."


@tool
def list_notes(project_id: int) -> str:
    """Zobrazí všechny poznámky daného projektu seřazené podle data vytvoření."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, content, created_at FROM documents WHERE project_id = ? ORDER BY created_at",
        (project_id,)
    ).fetchall()
    conn.close()
    if not rows:
        return f"Projekt {project_id} nemá žádné poznámky."
    lines = []
    for r in rows:
        lines.append(f"[{r['id']}] {r['name']} ({r['created_at']})\n{r['content']}")
    return "\n---\n".join(lines)


@tool
def search_notes(project_id: int, keyword: str) -> str:
    """Prohledá poznámky projektu podle klíčového slova v názvu nebo obsahu."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, content, created_at FROM documents "
        "WHERE project_id = ? AND (name LIKE ? OR content LIKE ?) "
        "ORDER BY created_at",
        (project_id, f"%{keyword}%", f"%{keyword}%")
    ).fetchall()
    conn.close()
    if not rows:
        return f"Žádné poznámky obsahující '{keyword}' nenalezeny."
    lines = []
    for r in rows:
        lines.append(f"[{r['id']}] {r['name']} ({r['created_at']})\n{r['content']}")
    return "\n---\n".join(lines)


@tool
def read_draft(project_id: int) -> str:
    """Přečte aktuální draft článku z projektu. Vrátí markdown obsah nebo info že draft je prázdný."""
    conn = get_connection()
    row = conn.execute(
        "SELECT draft_project_artefakt FROM projects WHERE id = ?",
        (project_id,)
    ).fetchone()
    conn.close()
    if not row or not row["draft_project_artefakt"]:
        return f"Projekt {project_id} zatím nemá žádný draft."
    return row["draft_project_artefakt"]


@tool
def save_draft(project_id: int, draft_content: str) -> str:
    """Uloží nebo přepíše draft článku v projektu. Obsah je markdown text."""
    conn = get_connection()
    conn.execute(
        "UPDATE projects SET draft_project_artefakt = ? WHERE id = ?",
        (draft_content, project_id)
    )
    conn.commit()
    conn.close()
    return f"Draft projektu {project_id} uložen."


# ==========================================================
# Wikipedia nástroj
# ==========================================================

@tool
def search_wikipedia(query: str) -> str:
    """Vyhledá článek na Wikipedii podle dotazu. Vrátí shrnutí a odkaz na článek."""
    import wikipedia
    wikipedia.set_lang("cs")
    results = wikipedia.search(query, results=3)
    if not results:
        # záložní pokus v angličtině
        wikipedia.set_lang("en")
        results = wikipedia.search(query, results=3)
        if not results:
            return f"Na Wikipedii nebylo nic nalezeno pro '{query}'."
    page = wikipedia.page(results[0], auto_suggest=False)
    # vrátíme prvních 1500 znaků jako shrnutí
    summary = page.summary[:1500]
    return f"**{page.title}**\n\n{summary}\n\nOdkaz: {page.url}"
