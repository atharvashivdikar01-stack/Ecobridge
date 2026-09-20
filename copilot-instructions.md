# Copilot instructions — Kabadiwala Connect

Project: offline-first Android app (Java) + Flask backend + recycler web dashboard for informal
e-waste collectors in India. Full context, data model and rules are in CONTEXT.md at the repo root.
Read it before suggesting schema, API or architecture changes.

## Who is writing this code
- The team are beginners (basic Java, Python, Android, web). Prefer simple, readable code over clever code.
- Add short comments for anything non-obvious, and summarise in one line what the code does.

## Stack (do not change without asking)
- Android: Java, XML layouts, Room (SQLite), WorkManager, CameraX, Retrofit, TensorFlow Lite
- Backend: Python, Flask, SQLAlchemy, JSON REST under /api/v1
- Web: Flask + Jinja templates + Bootstrap, Leaflet + OpenStreetMap
- Do not introduce new frameworks or libraries (no Kotlin, Compose, Flutter, React, Firebase) unless asked.

## Rules
- Offline-first: write to local SQLite first, sync later with an outbox queue.
  Lot IDs are UUIDs created on the device. Server endpoints must be idempotent.
- No hardcoded UI text: use strings.xml (values/, values-mr/, values-hi/).
- Timestamps are UTC ISO-8601, weights in kg, money in INR.
- Keep personal data minimal. Never invent prices, recycler names or registration numbers.
  Mark test data as synthetic.
- Naming: Java PascalCase/camelCase, Python snake_case, Android resources snake_case.
- Keep the APK small: avoid heavy dependencies.

## When unsure
- Ask a clarifying question or list your assumptions instead of guessing.
