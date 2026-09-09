"""Drive headless Chrome over CDP and save exact 1920x1080 PNGs of the dashboard.

Deterministic: no window management, nothing touches the desktop, and the
browser profile is a throwaway.
"""
import base64, json, os, subprocess, sys, time
import requests
import websocket

PORT = 9333
URL = "http://127.0.0.1:8420/"
COOKIE = sys.argv[1]
OUT = sys.argv[2]
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE = os.path.join(os.path.dirname(OUT), "chrome-profile-" + str(int(time.time())))

os.makedirs(OUT, exist_ok=True)

proc = subprocess.Popen([
    CHROME, "--headless=new", f"--remote-debugging-port={PORT}",
    f"--user-data-dir={PROFILE}", "--no-first-run", "--no-default-browser-check",
    "--disable-extensions", "--hide-scrollbars", "--remote-allow-origins=*", "--force-device-scale-factor=1",
    "--window-size=1920,1080", "about:blank",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# wait for the debugging endpoint
ws_url = None
for _ in range(60):
    try:
        for t in requests.get(f"http://127.0.0.1:{PORT}/json", timeout=1).json():
            if t.get("type") == "page":
                ws_url = t["webSocketDebuggerUrl"]
                break
        if ws_url:
            break
    except Exception:
        pass
    time.sleep(0.5)
if not ws_url:
    proc.kill()
    sys.exit("chrome did not expose a debugging target")

ws = websocket.create_connection(ws_url, timeout=30)
_id = [0]

def cmd(method, **params):
    _id[0] += 1
    ws.send(json.dumps({"id": _id[0], "method": method, "params": params}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == _id[0]:
            if "error" in msg:
                raise RuntimeError(f"{method}: {msg['error']}")
            return msg.get("result", {})

def js(expr):
    r = cmd("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
    return r.get("result", {}).get("value")

cmd("Page.enable")
cmd("Runtime.enable")
cmd("Network.enable")
cmd("Emulation.setDeviceMetricsOverride",
    width=1920, height=1080, deviceScaleFactor=1, mobile=False)

name, value = COOKIE.split("=", 1)
cmd("Network.setCookie", name=name, value=value, domain="127.0.0.1", path="/")

def goto(url):
    cmd("Page.navigate", url=url)
    for _ in range(80):
        if js("document.readyState") == "complete":
            break
        time.sleep(0.25)
    time.sleep(2.5)          # let the first poll paint

def shot(fname, full=False):
    params = {"format": "png"}
    if full:
        m = cmd("Page.getLayoutMetrics")["contentSize"]
        params["clip"] = {"x": 0, "y": 0, "width": m["width"],
                          "height": m["height"], "scale": 1}
        params["captureBeyondViewport"] = True
    data = cmd("Page.captureScreenshot", **params)["data"]
    path = os.path.join(OUT, fname)
    with open(path, "wb") as f:
        f.write(base64.b64decode(data))
    print(f"  {fname}  {os.path.getsize(path)//1024} KB")

goto(URL)
if js("!!document.querySelector('#login, .login')") and js("document.body.innerText.includes('Password')"):
    print("NOT AUTHENTICATED - cookie rejected")

print("capturing:")

# --- Board ----------------------------------------------------------------
js("document.querySelector('[data-view=\"board\"]').click()"); time.sleep(2)
shot("board.png")

# --- Analytics, light then dark ------------------------------------------
js("document.querySelector('[data-view=\"analytics\"]').click()"); time.sleep(3.5)
shot("analytics.png")
shot("analytics-full.png", full=True)

js("document.documentElement.dataset.theme='dark';"
   "localStorage.setItem('wq.theme','dark');"
   "document.querySelector('#theme-toggle').click()")
time.sleep(1)
js("if(document.documentElement.dataset.theme!=='dark'){document.querySelector('#theme-toggle').click()}")
time.sleep(3)
shot("analytics-dark.png")

# back to light
js("if(document.documentElement.dataset.theme==='dark'){document.querySelector('#theme-toggle').click()}")
time.sleep(2.5)

# --- Calendar -------------------------------------------------------------
js("document.querySelector('[data-view=\"calendar\"]').click()"); time.sleep(3)
shot("calendar.png")

# --- History --------------------------------------------------------------
js("document.querySelector('[data-view=\"history\"]').click()"); time.sleep(3)
shot("history.png")

# --- Machines -------------------------------------------------------------
js("document.querySelector('[data-view=\"machines\"]').click()"); time.sleep(2.5)
shot("machines.png")

# --- Task drawer ----------------------------------------------------------
js("document.querySelector('[data-view=\"board\"]').click()"); time.sleep(2.5)
opened = js("""(() => {
  const titles = [...document.querySelectorAll('.card .title')];
  const el = titles.find(e => e.textContent.includes('Reconcile')) || titles[0];
  if (el) { el.click(); return el.textContent.trim(); }
  return null;
})()""")
time.sleep(2.5)
print("  drawer opened on:", opened)
shot("task-drawer.png")

ws.close()
proc.terminate()
print("done")
