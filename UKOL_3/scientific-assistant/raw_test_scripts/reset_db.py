import sqlite3
from pathlib import Path

# --- Cesty do nadřazeného adresáře ---
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "assistant.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

def reset_db():
    """Smaže tabulky a vytvoří je znovu ze schema.sql."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DROP TABLE IF EXISTS documents")
    conn.execute("DROP TABLE IF EXISTS projects")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()
    conn.close()
    print(f"Databáze {DB_PATH} resetována.")

if __name__ == "__main__":
    reset_db()
