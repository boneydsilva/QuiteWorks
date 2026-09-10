# -*- coding: utf-8 -*-
"""Load a page of every kind in headless Chrome and assert zero console output.

    python tools\\preview.py 8021        # in one terminal
    python tools\\check_console.py 8021  # in another

One of each: the English core pages, every language's home, a full set of
Hindi pages, the India hub, an English state page, several native state
pages, and a 404. For each it also asserts that the language picker really
carries twelve languages, that the theme toggle and the JSON-LD survived,
that there is exactly one <h1> with text in it, and that the page does not
scroll sideways.

A fresh tab and a fresh CDP socket per page: reusing one socket across
navigations is faster and silently drops messages.

Needs `pip install requests websocket-client` and Chrome at the path below.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

import requests
import websocket

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TEMP = os.path.join(tempfile.gettempdir(), "quietworks-console-check")
PORT = sys.argv[1] if len(sys.argv) > 1 else "8000"
BASE = "http://localhost:%s" % PORT
DEV = "http://127.0.0.1:9333"

PAGES = [
    "/", "/workqueue", "/pricing", "/contact", "/india/",
    "/hi/", "/hi/workqueue", "/hi/pricing", "/hi/contact", "/hi/india/",
    "/mr/", "/bn/", "/ta/", "/te/", "/kn/", "/ml/", "/gu/", "/pa/", "/or/", "/as/",
    "/india/maharashtra", "/india/tamil-nadu", "/india/goa",
    "/india/dadra-and-nagar-haveli-and-daman-and-diu",
    "/mr/india/maharashtra", "/ta/india/tamil-nadu", "/as/india/assam",
    "/hi/india/uttar-pradesh", "/ml/india/lakshadweep",
    # The English-only landing pages: one of each shape.
    "/employee-task-tracker", "/work-tracker", "/task-management-software",
    "/alternatives/", "/alternatives/jira", "/alternatives/excel-and-whatsapp",
    "/nope-this-is-a-404",
]

PROBE = """
  (() => ({
    lang: document.documentElement.lang,
    title: document.title,
    h1: (document.querySelector('h1')||{}).textContent.trim(),
    h1count: document.querySelectorAll('h1').length,
    picker: document.querySelectorAll('[data-lang-pick] a[data-lang]').length,
    theme: !!document.querySelector('.theme-toggle'),
    alts: document.querySelectorAll('link[rel=alternate]').length,
    ld: document.querySelectorAll('script[type="application/ld+json"]').length,
    scrollX: document.documentElement.scrollWidth > window.innerWidth + 1,
    bg: getComputedStyle(document.body).backgroundColor,
  }))()"""


def check(path):
    tab = requests.put(DEV + "/json/new?about:blank", timeout=10).json()
    try:
        ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=25)
    except Exception:
        tab = requests.get(DEV + "/json/new?about:blank", timeout=10).json()
        ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=25)
    ids = [0]
    messages = []

    def send(method, **params):
        ids[0] += 1
        ws.send(json.dumps({"id": ids[0], "method": method, "params": params}))
        while True:
            data = json.loads(ws.recv())
            record(data)
            if data.get("id") == ids[0]:
                return data.get("result", {})

    def record(ev):
        m = ev.get("method")
        if m == "Runtime.consoleAPICalled":
            messages.append("console.%s %s" % (
                ev["params"]["type"],
                " ".join(str(a.get("value", a.get("description", "?")))
                         for a in ev["params"]["args"])))
        elif m == "Runtime.exceptionThrown":
            messages.append("exception %s"
                            % ev["params"]["exceptionDetails"].get("text"))
        elif m == "Log.entryAdded":
            e = ev["params"]["entry"]
            messages.append("log[%s] %s" % (e["level"], e["text"]))
        elif m == "Network.loadingFailed":
            if not ev["params"].get("canceled"):
                messages.append("request failed: %s"
                                % ev["params"].get("errorText"))

    try:
        send("Runtime.enable")
        send("Log.enable")
        send("Page.enable")
        send("Network.enable")
        send("Page.navigate", url=BASE + path)

        loaded = False
        deadline = time.time() + 15
        ws.settimeout(1.0)
        while time.time() < deadline:
            try:
                ev = json.loads(ws.recv())
            except websocket.WebSocketTimeoutException:
                if loaded:
                    break
                continue
            record(ev)
            if ev.get("method") == "Page.loadEventFired":
                loaded = True
                deadline = min(deadline, time.time() + 1.5)
        ws.settimeout(25)

        v = send("Runtime.evaluate", returnByValue=True,
                 expression=PROBE).get("result", {}).get("value", {})
        if not loaded:
            messages.append("never fired load")
        return v, messages
    finally:
        try:
            ws.close()
        except Exception:
            pass
        try:
            requests.get(DEV + "/json/close/" + tab["id"], timeout=5)
        except Exception:
            pass


proc = subprocess.Popen(
    [CHROME, "--headless=new", "--remote-debugging-port=9333",
     "--disable-gpu", "--no-first-run", "--no-default-browser-check",
     "--remote-allow-origins=*",
      "--user-data-dir=" + os.path.join(TEMP, "chrome-profile"),
     "--window-size=1280,900", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

try:
    for _ in range(60):
        try:
            requests.get(DEV + "/json/version", timeout=1)
            break
        except Exception:
            time.sleep(0.4)
    else:
        sys.exit("Chrome never came up")

    bad = []
    for path in PAGES:
        v, messages = check(path)

        if path.endswith("404"):
            messages = [m for m in messages
                        if "status of 404" not in m]   # the point of a 404
            if "not found" not in (v.get("title") or "").lower():
                messages.append("did not serve the 404 page")
        else:
            if v.get("picker") != 12:
                messages.append("picker has %s languages, want 12" % v.get("picker"))
            if not v.get("theme"):
                messages.append("no theme toggle")
            if v.get("h1count") != 1:
                messages.append("%s h1 elements" % v.get("h1count"))
            if not v.get("h1"):
                messages.append("empty h1")
            if v.get("alts", 0) < 2:
                messages.append("only %s hreflang alternates" % v.get("alts"))
            if v.get("ld", 0) < 1:
                messages.append("no JSON-LD")
        if v.get("scrollX"):
            messages.append("page scrolls horizontally")
        if v.get("bg") in ("rgba(0, 0, 0, 0)", "transparent"):
            messages.append("body has no background")

        if messages:
            bad.append((path, messages))
            print("FAIL %-47s %s" % (path, messages[0]))
        else:
            print("ok   %-47s lang=%-3s %s" % (path, v.get("lang"),
                                               (v.get("h1") or "")[:38]))

    print("\n%d pages checked" % len(PAGES))
    if bad:
        print("%d with problems:" % len(bad))
        for path, messages in bad:
            for m in messages:
                print("  %s: %s" % (path, m))
        sys.exit(1)
    print("zero console messages, every page complete")
finally:
    proc.terminate()
