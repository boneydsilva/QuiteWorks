"""Record the real WorkQueue workflow, for the film on the home page.

    python tools/record_demo.py "%TEMP%\wq-demo\shoot"

Needs the demo server already running against a seeded database (steps 1 and 2
of this folder's README) and a real WorkQueue bar running on this PC - the film
shows a genuine strip, so there has to be one on screen.

Two streams, one clock:
  * the admin dashboard, driven with real mouse and keyboard events in headless
    Chrome and captured with CDP's screencast
  * the employee strip, grabbed from the top 44 pixels of this screen - the band
    Windows reserves for an AppBar, which is where the real bar is running

Frames land in frames/ as JPEGs named with the millisecond they were taken, and
the script prints a beat list so compose.py knows what was happening when.
"""
import base64, ctypes, json, os, shutil, socket, subprocess, sys, threading, time
import requests, websocket
from PIL import ImageGrab

if len(sys.argv) < 2:
    sys.exit(__doc__)
OUT = os.path.abspath(sys.argv[1])
FRAMES = os.path.join(OUT, "frames")
os.makedirs(OUT, exist_ok=True)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9340
SERVER = "http://127.0.0.1:8420"
VIEW_W, VIEW_H = 1920, 936
SCALE = 2
BAND_H = 44

TITLE = "Reconcile the September invoice batch"
DESC = "Cross-check every total against the bank export before it goes to accounts."
STAR = "Asha Rao"          # the name the bar on this PC wears for the take

for d in (FRAMES, os.path.join(FRAMES, "dash"), os.path.join(FRAMES, "band")):
    shutil.rmtree(d, ignore_errors=True)
for d in (FRAMES, os.path.join(FRAMES, "dash"), os.path.join(FRAMES, "band")):
    os.makedirs(d, exist_ok=True)

# --- a session cookie for the dashboard ------------------------------------

S = requests.Session()
S.post(SERVER + "/api/admin/login", json={"password": "demo1234"}, timeout=5).raise_for_status()
COOKIE = S.cookies.get("wq_admin")
if not COOKIE:
    sys.exit("no admin cookie")

def api(method, path, **kw):
    r = S.request(method, SERVER + path, timeout=10, **kw)
    r.raise_for_status()
    return r.json() if r.content else {}

# The bar on this PC is the one the camera can see, so that is the machine the
# task gets assigned to. It registers itself by hostname.
here = socket.gethostname().lower()
machines = api("GET", "/api/admin/machines")["machines"]
mine = [m for m in machines if m["hostname"].lower() == here]
if not mine:
    sys.exit("no bar from this PC has registered with the demo server yet - "
             "start one, or wait for the running one to discover the server")
BAR = mine[0]["id"]
WAS_NAMED = mine[0]["display_name"]

# The seeded database reuses twenty task titles, so the one the film is about
# already exists several times over. A card the viewer cannot follow is worse
# than no card. Clear those, and empty this bar's queue so the strip visibly
# changes when the task lands on it.
cleared = 0
for t in api("GET", "/api/admin/tasks", params={"machine_id": BAR, "limit": 500})["tasks"]:
    api("DELETE", f"/api/admin/tasks/{t['id']}"); cleared += 1
for t in api("GET", "/api/admin/tasks", params={"q": TITLE, "limit": 500})["tasks"]:
    if t["title"] == TITLE:
        api("DELETE", f"/api/admin/tasks/{t['id']}"); cleared += 1
api("PATCH", f"/api/admin/machines/{BAR}", json={"display_name": STAR})
print(f"machine {BAR} is {STAR} for the take; {cleared} old tasks cleared")
print("waiting for the bar to show an empty queue...")
time.sleep(8)

# --- chrome ----------------------------------------------------------------

proc = subprocess.Popen([
    CHROME, f"--remote-debugging-port={PORT}",
    f"--user-data-dir={os.path.join(OUT, 'chrome-rec')}", "--no-first-run",
    "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
    "--remote-allow-origins=*", f"--force-device-scale-factor={SCALE}",
    f"--window-size={VIEW_W},{VIEW_H}",
    "--window-position=-2400,0",
    "--disable-features=CalculateNativeWinOcclusion",
    "--disable-backgrounding-occluded-windows", "--disable-renderer-backgrounding",
    "about:blank",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

ws_url = None
for _ in range(60):
    try:
        for t in requests.get(f"http://127.0.0.1:{PORT}/json", timeout=1).json():
            if t.get("type") == "page":
                ws_url = t["webSocketDebuggerUrl"]; break
        if ws_url: break
    except Exception:
        pass
    time.sleep(0.5)
if not ws_url:
    proc.kill(); sys.exit("chrome did not start")

ws = websocket.create_connection(ws_url, timeout=60)
_id = [0]
_lock = threading.Lock()
_waiting = {}
recording = threading.Event()
stop = threading.Event()
dash_count = [0]

def reader():
    while not stop.is_set():
        try:
            msg = json.loads(ws.recv())
        except Exception:
            return
        if "id" in msg:
            slot = _waiting.get(msg["id"])
            if slot:
                slot[0] = msg
                slot[1].set()
        elif msg.get("method") == "Page.screencastFrame":
            p = msg["params"]
            send("Page.screencastFrameAck", sessionId=p["sessionId"])
            if recording.is_set():
                ts = int(time.time() * 1000)
                with open(os.path.join(FRAMES, "dash", f"{ts}.jpg"), "wb") as f:
                    f.write(base64.b64decode(p["data"]))
                dash_count[0] += 1

def send(method, **params):
    """Fire and forget - used for the screencast acks."""
    with _lock:
        _id[0] += 1
        ws.send(json.dumps({"id": _id[0], "method": method, "params": params}))

def cmd(method, **params):
    ev = threading.Event()
    with _lock:
        _id[0] += 1
        mid = _id[0]
        _waiting[mid] = [None, ev]
        ws.send(json.dumps({"id": mid, "method": method, "params": params}))
    if not ev.wait(30):
        raise RuntimeError(method + ": timed out")
    msg = _waiting.pop(mid)[0]
    if "error" in msg:
        raise RuntimeError(f"{method}: {msg['error']}")
    return msg.get("result", {})

def js(expr):
    r = cmd("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
    if "exceptionDetails" in r:
        raise RuntimeError(json.dumps(r["exceptionDetails"])[:300])
    return r.get("result", {}).get("value")

threading.Thread(target=reader, daemon=True).start()

# --- the strip, straight off the screen ------------------------------------

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
SCREEN_W = user32.GetSystemMetrics(0)

def band_grabber():
    while not stop.is_set():
        if recording.is_set():
            try:
                im = ImageGrab.grab(bbox=(0, 0, SCREEN_W, BAND_H), all_screens=False)
                im.convert("RGB").save(
                    os.path.join(FRAMES, "band", f"{int(time.time()*1000)}.jpg"),
                    quality=92)
            except Exception:
                pass
        time.sleep(0.1)

threading.Thread(target=band_grabber, daemon=True).start()

# --- the cursor track ------------------------------------------------------
# Every mouse event is real; this list is only so compose.py can draw a pointer
# where the pointer actually was.

cursor = []
pos = [VIEW_W // 2, VIEW_H - 80]

def mouse(x, y, kind="mouseMoved", button="none", clicks=0):
    fire = send if kind == "mouseMoved" else cmd
    fire("Input.dispatchMouseEvent", type=kind, x=int(x), y=int(y),
         button=button, clickCount=clicks)
    pos[0], pos[1] = int(x), int(y)
    cursor.append({"t": time.time(), "x": int(x), "y": int(y),
                   "click": kind == "mousePressed"})

def glide(x, y, steps=26, seconds=0.5):
    x0, y0 = pos
    for i in range(1, steps + 1):
        k = i / steps
        k = k * k * (3 - 2 * k)                      # ease in and out
        mouse(x0 + (x - x0) * k, y0 + (y - y0) * k)
        time.sleep(seconds / steps)

def box(selector):
    r = js("(()=>{const e=document.querySelector(%s);const r=e.getBoundingClientRect();"
           "return JSON.stringify({x:r.x+r.width/2,y:r.y+r.height/2})})()" % json.dumps(selector))
    return json.loads(r)

def click(selector, pause=0.35):
    b = box(selector)
    glide(b["x"], b["y"])
    time.sleep(0.18)
    mouse(b["x"], b["y"], "mousePressed", "left", 1)
    time.sleep(0.09)
    mouse(b["x"], b["y"], "mouseReleased", "left", 1)
    time.sleep(pause)

def type_text(text, per_char=0.052):
    for ch in text:
        send("Input.insertText", text=ch)
        # A human types unevenly; a metronome reads as a machine.
        time.sleep(per_char * (0.72 if ch == " " else 1.0))

# --- beats -----------------------------------------------------------------

beats = []
T0 = [0.0]

def beat(label):
    beats.append({"t": time.time(), "label": label})
    print(f"  {time.time() - T0[0]:6.1f}s  {label}")

# --- go --------------------------------------------------------------------

cmd("Page.enable"); cmd("Runtime.enable"); cmd("Network.enable")
cmd("Emulation.setDeviceMetricsOverride", width=VIEW_W, height=VIEW_H,
    deviceScaleFactor=SCALE, mobile=False)
cmd("Network.setCookie", name="wq_admin", value=COOKIE, domain="127.0.0.1", path="/")
cmd("Page.navigate", url=SERVER + "/")
for _ in range(80):
    if js("document.readyState") == "complete":
        break
    time.sleep(0.25)
time.sleep(3)
if js("!!document.querySelector('#gate-password') && !document.querySelector('#gate-password').closest('[hidden]')"):
    print("WARNING: still on the login gate")

js("document.querySelector('[data-view=\"board\"]').click()")
time.sleep(2.5)

cmd("Page.startScreencast", format="jpeg", quality=80,
    maxWidth=VIEW_W * SCALE, maxHeight=VIEW_H * SCALE, everyNthFrame=1)
recording.set()
T0[0] = time.time()
beat("start")
time.sleep(2.0)

beat("compose")
click("#t-title")
type_text(TITLE, 0.11)
time.sleep(0.4)
click("#t-desc")
type_text(DESC, 0.055)
time.sleep(0.5)

# A native select popup does not render in a screencast, so the value is set
# the way the keyboard would set it - the field visibly changes to Urgent.
js("(()=>{const s=document.querySelector('#t-priority');s.value='urgent';"
   "s.dispatchEvent(new Event('change',{bubbles:true}))})()")
time.sleep(0.8)

beat("pick")
click("#t-machines-toggle", 0.6)
click('#t-machines .chip[data-id="%d"]' % BAR, 0.6)
click("#t-machines-toggle", 0.5)
time.sleep(0.6)

beat("assign")
click("#task-submit", 0.4)

# The board post lands straight away; the bar picks it up on its own 5s poll
# and the board shows the move on its next poll after that.
time.sleep(7.0)
beat("delivered")
time.sleep(10.0)

beat("working")
time.sleep(10.0)

# The employee's Complete. This is the exact call the bar makes when the button
# on the strip is pressed - same endpoint, same idempotency key.
tasks = requests.get(SERVER + "/api/tasks", params={"machine_id": BAR}, timeout=5).json()
mine = [t for t in tasks["tasks"] if t["title"] == TITLE and t["status"] != "completed"]
if mine:
    import uuid
    requests.post(SERVER + f"/api/tasks/{mine[0]['id']}/complete",
                  json={"machine_id": BAR, "client_action_id": str(uuid.uuid4())},
                  timeout=5).raise_for_status()
    beat("complete")
else:
    beat("complete (task not found)")
time.sleep(8.0)

beat("analytics")
click("#tab-analytics", 0.4)
time.sleep(7.0)

beat("history")
click("#tab-history", 0.4)
time.sleep(6.0)

beat("end")
time.sleep(1.0)

recording.clear()
cmd("Page.stopScreencast")
T1 = time.time()
stop.set()
time.sleep(0.4)

meta = {
    "t0": T0[0], "t1": T1, "beats": beats, "cursor": cursor,
    "view": [VIEW_W, VIEW_H], "scale": SCALE, "band": [SCREEN_W, BAND_H],
}
with open(os.path.join(OUT, "recording.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f)

# Put the real bar back the way it was found - no demo tasks, no demo name.
for t in api("GET", "/api/admin/tasks", params={"machine_id": BAR, "limit": 500})["tasks"]:
    api("DELETE", f"/api/admin/tasks/{t['id']}")
api("PATCH", f"/api/admin/machines/{BAR}", json={"display_name": WAS_NAMED or ""})
print("the bar on this PC has been put back to", WAS_NAMED or "unnamed, with no tasks")

print(f"\ndashboard frames: {dash_count[0]}")
print("band frames:     ", len(os.listdir(os.path.join(FRAMES, 'band'))))
print(f"duration:         {T1 - T0[0]:.1f}s")
try:
    ws.close()
except Exception:
    pass
proc.kill()
