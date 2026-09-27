# SwiftCopier V1 — Demo

This is a first demo-only trade copier.

## What V1 does

Master MT5 -> API -> Client MT5

It currently copies OPEN BUY/SELL trades. CLOSE/REVERSE mapping is intentionally disabled until open-copy testing is successful.

## Deploy

Recommended first test: Render + GitHub.

1. Create a GitHub repository.
2. Upload this project.
3. On Render, create a Web Service from the repository.
4. Render can use `render.yaml`, or use:
   Build: `pip install -r backend/requirements.txt`
   Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   MASTER_KEY = a long random secret
   CLIENT_KEY = another long random secret
6. Deploy.
7. Open `/health` and `/docs`.

Render documents Git-connected FastAPI deployment and the Uvicorn start command. Free web services can spin down after inactivity, so this free deployment is suitable for initial testing, not latency-sensitive production copying.

## MT5

On the desktop/VPS MT5 terminal:

1. Compile each `.mq5` file in MetaEditor.
2. Add the deployed API URL to:
   Tools -> Options -> Expert Advisors -> Allow WebRequest for listed URL.
3. Attach Master EA to a chart on the master demo account.
4. Attach Client EA to a chart on the client demo account.
5. Use demo accounts only.

Never put a real trading password or broker credentials into this project.

## Important V1 limitation

The server uses SQLite in `/tmp` for a quick prototype. That storage is not persistent on many hosted free services. Before any serious use, we will move signal storage to PostgreSQL and implement reliable position mapping, acknowledgements, reconnect handling, SL/TP modification, closes, risk limits, and multi-client controls.
