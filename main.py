import os
import sqlite3
from datetime import datetime, timezone
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

DB = os.getenv("DB_PATH", "swiftcopier.db")
MASTER_KEY = os.getenv("MASTER_KEY", "CHANGE_MASTER_KEY")
CLIENT_KEY = os.getenv("CLIENT_KEY", "CHANGE_CLIENT_KEY")

app = FastAPI(title="SwiftCopier V1", version="1.0.0")

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.execute("""CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        master_id TEXT NOT NULL,
        position_id TEXT NOT NULL,
        event TEXT NOT NULL,
        side TEXT NOT NULL,
        symbol TEXT NOT NULL,
        volume REAL NOT NULL,
        price REAL NOT NULL,
        sl REAL DEFAULT 0,
        tp REAL DEFAULT 0,
        created_at TEXT NOT NULL
    )""")
    con.execute("""CREATE UNIQUE INDEX IF NOT EXISTS uq_signal
                   ON signals(master_id, position_id, event, side, volume, price)""")
    con.commit()
    con.close()

init_db()

class TradeSignal(BaseModel):
    master_id: str
    position_id: str
    event: str
    side: str
    symbol: str
    volume: float
    price: float
    sl: float = 0
    tp: float = 0

@app.get("/")
def root():
    return HTMLResponse("""
    <html><head><title>SwiftCopier</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
    body{font-family:Arial;max-width:700px;margin:50px auto;padding:20px}
    .card{padding:20px;border:1px solid #ddd;border-radius:14px}
    </style></head>
    <body><div class="card">
    <h1>SwiftCopier</h1>
    <p>V1 API is online.</p>
    <p>Use <b>/docs</b> to test the API.</p>
    </div></body></html>
    """)

@app.get("/health")
def health():
    return {"status":"ok","service":"SwiftCopier","version":"1.0.0"}

@app.post("/api/v1/trade")
def receive_trade(trade: TradeSignal, authorization: str = Header(default="")):
    if authorization != f"Bearer {MASTER_KEY}":
        raise HTTPException(status_code=401, detail="Invalid master key")

    con = db()
    try:
        cur = con.execute("""INSERT OR IGNORE INTO signals
            (master_id,position_id,event,side,symbol,volume,price,sl,tp,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (trade.master_id, trade.position_id, trade.event, trade.side,
             trade.symbol, trade.volume, trade.price, trade.sl, trade.tp,
             datetime.now(timezone.utc).isoformat()))
        con.commit()
        return {"success": True, "signal_id": cur.lastrowid or 0}
    finally:
        con.close()

@app.get("/api/v1/signals")
def get_signals(after_id: int = 0, authorization: str = Header(default="")):
    if authorization != f"Bearer {CLIENT_KEY}":
        raise HTTPException(status_code=401, detail="Invalid client key")

    con = db()
    rows = con.execute("""SELECT * FROM signals
                          WHERE id > ? ORDER BY id ASC LIMIT 50""",
                       (after_id,)).fetchall()
    con.close()

    return {"signals":[dict(r) for r in rows]}

@app.get("/api/v1/status")
def status():
    con = db()
    count = con.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
    latest = con.execute(
        "SELECT * FROM signals ORDER BY id DESC LIMIT 10").fetchall()
    con.close()
    return {"signals_total": count, "latest":[dict(r) for r in latest]}
