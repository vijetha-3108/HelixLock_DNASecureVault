# 🧬 DNA Secure Vault

A full-stack cybersecurity project that uses **DNA-based cryptography** to securely
store and manage sensitive chemical data. Includes JWT authentication, RBAC,
brute-force protection, rate limiting, attack simulation, an admin audit
dashboard, animated DNA visualization, and a deployment-ready Docker/Render setup.

## Quick start

```bash
python -m venv venv
# Windows: venv\Scripts\activate    macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open <http://127.0.0.1:5000>.

## Features

### Authentication & RBAC
- JWT-based sessions with bcrypt password hashing
- Roles: **admin** and **user** (separate UIs and API permissions)
- Brute-force protection: configurable lockout after N failed attempts
- IP-based rate limiting on auth and attack endpoints (Flask-Limiter)

### DNA Cryptography Engine
- 24 key-derived binary→DNA permutations
- SHA-256 keyed mutation layer (XOR-style rotation in DNA space)
- SHA-256 integrity hash → tamper detection on decrypt
- Animated **double-helix SVG** visualization with colored A/T/G/C bases,
  Watson–Crick complement strand, and per-stage pipeline view

### Audit & Logging
- Every event tagged with severity (`info`, `warning`, `critical`),
  IP, user agent, user id
- **Admin audit dashboard**: stat tiles, event/severity filters, search

### Attack Simulation
- Wrong-key decryption
- Base-flipping tamper detection
- Unauthorized request

### Tests
- Unit tests for crypto, integrity, mapping, complement
- Integration tests for auth (incl. lockout), vault, RBAC, attack endpoints

```bash
pytest -q
```

### Deployment
- `Dockerfile` + `Procfile` + `render.yaml` for one-click Render deploy
- Notes for AWS Elastic Beanstalk and ECS in `docs/DEPLOYMENT.md`

## Project layout

```
dna-secure-vault/
├── app.py / run.py / config.py
├── Dockerfile / Procfile / render.yaml
├── backend/
│   ├── extensions.py
│   ├── routes/   (auth, vault, admin, attack)
│   ├── utils/    (auth, dna_crypto, integrity, security)
│   └── database/ (db.py — Mongo / in-memory)
├── frontend/     (html/, css/, js/)
├── tests/        (crypto, auth, vault, attack & admin)
└── docs/         (ARCHITECTURE.md, DEPLOYMENT.md)
```

## Default credentials
None — register your first account from `/register.html`. Pick **Admin** role
to access the audit dashboard.
