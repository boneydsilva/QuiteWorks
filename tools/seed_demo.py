"""Seed a throwaway WorkQueue database with realistic demo data for screenshots.

Writes only to WORKQUEUE_DATA_DIR, which the caller points at the scratchpad,
so a real install is never touched.
"""
import os, sys, random, sqlite3, datetime as dt

DATA_DIR = sys.argv[1]
REPO = os.environ.get("WORKQUEUE_REPO", r"D:\MyWorkUpdate")
os.environ["WORKQUEUE_DATA_DIR"] = DATA_DIR
sys.path.insert(0, REPO)

from server import db, auth  # noqa: E402

path = db.init()
auth.set_password("demo1234")
print("db:", path)

rnd = random.Random(20260910)
now = dt.datetime.now()
NOW = now.timestamp()

# --- people ---------------------------------------------------------------

PEOPLE = [
    ("DESKTOP-FRONTDESK", "asha",   "Asha Rao"),
    ("DESKTOP-ACCOUNTS",  "priya",  "Priya Nair"),
    ("DESKTOP-STORES",    "imran",  "Imran Shaikh"),
    ("DESKTOP-DISPATCH",  "deepa",  "Deepa Menon"),
    ("LAPTOP-SALES",      "vikas",  "Vikas Patil"),
]

con = sqlite3.connect(path)
con.execute("PRAGMA foreign_keys=ON")

machine_ids = []
for i, (host, user, name) in enumerate(PEOPLE):
    cur = con.execute(
        "INSERT INTO machines (hostname, os_user, display_name, last_ip, first_seen, last_seen, active)"
        " VALUES (?,?,?,?,?,?,1)",
        (host, user, name, f"192.168.0.{41 + i}", NOW - 86400 * 90, NOW - rnd.uniform(1, 8)),
    )
    machine_ids.append(cur.lastrowid)

# --- the work a small distribution office actually does -------------------

WORK = [
    ("Check the morning bank statement",      "Match yesterday's UPI receipts against the sales register."),
    ("Call the vendor about the delayed order", "Ask for a revised ETA and a credit note."),
    ("Reconcile the September invoice batch", "Cross-check every total against the bank export before it goes to accounts. Flag anything over 50."),
    ("Update the shipping tracker",           "Rows 40-120 are missing carrier codes."),
    ("Pack the Andheri orders",               "Six cartons. Print labels before sealing."),
    ("Chase the overdue payment",             "Third reminder. Copy me on the email."),
    ("Stock count - aisle 4",                 "Physical count against the system figure."),
    ("Fix the label printer",                 "It is skipping every second label."),
    ("Send the weekly sales summary",         "Same format as last week, to the WhatsApp group."),
    ("Raise a GST invoice for Deshmukh & Co", "PO number is on the email I forwarded."),
    ("File the transport bills",              "Everything from the last fortnight."),
    ("Follow up on the Pune enquiry",         "They asked for a revised quotation."),
    ("Update the price list",                 "New rates apply from Monday."),
    ("Audit the petty cash",                  "Receipts are in the drawer."),
    ("Reply to the customer complaint",       "Damaged carton on the Thane delivery."),
    ("Prepare the courier manifest",          "For tomorrow's 9am pickup."),
    ("Check the e-way bills",                 "Two are expiring today."),
    ("Restock the packing material",          "We are down to the last roll of tape."),
    ("Confirm tomorrow's deliveries",         "Call each customer to confirm someone will be there."),
    ("Clear the returns shelf",               "Decide restock or write-off for each item."),
]

PRIORITIES = ["low", "normal", "normal", "normal", "high", "high", "urgent"]

def work_hour(day: dt.date, rnd) -> float:
    """A timestamp during that day's working hours."""
    h = rnd.choice([9, 10, 10, 11, 11, 12, 14, 14, 15, 15, 16, 16, 17, 18])
    return dt.datetime.combine(day, dt.time(h, rnd.randrange(0, 60), rnd.randrange(0, 60))).timestamp()

def add_task(mid, title, desc, prio, created, accepted, completed, status, due):
    cur = con.execute(
        "INSERT INTO tasks (machine_id, title, description, priority, due_at, status,"
        " created_at, accepted_at, completed_at, created_by) VALUES (?,?,?,?,?,?,?,?,?,'admin')",
        (mid, title, desc, prio, due, status, created, accepted, completed),
    )
    tid = cur.lastrowid
    con.execute("INSERT INTO task_events (task_id, event, at, note) VALUES (?,'created',?,'')", (tid, created))
    if accepted:
        con.execute("INSERT INTO task_events (task_id, event, at, note) VALUES (?,'accepted',?,'delivered to the PC')", (tid, accepted))
    if status == "completed" and completed:
        con.execute("INSERT INTO task_events (task_id, event, at, note) VALUES (?,'completed',?,'')", (tid, completed))
    if status == "cancelled" and completed:
        con.execute("INSERT INTO task_events (task_id, event, at, note) VALUES (?,'cancelled',?,'no longer needed')", (tid, completed))
    return tid

# --- 32 days of history ---------------------------------------------------

total = 0
for back in range(32, 0, -1):
    day = (now - dt.timedelta(days=back)).date()
    if day.weekday() == 6:                      # Sunday off
        continue
    count = rnd.randrange(4, 12) if day.weekday() < 5 else rnd.randrange(2, 6)
    for _ in range(count):
        mid = rnd.choice(machine_ids)
        title, desc = rnd.choice(WORK)
        prio = rnd.choice(PRIORITIES)
        created = work_hour(day, rnd)
        # response: usually a couple of minutes, occasionally much longer
        resp = rnd.choice([20, 45, 90, 150, 240, 400, 900, 1800, 3400])
        accepted = created + resp
        work = rnd.choice([300, 600, 900, 1500, 2400, 3600, 5400, 7200, 11000])
        completed = accepted + work
        due = created + rnd.choice([7200, 14400, 28800, 86400]) if rnd.random() < 0.65 else None
        if due and rnd.random() < 0.07:         # a few genuinely late
            due = accepted + work * 0.6
        status = "completed"
        if rnd.random() < 0.05:
            status = "cancelled"
        add_task(mid, title, desc, prio, created, accepted, completed, status, due)
        total += 1

# --- today: a board worth looking at --------------------------------------
#
# Everything below is placed relative to the real clock and strictly ordered
# created < accepted < completed < now, so no card can show a future time or a
# zero-second duration. Titles are drawn without replacement so no column
# repeats itself.

# Titles the open columns below claim, so a completed card never repeats one.
RESERVED = {
    "Pack the Andheri orders", "Stock count - aisle 4", "Update the price list",
    "Confirm tomorrow's deliveries", "Reconcile the September invoice batch",
    "Follow up on the Pune enquiry", "Update the shipping tracker",
    "Prepare the courier manifest",
}
pool = [w for w in WORK if w[0] not in RESERVED]
rnd.shuffle(pool)
def take():
    return pool.pop()

# completed over the working stretch that just ended: oldest first
for i in range(12):
    mid = rnd.choice(machine_ids)
    title, desc = take()
    # slot i sits in its own window, so completions spread across the day
    completed = NOW - (12 - i) * 3300 - rnd.uniform(0, 1800)
    work = rnd.choice([600, 900, 1500, 2400, 3000, 4200, 5400])
    accepted = completed - work
    created = accepted - rnd.choice([30, 90, 180, 420, 900])
    add_task(mid, title, desc, rnd.choice(PRIORITIES), created, accepted, completed,
             "completed", created + rnd.choice([10800, 21600, 28800]))
    total += 1

# in progress right now
in_progress = [
    (machine_ids[3], "Pack the Andheri orders", "Six cartons. Print labels before sealing.", "urgent"),
    (machine_ids[2], "Stock count - aisle 4", "Physical count against the system figure.", "normal"),
    (machine_ids[1], "Update the price list", "New rates apply from Monday.", "high"),
]
for mid, title, desc, prio in in_progress:
    created = NOW - rnd.uniform(2400, 6000)
    accepted = created + rnd.uniform(30, 180)
    add_task(mid, title, desc, prio, created, accepted, None, "accepted", NOW + rnd.uniform(7200, 21600))
    total += 1

# waiting
waiting = [
    (machine_ids[0], "Confirm tomorrow's deliveries", "Call each customer to confirm someone will be there.", "normal"),
    (machine_ids[1], "Reconcile the September invoice batch", "Cross-check every total against the bank export before it goes to accounts. Flag anything over 50.", "urgent"),
    (machine_ids[4], "Follow up on the Pune enquiry", "They asked for a revised quotation.", "high"),
    (machine_ids[0], "Update the shipping tracker", "Rows 40-120 are missing carrier codes.", "normal"),
    (machine_ids[3], "Prepare the courier manifest", "For tomorrow's 9am pickup.", "high"),
]
waiting_ids = []
for i, (mid, title, desc, prio) in enumerate(waiting):
    created = NOW - rnd.uniform(120, 2400)
    # comfortably in the future, so nothing on the board reads as already late
    waiting_ids.append(
        add_task(mid, title, desc, prio, created, None, None, "assigned",
                 NOW + 9000 + i * 5400)
    )
    total += 1

# --- comments, so the badges and the drawer have something to show --------

con.execute("INSERT INTO task_comments (task_id, author, body, at) VALUES (?,?,?,?)",
            (waiting_ids[1], "Priya Nair", "The bank export for the 3rd is missing. Shall I use the PDF statement instead?", NOW - 900))
con.execute("INSERT INTO task_comments (task_id, author, body, at) VALUES (?,?,?,?)",
            (waiting_ids[1], "Admin", "Yes, use the PDF. I will get the export re-sent tomorrow.", NOW - 780))
con.execute("INSERT INTO task_comments (task_id, author, body, at) VALUES (?,?,?,?)",
            (waiting_ids[4], "Deepa Menon", "Pickup moved to 9.30. Confirmed with the driver.", NOW - 420))

con.commit()
con.close()
print(f"seeded {total} tasks across {len(machine_ids)} people")
