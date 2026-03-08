-- ==================================================
-- DDL schéma pro vědeckého asistenta
-- SQLite databáze pro správu projektů a poznámek
-- ==================================================

-- Tabulka projektů (odborných článků)
-- Draft článku žije na úrovni projektu jako jeho atribut (MD obsah)
CREATE TABLE IF NOT EXISTS projects (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    name                    TEXT    NOT NULL,
    description             TEXT,
    draft_project_artefakt  TEXT,
    created_at              TEXT    DEFAULT (datetime('now'))
);

-- Tabulka poznámek (1:N k projektům)
-- Kompozice ku N — poznámka se nesmí narodit bez projektu
CREATE TABLE IF NOT EXISTS documents (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER NOT NULL,
    name        TEXT    NOT NULL,
    content     TEXT,
    blob        BLOB,
    created_at  TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
