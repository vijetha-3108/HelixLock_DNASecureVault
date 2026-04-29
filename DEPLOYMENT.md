# Deployment

## Render (one-click)

1. Push this repo to GitHub.
2. In Render, click **New → Blueprint** and pick the repo.
3. Render reads `render.yaml`, provisions the service, and generates `SECRET_KEY` / `JWT_SECRET`.
4. Visit the service URL — `/health` should return `{"status": "ok"}`.

## Docker (anywhere)

```bash
docker build -t dna-secure-vault .
docker run -p 5000:5000 \
  -e SECRET_KEY=$(openssl rand -hex 32) \
  -e JWT_SECRET=$(openssl rand -hex 32) \
  dna-secure-vault
```

## AWS (Elastic Beanstalk)

```bash
pip install awsebcli
eb init -p python-3.11 dna-secure-vault
eb create dna-secure-vault-env
eb setenv SECRET_KEY=... JWT_SECRET=... USE_INMEMORY_DB=true
eb deploy
```

EB picks up `Procfile` automatically. For persistent storage, set
`USE_INMEMORY_DB=false` and provide a `MONGO_URI` (e.g. MongoDB Atlas).

## AWS (ECS / Fargate)

Push the Docker image to ECR and run a Fargate task on port 5000 behind an ALB.
Add the same env vars as above in the task definition.

## Environment variables

See `.env.example` for the full list. The most important:

| Var | Purpose |
| --- | --- |
| `SECRET_KEY` | Flask secret |
| `JWT_SECRET` | JWT signing key |
| `USE_INMEMORY_DB` | `true` for zero-setup, `false` to use Mongo |
| `MONGO_URI` | Mongo connection string when not in-memory |
| `LOGIN_MAX_ATTEMPTS` | Failed logins before lockout |
| `LOGIN_LOCKOUT_SECONDS` | Lockout duration |
| `RATE_LIMIT_DEFAULT` | Per-IP global limit |
| `RATE_LIMIT_AUTH` | Per-IP auth endpoint limit |
| `CORS_ORIGINS` | Comma-separated allowed origins, or `*` |
