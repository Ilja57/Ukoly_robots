FAQ Agent – odpovídá na dotazy zaměstnanců nad SQLite databází pomocí Claude Sonnet  Agent využívá SQL nástroj pro vyhledávání v databázi FAQ (kategorie HR, IT, Finance, Obecné) a formuluje odpovědi v ČJ
 

Database URL v SQL Database komponentě je nastavena na sqlite:////app/data/faq.db, což odpovídá namapovanému volume v Dockeru. 
Jedná se o test DB s patnácti otázkami
Soubor je přiložen.  

Samotné první spuštění může občas skončit chybou „empty content", ale je to funkční, stačí položit dotaz.
Údajně chyba  

Obsah DB generován PY skriptem.
V adresáři přiloženy py skripty plnící test databázi otízkami a odpověďmi + check výpisem. 
  


