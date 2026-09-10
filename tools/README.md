# Regenerating the product screenshots and the demo film

The images in `public/assets/img/` are real screenshots of WorkQueue running against a
throwaway database full of realistic demo data. When the UI changes, regenerate
them rather than editing the old ones — a stale screenshot on a sales page is
worse than no screenshot.

Nothing here touches a real install: the server runs against
`WORKQUEUE_DATA_DIR` in a temp folder, and the browser is a headless Chrome with
its own throwaway profile.

## The three steps

Run these from the WorkQueue repo (`D:\MyWorkUpdate`), using its virtualenv.
Set `WORKQUEUE_REPO` first if the repo lives somewhere else.

```powershell
$TOOLS = "D:\BoneysNewWebsiteProcessAutoamation\tools"
$DEMO  = "$env:TEMP\wq-demo"
cd D:\MyWorkUpdate
```

**1. Seed a demo database.** 220 tasks over 32 days across five people, plus a
board worth photographing: five waiting, three in progress, a day of
completions, and a comment thread.

```powershell
.\.venv\Scripts\python.exe $TOOLS\seed_demo.py "$DEMO\data"
```

It sets the admin password to `demo1234`. That password only ever exists in
this throwaway database.

**2. Start the server against it.**

```powershell
$env:WORKQUEUE_DATA_DIR = "$DEMO\data"
.\.venv\Scripts\python.exe -m server.app
```

Leave it running in that window.

**3. Take the shots.** In a second window, log in for a session cookie and hand
it to the capture script:

```powershell
cd D:\MyWorkUpdate
$r = Invoke-WebRequest -Uri http://127.0.0.1:8420/api/admin/login -Method POST `
       -ContentType application/json -Body '{"password":"demo1234"}' -SessionVariable s
$cookie = "wq_admin=" + $s.Cookies.GetCookies("http://127.0.0.1:8420")["wq_admin"].Value
.\.venv\Scripts\python.exe $TOOLS\shoot.py $cookie "$DEMO\shots"
```

You get exact 1920x1080 PNGs in `$DEMO\shots`: `board`, `analytics`,
`analytics-dark`, `analytics-full`, `calendar`, `history`, `machines`,
`task-drawer`. Copy the ones you want into `public/assets/img/` as `dashboard-*.png`.

Stop the server when you are done, and delete `$DEMO`.

## 4. The demo film on the home page

`public/assets/video/workqueue-demo.mp4` is a real recording, not an animation:
the dashboard captured out of the browser, the employee strip captured off the
top of this Windows desktop, cut together afterwards.

**It needs a real bar running on this PC.** The strip in the film is a genuine
one. A bar with no server finds the demo server by itself within a minute or
so; check the **Machines** tab for a row with this computer's hostname before
you start.

With the demo server from step 2 still running:

```powershell
$SHOOT = "$DEMO\shoot"
cd D:\MyWorkUpdate
.\.venv\Scripts\python.exe $TOOLS
ecord_demo.py $SHOOT
```

It takes about 100 seconds and you should leave the machine alone while it
runs - it is watching the top of your screen. What it does:

1. Names the bar on this PC **Asha Rao** and empties its queue, so the strip
   visibly changes when the task lands, and deletes the seeded copies of the
   task title the film is about - the seeder reuses twenty titles, and a card
   that is on the board three times is a card nobody can follow.
2. Drives the dashboard with real mouse and keyboard events in an off-screen
   Chrome window - types the task, picks the person, presses Assign.
3. Captures both streams at once, timestamped to the same clock.
4. Completes the task through the employee endpoint - the same call the bar
   makes when Complete is pressed - and records the board catching up.
5. Visits Analytics and History.
6. **Puts the bar back**: deletes the demo task and clears the name, so the
   strip returns to "Unnamed PC - No tasks available".

Then cut it:

```powershell
python $TOOLS\compose_demo.py $SHOOT   # needs pillow, numpy, imageio-ffmpeg
copy $SHOOT\workqueue-demo.mp4 publicssetsideocopy $SHOOT\demo-poster.jpg    publicssets\img```

That also writes the score and muxes it in. `score_demo.py` synthesises the
music from sine partials - nothing is sampled and nothing is licensed, so the
file the site publishes is ours to publish. Run it on its own if you want to
hear the music by itself:

```powershell
python $TOOLS\score_demo.py $SHOOT\score.wav
```

That writes a 1920x1080 H.264 file of about 10 MB and its poster frame. The
render takes four or five minutes; to check a shot's framing without waiting,
ask for a single frame instead:

```powershell
python $TOOLS\compose_demo.py $SHOOT still 7 25 36 58
```

**The shot list is the top half of `compose_demo.py`** - one entry per shot,
each naming the seconds of the recording it plays, the camera (centre and width,
in the dashboard's CSS pixels) at the start and end of the move, and the caption.
Reframing a shot is two numbers. If you change the *timing* of the film, update
the five chapter marks in `FILM_CHAPTERS` in `public/assets/js/site.js`, or the
buttons under the video will seek to the wrong places.

### If the film comes out wrong

- **The strip never changes** - no bar on this PC had registered, so the task
  went to a seeded machine that does not exist. Check the Machines tab first.
- **The strip capture is of something else** - something was covering the top
  of the screen. Windows reserves that band for the AppBar, so this should not
  happen; if it does, nothing else can have been dragged up there.
- **The typing looks like a slideshow** - the capture rate fell. It runs at
  about six frames a second; close anything heavy and re-record.

---

## The employee strip and panel

These two cannot be captured headlessly — the strip is a native Windows AppBar,
not a web page. They were taken by hand:

1. With the demo server running, let a real bar find it (it discovers the server
   on the LAN by itself) or start one:
   `$env:WORKQUEUE_CLIENT_DIR="$DEMO\client"; .\.venv\Scripts\python.exe -m client.main`
2. In the dashboard, give that machine a name on the **Machines** tab.
3. Assign it two or three tasks of different priorities.
4. Screenshot the top 41 physical pixels of the screen for the strip. Windows
   reserves that band for the AppBar, so nothing can overlap it — an ordinary
   region grab is safe there.
5. Click the task title on the strip to open the panel, and grab that region.

**Afterwards, put the bar back:** delete those demo tasks and clear the
machine's display name, so the bar returns to "Unnamed PC · No tasks available"
before you stop the server.

### The two strip close-ups

The strip is 1920x41 — a 47:1 ribbon. Shown at page width its text is about six
pixels tall and nobody can read it, so the site also carries two crops of the
same capture, displayed at roughly 1:1:

| File (in `public/assets/img/`) | Crop from `bar-strip.png` |
|---|---|
| `bar-strip-left.png` | x 0, width 500 — the dot, the name, the current task |
| `bar-strip-chips.png` | x 1360, width 560 — the priority chips and the menu arrow |

Both are full height (41). Re-cut them after any new strip capture — the site's
copy describes what is in them, so check the captions still match. Any image
editor will do; the exact numbers above are what the current crops used.

## If the shots come out wrong

- **A blank or login page** — the cookie expired (12 h) or the server restarted.
  Get a fresh one.
- **The drawer shot shows only the board** — the selector in `shoot.py` is
  `.card .title`. If the dashboard markup changed, update it.
- **Chrome will not start** — a previous headless run is still holding the
  profile. `shoot.py` uses a timestamped profile directory to avoid this, but
  kill leftover `chrome.exe` processes whose command line mentions your temp
  folder if it happens.

---

# The English-only landing pages

`tools/content/pages.py` holds eight more pages, rendered by `build_landing()`
in the same builder. They target what people actually type into Google —
"employee task tracker", "work tracker", "task management software",
"something simpler than Jira" — which is not how the rest of the site is
written.

| | |
|---|---|
| The pages | `/employee-task-tracker`, `/work-tracker`, `/task-management-software`, `/alternatives/` + jira, trello, asana, excel-and-whatsapp |
| Copy | `tools/content/pages.py` — data only |
| Renderer | `build_landing()` and the `b_*` block functions in `build_i18n.py` |
| Languages | English, and only English |

A page is a list of `(kind, dict)` blocks — `hero`, `prose`, `cards`,
`checks`, `steps`, `spec`, `table`, `shots`, `links`, `callout` — each
rendered into a component the site already had, so nothing new lands in the
CSS. The block vocabulary is documented in the comment above `RICH` in
`build_i18n.py`. Inside any string, `**bold**` and `[text](/href)` work and
nothing else does.

**Adding one:** a dict in `PAGES`, then rebuild. The `hreflang` set, the
sitemap entry, the breadcrumb, the FAQ section, the closing CTA and the
JSON-LD graph all come out of the slug and the copy.

**What must not slip:**

- Each page is a *different argument*, not the same argument with the keyword
  changed. Eight variations on one page is a doorway set, and it reads like
  one long before Google decides so.
- Every comparison carries a "stay where you are if" section, and three rows
  of every comparison table go against WorkQueue. That is the reason anyone
  believes the other rows.
- Nothing quantitative about somebody else's product. Their prices and plan
  limits change; ours would go stale and be wrong on their behalf.

---

# The generated pages: languages and states

`public/` is not all hand-written any more. 121 of its 125 pages come out of
`tools/build_i18n.py`, because eleven translations of four pages plus a page
for every state and union territory is not something anybody keeps in step by
hand. What is generated is still plain static HTML — open
`public/ta/pricing.html` and it is exactly what a reader is served.

```powershell
python tools\build_i18n.py           # write everything
python tools\build_i18n.py --check   # fail if public/ is out of date
```

| | |
|---|---|
| Hand-written, canonical | `public/index.html`, `workqueue.html`, `pricing.html`, `contact.html`, `404.html` |
| Generated | `public/<lang>/*`, `public/india/*`, `public/<lang>/india/*`, `sitemap.xml`, `robots.txt` |
| Languages | `tools/content/langs.py` — twelve, English plus eleven |
| States | `tools/content/states.py` — 28 states, 8 union territories |
| Copy | `tools/content/strings/<lang>.py` — 434 keys each, `en.py` is the reference |

**The four English pages are still written by hand.** The builder only replaces
what sits between the `<!-- qw:hreflang -->`, `<!-- qw:langpicker -->` and
`<!-- qw:jsonld -->` markers in them, so the machine-maintained parts stay in
step while the prose does not get regenerated over. Delete a marker and the
build stops with an error rather than silently dropping the block.

## Which pages exist

Every core page exists in all twelve languages. A **state page** exists in
English always, and in that state's own language when the two differ — so
Maharashtra has `/india/maharashtra` and `/mr/india/maharashtra`, while Goa,
whose businesses work in English, has only the English one. The `hreflang`
block lists only the versions that really exist; the language picker still
offers all twelve, sending a reader with no version of that page to their own
language's `/india` hub.

## Adding a language

1. A row in `tools/content/langs.py`.
2. A `tools/content/strings/<code>.py` with the same 434 keys as `en.py`.
3. `python tools\build_i18n.py`.

The build refuses to run if a key is missing, so a half-finished translation
cannot ship a page with a hole in it.

## Adding a state

One dict in `tools/content/states.py`, then rebuild. `lang` is the language
that state's own page is written in — leave it `en` where the local language
is not one of the eleven, because a page in a language nobody there reads is
worse than an honest English one. `trade` is what stops the page being a
find-and-replace of the last one, so keep it true.

## The placeholders and grammar

`{state}`, `{hub}`, `{cities}`, `{lang}` are filled in at build time, which is
a trap in most of these languages: a case ending cannot simply be appended to
a proper noun. Three different solutions are in use, and a new language needs
to pick one:

- **Free postposition** (Hindi, Punjabi) — `{state} में` is already correct.
- **Bound suffix** (Kannada, Telugu, Odia, Assamese, Gujarati) — written with
  no space, `{state}ದಲ್ಲಿ`, so it joins the name.
- **Head noun carries the case** (Marathi, Bengali) — `{state} राज्यातील`,
  because महाराष्ट्र + मध्ये is not महाराष्ट्रमध्ये.
- **No inflection at all** (Tamil, Malayalam) — the ending changes with the
  noun (தமிழ்நாடு → தமிழ்நாட்டில்), so the templates use apposition or a
  compound and never inflect the placeholder.

Read a generated `<h1>` in the language before believing a new template.

## Checking it

```powershell
python tools\build_i18n.py
python tools\audit_seo.py              # no browser needed
python tools\preview.py 8021           # then, in another window:
python tools\check_console.py 8021
```

`audit_seo.py` walks all 125 pages: one `<h1>`, sane title and description
lengths, a canonical that matches where the file is, every internal link
resolving, `hreflang` sets that are self-referential and reciprocal, and a
sitemap that agrees with the tree. `check_console.py` drives headless Chrome
over one page of every kind and asserts zero console messages — the rule the
site has always held itself to, now across twelve languages.
