# SQL Question Answering System (Day 4)

## Objective

Build a safe SQL-QA pipeline that converts natural language into SQL, runs it on SQLite, and returns a natural language answer.

---

## Implemented Files

- `src/scripts/sql_pipeline.py`
- `src/generator/sql_generator.py`
- `src/utils/schema_loader.py`
- `src/utils/sql_validator.py`
- `src/scripts/init_db.py`

Note:
The requirement mentions `/pipelines/sql_pipeline.py`. In this codebase, the SQL pipeline is implemented in `src/scripts/sql_pipeline.py` and is used by `src/pipelines/main_pipeline.py`.

---

## End-to-End Flow

1. User asks a natural language SQL question.
2. `schema_loader.py` reads the SQLite schema from `src/data/sales.db`.
3. `sql_generator.py` prompts the LLM to generate exactly one `SELECT` query.
4. `sql_validator.py` validates safety rules before execution.
5. `sql_pipeline.py` executes SQL with pandas + sqlite3.
6. If SQL fails, `auto_fix_sql()` asks the LLM to repair the query and retries.
7. Final table result is summarized into clear text using the LLM.

---

## Core Features

### 1. Auto Schema Loader

- Reads table names from `sqlite_master`.
- Reads columns with `PRAGMA table_info(...)`.
- Formats schema into prompt-friendly text.

### 2. SQL Generation

- Prompt forces:
  - single SQL query
  - SQLite syntax
  - query must end with semicolon
  - no explanation text
- Regex extracts `select ... ;` from model output.

### 3. SQL Validation (Safety Gate)

- Only allows queries that start with `SELECT`.
- Blocks dangerous keywords:
  - `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`
- Blocks multi-statement SQL (`;` count check).

### 4. Execution + Auto Repair

- Runs SQL with `pd.read_sql_query`.
- On failure:
  - sends failed SQL + error + schema to LLM
  - gets corrected SQL
  - validates again
  - executes again

### 5. Result Summarization

- Converts top rows into a table preview.
- Asks LLM to summarize answer in concise natural language.

---

## Database Initialization

`src/scripts/init_db.py` builds `src/data/sales.db` from `src/data/raw/product.csv`:

- Drops old `products` table
- Creates table schema
- Loads CSV into SQLite

---

## How It Is Used in Capstone

`EnterpriseAssistant.handle_sql()` in `src/pipelines/main_pipeline.py`:

1. Calls SQL pipeline
2. Runs refinement pass for better readability
3. Evaluates response faithfulness/confidence
4. Stores interaction in memory

---

## Status

Implemented and working:

- Natural language -> SQL -> answer
- Schema-aware prompting
- Query validator
- Auto-fix loop
- Result summarization
