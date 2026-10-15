import csv
import io
from datetime import date
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, Response)
import database as db

app = Flask(__name__)
app.secret_key = "undajamii-secret-key-change-in-production"

PRIORITY_NAMES = {1: "Low", 2: "Medium", 3: "High"}
STATUS_NAMES   = {1: "Open", 2: "In Progress", 3: "Resolved"}

def is_overdue(issue):
    if issue["status"] == 3 or not issue["due_date"]:
        return False
    try:
        return issue["due_date"] < date.today().isoformat()
    except Exception:
        return False

@app.route("/")
def index():
    issues = db.get_all_issues({"sort": "newest"})[:6]
    summary = db.get_summary()
    overdue_count = sum(1 for i in issues if is_overdue(i))
    return render_template(
        "index.html",
        issues=issues,
        summary=summary,
        overdue_count=overdue_count,
        priority_names=PRIORITY_NAMES,
        status_names=STATUS_NAMES,
        is_overdue=is_overdue,
    )

@app.route("/filter")
def filter_page():
    filters = {
        "status":   request.args.get("status", ""),
        "priority": request.args.get("priority", ""),
        "facility": request.args.get("facility", "").strip(),
        "sort":     request.args.get("sort", "newest"),
    }
    issues = db.get_all_issues(filters)
    return render_template(
        "filter.html",
        issues=issues,
        filters=filters,
        priority_names=PRIORITY_NAMES,
        status_names=STATUS_NAMES,
    )

@app.route("/stats")
def stats_page():
    summary = db.get_summary()
    monthly = db.get_monthly_stats()
    return render_template(
        "stats.html",
        summary=summary,
        monthly=monthly,
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        facility    = request.form.get("facility", "").strip()
        description = request.form.get("description", "").strip()
        reported_by = request.form.get("reported_by", "").strip() or "Anonymous"
        assigned_to = request.form.get("assigned_to", "").strip()
        due_date    = request.form.get("due_date", "").strip()

        try:
            priority = int(request.form.get("priority", 0))
        except ValueError:
            priority = 0

        if not facility or not description:
            flash("Facility and description are required.", "danger")
        elif priority not in (1, 2, 3):
            flash("Priority must be Low, Medium, or High.", "danger")
        else:
            db.add_issue(facility, description, priority, reported_by,
                         assigned_to, due_date)
            flash("Issue registered successfully.", "success")
            return redirect(url_for("index"))

    return render_template("register.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    issue = None
    searched = False
    if request.method == "POST":
        searched = True
        try:
            ticket_id = int(request.form.get("ticket_id", 0))
        except ValueError:
            ticket_id = 0
        issue = db.get_issue(ticket_id) if ticket_id > 0 else None

    return render_template(
        "search.html",
        issue=issue,
        searched=searched,
        priority_names=PRIORITY_NAMES,
        status_names=STATUS_NAMES,
        is_overdue=is_overdue,
    )

@app.route("/edit/<int:ticket_id>", methods=["GET", "POST"])
def edit(ticket_id):
    issue = db.get_issue(ticket_id)
    if issue is None:
        flash("Ticket not found.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        action = request.form.get("action", "update")

        if action == "comment":
            author = request.form.get("author", "").strip() or "Anonymous"
            body   = request.form.get("body", "").strip()
            if body:
                db.add_comment(ticket_id, author, body)
                flash("Comment added.", "success")
            else:
                flash("Comment cannot be empty.", "danger")
            return redirect(url_for("edit", ticket_id=ticket_id))

        facility    = request.form.get("facility", "").strip()
        description = request.form.get("description", "").strip()
        reported_by = request.form.get("reported_by", "").strip() or "Anonymous"
        assigned_to = request.form.get("assigned_to", "").strip()
        due_date    = request.form.get("due_date", "").strip()

        try:
            priority = int(request.form.get("priority", 0))
            status   = int(request.form.get("status", 0))
        except ValueError:
            priority, status = 0, 0

        if not facility or not description:
            flash("Facility and description are required.", "danger")
        elif priority not in (1, 2, 3) or status not in (1, 2, 3):
            flash("Invalid priority or status.", "danger")
        else:
            db.update_issue(ticket_id, facility, description, priority, status,
                            reported_by, assigned_to, due_date)
            flash("Issue updated.", "success")
            return redirect(url_for("index"))

        issue = db.get_issue(ticket_id)

    comments = db.get_comments(ticket_id)
    return render_template(
        "edit.html",
        issue=issue,
        comments=comments,
        priority_names=PRIORITY_NAMES,
        status_names=STATUS_NAMES,
        is_overdue=is_overdue,
    )

@app.route("/delete/<int:ticket_id>", methods=["POST"])
def delete(ticket_id):
    db.delete_issue(ticket_id)
    flash(f"Ticket {ticket_id} deleted.", "success")
    return redirect(url_for("index"))

@app.route("/delete_resolved", methods=["POST"])
def delete_resolved():
    count = db.delete_resolved()
    flash(f"{count} resolved issue(s) deleted.", "success")
    return redirect(url_for("stats_page"))

@app.route("/export.csv")
def export_csv():
    issues = db.get_all_issues({"sort": "oldest"})
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Facility", "Description", "Priority",
                     "Status", "Reported By", "Assigned To",
                     "Due Date", "Created At"])
    for i in issues:
        writer.writerow([
            i["id"], i["facility"], i["description"],
            PRIORITY_NAMES[i["priority"]], STATUS_NAMES[i["status"]],
            i["reported_by"], i["assigned_to"], i["due_date"], i["created_at"]
        ])
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition":
                 "attachment; filename=undajamii_issues.csv"}
    )

if __name__ == "__main__":
    import os
    db.init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)