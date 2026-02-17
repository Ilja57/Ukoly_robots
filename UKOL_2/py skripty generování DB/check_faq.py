#!/usr/bin/env python3
"""
Kontrola obsahu FAQ databáze.
"""

import sqlite3
from pathlib import Path

DB_FILE = Path("faq.db")


def main():
    if not DB_FILE.exists():
        print(f"Soubor {DB_FILE} neexistuje. Spusťte nejprve gener_faq.py")
        return

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Celkový počet
    cur.execute("SELECT COUNT(*) FROM faq")
    count = cur.fetchone()[0]
    print(f"Celkem záznamů: {count}\n")

    # Počet dle kategorií
    cur.execute("SELECT category, COUNT(*) FROM faq GROUP BY category ORDER BY category")
    print("Kategorie:")
    for cat, cnt in cur.fetchall():
        print(f"  {cat}: {cnt} otázek")
    print()

    # Výpis všech FAQ
    cur.execute("SELECT id, category, question, answer, keywords FROM faq ORDER BY category, id")
    for row_id, category, question, answer, keywords in cur.fetchall():
        print("=" * 60)
        print(f"[{row_id}] {category}")
        print(f"Q: {question}")
        print(f"A: {answer}")
        print(f"Keywords: {keywords}")
        print()

    conn.close()


if __name__ == "__main__":
    main()
