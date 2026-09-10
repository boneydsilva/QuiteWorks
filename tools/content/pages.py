# -*- coding: utf-8 -*-
"""The English-only landing pages: the search terms people actually type.

The rest of the site is written brand-first — "team software that runs on your
own Wi-Fi" — which is true and which nobody searches for. These eight pages
answer the queries instead: employee task tracker, work tracker, task
management software, and "is there something simpler than Jira".

**English only, deliberately.** These phrases are typed in English in India
even by people who then read the site in Hindi or Tamil, and eight pages of
copy in eleven languages is eight pages nobody can check. The language picker
on these pages sends a reader to that language's /workqueue, which is the
nearest thing that does exist. Nothing here is in tools/content/strings/, so
the twelve-language key set is untouched.

**These are not doorway pages and must not become them.** Each one is a
different argument, not the same argument with the keyword swapped:

    /employee-task-tracker       what it is like to be the tracked employee
    /work-tracker                the two timestamps and what they measure
    /task-management-software    the buying decision, and the arithmetic
    /alternatives/*              four honest comparisons

Every comparison page carries a "stay where you are if" section. That is not
modesty. A comparison that finds no reason to stay is an advertisement, and
readers can tell.

Facts about other people's products are kept qualitative on purpose. Their
plans and prices change; ours would go stale and be wrong on someone else's
behalf. Say what shape a tool is, not what it costs this month.

Blocks are rendered by build_i18n.build_page(); the vocabulary is documented
there. Inside any string, **bold** and [text](/href) work, and nothing else.
"""

# Facts repeated across pages. One place, so a price change is one edit.
PRICE = "₹14,999"
RENEW = "₹4,999"
SEAT = "₹600"


# --- The shared comparison rows ---------------------------------------------
# Three of these eight rows go against WorkQueue. That is the point of having
# a table at all.

VS_CLOUD = [
    ["How you pay", ("yes", "Once, for the whole company"),
     "Per person, per month, forever"],
    ["Where the work is stored", ("yes", "A file on a PC in your office"),
     "The vendor's servers"],
    ["What the employee opens", ("yes", "Nothing — the strip is already there"),
     "A web app or a phone app"],
    ["Timing", ("yes", "Automatic, two timestamps a task"),
     "A manual timer, or nothing"],
    ["With the internet down", ("yes", "Keeps working on the office network"),
     ("no", "Stops")],
    ["Project planning features", ("no", "None at all"),
     ("yes", "Usually plenty")],
    ["Mac and Linux employees", ("no", "Not yet"), ("yes", "Yes")],
    ["Fully remote teams", "Possible, over a private network",
     ("yes", "What they are built for")],
]


PAGES = [

# =============================================================================
#  1. Employee task tracker — the employee's side of it
# =============================================================================
{
 "slug": "employee-task-tracker",
 "title": "Employee task tracker for small teams in India — WorkQueue",
 "desc": "An employee task tracker that runs on your own office PCs. Each "
         "person's work sits in a thin strip at the top of their screen, the "
         "clock starts by itself, and you pay once for the whole company "
         "instead of every month per person.",
 "crumb": "Employee task tracker",
 "blocks": [

  ("hero", {
   "eyebrow": "Employee task tracking",
   "h1": "An employee task tracker that lives at the top of the screen.",
   "lede": "Most task trackers are a website somebody has to remember to open. "
           "WorkQueue is a strip docked into Windows — thirty-four pixels tall, "
           "always visible, never covering a window — that shows each person "
           "only the work that is theirs, and records when it arrived and when "
           "they finished without anybody starting a timer.",
   "trust": ["Nothing for the employee to open",
             "Two timestamps, taken automatically",
             PRICE + " once, for the whole company"],
   "b1": "Try it free for 30 days",
   "b2": "See how the whole thing works",
   "b2href": "/workqueue",
  }),

  ("shots", {
   "items": [
    ("/assets/img/bar-strip-left.png", 500, 41,
     "Close-up of the left end of the employee strip: a green connected dot, "
     "the name Asha Rao, then a red diamond and the task title Reconcile the "
     "September invoice batch.",
     "**Left end.** A green dot while the server is reachable, their name, and "
     "the job they are on. The red diamond means urgent."),
    ("/assets/img/bar-strip-chips.png", 560, 41,
     "Close-up of the right end of the employee strip: three colour-coded "
     "chips, one per open task, and a small menu arrow.",
     "**Right end.** One chip for every other task waiting, coloured by "
     "priority. Clicking one switches to it."),
   ],
  }),

  ("prose", {
   "eyebrow": "The employee's side",
   "h2": "What a tracked employee actually sees.",
   "paras": [
    "That is the entire interface. There is no dashboard for them, no project "
    "view, no login screen and no inbox — their name, the job they are on now, "
    "and a chip for each other task waiting.",
    "It is a Windows AppBar, the same kind of thing the taskbar is. Windows "
    "reserves the band at the top of the screen for it, so a maximised window "
    "cannot cover it and twelve open tabs cannot bury it. A new task appears "
    "there within a couple of seconds of being assigned.",
    "When the job is done they press **Complete** once. That is the whole "
    "workflow, and it is the only thing anyone has to be trained on.",
   ],
  }),

  ("checks", {
   "h2": "What it records, and what it will never record.",
   "band": True,
   "cols": [
    ("Recorded, for every task", [
     ("When it reached their screen.",
      "The moment the strip received it — not when somebody remembered to "
      "click Accept, because there is nothing to accept."),
     ("When they pressed Complete.",
      "One click, from the strip or from the panel behind it."),
     ("Who it went to,",
      "what it said, and what priority you gave it."),
     ("Anything they typed back.",
      "The panel has a box for asking the manager a question about the job."),
    ]),
    ("Never recorded, on any plan", [
     ("No screenshots.", "Not on a timer, not at random, not once."),
     ("No keystrokes.", "Nothing is read from the keyboard."),
     ("No idle or active time.", "The mouse is not being watched."),
     ("No browsing history.",
      "Which sites and apps somebody uses is not our business, and not yours "
      "through us."),
    ]),
   ],
  }),

  ("callout", {
   "h3": "This is why teams accept it.",
   "paras": [
    "That second list is a deliberate line, not a gap in the feature set. A "
    "tracker that watches people gets worked around within a fortnight; one "
    "that timestamps jobs mostly gets left alone.",
    "In practice the argument it ends is **\"I sent you that hours ago\"** — "
    "which stops being an argument when both people are looking at the same "
    "two timestamps.",
   ],
  }),

  ("steps", {
   "h2": "Putting it on a team.",
   "lede": "An afternoon, and nobody has to be an administrator.",
   "items": [
    ("Install the server",
     "One file, on a PC that stays switched on — usually the manager's. It "
     "starts itself after that and tells you the dashboard address."),
    ("Install the strip",
     "One file on each employee PC. It finds the server on your network by "
     "itself, so there is no address for anyone to type and nothing to "
     "configure."),
    ("Name the machines",
     "Open the dashboard, put a person's name against each PC, and start "
     "handing out work. That name is what shows on their strip and in every "
     "report afterwards."),
   ],
  }),

  ("shots", {
   "zoom": True,
   "browser": "http://192.168.0.10:8420 &mdash; WorkQueue",
   "items": [
    ("/assets/img/dashboard-board.png", 1920, 1080,
     "The WorkQueue board: a task composer at the top, and three live columns "
     "showing Waiting, In progress and Completed today.",
     "The manager's side, open in a browser on the office network. Type the "
     "job, pick whose screen it goes to, press Assign. Click for full size."),
   ],
  }),

  ("prose", {
   "h2": "What it costs to track a team this way.",
   "band": True,
   "paras": [
    PRICE + ", once, for your whole company. Not per employee and not per "
    "month. Hire five more people next year and the number does not move — "
    "there is no seat count anywhere in the software to move it.",
    "Thirty days free first, every feature, no card. If you buy afterwards "
    "the data from the trial carries over. After the first year, updates and "
    "support are " + RENEW + " a year and entirely optional; skip it and the "
    "version you have keeps running.",
    "[The full pricing, and the arithmetic against a per-seat tool](/pricing)",
   ],
  }),

  ("links", {
   "h2": "If you are still comparing.",
   "items": [
    ("/work-tracker", "The timing side of it",
     "What the two timestamps actually measure, and what they cannot"),
    ("/alternatives/jira", "Compared with Jira",
     "Including who should stay on Jira"),
    ("/alternatives/excel-and-whatsapp", "Compared with WhatsApp and Excel",
     "What most small businesses in India are really using"),
   ],
  }),
 ],

 "faq": [
  ("Is this employee monitoring? Will my team hate it?",
   "It records two things per task: when it reached the screen and when the "
   "person pressed Complete. It does not take screenshots, log keystrokes, "
   "track idle time or watch which websites anyone visits, and it never will "
   "— that is a deliberate line, not an oversight. In practice teams tend to "
   "like it, because \"I sent you that hours ago\" stops being an argument. "
   "Everyone is looking at the same timestamps."),
  ("Do employees need a login or a password?",
   "No. The strip belongs to the PC, and you give that PC a person's name in "
   "the dashboard. There is nothing for an employee to sign into, nothing to "
   "forget, and nothing to install after the first time."),
  ("What happens when the Wi-Fi goes down?",
   "Employees keep seeing their tasks and keep marking them complete. Those "
   "actions queue up on their own PC with the real time they were clicked, "
   "and are delivered when the network comes back — so a task finished at "
   "10:35 during an outage is still recorded as 10:35."),
  ("Can people use it from home, or from another branch?",
   "Yes. WorkQueue can be joined to a private network (Tailscale) so laptops "
   "outside the office reach the same server securely, with nothing exposed "
   "to the public internet. It is one extra step during setup, and it is "
   "included."),
  ("How many employees can it track?",
   "It is built and load-tested for a single office — around 25 machines at "
   "once on ordinary hardware, with responses well under a tenth of a second. "
   "If you are bigger than that, talk to us before you buy rather than after."),
  ("Does it work on Mac?",
   "Not today. The dashboard is an ordinary web page and opens on anything, "
   "including a phone, but the employee strip needs Windows 10 or 11. Mac and "
   "Linux are on the roadmap rather than in the box, and we would rather say "
   "so plainly than let you find out."),
 ],
},


# =============================================================================
#  2. Work tracker — the measurement argument
# =============================================================================
{
 "slug": "work-tracker",
 "title": "Work tracker that times every job by itself — WorkQueue",
 "desc": "A work tracker for small teams that asks nobody to fill in a "
         "timesheet. WorkQueue records when a task reached the screen and "
         "when it was finished, so response time and work time come out on "
         "their own. Runs on your own office network.",
 "crumb": "Work tracker",
 "blocks": [

  ("hero", {
   "eyebrow": "Work tracking",
   "h1": "A work tracker where nobody fills in a timesheet.",
   "lede": "A timesheet is a guess written on Friday about a Tuesday. "
           "WorkQueue takes two timestamps for every task — the second it "
           "arrived on the employee's screen, and the second they pressed "
           "Complete — and every number on the reports is arithmetic on those "
           "two. Nobody starts a clock, so nobody forgets to.",
   "trust": ["No timer to start or stop",
             "Response time and work time, per task",
             "The numbers never leave your office"],
   "b1": "Try it free for 30 days",
   "b2": "See the whole tool",
   "b2href": "/workqueue",
  }),

  ("spec", {
   "eyebrow": "What is measured",
   "h2": "Two clocks, and why they are different.",
   "items": [
    ("Response time",
     "From the moment you press Assign to the moment the job is on their "
     "screen. On a healthy office network that is a couple of seconds. When "
     "it is not, that is worth knowing, and it is the number that tells you."),
    ("Work time",
     "From arriving on the screen to the click on Complete. There is no pause "
     "button, because a pause button is somewhere to put a lie."),
    ("Everything else on the reports",
     "Tasks closed per person per day, what is overdue, which priorities slip, "
     "how this Tuesday compares with last Tuesday. All of it is those two "
     "numbers grouped differently — there is no third source."),
   ],
  }),

  ("shots", {
   "zoom": True,
   "browser": "http://192.168.0.10:8420 &mdash; Analytics",
   "items": [
    ("/assets/img/dashboard-analytics.png", 1920, 1080,
     "The WorkQueue analytics page, showing completion counts and average "
     "response and work times per person over a date range.",
     "Thirty days of two timestamps, with nobody having typed a duration. "
     "Click for full size."),
   ],
  }),

  ("cards", {
   "h2": "Questions you can answer on Monday morning.",
   "cols": 3,
   "items": [
    ("Who is actually carrying it",
     "Not who says they are busy — how many jobs each person closed, and how "
     "long each one took."),
    ("What is sitting still",
     "A task assigned at nine and still open at four is on the board in the "
     "colour it went on with. Nothing has to be chased to find that out."),
    ("Whether it is getting better",
     "Thirty days of the same two timestamps is a trend, and a trend is the "
     "only honest way to tell whether a change you made worked."),
   ],
  }),

  ("prose", {
   "h2": "It keeps time when the network does not.",
   "band": True,
   "paras": [
    "If the Wi-Fi drops, the strip keeps showing the tasks it already has and "
    "keeps accepting Complete. Those clicks queue on the employee's own PC "
    "with the real time they happened, and are delivered when the network "
    "comes back.",
    "A job finished at **10:35** during an outage is recorded as 10:35, not "
    "as whenever the router recovered. Timing that only works on a good day "
    "is not timing.",
   ],
  }),

  ("checks", {
   "h2": "What this deliberately is not.",
   "lede": "Both halves matter when you are choosing. One of them is why the "
           "team will tolerate it; the other is why it might be too small for "
           "you.",
   "cols": [
    ("It is not surveillance", [
     ("No screenshots, ever.", "Not on a timer and not at random."),
     ("No keystrokes, no idle time.",
      "The keyboard and the mouse are not being read."),
     ("No list of sites or apps.",
      "The software has no idea what else is open."),
     ("No telemetry to us.",
      "It never contacts Quietworks. There is no licence check-in and no "
      "analytics call."),
    ]),
    ("And it is not attendance software", [
     ("No clock-in or clock-out.",
      "It times tasks, not people. There is no daily total of hours at a desk."),
     ("No hours-worked report.",
      "If payroll needs one, this is the wrong tool and we would rather say "
      "so now."),
     ("No sprints or Gantt charts.",
      "It hands out jobs and times them. If you need a work-breakdown "
      "structure, buy one."),
     ("Only what goes through it.",
      "Work handed out in the corridor is not in the numbers. That is true of "
      "every tool of this shape, and worth deciding up front."),
    ], True),
   ],
  }),

  ("prose", {
   "h2": "Getting the numbers back out.",
   "paras": [
    "History exports to CSV, so it lands in the spreadsheet you already "
    "report from. The whole database exports as a JSON snapshot, or as the "
    "SQLite file itself if you would rather have the original.",
    "There is no lock-in, because there is nothing of yours on our side to "
    "lock. The file is on your PC and you can copy it anywhere.",
   ],
  }),

  ("links", {
   "h2": "Related.",
   "items": [
    ("/employee-task-tracker", "The employee's side",
     "What the strip looks like, and what is never recorded"),
    ("/task-management-software", "What it costs against a subscription",
     "The three-year arithmetic for five, ten and twenty-five people"),
    ("/alternatives/", "How it compares",
     "Jira, Trello, Asana, and a WhatsApp group"),
   ],
  }),
 ],

 "faq": [
  ("Does it track hours worked, like attendance software?",
   "No. It times tasks, not people — there is no clock-in, no clock-out and "
   "no daily total of hours at a desk. If what you need is attendance or "
   "payroll hours, this is the wrong tool, and we would rather you knew that "
   "before the trial than after it."),
  ("Can an employee edit the times?",
   "There is no field anywhere for typing in a duration. Every number on the "
   "reports comes from a click that actually happened — the task arriving on "
   "the strip, and Complete being pressed — so there is nothing to round up "
   "at the end of the week."),
  ("What about work that never goes on the board?",
   "It is not in the numbers. If half the day's jobs get handed over in the "
   "corridor, half the day is missing, and no tool of this kind can fix that. "
   "It is worth agreeing up front how much of the work will actually go "
   "through it."),
  ("Do you see any of our numbers?",
   "No. The software never contacts us. There is no telemetry, no licence "
   "check-in and no analytics call. If your office had no internet at all, "
   "WorkQueue would not notice."),
  ("Can I see the reports on my phone?",
   "Yes. The dashboard is an ordinary web page served on your own network, so "
   "any phone on the office Wi-Fi opens it. Windows is only needed for the "
   "employee strip."),
  ("How accurate is the response time?",
   "It is the gap between two events the software itself observed, on a local "
   "network, so it is generally a second or two rather than a guess. What it "
   "measures is the job reaching the screen — whether the person was looking "
   "at the screen is something no software can honestly tell you."),
 ],
},


# =============================================================================
#  3. Task management software — the buying decision
# =============================================================================
{
 "slug": "task-management-software",
 "title": "Task management software for small businesses in India",
 "desc": "Task management software you buy once instead of renting per "
         "person. WorkQueue runs on a Windows PC in your own office, hands "
         "work to your team and times it automatically. " + PRICE + " for the "
         "whole company, free for 30 days, GST invoice.",
 "crumb": "Task management software",
 "blocks": [

  ("hero", {
   "eyebrow": "Task management software",
   "h1": "Task management software you buy once.",
   "lede": "Almost everything in this category is rented — per person, per "
           "month, forever, with your work kept on somebody else's computer. "
           "WorkQueue is the other kind: one payment, installed on a PC in "
           "your own office, and it keeps working whether or not you ever pay "
           "us again.",
   "trust": ["One payment, not a subscription",
             "Runs on your own network",
             "Rupees, and a GST invoice"],
   "b1": "Try it free for 30 days",
   "b2": "See the pricing",
   "b2href": "/pricing",
  }),

  ("table", {
   "eyebrow": "The arithmetic",
   "h2": "What renting the same thing costs.",
   "lede": "Per-seat task tools generally land around " + SEAT + " per person "
           "per month. Over three years — roughly how long a small business "
           "keeps a tool it likes — that looks like this.",
   "caption": "Three-year cost of WorkQueue against a per-seat subscription",
   "head": ["Your team", "WorkQueue, three years",
            "A per-seat tool, three years", "Difference"],
   "rows": [
    ["5 people", ("b", PRICE + " once"), "₹54,000", ("yes", "₹39,001 kept")],
    ["10 people", ("b", PRICE + " once"), "₹1,08,000", ("yes", "₹93,001 kept")],
    ["25 people", ("b", PRICE + " once"), "₹2,70,000", ("yes", "₹2,55,001 kept")],
   ],
   "note": "Illustrative, using " + SEAT + " per person per month as a typical "
           "mid-range figure. Check it against whatever you are actually "
           "paying — the comparison only gets better as you hire.",
  }),

  ("checks", {
   "h2": "Who this fits, and who it does not.",
   "lede": "The second column is the more useful one. This is a narrow tool "
           "and it is cheaper for everybody if you find that out now.",
   "band": True,
   "cols": [
    ("A good fit", [
     ("One office or one floor.",
      "Five to twenty-five people on Windows PCs, in one place, on one "
      "network."),
     ("Work that arrives as jobs.",
      "Orders, service calls, tickets, deliveries, batches — things with a "
      "beginning and an end."),
     ("A manager who hands work out.",
      "One person deciding who does what, rather than a team that "
      "self-organises out of a backlog."),
     ("Nobody whose job is IT.",
      "If someone can install a printer, they can install this. If you would "
      "rather not, we will do it over a remote session."),
    ]),
    ("A bad fit — better said now", [
     ("Software projects.",
      "No sprints, no epics, no story points, no dependency graphs. Jira "
      "exists and is good at that."),
     ("Mac or Linux employees.",
      "The dashboard opens anywhere; the strip needs Windows 10 or 11. That "
      "is on the roadmap, not in the box."),
     ("A fully remote team.",
      "It can run over a private network and that is included, but if nobody "
      "is ever in the office there are better-shaped tools."),
     ("More than about 25 machines.",
      "It is built and tested for a single office. Talk to us before you buy "
      "rather than after."),
    ], True),
   ],
  }),

  ("prose", {
   "h2": "Where your work actually sits.",
   "paras": [
    "On one PC in your office, in one file. The dashboard is a web page that "
    "PC serves to the rest of your network, which is why it opens on a phone "
    "or a laptop without anything being installed on them.",
    "Nothing is uploaded. There is no third-party server holding your task "
    "history, no data-processing agreement to read, and nothing to leak if a "
    "vendor somewhere gets breached. Backing it up is copying a file.",
    "The trade for that is honest and worth stating: if the office PC dies "
    "and you have no copy, the history goes with it. The dashboard nags you "
    "about the export for exactly that reason.",
   ],
  }),

  ("links", {
   "h2": "Compared with what you are probably using now.",
   "items": [
    ("/alternatives/jira", "Instead of Jira",
     "For teams who are not shipping software"),
    ("/alternatives/trello", "Instead of Trello",
     "For when the cards keep going stale"),
    ("/alternatives/asana", "Instead of Asana",
     "For one office and one payment"),
    ("/alternatives/excel-and-whatsapp", "Instead of WhatsApp and Excel",
     "What it is really costing you"),
   ],
  }),
 ],

 "faq": [
  ("What exactly do I get for the money?",
   "A licence for your whole company — every PC in the office, with no seat "
   "counting — a year of updates, and email support answered by the person "
   "who wrote the software. After twelve months, updates and support are " +
   RENEW + " a year and optional; the licence itself does not expire and the "
   "software does not stop."),
  ("Is there a free plan?",
   "No, there is a free trial: thirty days, every feature, unlimited PCs, no "
   "card and nothing to cancel. We would rather have thirty honest days than "
   "a crippled free tier that tells you nothing about whether this fits."),
  ("Can I get a GST invoice?",
   "Yes — a proper invoice made out to your business, paid by UPI, bank "
   "transfer or card. The price is in rupees and does not move with the "
   "exchange rate."),
  ("Do we need a server, or IT people?",
   "Neither. The \"server\" is a program that runs on an ordinary Windows PC "
   "you already have — usually the manager's. If someone in the office can "
   "install a printer, they can install this. If you would rather not, we "
   "will do it for you over a remote session."),
  ("Can I get my data out later?",
   "Yes, at any time and without asking us. History exports to CSV, and the "
   "whole database exports as a JSON snapshot or as the SQLite file itself. "
   "There is no lock-in because there is nothing of yours on our side to "
   "lock."),
  ("What if the manager's PC dies?",
   "Install the server on another PC and import your last export. This is why "
   "the backup is one file and why the dashboard keeps asking you to put a "
   "copy somewhere else. The employee PCs find the new server by themselves."),
 ],
},


# =============================================================================
#  4. The comparison hub
# =============================================================================
{
 "slug": "alternatives/",
 "title": "WorkQueue compared with Jira, Trello, Asana and WhatsApp",
 "desc": "Honest comparisons between WorkQueue and the tools small Indian "
         "businesses usually try first — Jira, Trello, Asana, and an Excel "
         "sheet with a WhatsApp group. Each one includes the cases where you "
         "should stay exactly where you are.",
 "crumb": "How it compares",
 "blocks": [

  ("hero", {
   "eyebrow": "Comparisons",
   "h1": "How WorkQueue compares with what you are probably using.",
   "lede": "Every page below has a section on who should not switch, because "
           "a comparison that finds no reason to stay is an advertisement. "
           "WorkQueue is a narrow tool — it hands out jobs on one office "
           "network and times them. Here is where that beats a subscription, "
           "and where it plainly does not.",
   "b1": "Try it free for 30 days",
   "b2": "See what it does",
   "b2href": "/workqueue",
  }),

  ("links", {
   "h2": "The four comparisons.",
   "items": [
    ("/alternatives/jira", "WorkQueue vs Jira",
     "Simpler than an issue tracker built for software teams"),
    ("/alternatives/trello", "WorkQueue vs Trello",
     "Pushed to the screen instead of waiting on a board"),
    ("/alternatives/asana", "WorkQueue vs Asana",
     "One office, one payment, no per-person meter"),
    ("/alternatives/excel-and-whatsapp", "WorkQueue vs WhatsApp and Excel",
     "The system most small businesses actually run on"),
   ],
  }),

  ("table", {
   "h2": "The short version.",
   "lede": "The shape of the difference, before any particular product. Three "
           "of these rows go the other way.",
   "caption": "WorkQueue compared with a typical cloud task tool",
   "head": ["", "WorkQueue", "A typical cloud task tool"],
   "rows": VS_CLOUD,
   "note": "The other products are described in general terms on purpose. "
           "Their plans and prices change, and a page of ours going stale on "
           "somebody else's behalf would help nobody — check their current "
           "ones before you decide anything.",
   "band": True,
  }),

  ("prose", {
   "h2": "What we are not going to claim.",
   "paras": [
    "That the other tools are bad. They are not, and most of them are better "
    "resourced than this one by several orders of magnitude.",
    "The case for WorkQueue is narrow and it is about shape: if your work is "
    "jobs handed to people at PCs in one building, a product built for "
    "planning projects across the internet is going to ask you for a lot of "
    "structure you do not have, and charge you every month for holding it.",
    "If that is not your situation, one of the tools above is the right "
    "answer and we would rather you used it.",
   ],
   "band": True,
  }),
 ],

 "faq": [
  ("Can I import my tasks from another tool?",
   "Not automatically — there is no importer today, for any of them. Most "
   "teams switching are moving the day-to-day work rather than a history, and "
   "start clean. If you have a backlog you genuinely need to carry over, ask "
   "before you buy rather than after."),
  ("Can I run WorkQueue alongside what we already have?",
   "Yes, and during a thirty-day trial that is usually the sensible way to do "
   "it. Put one team or one kind of job through it and leave everything else "
   "where it is."),
  ("Why is there no page comparing it with the tool I use?",
   "Because we have only written the four we get asked about. If you are "
   "weighing it against something else, ask — the answer will be the same "
   "shape and it will be honest about where the other one wins."),
 ],
},


# =============================================================================
#  5. vs Jira
# =============================================================================
{
 "slug": "alternatives/jira",
 "title": "A simpler alternative to Jira for small teams — WorkQueue",
 "desc": "If Jira is more than your team needs, WorkQueue hands out jobs on "
         "your own office network and times them automatically. One payment "
         "for the whole company, free for 30 days — with an honest list of "
         "who should stay on Jira.",
 "parent": ("How it compares", "/alternatives/"),
 "crumb": "Jira",
 "blocks": [

  ("hero", {
   "eyebrow": "Jira alternative",
   "h1": "Looking for something simpler than Jira?",
   "lede": "Jira is an issue tracker built for software teams, and it is very "
           "good at being one. If you have landed here it is probably because "
           "you are not a software team — you are handing jobs to people in an "
           "office, and a tool with sprints, epics and workflow schemes is "
           "asking you to describe your work in a language you do not speak.",
   "b1": "Try WorkQueue free for 30 days",
   "b2": "See what it does",
   "b2href": "/workqueue",
  }),

  ("prose", {
   "eyebrow": "Said plainly",
   "h2": "If you searched for a free Jira board.",
   "paras": [
    "Then take it. Jira has a free plan for small teams, it is a real product "
    "and not a trap, and if a free board is what you need there is no argument "
    "here worth " + PRICE + " to you.",
    "**WorkQueue is not free.** It is free for thirty days, and then " + PRICE +
    " once for your whole company — no monthly bill, no per-person count, and "
    "no renewal you are obliged to pay. Whether that beats free comes down to "
    "two things.",
    "**Where the work lives.** A cloud plan keeps your task history on "
    "somebody else's servers, and free plans are the ones that get changed. "
    "WorkQueue keeps everything in one file on a PC in your office and cannot "
    "phone home, because it has nowhere to phone.",
    "**Who has to open something.** A board only works if people look at it. "
    "WorkQueue puts the job on a strip that is already on the employee's "
    "screen and starts timing it whether or not anybody looks.",
   ],
  }),

  ("table", {
   "h2": "Side by side.",
   "caption": "WorkQueue compared with Jira",
   "head": ["", "WorkQueue", "Jira"],
   "band": True,
   "rows": [
    ["Built for", "Handing jobs to people in an office",
     "Software teams tracking issues"],
    ["How you pay", ("yes", PRICE + " once, whole company"),
     "Per user per month, with a free tier for small teams"],
    ["Where the data lives", ("yes", "A PC in your office"),
     "Atlassian's cloud, or your own servers on their self-managed plan"],
    ["Setting it up", ("yes", "An afternoon"),
     "Longer, and usually somebody's actual job"],
    ["What an employee opens", ("yes", "Nothing"), "The web app"],
    ["Time tracking", ("yes", "Automatic, two timestamps a task"),
     "Manual, or an add-on"],
    ["Sprints, epics, workflows", ("no", "None"), ("yes", "All of it")],
    ["Custom fields and automation", ("no", "No"), ("yes", "Extensive")],
    ["With the internet down", ("yes", "Keeps working on the office network"),
     ("no", "Stops")],
    ["Mac and Linux employees", ("no", "Not yet"), ("yes", "Yes")],
   ],
   "note": "Jira's plans and limits change; check the current ones yourself. "
           "What is compared here is the shape of the two tools, which does "
           "not.",
  }),

  ("checks", {
   "h2": "Which way you should go.",
   "cols": [
    ("Stay on Jira if", [
     ("You ship software.",
      "Backlogs, releases, branches, code review — WorkQueue has none of it "
      "and is not going to."),
     ("You need real workflow states.",
      "WorkQueue has waiting, in progress and completed. That is the entire "
      "list and you cannot add to it."),
     ("Your team is spread across cities.",
      "WorkQueue can be joined to a private network, but Jira was born "
      "remote and it shows."),
     ("Anyone works on a Mac.",
      "The employee strip is Windows-only today."),
    ], True),
    ("Move to WorkQueue if", [
     ("You are paying per person",
      "for a fraction of the features, and the bill grows every time you "
      "hire."),
     ("Half the team never opens the board.",
      "The strip is docked into Windows and cannot be covered or ignored into "
      "the background."),
     ("You want to know how long jobs took",
      "without asking anybody to log their time against a ticket."),
     ("The work should not sit abroad.",
      "One file, one PC, your office, and a GST invoice in rupees."),
    ]),
   ],
  }),

  ("links", {
   "h2": "The rest of the comparison.",
   "items": [
    ("/alternatives/trello", "Compared with Trello",
     "The other board people try first"),
    ("/employee-task-tracker", "What the employee sees",
     "The strip, and what is never recorded"),
    ("/pricing", "The pricing",
     PRICE + " once, and the three-year arithmetic"),
   ],
  }),
 ],

 "faq": [
  ("Can I import my Jira issues?",
   "Not automatically — there is no importer today. Most teams making this "
   "move are switching how tomorrow's work gets handed out rather than "
   "carrying a history across, and start clean. If you have a backlog you "
   "genuinely need, ask before you buy rather than after."),
  ("Is WorkQueue cheaper than Jira's free plan?",
   "No, and nothing is. The comparison worth doing is against what you pay "
   "once the free plan stops fitting: ten people on a per-seat tool at " +
   SEAT + " a month is around ₹72,000 a year, every year. WorkQueue is " +
   PRICE + " once."),
  ("Does it do kanban?",
   "There is one board with three columns — waiting, in progress, and "
   "completed today. You cannot add a column or rename one. That is a real "
   "limitation, and it is also the point: there is no configuration meeting."),
  ("Could I self-host Jira instead?",
   "You can, on their self-managed plan, and if you have people to run it "
   "that is a legitimate answer to the same problem. WorkQueue is the version "
   "for an office where nobody's job is IT."),
  ("We are a software team but tiny. Which one?",
   "Jira, or one of the lighter issue trackers. WorkQueue has no concept of a "
   "branch, a release or a bug report, and pretending otherwise would waste "
   "your thirty days."),
 ],
},


# =============================================================================
#  6. vs Trello
# =============================================================================
{
 "slug": "alternatives/trello",
 "title": "A Trello alternative for teams who forget the board",
 "desc": "Trello is a board somebody has to look at. WorkQueue pushes each "
         "job onto a strip already on the employee's screen and times it "
         "automatically, on your own office network, for one payment. Free "
         "for 30 days.",
 "parent": ("How it compares", "/alternatives/"),
 "crumb": "Trello",
 "blocks": [

  ("hero", {
   "eyebrow": "Trello alternative",
   "h1": "If the Trello cards keep going stale.",
   "lede": "Trello is a lovely piece of software and its free plan is "
           "genuinely generous. The reason people go looking for an "
           "alternative is almost never Trello itself — it is that a board "
           "only works if everybody opens it, and on a shop floor or a service "
           "desk most people do not.",
   "b1": "Try WorkQueue free for 30 days",
   "b2": "See what it does",
   "b2href": "/workqueue",
  }),

  ("prose", {
   "eyebrow": "The actual difference",
   "h2": "Pushed, not published.",
   "paras": [
    "A card sits on a board waiting to be looked at. WorkQueue puts the job on "
    "a strip docked at the top of that person's screen — thirty-four pixels "
    "tall, which Windows will not let a maximised window cover. There is "
    "nothing to open and no notification to swipe away.",
    "And because the software knows the second the job landed there, it can "
    "time it. In Trello, timing is a Power-Up or a habit; here it is the pair "
    "of timestamps that every number on the reports is calculated from.",
    "The cost of that is rigidity. Three columns, fixed, and a task is a "
    "title, a description, a priority and the comment thread about it. If "
    "your work needs more structure inside a single card than that, Trello is "
    "the better tool and this page is not going to argue.",
   ],
  }),

  ("shots", {
   "items": [
    ("/assets/img/bar-strip-left.png", 500, 41,
     "Close-up of the left end of the employee strip: a green connected dot, "
     "the name Asha Rao, then a red diamond and the task title Reconcile the "
     "September invoice batch.",
     "**This is the whole employee interface.** No board, no login, no app."),
    ("/assets/img/bar-strip-chips.png", 560, 41,
     "Close-up of the right end of the employee strip: three colour-coded "
     "chips, one per open task, and a small menu arrow.",
     "**One chip per open job,** coloured by priority. Shown here at its real "
     "size on a 1920-pixel screen."),
   ],
  }),

  ("table", {
   "h2": "Side by side.",
   "caption": "WorkQueue compared with Trello",
   "head": ["", "WorkQueue", "Trello"],
   "band": True,
   "rows": [
    ["Built for", "Handing jobs to people at PCs",
     "Visual planning on shared boards"],
    ["The employee has to open it", ("yes", "No — it is already on screen"),
     ("no", "Yes")],
    ["Time tracking", ("yes", "Automatic"), "Manual, or a Power-Up"],
    ["How you pay", ("yes", PRICE + " once, whole company"),
     "Free tier, then per user per month"],
    ["Where the data lives", ("yes", "A PC in your office"),
     "Atlassian's cloud"],
    ["With the internet down", ("yes", "Keeps working on the office network"),
     ("no", "Little or nothing")],
    ["Columns you can design", ("no", "Three, fixed"),
     ("yes", "As many as you like")],
    ["Checklists, labels, attachments", ("no", "No"), ("yes", "Yes")],
    ["Phone app", ("no", "Dashboard in a browser; no strip on a phone"),
     ("yes", "Full app")],
   ],
   "note": "Trello's plans change; check the current ones yourself. The shape "
           "of the difference does not.",
  }),

  ("checks", {
   "h2": "Which way you should go.",
   "cols": [
    ("Stay on Trello if", [
     ("People do open the board.",
      "If the habit exists, it is a better board than this one and it costs "
      "you nothing."),
     ("You plan visually.",
      "Columns you design, cards you drag, labels you invent — none of that "
      "exists here."),
     ("Your team is on phones",
      "or spread across places, or on Macs. Trello is built for all three."),
     ("A job needs sub-structure.",
      "Checklists and attachments inside a card have no equivalent in "
      "WorkQueue."),
    ], True),
    ("Move to WorkQueue if", [
     ("The cards go stale.",
      "The commonest reason people leave a board: it stops being looked at "
      "and stops being true."),
     ("You want the timings.",
      "How long a job waited and how long it took, without asking anyone."),
     ("Everybody is at a Windows PC",
      "in one building, on one network, all day."),
     ("You would rather own it.",
      "One payment, and the record stays in your office."),
    ]),
   ],
  }),

  ("links", {
   "h2": "The rest of the comparison.",
   "items": [
    ("/alternatives/jira", "Compared with Jira",
     "Including who should stay on Jira"),
    ("/alternatives/asana", "Compared with Asana",
     "One office, one payment"),
    ("/work-tracker", "The timing side",
     "What the two timestamps measure"),
   ],
  }),
 ],

 "faq": [
  ("Can I import my Trello boards?",
   "Not automatically — there is no importer today. What most teams move is "
   "how tomorrow's jobs get handed out, not a history of finished cards."),
  ("Does a task have checklists or attachments?",
   "No. A task is a title, a description, a priority and the comment thread "
   "between the manager and the person doing it. That is deliberate, and it "
   "is a genuine reason to stay on Trello if your jobs need more."),
  ("Can I have more than three columns?",
   "No. Waiting, in progress, completed today. There is no setting for it."),
  ("Does it work on phones?",
   "The dashboard does — it is an ordinary web page on your office network, "
   "so any phone on the same Wi-Fi opens it. The employee strip is a Windows "
   "program and has no phone version."),
 ],
},


# =============================================================================
#  7. vs Asana
# =============================================================================
{
 "slug": "alternatives/asana",
 "title": "An Asana alternative that does not charge per person",
 "desc": "WorkQueue is a smaller and cheaper way to hand out work than Asana: "
         "one payment for the whole company, running on a PC in your own "
         "office, with every task timed automatically. Free for 30 days, GST "
         "invoice, no per-seat meter.",
 "parent": ("How it compares", "/alternatives/"),
 "crumb": "Asana",
 "blocks": [

  ("hero", {
   "eyebrow": "Asana alternative",
   "h1": "An Asana alternative for one office and one payment.",
   "lede": "Asana is built for coordinating projects across a company, mostly "
           "across the internet, mostly for people who live in a browser all "
           "day. If your team is twelve people in one building doing jobs that "
           "arrive one at a time, you are paying every month for most of a "
           "product nobody there opens.",
   "b1": "Try WorkQueue free for 30 days",
   "b2": "See what it does",
   "b2href": "/workqueue",
  }),

  ("prose", {
   "eyebrow": "The difference in one idea",
   "h2": "Projects, or jobs.",
   "paras": [
    "Asana's unit is a **project**: something you lay out, break down, assign "
    "across and then maintain. WorkQueue's unit is a **job somebody does "
    "today**. There is no plan to draw, no timeline to keep current and no "
    "dependency to model — you type what needs doing, pick whose screen it "
    "goes to, and it is timed from the second it lands there.",
    "That is a smaller idea and it does not stretch. If a real part of your "
    "work needs planning weeks ahead, WorkQueue will feel thin, and it is "
    "meant to.",
    "What you get for the smallness is that nobody has to be taught it. The "
    "employee's entire interface is a strip at the top of the screen with "
    "their current job on it and a Complete button.",
   ],
  }),

  ("table", {
   "h2": "Side by side.",
   "caption": "WorkQueue compared with Asana",
   "head": ["", "WorkQueue", "Asana"],
   "band": True,
   "rows": [
    ["Built for", "Jobs handed out in one office",
     "Projects coordinated across a company"],
    ["How you pay", ("yes", PRICE + " once, whole company"),
     "Per user per month, with a free tier for small teams"],
    ["Cost of hiring five more", ("yes", "Nothing"), "Five more seats"],
    ["Where the data lives", ("yes", "A PC in your office"), "Asana's cloud"],
    ["What an employee opens", ("yes", "Nothing"), "The web or phone app"],
    ["Time tracking", ("yes", "Automatic, two timestamps a task"),
     "On higher plans, or manual"],
    ["Timelines, portfolios, goals", ("no", "None"), ("yes", "All of it")],
    ["External guests and clients", ("no", "No — it is not on the internet"),
     ("yes", "Yes")],
    ["With the internet down", ("yes", "Keeps working on the office network"),
     ("no", "Stops")],
    ["Mac, Linux and phones", ("no", "Dashboard yes, strip Windows only"),
     ("yes", "Everywhere")],
   ],
   "note": "Asana's plans change; check the current ones yourself. What is "
           "compared here is the shape of the two tools.",
  }),

  ("checks", {
   "h2": "Which way you should go.",
   "cols": [
    ("Stay on Asana if", [
     ("You run projects, not jobs.",
      "Anything with phases, milestones and dependencies is the thing Asana "
      "is for."),
     ("People work from everywhere.",
      "Different cities, different devices, clients in the workspace — none "
      "of that is WorkQueue's shape."),
     ("You need reporting across teams.",
      "Portfolios and goals have no equivalent here at all."),
     ("Your team is not on Windows.",
      "The strip needs Windows 10 or 11 on each employee PC."),
    ], True),
    ("Move to WorkQueue if", [
     ("The per-seat bill is the problem.",
      "Ten people at " + SEAT + " a month is about ₹72,000 a year, every "
      "year, for a product most of them barely open."),
     ("Work arrives one job at a time.",
      "Orders, service calls, deliveries, batches — no plan required."),
     ("You want timings for free.",
      "Response time and work time on every job, with nobody logging hours."),
     ("Everyone is in one building.",
      "That is the case this is built for, and the only one it is good at."),
    ]),
   ],
  }),

  ("links", {
   "h2": "The rest of the comparison.",
   "items": [
    ("/alternatives/trello", "Compared with Trello",
     "The board people try first"),
    ("/task-management-software", "The buying case",
     "What renting the same thing costs over three years"),
    ("/pricing", "The pricing", PRICE + " once, for the whole company"),
   ],
  }),
 ],

 "faq": [
  ("Can I import from Asana?",
   "Not automatically — there is no importer today. Teams making this move "
   "are usually changing how tomorrow's work is handed out, not carrying a "
   "project archive across."),
  ("Can clients or contractors see a task?",
   "Only if they are on your network. The dashboard is not published to the "
   "internet — that is the whole design — so there is no guest link to share. "
   "People outside the office can be brought onto a private network during "
   "setup, and that is included, but it is your network they join, not a "
   "public workspace."),
  ("Does it have a phone app?",
   "The dashboard is a web page and opens on any phone on your office Wi-Fi. "
   "The employee strip is a Windows program and has no phone version, because "
   "it is docked into the desktop the way the taskbar is."),
  ("We are ten people. Is the maths really better?",
   "Over three years, on a " + SEAT + "-per-person figure, ten people pay "
   "about ₹1,08,000 for a per-seat tool against " + PRICE + " once here. "
   "Check it against your actual invoice rather than ours — and if most of "
   "those ten never open the tool, that is the more interesting number."),
 ],
},


# =============================================================================
#  8. vs the WhatsApp group and the Excel sheet
# =============================================================================
{
 "slug": "alternatives/excel-and-whatsapp",
 "title": "Tracking work in WhatsApp and Excel — what it costs",
 "desc": "Most small Indian businesses hand out work in a WhatsApp group and "
         "track it in an Excel sheet. It is free, it works, and here is "
         "exactly where it stops working — plus what WorkQueue does instead, "
         "for one payment.",
 "parent": ("How it compares", "/alternatives/"),
 "crumb": "WhatsApp and Excel",
 "blocks": [

  ("hero", {
   "eyebrow": "The real incumbent",
   "h1": "The WhatsApp group and the Excel sheet.",
   "lede": "This is what most small businesses in India actually run on, and "
           "it deserves more respect than software companies usually give it: "
           "it costs nothing, everybody already knows how, and it works. It "
           "stops working in four specific places. If none of them hurt yet, "
           "change nothing.",
   "b1": "Try WorkQueue free for 30 days",
   "b2": "See what it does",
   "b2href": "/workqueue",
  }),

  ("cards", {
   "h2": "The four places it breaks.",
   "cols": 2,
   "items": [
    ("Nobody can tell what is still open",
     "A message scrolls. Ten minutes of chat and this morning's job is above "
     "the fold. There is no list of what has not been done — only a history "
     "of what was said, in the order it was said."),
    ("Everything becomes \"I sent you that\"",
     "There is no record of when anything reached anyone, so a disagreement "
     "about whether a job was passed on has no answer. Everybody remembers it "
     "differently and everybody is sincere."),
    ("The sheet is always yesterday",
     "Somebody has to type into it, and they are doing it from memory at the "
     "end of the day. A duration typed on Friday about Tuesday is a number, "
     "not a fact."),
    ("It does not survive the person",
     "The system lives in one manager's head and one laptop's Downloads "
     "folder. When they are on leave, so is the system."),
   ],
  }),

  ("prose", {
   "h2": "What changes.",
   "band": True,
   "paras": [
    "The job is typed once, into a box, and pointed at one person. It appears "
    "on their screen a couple of seconds later and stays there until they "
    "press Complete. It cannot scroll away, and there is no group for it to "
    "get lost in.",
    "The two timestamps are taken by the software, so the sheet fills itself. "
    "History still exports to CSV — a lot of people want it in Excel anyway, "
    "and that is fine.",
    "And it is still your office. The file sits on a PC you own, the software "
    "never contacts us, and nobody's personal phone number is part of the "
    "system.",
   ],
  }),

  ("callout", {
   "h3": "Keep the WhatsApp group.",
   "paras": [
    "This replaces the part of it that hands out jobs. It does not replace the "
    "part where people talk to each other, and a tool that tried to would "
    "lose to WhatsApp on the first afternoon.",
   ],
  }),

  ("table", {
   "h2": "The cost of free.",
   "caption": "A WhatsApp group and a spreadsheet compared with WorkQueue",
   "head": ["", "WhatsApp and Excel", "WorkQueue"],
   "rows": [
    ["What you pay", ("yes", "Nothing"), PRICE + " once"],
    ["What it costs", ("no", "Somebody's evening, every evening"),
     "An afternoon to install"],
    ["What is still open", ("no", "Read back through the chat"),
     ("yes", "One column on a board")],
    ["When it was received", ("no", "Nobody knows"), ("yes", "To the second")],
    ["How long it took", ("no", "Whatever gets typed in"),
     ("yes", "Measured, not reported")],
    ["If the manager is on leave", ("no", "It stops"),
     ("yes", "It keeps running")],
    ["Where the record is", ("no", "A phone and somebody's laptop"),
     ("yes", "One file you can copy anywhere")],
    ["Personal phone numbers involved", ("no", "Everybody's"),
     ("yes", "None")],
   ],
  }),

  ("links", {
   "h2": "If that sounds like your office.",
   "items": [
    ("/employee-task-tracker", "What your team would see",
     "The strip, and what is never recorded"),
    ("/pricing", "What it costs", PRICE + " once, free for thirty days"),
    ("/india/", "Wherever you are",
     "A page for every state, in twelve languages"),
   ],
  }),
 ],

 "faq": [
  ("We are only six people. Is this overkill?",
   "Possibly. If everyone can see everyone and nothing gets lost, a group and "
   "a sheet is a perfectly good system and you should keep it. The trial is "
   "thirty days precisely so you can find out instead of arguing about it."),
  ("Can we keep using Excel?",
   "Yes. History exports to CSV whenever you want it, so whatever report you "
   "already build in a spreadsheet, you can keep building — from numbers "
   "nobody typed in by hand."),
  ("Do employees need smartphones?",
   "No, and that is one of the better reasons to move off a group. This runs "
   "on the office PCs people already work at. Nobody installs anything on "
   "their own phone, and nobody's personal number has to be in a work group."),
  ("What about people who are not at a PC?",
   "Then this is not for them. The strip needs a Windows PC that is switched "
   "on while they work — drivers, field staff and shop floors without screens "
   "are a real limitation and not something we can talk you around."),
  ("Is our data safer than in a WhatsApp group?",
   "It is somewhere different: one file on a PC in your office, rather than "
   "spread across everybody's phone backups. Whether that is safer depends "
   "entirely on whether you keep a copy of it — which is why the dashboard "
   "keeps asking you to export one."),
 ],
},

]
