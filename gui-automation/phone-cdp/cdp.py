import json, time, websocket, urllib.request, sys
class Tab:
    def __init__(self, port, url=None, ws=None):
        if ws is None:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/json/new?{url}", method="PUT")
            info = json.load(urllib.request.urlopen(req, timeout=20)); ws = info["webSocketDebuggerUrl"]; self.id=info["id"]
        self.ws = websocket.create_connection(ws, timeout=60, suppress_origin=True); self.n=0
    def send(self, method, **params):
        self.n+=1; self.ws.send(json.dumps({"id":self.n,"method":method,"params":params}))
        while True:
            m=json.loads(self.ws.recv())
            if m.get("id")==self.n: return m.get("result", m)
    def js(self, expr):
        r=self.send("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        return r.get("result",{}).get("value", r)
    def type(self, text):
        for ch in text: self.send("Input.insertText", text=ch); time.sleep(0.05)
