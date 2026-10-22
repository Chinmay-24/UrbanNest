from datetime import date, datetime, time as time_type, timedelta
from decimal import Decimal, InvalidOperation

from flask import Flask, flash, redirect, render_template, request, url_for

import config
from db import DatabaseError, fetch_all, fetch_one, execute

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

BHK_TYPES = ["1BHK", "2BHK", "3BHK", "4BHK"]
OCCUPANCY = ["Vacant", "Occupied", "Maintenance"]
ID_PROOFS = ["Aadhaar", "Passport", "Driving Licence", "Voter ID"]
RESIDENT_TYPES = ["Owner", "Tenant", "Family"]
STAFF_ROLES = ["Manager", "Security", "Housekeeping", "Accountant", "Maintenance"]
EMPLOYMENT = ["Active", "On Leave", "Resigned"]
BILL_STATUSES = ["Unpaid", "Partially Paid", "Paid", "Overdue"]
PAY_MODES = ["Cash", "UPI", "Card", "Net Banking"]
COMPLAINT_CATEGORIES = ["Plumbing", "Electrical", "Security", "Cleaning", "Other"]
COMPLAINT_STATUSES = ["Open", "In Progress", "Resolved", "Closed"]
BOOKING_STATUSES = ["Booked", "Cancelled", "Completed"]
NOTICE_CATEGORIES = ["General", "Maintenance", "Emergency", "Event"]
MONTHS = list(range(1, 13))


def blank(value):
    value = (value or "").strip()
    return value or None


def as_int(value, field, required=True):
    value = blank(value)
    if value is None:
        if required:
            raise ValueError(f"{field} is required.")
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be a whole number.") from exc


def as_decimal(value, field, required=True):
    value = blank(value)
    if value is None:
        if required:
            raise ValueError(f"{field} is required.")
        return None
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{field} must be a valid amount.") from exc


def as_date(value, field, required=True):
    value = blank(value)
    if value is None:
        if required:
            raise ValueError(f"{field} is required.")
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"{field} must be a valid date.") from exc


def as_datetime(value, field, required=True):
    value = blank(value)
    if value is None:
        if required:
            raise ValueError(f"{field} is required.")
        return None
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"{field} must be a valid date and time.")


def as_time(value, field):
    value = blank(value)
    if value is None:
        raise ValueError(f"{field} is required.")
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    raise ValueError(f"{field} must be a valid time.")


def checkbox(name):
    return 1 if request.form.get(name) else 0


def handle_db(action):
    try:
        action()
        return True
    except ValueError as exc:
        flash(str(exc), "danger")
    except DatabaseError as exc:
        flash(friendly_db_error(str(exc)), "danger")
    return False


def friendly_db_error(message):
    lower = message.lower()
    if "duplicate" in lower:
        return "This record conflicts with an existing unique value (name, email, phone, or period)."
    if "foreign key" in lower or "cannot delete" in lower:
        return "This record is linked to other data. Remove or reassign related records first."
    if "check constraint" in lower:
        return "A database check constraint failed. Review amounts, dates, and required ranges."
    return message


def fmt_money(value):
    if value is None:
        return "0.00"
    return f"{Decimal(value):,.2f}"


def fmt_dt(value):
    if value is None:
        return "—"
    if isinstance(value, datetime):
        return value.strftime("%d %b %Y, %H:%M")
    if isinstance(value, date):
        return value.strftime("%d %b %Y")
    return str(value)


def input_dt(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%dT%H:%M")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return str(value)[:16]


def input_time(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%H:%M")
    if isinstance(value, time_type):
        return value.strftime("%H:%M")
    if isinstance(value, timedelta):
        total = int(value.total_seconds())
        hours, rem = divmod(total, 3600)
        minutes, _ = divmod(rem, 60)
        return f"{hours:02d}:{minutes:02d}"
    return str(value)[:5]


app.jinja_env.filters["money"] = fmt_money
app.jinja_env.filters["when"] = fmt_dt
app.jinja_env.filters["input_dt"] = input_dt
app.jinja_env.filters["input_time"] = input_time
app.jinja_env.filters["input_date"] = input_dt


def block_options():
    return fetch_all("SELECT block_id, block_name FROM blocks ORDER BY block_name")


def flat_options():
    return fetch_all(
        """
        SELECT f.flat_id, f.flat_number, b.block_name
        FROM flats f
        JOIN blocks b ON b.block_id = f.block_id
        ORDER BY b.block_name, f.flat_number
        """
    )


def resident_options():
    return fetch_all(
        """
        SELECT r.resident_id, r.full_name, f.flat_number
        FROM residents r
        JOIN flats f ON f.flat_id = r.flat_id
        ORDER BY r.full_name
        """
    )


def staff_options():
    return fetch_all(
        "SELECT staff_id, full_name, role FROM staff ORDER BY full_name"
    )


def facility_options():
    return fetch_all(
        "SELECT facility_id, facility_name, hourly_rate FROM facilities ORDER BY facility_name"
    )


def bill_options():
    return fetch_all(
        """
        SELECT mb.bill_id, r.full_name, mb.bill_month, mb.bill_year, mb.amount, mb.status
        FROM maintenance_bills mb
        JOIN residents r ON r.resident_id = mb.resident_id
        ORDER BY mb.bill_year DESC, mb.bill_month DESC, r.full_name
        """
    )


@app.route("/")
def dashboard():
    stats = {
        "blocks": fetch_one("SELECT COUNT(*) AS n FROM blocks")["n"],
        "flats": fetch_one("SELECT COUNT(*) AS n FROM flats")["n"],
        "occupied": fetch_one(
            "SELECT COUNT(*) AS n FROM flats WHERE occupancy_status = 'Occupied'"
        )["n"],
        "residents": fetch_one(
            "SELECT COUNT(*) AS n FROM residents WHERE move_out_date IS NULL"
        )["n"],
        "open_complaints": fetch_one(
            "SELECT COUNT(*) AS n FROM complaints WHERE status IN ('Open', 'In Progress')"
        )["n"],
        "inside_visitors": fetch_one(
            "SELECT COUNT(*) AS n FROM visitors WHERE exit_time IS NULL"
        )["n"],
        "bookings": fetch_one(
            """
            SELECT COUNT(*) AS n FROM facility_bookings
            WHERE status = 'Booked' AND booking_date >= CURDATE()
            """
        )["n"],
        "outstanding": fetch_one(
            "SELECT COALESCE(SUM(outstanding), 0) AS n FROM vw_resident_dues"
        )["n"],
        "avg_bill": fetch_one(
            "SELECT COALESCE(AVG(amount), 0) AS n FROM maintenance_bills"
        )["n"],
    }
    occupancy = fetch_all(
        """
        SELECT occupancy_status, COUNT(*) AS n
        FROM flats
        GROUP BY occupancy_status
        """
    )
    dues = fetch_all(
        """
        SELECT full_name, block_name, flat_number, outstanding, total_billed, total_paid
        FROM vw_resident_dues
        WHERE outstanding > 0
        ORDER BY outstanding DESC
        LIMIT 8
        """
    )
    workload = fetch_all(
        """
        SELECT category, status, complaint_count, ROUND(avg_hours_open, 1) AS avg_hours_open
        FROM vw_complaint_workload
        ORDER BY complaint_count DESC
        """
    )
    notices = fetch_all(
        """
        SELECT n.title, n.category, n.publish_date, s.full_name AS publisher
        FROM notices n
        JOIN staff s ON s.staff_id = n.published_by_staff_id
        WHERE n.is_active = 1
        ORDER BY n.publish_date DESC
        LIMIT 5
        """
    )
    recent_visitors = fetch_all(
        """
        SELECT v.visitor_name, v.purpose, v.entry_time, v.exit_time,
               r.full_name AS host_name, f.flat_number
        FROM visitors v
        JOIN residents r ON r.resident_id = v.host_resident_id
        JOIN flats f ON f.flat_id = r.flat_id
        ORDER BY v.entry_time DESC
        LIMIT 5
        """
    )
    return render_template(
        "dashboard.html",
        stats=stats,
        occupancy=occupancy,
        dues=dues,
        workload=workload,
        notices=notices,
        recent_visitors=recent_visitors,
    )


@app.route("/blocks", methods=["GET", "POST"])
def blocks():
    if request.method == "POST":
        def save():
            execute(
                """
                INSERT INTO blocks (block_name, total_floors, total_flats, constructed_year, description)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    blank(request.form.get("block_name")),
                    as_int(request.form.get("total_floors"), "Total floors"),
                    as_int(request.form.get("total_flats"), "Total flats"),
                    as_int(request.form.get("constructed_year"), "Constructed year"),
                    blank(request.form.get("description")),
                ),
            )
            if not blank(request.form.get("block_name")):
                raise ValueError("Block name is required.")

        if not blank(request.form.get("block_name")):
            flash("Block name is required.", "danger")
        elif handle_db(save):
            flash("Block added.", "success")
            return redirect(url_for("blocks"))
    rows = fetch_all(
        """
        SELECT b.*, COUNT(f.flat_id) AS flat_count
        FROM blocks b
        LEFT JOIN flats f ON f.block_id = b.block_id
        GROUP BY b.block_id
        ORDER BY b.block_name
        """
    )
    return render_template("blocks.html", rows=rows)


@app.route("/blocks/<int:block_id>/edit", methods=["GET", "POST"])
def edit_block(block_id):
    row = fetch_one("SELECT * FROM blocks WHERE block_id = %s", (block_id,))
    if not row:
        flash("Block not found.", "danger")
        return redirect(url_for("blocks"))
    if request.method == "POST":
        def save():
            name = blank(request.form.get("block_name"))
            if not name:
                raise ValueError("Block name is required.")
            execute(
                """
                UPDATE blocks
                SET block_name = %s, total_floors = %s, total_flats = %s,
                    constructed_year = %s, description = %s
                WHERE block_id = %s
                """,
                (
                    name,
                    as_int(request.form.get("total_floors"), "Total floors"),
                    as_int(request.form.get("total_flats"), "Total flats"),
                    as_int(request.form.get("constructed_year"), "Constructed year"),
                    blank(request.form.get("description")),
                    block_id,
                ),
            )

        if handle_db(save):
            flash("Block updated.", "success")
            return redirect(url_for("blocks"))
    return render_template("block_form.html", row=row)


@app.route("/blocks/<int:block_id>/delete", methods=["POST"])
def delete_block(block_id):
    def save():
        execute("DELETE FROM blocks WHERE block_id = %s", (block_id,))

    if handle_db(save):
        flash("Block deleted.", "success")
    return redirect(url_for("blocks"))


@app.route("/flats", methods=["GET", "POST"])
def flats():
    if request.method == "POST":
        def save():
            execute(
                """
                INSERT INTO flats
                (block_id, flat_number, floor_no, bhk_type, area_sqft, occupancy_status)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    as_int(request.form.get("block_id"), "Block"),
                    blank(request.form.get("flat_number")),
                    as_int(request.form.get("floor_no"), "Floor"),
                    blank(request.form.get("bhk_type")),
                    as_decimal(request.form.get("area_sqft"), "Area"),
                    blank(request.form.get("occupancy_status")),
                ),
            )
            if not blank(request.form.get("flat_number")):
                raise ValueError("Flat number is required.")

        if not blank(request.form.get("flat_number")):
            flash("Flat number is required.", "danger")
        elif handle_db(save):
            flash("Flat added.", "success")
            return redirect(url_for("flats"))
    rows = fetch_all(
        """
        SELECT f.*, b.block_name, occ.resident_count
        FROM flats f
        JOIN blocks b ON b.block_id = f.block_id
        JOIN vw_flat_occupancy occ ON occ.flat_id = f.flat_id
        ORDER BY b.block_name, f.flat_number
        """
    )
    return render_template(
        "flats.html",
        rows=rows,
        blocks=block_options(),
        bhk_types=BHK_TYPES,
        occupancy=OCCUPANCY,
    )


@app.route("/flats/<int:flat_id>/edit", methods=["GET", "POST"])
def edit_flat(flat_id):
    row = fetch_one("SELECT * FROM flats WHERE flat_id = %s", (flat_id,))
    if not row:
        flash("Flat not found.", "danger")
        return redirect(url_for("flats"))
    if request.method == "POST":
        def save():
            number = blank(request.form.get("flat_number"))
            if not number:
                raise ValueError("Flat number is required.")
            execute(
                """
                UPDATE flats
                SET block_id = %s, flat_number = %s, floor_no = %s,
                    bhk_type = %s, area_sqft = %s, occupancy_status = %s
                WHERE flat_id = %s
                """,
                (
                    as_int(request.form.get("block_id"), "Block"),
                    number,
                    as_int(request.form.get("floor_no"), "Floor"),
                    blank(request.form.get("bhk_type")),
                    as_decimal(request.form.get("area_sqft"), "Area"),
                    blank(request.form.get("occupancy_status")),
                    flat_id,
                ),
            )

        if handle_db(save):
            flash("Flat updated.", "success")
            return redirect(url_for("flats"))
    return render_template(
        "flat_form.html",
        row=row,
        blocks=block_options(),
        bhk_types=BHK_TYPES,
        occupancy=OCCUPANCY,
    )


@app.route("/flats/<int:flat_id>/delete", methods=["POST"])
def delete_flat(flat_id):
    def save():
        execute("DELETE FROM flats WHERE flat_id = %s", (flat_id,))

    if handle_db(save):
        flash("Flat deleted.", "success")
    return redirect(url_for("flats"))


@app.route("/residents", methods=["GET", "POST"])
def residents():
    if request.method == "POST":
        def save():
            name = blank(request.form.get("full_name"))
            if not name:
                raise ValueError("Resident name is required.")
            execute(
                """
                INSERT INTO residents
                (flat_id, full_name, email, phone, id_proof_type, id_proof_number,
                 resident_type, move_in_date, move_out_date, is_primary_contact)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    as_int(request.form.get("flat_id"), "Flat"),
                    name,
                    blank(request.form.get("email")),
                    blank(request.form.get("phone")),
                    blank(request.form.get("id_proof_type")),
                    blank(request.form.get("id_proof_number")),
                    blank(request.form.get("resident_type")),
                    as_date(request.form.get("move_in_date"), "Move-in date"),
                    as_date(request.form.get("move_out_date"), "Move-out date", required=False),
                    checkbox("is_primary_contact"),
                ),
            )

        if handle_db(save):
            flash("Resident added.", "success")
            return redirect(url_for("residents"))
    rows = fetch_all(
        """
        SELECT r.*, f.flat_number, b.block_name
        FROM residents r
        JOIN flats f ON f.flat_id = r.flat_id
        JOIN blocks b ON b.block_id = f.block_id
        ORDER BY r.full_name
        """
    )
    return render_template(
        "residents.html",
        rows=rows,
        flats=flat_options(),
        id_proofs=ID_PROOFS,
        resident_types=RESIDENT_TYPES,
    )


@app.route("/residents/<int:resident_id>/edit", methods=["GET", "POST"])
def edit_resident(resident_id):
    row = fetch_one("SELECT * FROM residents WHERE resident_id = %s", (resident_id,))
    if not row:
        flash("Resident not found.", "danger")
        return redirect(url_for("residents"))
    if request.method == "POST":
        def save():
            name = blank(request.form.get("full_name"))
            if not name:
                raise ValueError("Resident name is required.")
            execute(
                """
                UPDATE residents
                SET flat_id = %s, full_name = %s, email = %s, phone = %s,
                    id_proof_type = %s, id_proof_number = %s, resident_type = %s,
                    move_in_date = %s, move_out_date = %s, is_primary_contact = %s
                WHERE resident_id = %s
                """,
                (
                    as_int(request.form.get("flat_id"), "Flat"),
                    name,
                    blank(request.form.get("email")),
                    blank(request.form.get("phone")),
                    blank(request.form.get("id_proof_type")),
                    blank(request.form.get("id_proof_number")),
                    blank(request.form.get("resident_type")),
                    as_date(request.form.get("move_in_date"), "Move-in date"),
                    as_date(request.form.get("move_out_date"), "Move-out date", required=False),
                    checkbox("is_primary_contact"),
                    resident_id,
                ),
            )

        if handle_db(save):
            flash("Resident updated.", "success")
            return redirect(url_for("residents"))
    return render_template(
        "resident_form.html",
        row=row,
        flats=flat_options(),
        id_proofs=ID_PROOFS,
        resident_types=RESIDENT_TYPES,
    )


@app.route("/residents/<int:resident_id>/delete", methods=["POST"])
def delete_resident(resident_id):
    def save():
        execute("DELETE FROM residents WHERE resident_id = %s", (resident_id,))

    if handle_db(save):
        flash("Resident deleted.", "success")
    return redirect(url_for("residents"))


@app.route("/staff", methods=["GET", "POST"])
def staff():
    if request.method == "POST":
        def save():
            name = blank(request.form.get("full_name"))
            if not name:
                raise ValueError("Staff name is required.")
            execute(
                """
                INSERT INTO staff
                (full_name, role, phone, email, salary, join_date, employment_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    name,
                    blank(request.form.get("role")),
                    blank(request.form.get("phone")),
                    blank(request.form.get("email")),
                    as_decimal(request.form.get("salary"), "Salary"),
                    as_date(request.form.get("join_date"), "Join date"),
                    blank(request.form.get("employment_status")),
                ),
            )

        if handle_db(save):
            flash("Staff member added.", "success")
            return redirect(url_for("staff"))
    rows = fetch_all("SELECT * FROM staff ORDER BY full_name")
    return render_template(
        "staff.html",
        rows=rows,
        roles=STAFF_ROLES,
        employment=EMPLOYMENT,
    )


@app.route("/staff/<int:staff_id>/edit", methods=["GET", "POST"])
def edit_staff(staff_id):
    row = fetch_one("SELECT * FROM staff WHERE staff_id = %s", (staff_id,))
    if not row:
        flash("Staff member not found.", "danger")
        return redirect(url_for("staff"))
    if request.method == "POST":
        def save():
            name = blank(request.form.get("full_name"))
            if not name:
                raise ValueError("Staff name is required.")
            execute(
                """
                UPDATE staff
                SET full_name = %s, role = %s, phone = %s, email = %s,
                    salary = %s, join_date = %s, employment_status = %s
                WHERE staff_id = %s
                """,
                (
                    name,
                    blank(request.form.get("role")),
                    blank(request.form.get("phone")),
                    blank(request.form.get("email")),
                    as_decimal(request.form.get("salary"), "Salary"),
                    as_date(request.form.get("join_date"), "Join date"),
                    blank(request.form.get("employment_status")),
                    staff_id,
                ),
            )

        if handle_db(save):
            flash("Staff member updated.", "success")
            return redirect(url_for("staff"))
    return render_template(
        "staff_form.html",
        row=row,
        roles=STAFF_ROLES,
        employment=EMPLOYMENT,
    )


@app.route("/staff/<int:staff_id>/delete", methods=["POST"])
def delete_staff(staff_id):
    def save():
        execute("DELETE FROM staff WHERE staff_id = %s", (staff_id,))

    if handle_db(save):
        flash("Staff member deleted.", "success")
    return redirect(url_for("staff"))


@app.route("/bills", methods=["GET", "POST"])
def bills():
    if request.method == "POST":
        def save():
            execute(
                """
                INSERT INTO maintenance_bills
                (resident_id, bill_month, bill_year, amount, due_date, status, generated_on)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    as_int(request.form.get("resident_id"), "Resident"),
                    as_int(request.form.get("bill_month"), "Month"),
                    as_int(request.form.get("bill_year"), "Year"),
                    as_decimal(request.form.get("amount"), "Amount"),
                    as_date(request.form.get("due_date"), "Due date"),
                    blank(request.form.get("status")),
                    as_date(request.form.get("generated_on"), "Generated on"),
                ),
            )

        if handle_db(save):
            flash("Bill generated.", "success")
            return redirect(url_for("bills"))
    rows = fetch_all(
        """
        SELECT mb.*, r.full_name, f.flat_number, b.block_name,
               COALESCE(p.paid, 0) AS paid
        FROM maintenance_bills mb
        JOIN residents r ON r.resident_id = mb.resident_id
        JOIN flats f ON f.flat_id = r.flat_id
        JOIN blocks b ON b.block_id = f.block_id
        LEFT JOIN (
            SELECT bill_id, SUM(amount_paid) AS paid
            FROM payments
            GROUP BY bill_id
        ) p ON p.bill_id = mb.bill_id
        ORDER BY mb.bill_year DESC, mb.bill_month DESC, r.full_name
        """
    )
    return render_template(
        "bills.html",
        rows=rows,
        residents=resident_options(),
        statuses=BILL_STATUSES,
        months=MONTHS,
        today=date.today().isoformat(),
    )


@app.route("/bills/<int:bill_id>/edit", methods=["GET", "POST"])
def edit_bill(bill_id):
    row = fetch_one("SELECT * FROM maintenance_bills WHERE bill_id = %s", (bill_id,))
    if not row:
        flash("Bill not found.", "danger")
        return redirect(url_for("bills"))
    if request.method == "POST":
        def save():
            execute(
                """
                UPDATE maintenance_bills
                SET resident_id = %s, bill_month = %s, bill_year = %s, amount = %s,
                    due_date = %s, status = %s, generated_on = %s
                WHERE bill_id = %s
                """,
                (
                    as_int(request.form.get("resident_id"), "Resident"),
                    as_int(request.form.get("bill_month"), "Month"),
                    as_int(request.form.get("bill_year"), "Year"),
                    as_decimal(request.form.get("amount"), "Amount"),
                    as_date(request.form.get("due_date"), "Due date"),
                    blank(request.form.get("status")),
                    as_date(request.form.get("generated_on"), "Generated on"),
                    bill_id,
                ),
            )

        if handle_db(save):
            flash("Bill updated.", "success")
            return redirect(url_for("bills"))
    return render_template(
        "bill_form.html",
        row=row,
        residents=resident_options(),
        statuses=BILL_STATUSES,
        months=MONTHS,
    )


@app.route("/bills/<int:bill_id>/delete", methods=["POST"])
def delete_bill(bill_id):
    def save():
        execute("DELETE FROM maintenance_bills WHERE bill_id = %s", (bill_id,))

    if handle_db(save):
        flash("Bill deleted.", "success")
    return redirect(url_for("bills"))


@app.route("/payments", methods=["GET", "POST"])
def payments():
    if request.method == "POST":
        def save():
            execute(
                """
                INSERT INTO payments
                (bill_id, received_by_staff_id, amount_paid, payment_date, payment_mode, transaction_ref)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    as_int(request.form.get("bill_id"), "Bill"),
                    as_int(request.form.get("received_by_staff_id"), "Received by"),
                    as_decimal(request.form.get("amount_paid"), "Amount paid"),
                    as_date(request.form.get("payment_date"), "Payment date"),
                    blank(request.form.get("payment_mode")),
                    blank(request.form.get("transaction_ref")),
                ),
            )

        if handle_db(save):
            flash("Payment recorded.", "success")
            return redirect(url_for("payments"))
    rows = fetch_all(
        """
        SELECT p.*, r.full_name, mb.bill_month, mb.bill_year, s.full_name AS staff_name
        FROM payments p
        JOIN maintenance_bills mb ON mb.bill_id = p.bill_id
        JOIN residents r ON r.resident_id = mb.resident_id
        JOIN staff s ON s.staff_id = p.received_by_staff_id
        ORDER BY p.payment_date DESC, p.payment_id DESC
        """
    )
    return render_template(
        "payments.html",
        rows=rows,
        bills=bill_options(),
        staff=staff_options(),
        modes=PAY_MODES,
        today=date.today().isoformat(),
    )


@app.route("/payments/<int:payment_id>/edit", methods=["GET", "POST"])
def edit_payment(payment_id):
    row = fetch_one("SELECT * FROM payments WHERE payment_id = %s", (payment_id,))
    if not row:
        flash("Payment not found.", "danger")
        return redirect(url_for("payments"))
    if request.method == "POST":
        def save():
            execute(
                """
                UPDATE payments
                SET bill_id = %s, received_by_staff_id = %s, amount_paid = %s,
                    payment_date = %s, payment_mode = %s, transaction_ref = %s
                WHERE payment_id = %s
                """,
                (
                    as_int(request.form.get("bill_id"), "Bill"),
                    as_int(request.form.get("received_by_staff_id"), "Received by"),
                    as_decimal(request.form.get("amount_paid"), "Amount paid"),
                    as_date(request.form.get("payment_date"), "Payment date"),
                    blank(request.form.get("payment_mode")),
                    blank(request.form.get("transaction_ref")),
                    payment_id,
                ),
            )

        if handle_db(save):
            flash("Payment updated.", "success")
            return redirect(url_for("payments"))
    return render_template(
        "payment_form.html",
        row=row,
        bills=bill_options(),
        staff=staff_options(),
        modes=PAY_MODES,
    )


@app.route("/payments/<int:payment_id>/delete", methods=["POST"])
def delete_payment(payment_id):
    def save():
        execute("DELETE FROM payments WHERE payment_id = %s", (payment_id,))

    if handle_db(save):
        flash("Payment deleted.", "success")
    return redirect(url_for("payments"))


@app.route("/visitors", methods=["GET", "POST"])
def visitors():
    if request.method == "POST":
        def save():
            name = blank(request.form.get("visitor_name"))
            if not name:
                raise ValueError("Visitor name is required.")
            execute(
                """
                INSERT INTO visitors
                (host_resident_id, visitor_name, visitor_phone, purpose,
                 entry_time, exit_time, vehicle_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    as_int(request.form.get("host_resident_id"), "Host resident"),
                    name,
                    blank(request.form.get("visitor_phone")),
                    blank(request.form.get("purpose")),
                    as_datetime(request.form.get("entry_time"), "Entry time"),
                    as_datetime(request.form.get("exit_time"), "Exit time", required=False),
                    blank(request.form.get("vehicle_number")),
                ),
            )

        if handle_db(save):
            flash("Visitor log added.", "success")
            return redirect(url_for("visitors"))
    rows = fetch_all(
        """
        SELECT v.*, r.full_name AS host_name, f.flat_number, b.block_name
        FROM visitors v
        JOIN residents r ON r.resident_id = v.host_resident_id
        JOIN flats f ON f.flat_id = r.flat_id
        JOIN blocks b ON b.block_id = f.block_id
        ORDER BY v.entry_time DESC
        """
    )
    return render_template("visitors.html", rows=rows, residents=resident_options())


@app.route("/visitors/<int:visitor_log_id>/edit", methods=["GET", "POST"])
def edit_visitor(visitor_log_id):
    row = fetch_one(
        "SELECT * FROM visitors WHERE visitor_log_id = %s", (visitor_log_id,)
    )
    if not row:
        flash("Visitor log not found.", "danger")
        return redirect(url_for("visitors"))
    if request.method == "POST":
        def save():
            name = blank(request.form.get("visitor_name"))
            if not name:
                raise ValueError("Visitor name is required.")
            execute(
                """
                UPDATE visitors
                SET host_resident_id = %s, visitor_name = %s, visitor_phone = %s,
                    purpose = %s, entry_time = %s, exit_time = %s, vehicle_number = %s
                WHERE visitor_log_id = %s
                """,
                (
                    as_int(request.form.get("host_resident_id"), "Host resident"),
                    name,
                    blank(request.form.get("visitor_phone")),
                    blank(request.form.get("purpose")),
                    as_datetime(request.form.get("entry_time"), "Entry time"),
                    as_datetime(request.form.get("exit_time"), "Exit time", required=False),
                    blank(request.form.get("vehicle_number")),
                    visitor_log_id,
                ),
            )

        if handle_db(save):
            flash("Visitor log updated.", "success")
            return redirect(url_for("visitors"))
    return render_template(
        "visitor_form.html", row=row, residents=resident_options()
    )


@app.route("/visitors/<int:visitor_log_id>/delete", methods=["POST"])
def delete_visitor(visitor_log_id):
    def save():
        execute("DELETE FROM visitors WHERE visitor_log_id = %s", (visitor_log_id,))

    if handle_db(save):
        flash("Visitor log deleted.", "success")
    return redirect(url_for("visitors"))


@app.route("/complaints", methods=["GET", "POST"])
def complaints():
    if request.method == "POST":
        def save():
            title = blank(request.form.get("title"))
            if not title:
                raise ValueError("Title is required.")
            execute(
                """
                INSERT INTO complaints
                (resident_id, assigned_staff_id, category, title, description,
                 status, raised_on, resolved_on)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    as_int(request.form.get("resident_id"), "Resident"),
                    as_int(request.form.get("assigned_staff_id"), "Staff", required=False),
                    blank(request.form.get("category")),
                    title,
                    blank(request.form.get("description")) or "",
                    blank(request.form.get("status")),
                    as_datetime(request.form.get("raised_on"), "Raised on"),
                    as_datetime(request.form.get("resolved_on"), "Resolved on", required=False),
                ),
            )

        if handle_db(save):
            flash("Complaint registered.", "success")
            return redirect(url_for("complaints"))
    rows = fetch_all(
        """
        SELECT c.*, r.full_name, f.flat_number, s.full_name AS staff_name
        FROM complaints c
        JOIN residents r ON r.resident_id = c.resident_id
        JOIN flats f ON f.flat_id = r.flat_id
        LEFT JOIN staff s ON s.staff_id = c.assigned_staff_id
        ORDER BY c.raised_on DESC
        """
    )
    return render_template(
        "complaints.html",
        rows=rows,
        residents=resident_options(),
        staff=staff_options(),
        categories=COMPLAINT_CATEGORIES,
        statuses=COMPLAINT_STATUSES,
    )


@app.route("/complaints/<int:complaint_id>/edit", methods=["GET", "POST"])
def edit_complaint(complaint_id):
    row = fetch_one(
        "SELECT * FROM complaints WHERE complaint_id = %s", (complaint_id,)
    )
    if not row:
        flash("Complaint not found.", "danger")
        return redirect(url_for("complaints"))
    if request.method == "POST":
        def save():
            title = blank(request.form.get("title"))
            if not title:
                raise ValueError("Title is required.")
            execute(
                """
                UPDATE complaints
                SET resident_id = %s, assigned_staff_id = %s, category = %s,
                    title = %s, description = %s, status = %s, raised_on = %s,
                    resolved_on = %s
                WHERE complaint_id = %s
                """,
                (
                    as_int(request.form.get("resident_id"), "Resident"),
                    as_int(request.form.get("assigned_staff_id"), "Staff", required=False),
                    blank(request.form.get("category")),
                    title,
                    blank(request.form.get("description")) or "",
                    blank(request.form.get("status")),
                    as_datetime(request.form.get("raised_on"), "Raised on"),
                    as_datetime(request.form.get("resolved_on"), "Resolved on", required=False),
                    complaint_id,
                ),
            )

        if handle_db(save):
            flash("Complaint updated.", "success")
            return redirect(url_for("complaints"))
    return render_template(
        "complaint_form.html",
        row=row,
        residents=resident_options(),
        staff=staff_options(),
        categories=COMPLAINT_CATEGORIES,
        statuses=COMPLAINT_STATUSES,
    )


@app.route("/complaints/<int:complaint_id>/delete", methods=["POST"])
def delete_complaint(complaint_id):
    def save():
        execute("DELETE FROM complaints WHERE complaint_id = %s", (complaint_id,))

    if handle_db(save):
        flash("Complaint deleted.", "success")
    return redirect(url_for("complaints"))


@app.route("/facilities", methods=["GET", "POST"])
def facilities():
    if request.method == "POST":
        def save():
            name = blank(request.form.get("facility_name"))
            if not name:
                raise ValueError("Facility name is required.")
            execute(
                """
                INSERT INTO facilities
                (facility_name, location, capacity, hourly_rate, is_active)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    name,
                    blank(request.form.get("location")),
                    as_int(request.form.get("capacity"), "Capacity"),
                    as_decimal(request.form.get("hourly_rate"), "Hourly rate"),
                    checkbox("is_active"),
                ),
            )

        if handle_db(save):
            flash("Facility added.", "success")
            return redirect(url_for("facilities"))
    rows = fetch_all("SELECT * FROM facilities ORDER BY facility_name")
    return render_template("facilities.html", rows=rows)


@app.route("/facilities/<int:facility_id>/edit", methods=["GET", "POST"])
def edit_facility(facility_id):
    row = fetch_one(
        "SELECT * FROM facilities WHERE facility_id = %s", (facility_id,)
    )
    if not row:
        flash("Facility not found.", "danger")
        return redirect(url_for("facilities"))
    if request.method == "POST":
        def save():
            name = blank(request.form.get("facility_name"))
            if not name:
                raise ValueError("Facility name is required.")
            execute(
                """
                UPDATE facilities
                SET facility_name = %s, location = %s, capacity = %s,
                    hourly_rate = %s, is_active = %s
                WHERE facility_id = %s
                """,
                (
                    name,
                    blank(request.form.get("location")),
                    as_int(request.form.get("capacity"), "Capacity"),
                    as_decimal(request.form.get("hourly_rate"), "Hourly rate"),
                    checkbox("is_active"),
                    facility_id,
                ),
            )

        if handle_db(save):
            flash("Facility updated.", "success")
            return redirect(url_for("facilities"))
    return render_template("facility_form.html", row=row)


@app.route("/facilities/<int:facility_id>/delete", methods=["POST"])
def delete_facility(facility_id):
    def save():
        execute("DELETE FROM facilities WHERE facility_id = %s", (facility_id,))

    if handle_db(save):
        flash("Facility deleted.", "success")
    return redirect(url_for("facilities"))


@app.route("/bookings", methods=["GET", "POST"])
def bookings():
    if request.method == "POST":
        def save():
            execute(
                """
                INSERT INTO facility_bookings
                (facility_id, resident_id, booking_date, start_time, end_time, status, total_charge)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    as_int(request.form.get("facility_id"), "Facility"),
                    as_int(request.form.get("resident_id"), "Resident"),
                    as_date(request.form.get("booking_date"), "Booking date"),
                    as_time(request.form.get("start_time"), "Start time"),
                    as_time(request.form.get("end_time"), "End time"),
                    blank(request.form.get("status")),
                    as_decimal(request.form.get("total_charge"), "Total charge"),
                ),
            )

        if handle_db(save):
            flash("Booking created.", "success")
            return redirect(url_for("bookings"))
    rows = fetch_all(
        """
        SELECT bk.*, fa.facility_name, r.full_name, f.flat_number
        FROM facility_bookings bk
        JOIN facilities fa ON fa.facility_id = bk.facility_id
        JOIN residents r ON r.resident_id = bk.resident_id
        JOIN flats f ON f.flat_id = r.flat_id
        ORDER BY bk.booking_date DESC, bk.start_time
        """
    )
    return render_template(
        "bookings.html",
        rows=rows,
        facilities=facility_options(),
        residents=resident_options(),
        statuses=BOOKING_STATUSES,
        today=date.today().isoformat(),
    )


@app.route("/bookings/<int:booking_id>/edit", methods=["GET", "POST"])
def edit_booking(booking_id):
    row = fetch_one(
        "SELECT * FROM facility_bookings WHERE booking_id = %s", (booking_id,)
    )
    if not row:
        flash("Booking not found.", "danger")
        return redirect(url_for("bookings"))
    if request.method == "POST":
        def save():
            execute(
                """
                UPDATE facility_bookings
                SET facility_id = %s, resident_id = %s, booking_date = %s,
                    start_time = %s, end_time = %s, status = %s, total_charge = %s
                WHERE booking_id = %s
                """,
                (
                    as_int(request.form.get("facility_id"), "Facility"),
                    as_int(request.form.get("resident_id"), "Resident"),
                    as_date(request.form.get("booking_date"), "Booking date"),
                    as_time(request.form.get("start_time"), "Start time"),
                    as_time(request.form.get("end_time"), "End time"),
                    blank(request.form.get("status")),
                    as_decimal(request.form.get("total_charge"), "Total charge"),
                    booking_id,
                ),
            )

        if handle_db(save):
            flash("Booking updated.", "success")
            return redirect(url_for("bookings"))
    return render_template(
        "booking_form.html",
        row=row,
        facilities=facility_options(),
        residents=resident_options(),
        statuses=BOOKING_STATUSES,
    )


@app.route("/bookings/<int:booking_id>/delete", methods=["POST"])
def delete_booking(booking_id):
    def save():
        execute("DELETE FROM facility_bookings WHERE booking_id = %s", (booking_id,))

    if handle_db(save):
        flash("Booking deleted.", "success")
    return redirect(url_for("bookings"))


@app.route("/notices", methods=["GET", "POST"])
def notices():
    if request.method == "POST":
        def save():
            title = blank(request.form.get("title"))
            if not title:
                raise ValueError("Title is required.")
            execute(
                """
                INSERT INTO notices
                (published_by_staff_id, title, content, category, publish_date, expiry_date, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    as_int(request.form.get("published_by_staff_id"), "Publisher"),
                    title,
                    blank(request.form.get("content")) or "",
                    blank(request.form.get("category")),
                    as_date(request.form.get("publish_date"), "Publish date"),
                    as_date(request.form.get("expiry_date"), "Expiry date", required=False),
                    checkbox("is_active"),
                ),
            )

        if handle_db(save):
            flash("Notice published.", "success")
            return redirect(url_for("notices"))
    rows = fetch_all(
        """
        SELECT n.*, s.full_name AS publisher
        FROM notices n
        JOIN staff s ON s.staff_id = n.published_by_staff_id
        ORDER BY n.publish_date DESC
        """
    )
    return render_template(
        "notices.html",
        rows=rows,
        staff=staff_options(),
        categories=NOTICE_CATEGORIES,
        today=date.today().isoformat(),
    )


@app.route("/notices/<int:notice_id>/edit", methods=["GET", "POST"])
def edit_notice(notice_id):
    row = fetch_one("SELECT * FROM notices WHERE notice_id = %s", (notice_id,))
    if not row:
        flash("Notice not found.", "danger")
        return redirect(url_for("notices"))
    if request.method == "POST":
        def save():
            title = blank(request.form.get("title"))
            if not title:
                raise ValueError("Title is required.")
            execute(
                """
                UPDATE notices
                SET published_by_staff_id = %s, title = %s, content = %s, category = %s,
                    publish_date = %s, expiry_date = %s, is_active = %s
                WHERE notice_id = %s
                """,
                (
                    as_int(request.form.get("published_by_staff_id"), "Publisher"),
                    title,
                    blank(request.form.get("content")) or "",
                    blank(request.form.get("category")),
                    as_date(request.form.get("publish_date"), "Publish date"),
                    as_date(request.form.get("expiry_date"), "Expiry date", required=False),
                    checkbox("is_active"),
                    notice_id,
                ),
            )

        if handle_db(save):
            flash("Notice updated.", "success")
            return redirect(url_for("notices"))
    return render_template(
        "notice_form.html",
        row=row,
        staff=staff_options(),
        categories=NOTICE_CATEGORIES,
    )


@app.route("/notices/<int:notice_id>/delete", methods=["POST"])
def delete_notice(notice_id):
    def save():
        execute("DELETE FROM notices WHERE notice_id = %s", (notice_id,))

    if handle_db(save):
        flash("Notice deleted.", "success")
    return redirect(url_for("notices"))


@app.errorhandler(DatabaseError)
def on_database_error(exc):
    flash(friendly_db_error(str(exc)), "danger")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
