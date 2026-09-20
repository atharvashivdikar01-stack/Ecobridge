# infra/docker 🐳

Docker orchestration and container configurations for local development and production image packaging.

## Local Infrastructure Stack
Start supporting services via Docker Compose:
```bash
docker compose up -d
```
- **PostgreSQL 16 + PostGIS:** Local database on port `5432`
- **Redis 7:** Caching & task queues on port `6379`
- **MinIO:** S3-compatible local object storage on ports `9000` (API) and `9001` (Web Console)
