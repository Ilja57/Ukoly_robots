#!/usr/bin/env python3
"""
Generátor FAQ databáze pro LangFlow SQLAgent.
Vytvoří SQLite databázi s firemními FAQ daty.
"""

import sqlite3
from pathlib import Path

DB_FILE = Path("faq.db")

FAQ_DATA = [
    # HR
    ("HR", "Kolik dní dovolené mám nárok?",
     "Každý zaměstnanec má nárok na 25 dní dovolené ročně. Po 5 letech ve firmě se nárok zvyšuje na 27 dní. Dovolenou je třeba schválit nadřízeným minimálně 14 dní předem.",
     "dovolená, volno, nárok, dny, odpočinek"),

    ("HR", "Jak požádat o home office?",
     "O home office požádáte přes interní systém HRIS v sekci 'Žádosti'. Je potřeba souhlas přímého nadřízeného. Maximálně 3 dny v týdnu, pondělí a středa jsou povinné office dny.",
     "home office, práce z domova, remote, vzdálená práce"),

    ("HR", "Jaká je zkušební doba?",
     "Zkušební doba je 3 měsíce pro běžné pozice a 6 měsíců pro manažerské pozice. Během zkušební doby může být pracovní poměr ukončen bez udání důvodu s 15denní výpovědní lhůtou.",
     "zkušební doba, nástup, nový zaměstnanec, výpovědní lhůta"),

    ("HR", "Jak fungují sick days?",
     "Zaměstnanci mají nárok na 5 sick days ročně. Není potřeba lékařské potvrzení. Sick day se hlásí nadřízenému do 9:00 daného dne telefonicky nebo přes Slack.",
     "sick day, nemoc, neschopenka, zdraví, absence"),

    ("HR", "Jaké jsou firemní benefity?",
     "Firma nabízí: Multisport kartu (příspěvek 50%), stravenky 150 Kč/den, příspěvek na penzijní připojištění 1000 Kč/měsíc, jazykové kurzy zdarma, a roční bonus až 15% platu dle hodnocení.",
     "benefity, výhody, stravenky, multisport, penze, bonus"),

    # IT
    ("IT", "Jak resetovat heslo do firemního systému?",
     "Přejděte na portal.firma.cz/reset, zadejte firemní email a klikněte na 'Obnovit heslo'. Nové heslo přijde na email do 5 minut. Pokud problém přetrvává, kontaktujte IT helpdesk na lince 555.",
     "heslo, reset, přihlášení, login, zapomenuté heslo, portal"),

    ("IT", "Jak se připojit k firemní VPN?",
     "Stáhněte aplikaci FortiClient z intranetu (intranet.firma.cz/vpn). Použijte server vpn.firma.cz, port 443. Přihlašovací údaje jsou stejné jako do firemního systému. Při problémech volejte IT helpdesk 555.",
     "VPN, připojení, vzdálený přístup, FortiClient, síť"),

    ("IT", "Jak objednat nový hardware?",
     "Požadavek na hardware (notebook, monitor, klávesnici apod.) zadejte přes JIRA projekt 'IT-PROCUREMENT'. Schválení trvá 3-5 pracovních dní. Standardní výměna notebooku je po 3 letech.",
     "hardware, notebook, počítač, monitor, objednávka, výměna"),

    ("IT", "Jaký software mohu instalovat na firemní počítač?",
     "Povolený software je uveden na intranetu v sekci 'IT Politiky'. Instalace neautorizovaného softwaru je zakázána. Pro výjimky podejte žádost přes IT helpdesk s odůvodněním.",
     "software, instalace, program, licence, povolený"),

    # Finance
    ("Finance", "Kdy je výplatní termín?",
     "Výplata je vždy 10. dne v měsíci. Pokud 10. připadne na víkend nebo svátek, výplata proběhne poslední pracovní den před tímto datem. Výplatní páska je dostupná v HRIS systému.",
     "výplata, plat, mzda, termín, peníze, výplatní páska"),

    ("Finance", "Jak proplatit cestovní náklady?",
     "Cestovní příkaz vyplňte v systému SAP do 5 pracovních dní po návratu. Přiložte účtenky a jízdenky. Diety se počítají automaticky dle zákona. Proplacení proběhne s nejbližší výplatou.",
     "cestovné, diety, cestovní příkaz, účtenky, služební cesta"),

    ("Finance", "Jak funguje firemní kreditní karta?",
     "Firemní kartu lze žádat pro pozice od senior úrovně výše. Měsíční limit je 30 000 Kč. Účtenky je nutné nahrát do SAP do 3 dnů od transakce. Osobní použití je zakázáno.",
     "kreditní karta, firemní karta, platba, limit, SAP"),

    # Obecné
    ("Obecné", "Jaká je pracovní doba?",
     "Pracovní doba je pružná s povinným jádrem 9:00-15:00. Celkový fond je 8 hodin denně, 40 hodin týdně. Přesčasy nad 150 hodin ročně musí schválit ředitel divize.",
     "pracovní doba, hodiny, přesčas, jádro, pružná"),

    ("Obecné", "Kde najdu firemní dokumenty a šablony?",
     "Všechny firemní dokumenty, šablony a směrnice jsou na SharePointu: sharepoint.firma.cz/dokumenty. Přístup máte automaticky po přihlášení firemním účtem.",
     "dokumenty, šablony, směrnice, SharePoint, formuláře"),

    ("Obecné", "Jak nahlásit bezpečnostní incident?",
     "Bezpečnostní incidenty hlaste okamžitě na security@firma.cz nebo linku 911. Pro IT incidenty (phishing, malware) kontaktujte SOC tým přes Slack kanál #security-incidents.",
     "bezpečnost, incident, security, nahlášení, phishing"),
]


def main():
    if DB_FILE.exists():
        DB_FILE.unlink()

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE faq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            keywords TEXT NOT NULL
        )
    """)

    for category, question, answer, keywords in FAQ_DATA:
        cur.execute(
            "INSERT INTO faq (category, question, answer, keywords) VALUES (?, ?, ?, ?)",
            (category, question, answer, keywords)
        )

    conn.commit()
    conn.close()

    print(f"Hotovo. Vytvořeno {len(FAQ_DATA)} FAQ záznamů v {DB_FILE}")


if __name__ == "__main__":
    main()
