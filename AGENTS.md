# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

AAIS 2026 EUC Hackathon — A Fallout-themed retro terminal web application for managing a hackathon. Teams select use cases, register their solutions, and panelists score submissions through an immersive CRT terminal interface.

## Architecture

### Frontend (Static HTML)
- **No build system** — Plain HTML/CSS/JavaScript files served from S3/CloudFront
- `terminal.html` / `index.html` — Main landing page with use case selection menu
- `login.html` — Team and panelist authentication
- `team-dashboard.html` — Team registration and solution submission
- `panelist-dashboard.html` — Scoring interface and admin controls
- All pages share the same Fallout terminal aesthetic (VT323 font, green phosphor CRT effects)

### Backend (AWS Lambda)
- Single Lambda function (`lambda-api/lambda_function.py`) handles all API routes
- API Gateway endpoint: `https://fc4xp2lydj.execute-api.us-east-1.amazonaws.com/prod`
- Custom JWT implementation for authentication (not AWS Cognito)
- Three user types: `team`, `panelist`, and `admin` (panelist with `is_admin=true`)

### Data (DynamoDB Tables)
- `aais-hackathon-teams` — Team registrations and solution details
- `aais-hackathon-panelists` — Panelist credentials (password stored as SHA-256 hash)
- `aais-hackathon-scores` — Panelist scores per team (composite key: team_id + panelist_id)
- `aais-hackathon-use-cases` — Dynamic use case content (editable by admin)
- `aais-hackathon-judging-criteria` — Single document with criteria_id="main"

### Hosting
- S3 Bucket: `aais2026euchackathon.com`
- CloudFront Distribution: `E2K0ALSZE884A6`
- Region: `us-east-1`

## Common Commands

### Deploy Lambda
```bash
cd lambda-api && zip -r ../lambda-deploy.zip . && \
aws lambda update-function-code --function-name aais-hackathon-api \
  --zip-file fileb://../lambda-deploy.zip --region us-east-1
```

### Deploy Frontend to S3
```bash
aws s3 cp terminal.html s3://aais2026euchackathon.com/terminal.html --content-type "text/html"
aws s3 cp terminal.html s3://aais2026euchackathon.com/index.html --content-type "text/html"
# Repeat for other HTML files as needed
```

### Invalidate CloudFront Cache
```bash
aws cloudfront create-invalidation --distribution-id E2K0ALSZE884A6 --paths "/*"
```

### Backup DynamoDB Table
```bash
aws dynamodb scan --table-name aais-hackathon-use-cases --region us-east-1 > backups/use-cases-backup-$(date +%Y%m%d-%H%M%S).json
```

## API Route Structure

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/team-login` | None | Team login |
| POST | `/auth/panelist-login` | None | Panelist login |
| POST | `/auth/team-register` | None | New team registration |
| GET | `/use-cases` | None | List active use cases |
| GET | `/judging-criteria` | None | Get judging criteria |
| GET/PUT | `/team/me` | Team | Get/update own team |
| GET | `/teams` | Panelist | List all teams |
| POST/GET | `/scores` | Panelist | Submit/get scores |
| POST/PUT/DELETE | `/use-cases/*` | Admin | Manage use cases |
| PUT | `/judging-criteria` | Admin | Update criteria |
| PUT | `/teams/{id}/reset-password` | Admin | Reset team password |
| DELETE | `/teams/{id}` | Admin | Delete team (and scores) |
| GET | `/panelists` | Admin | List all panelists |
| POST | `/panelists` | Admin | Create new panelist |
| PUT | `/panelists/{id}/reset-password` | Admin | Reset panelist password |
| PUT | `/panelists/{id}/toggle-admin` | Admin | Toggle admin status |

## Key Implementation Details

- **Use case fields**: `name`, `archetype`, `quote`, `background`, `reality`, `persona`, `tension`, `focus`, `challenges[]`, `values[]`, `closing`, `ascii_logo`, `loading_message`, `sort_order`, `active`
- **DynamoDB reserved words**: The Lambda uses `ExpressionAttributeNames` mapping (e.g., `#fvalues` for `values`) to avoid conflicts
- **Decimal handling**: DynamoDB returns `Decimal` types; `decimal_to_num()` converts for JSON serialization
- **Scores**: Four categories (presentation, innovation, functionality, aws_well_architected), each 1-5 points

## Styling Conventions

- Font: `VT323` (Google Fonts) for terminal aesthetic
- Colors: Green phosphor (`#33ff33`), muted green (`#66aa66`), amber for highlights (`#ffcc66`)
- Effects: CSS scanlines, CRT curvature overlay, subtle text-shadow glow
- Keep `terminal.html` and `index.html` in sync (index.html is a copy of terminal.html)
