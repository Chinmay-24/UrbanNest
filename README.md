# UrbanNest — Smart Apartment Management System

College DBMS mini project: a **web application** for apartment society operations. The backend is **Python Flask**. The database is **MySQL 8**. The UI uses **HTML, CSS, Bootstrap 5, and JavaScript**. All SQL is sent through **parameterized queries** (`%s`) via **MySQL Connector/Python**.

## Features

1. Dashboard with JOIN/aggregate statistics and three MySQL views
2. Block and flat management
3. Resident management
4. Monthly maintenance bills and payment records
5. Visitor entry and exit logs
6. Complaint registration and resolution
7. Staff management
8. Common facility bookings
9. Apartment notices

Every module supports **INSERT, SELECT, UPDATE, and DELETE** from the browser.

## Database

Database name: `urbannest`

| Table | Role |
|---|---|
| `blocks` | Society wings / towers |
| `flats` | Units inside a block |
| `residents` | People living in a flat |
| `staff` | Society employees |
| `maintenance_bills` | Monthly bills issued to a resident |
| `payments` | Payments against a bill |
| `visitors` | Gate logs linked to a host resident |
| `complaints` | Tickets raised by a resident |
| `facilities` | Clubhouse, gym, pool, and similar |
| `facility_bookings` | Resident bookings of a facility |
| `notices` | Circulars published by staff |

Constraints used: **PRIMARY KEY**, **FOREIGN KEY**, **NOT NULL**, **UNIQUE**, and **CHECK**.

Views:

- `vw_flat_occupancy` — blocks ⋈ flats ⋈ residents, with `COUNT`
- `vw_resident_dues` — residents ⋈ bills ⋈ payments, with `SUM`
- `vw_complaint_workload` — complaints grouped by category/status, with `COUNT` and `AVG`

Sample data: at least five rows in every table (`schema/seed.sql`).

## Requirements

- Python 3.10 or newer
- MySQL 8.0.16 or newer (CHECK constraints are enforced from this version)
- pip

## Setup

1. Install MySQL and start the server. Create a user that can create databases, or use `root`.

2. Clone or copy this folder, then open a terminal in `UrbanNest`.

3. Create a virtual environment and install packages:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS / Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

4. Set connection details if they are not the defaults (`127.0.0.1`, user `root`, empty password, database `urbannest`):

Windows PowerShell:

```powershell
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "your_password"
$env:MYSQL_DATABASE = "urbannest"
```

macOS / Linux:

```bash
export MYSQL_HOST=127.0.0.1
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=urbannest
```

5. Create tables, views, and sample rows:

```bash
python init_db.py
```

You can also run the SQL files in MySQL Workbench in this order: `schema/schema.sql`, `schema/views.sql`, `schema/seed.sql`.

6. Start the web app:

```bash
python app.py
```

7. Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

`init_db.py` drops and recreates the `urbannest` tables. Do not run it on a database you want to keep.

## Project layout

```text
UrbanNest/
  app.py                 Flask routes (parameterized CRUD)
  config.py              MySQL and Flask settings
  db.py                  mysql-connector-python helpers
  init_db.py             Loads schema, views, and seed data
  requirements.txt
  schema/
    schema.sql
    views.sql
    seed.sql
  static/css/style.css
  static/js/app.js
  templates/             Bootstrap 5 pages
```

## SQL injection

Queries are built with placeholders, never with string concatenation of form values:

```python
cursor.execute(
    "INSERT INTO residents (flat_id, full_name, email) VALUES (%s, %s, %s)",
    (flat_id, full_name, email),
)
```
