# Regenerating the product screenshots

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
