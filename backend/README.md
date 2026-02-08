# CRM Project Approval Backend

Backend-only scaffold (FastAPI + PostgreSQL) for the project approval workflow.

## Assumptions
- Frontend is out of scope.
- Auth is mocked via headers: `X-User-Id` and `X-Role` (`creator` or `approver`).
- Storage defaults to local `./uploads`. Set `STORAGE_MODE=s3` for S3 uploads.

## Setup
1. Create a virtualenv and install dependencies:
   - `pip install -r requirements.txt`
2. Configure environment variables (optional):
   - `DATABASE_URL`
   - `AWS_REGION`
   - `S3_BUCKET`
   - `STORAGE_MODE` (`local` or `s3`)
3. Run the API:
   - `uvicorn app.main:app --reload --port 8000`

## Key Endpoints
- `GET /health`
- `POST /api/v1/clients`
- `GET /api/v1/clients`
- `POST /api/v1/projects`
- `PUT /api/v1/projects/{project_id}/draft`
- `POST /api/v1/projects/{project_id}/new-version`
- `POST /api/v1/projects/{project_id}/submit`
- `POST /api/v1/projects/{project_id}/versions/{version_id}/contracts`
- `POST /api/v1/projects/{project_id}/versions/{version_id}/job-categories`
- `GET /api/v1/approvals/pending`
- `POST /api/v1/approvals/{version_id}/approve`
- `POST /api/v1/approvals/{version_id}/reject`
- `GET /api/v1/audit`

## Notes
- Database migrations are not included yet.
- Rate cards are mocked via `/api/v1/rate-cards`.
