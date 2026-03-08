import sqlite3
from pathlib import Path

# --- Cesta do nadřazeného adresáře ---
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "assistant.db"

def select_all():
    """Vypíše všechny poznámky přes JOIN — projekt se opakuje u každého řádku."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT p.id AS project_id, p.name AS project_name, p.description, "
        "d.id AS doc_id, d.name AS doc_name, d.content, d.created_at "
        "FROM documents d JOIN projects p ON d.project_id = p.id "
        "ORDER BY p.id, d.created_at"
    ).fetchall()
    conn.close()

    if not rows:
        print("Žádné poznámky v databázi.")
        return

    for r in rows:
        print(f"projekt: [{r['project_id']}] {r['project_name']} — {r['description']}")
        print(f"  poznámka: [{r['doc_id']}] {r['doc_name']} ({r['created_at']})")
        print(f"  obsah: {r['content']}")
        print("-" * 60)

if __name__ == "__main__":
    select_all()
