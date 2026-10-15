import sqlite3
from datetime import datetime, date

DB_NAME = "undajamii.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS issues (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            facility    TEXT    NOT NULL,
            description TEXT    NOT NULL,
            priority    INTEGER NOT NULL CHECK(priority BETWEEN 1 AND 3),
            status      INTEGER NOT NULL DEFAULT 1 CHECK(status BETWEEN 1 AND 3),
            reported_by TEXT    NOT NULL DEFAULT 'Anonymous',
            assigned_to TEXT    NOT NULL DEFAULT '',
            due_date    TEXT    NOT NULL DEFAULT '',
            created_at  TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS comments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_id   INTEGER NOT NULL,
            author     TEXT    NOT NULL DEFAULT 'Anonymous',
            body       TEXT    NOT NULL,
            created_at TEXT    NOT NULL,
            FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()

def add_issue(facility, description, priority, reported_by,
              assigned_to="", due_date=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO issues (facility, description, priority, reported_by, "
        "assigned_to, due_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (facility, description, priority, reported_by, assigned_to, due_date,
         datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()
    conn.close()

def get_all_issues(filters=None):
    filters = filters or {}
    query = "SELECT * FROM issues WHERE 1=1"
    params = []

    if filters.get("status"):
        query += " AND status = ?"
        params.append(int(filters["status"]))

    if filters.get("priority"):
        query += " AND priority = ?"
        params.append(int(filters["priority"]))

    if filters.get("facility"):
        query += " AND LOWER(facility) LIKE ?"
        params.append(f"%{filters['facility'].lower()}%")

    sort = filters.get("sort", "newest")
    if sort == "oldest":
        query += " ORDER BY id ASC"
    elif sort == "priority":
        query += " ORDER BY priority DESC, status ASC, id ASC"
    elif sort == "status":
        query += " ORDER BY status ASC, priority DESC, id ASC"
    else:
        query += " ORDER BY id DESC"

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows

def get_issue(ticket_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM issues WHERE id = ?", (ticket_id,)).fetchone()
    conn.close()
    return row

def update_issue(ticket_id, facility, description, priority, status,
                 reported_by, assigned_to, due_date):
    conn = get_connection()
    conn.execute(
        "UPDATE issues SET facility = ?, description = ?, priority = ?, "
        "status = ?, reported_by = ?, assigned_to = ?, due_date = ? WHERE id = ?",
        (facility, description, priority, status, reported_by,
         assigned_to, due_date, ticket_id)
    )
    conn.commit()
    conn.close()

def delete_issue(ticket_id):
    conn = get_connection()
    conn.execute("DELETE FROM issues WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()

def delete_resolved():
    conn = get_connection()
    cur = conn.execute("DELETE FROM issues WHERE status = 3")
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count

def get_summary():
    conn = get_connection()
    row = conn.execute("""
        SELECT
            COUNT(*)                                                       AS total,
            SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END)                   AS open,
            SUM(CASE WHEN status = 2 THEN 1 ELSE 0 END)                   AS in_progress,
            SUM(CASE WHEN status = 3 THEN 1 ELSE 0 END)                   AS resolved,
            SUM(CASE WHEN priority = 3 AND status != 3 THEN 1 ELSE 0 END) AS high_unresolved
        FROM issues
    """).fetchone()
    conn.close()
    return row

def add_comment(issue_id, author, body):
    conn = get_connection()
    conn.execute(
        "INSERT INTO comments (issue_id, author, body, created_at) VALUES (?, ?, ?, ?)",
        (issue_id, author, body, datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()
    conn.close()

def get_comments(issue_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM comments WHERE issue_id = ? ORDER BY id ASC",
        (issue_id,)
    ).fetchall()
    conn.close()
    return rows

def get_monthly_stats():
    conn = get_connection()
    rows = conn.execute("""
        SELECT substr(created_at, 1, 7) AS month,
               COUNT(*) AS created,
               SUM(CASE WHEN status = 3 THEN 1 ELSE 0 END) AS resolved
        FROM issues
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
    """).fetchall()
    conn.close()
    return list(reversed(rows))