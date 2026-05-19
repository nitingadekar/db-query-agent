# Quickstart Guide

Complete setup guide to get the DB Query Agent running locally from scratch.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- An AWS account with Bedrock access

---

## 1. AWS Account Setup

### 1.1 Create an IAM User (or use an existing one)

1. Go to [IAM Console](https://console.aws.amazon.com/iam/)
2. Navigate to **Users → Create user**
3. Attach the following managed policy or create a custom one:

**Minimum IAM Policy Required:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.*"
    }
  ]
}
```

> If you're using an existing role or SSO profile, ensure it has the above Bedrock permissions.

### 1.2 Enable the Claude Model in Bedrock

Models must be explicitly enabled before use:

1. Go to [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Select your region (e.g., `eu-west-2`)
3. Navigate to **Model access** (left sidebar)
4. Click **Manage model access**
5. Find **Anthropic → Claude** models and enable:
   - `Claude 3.7 Sonnet` (or whichever you plan to use)
6. Click **Save changes**
7. Wait for status to show **Access granted** (usually instant)

> **Cross-region inference**: If using model IDs prefixed with `eu.` (e.g., `eu.anthropic.claude-sonnet-4-6`), ensure model access is enabled in at least one EU region. The `eu.` prefix routes to the nearest available EU endpoint.

### 1.3 Verify Model Access

```bash
aws bedrock list-foundation-models --region eu-west-2 --by-provider Anthropic --query "modelSummaries[].modelId" --output table
```

---

## 2. Configure AWS Credentials

Choose one of the following options:

### Option A: Environment Variables (simplest)

```bash
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=wJalr...
export AWS_DEFAULT_REGION=eu-west-2
```

Then run:
```bash
make run
```

### Option B: AWS CLI Named Profile

Configure a profile in `~/.aws/credentials`:

```ini
[db-query-agent]
aws_access_key_id = AKIA...
aws_secret_access_key = wJalr...
region = eu-west-2
```

Then run:
```bash
AWS_PROFILE=db-query-agent make run
```

### Option C: aws-vault (recommended for SSO/MFA)

If you use AWS SSO or MFA-protected roles:

```bash
# Login to SSO (if applicable)
aws sso login --profile your-profile

# Run with temporary credentials
aws-vault exec your-profile -- make run
```

> The agent reads credentials from the standard AWS credential chain (env vars → profile → instance metadata). No AWS keys are stored in the project.

---

## 3. Database Setup

### Option A: Use the Demo SQLite Database (quickest)

A seed script creates a local SQLite database with sample data:

```bash
make seed-db
```

This creates `demo.db` in the project root with:
- **customers** table (5 rows): id, name, email, country, created_at
- **orders** table (8 rows): id, customer_id, product, amount, status, ordered_at

No additional configuration needed — the default `.env` points to this file.

### Option B: Connect to an Existing PostgreSQL Database

Update your `.env` file:

```bash
DQA_DATABASE_URL=postgresql://username:password@hostname:5432/dbname
```

Install the PostgreSQL driver (already included in dependencies):
```bash
# psycopg2-binary is included by default
# For production, use psycopg2 (requires libpq):
# uv add psycopg2
```

### Option C: Connect to an Existing MySQL Database

```bash
# Install MySQL driver
uv add pymysql

# Update .env
DQA_DATABASE_URL=mysql+pymysql://username:password@hostname:3306/dbname
```

### Connection String Reference

| Database   | Connection String Format                                      |
|------------|---------------------------------------------------------------|
| SQLite     | `sqlite:///./path/to/file.db`                                 |
| PostgreSQL | `postgresql://user:pass@host:5432/dbname`                     |
| MySQL      | `mysql+pymysql://user:pass@host:3306/dbname`                  |
| SQL Server | `mssql+pyodbc://user:pass@host:1433/dbname?driver=ODBC+Driver+18+for+SQL+Server` |

> The agent auto-introspects the schema at startup. It works with any SQLAlchemy-compatible database.

---

## 4. Configuration Reference

Copy the example and edit:

```bash
cp .env.example .env
```

**`.env` file:**

```bash
# AWS / Bedrock
DQA_AWS_REGION=eu-west-2
DQA_BEDROCK_MODEL_ID=eu.anthropic.claude-sonnet-4-6

# Database
DQA_DATABASE_URL=sqlite:///./demo.db

# Agent behaviour
DQA_MAX_QUERY_ROWS=100        # Max rows returned per query
DQA_ALLOW_MUTATIONS=false     # Set true to allow INSERT/UPDATE/DELETE
DQA_DEFAULT_FORMAT=json       # json | csv | table | summary

# API server
DQA_API_HOST=0.0.0.0
DQA_API_PORT=8000
```

All settings use the `DQA_` prefix and can also be set as environment variables (env vars take precedence over `.env` file).

---

## 5. Run the Agent

```bash
# Install dependencies
make dev

# Seed demo database (skip if using your own DB)
make seed-db

# Start the server
make run
```

Open:
- **Chat UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 6. Test It

Try these prompts in the chat UI:

- "Show me all customers from the UK"
- "What's the total revenue by product?"
- "Which customer has the most orders?"
- "List pending orders with customer names"

Or use the API directly:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show all customers", "format": "table"}'
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ValidationException: model identifier is invalid` | Ensure model is enabled in Bedrock console and ID matches exactly (include `eu.` prefix for cross-region) |
| `NoCredentialProviders` | AWS credentials not configured — see Section 2 |
| `AccessDeniedException` | IAM policy missing `bedrock:InvokeModel*` permissions |
| `Connection refused` on database | Check `DQA_DATABASE_URL` format and that the DB is reachable |
| `ModuleNotFoundError` | Run `make dev` to install dependencies |
