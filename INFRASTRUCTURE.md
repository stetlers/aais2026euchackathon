# ☢️ INFRASTRUCTURE DEPLOYMENT GUIDE ☢️

**VAULT-TEC ENGINEERING DIVISION • CLEARANCE: OVERSEER**

```
╔═══════════════════════════════════════════════════════════════════╗
║  "Building for the future, even if that future is a wasteland."  ║
╚═══════════════════════════════════════════════════════════════════╝
```

This guide covers deploying the complete AWS infrastructure for the AAIS 2026 EUC Hackathon platform.

## 📋 Prerequisites

- AWS CLI configured with appropriate credentials
- AWS Region: `us-east-1` (all resources)
- Permissions to create: DynamoDB tables, Lambda functions, API Gateway, S3 buckets, CloudFront distributions

---

## 🗄️ DynamoDB Tables

### 1. Teams Table

```bash
aws dynamodb create-table \
  --table-name aais-hackathon-teams \
  --attribute-definitions AttributeName=team_id,AttributeType=S \
  --key-schema AttributeName=team_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

**Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `team_id` | String (PK) | Unique team identifier (used for login) |
| `password_hash` | String | SHA-256 hashed password |
| `team_name` | String | Display name for the team |
| `use_case` | Number | Selected use case (1-6) |
| `members` | List | Array of `{name, role}` objects |
| `solution_description` | String | Team's solution description |
| `services_used` | List | AWS services being used |
| `created_at` | String | ISO 8601 timestamp |
| `updated_at` | String | ISO 8601 timestamp |

---

### 2. Panelists Table

```bash
aws dynamodb create-table \
  --table-name aais-hackathon-panelists \
  --attribute-definitions AttributeName=panelist_id,AttributeType=S \
  --key-schema AttributeName=panelist_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

**Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `panelist_id` | String (PK) | Unique panelist identifier (used for login) |
| `password_hash` | String | SHA-256 hashed password |
| `name` | String | Display name |
| `is_admin` | Boolean | Whether panelist has admin privileges |
| `created_at` | String | ISO 8601 timestamp |

**Seed an admin panelist:**
```bash
# Generate password hash (Python)
python3 -c "import hashlib; print(hashlib.sha256('your-password'.encode()).hexdigest())"

# Insert panelist
aws dynamodb put-item \
  --table-name aais-hackathon-panelists \
  --item '{
    "panelist_id": {"S": "admin-username"},
    "password_hash": {"S": "YOUR_HASH_HERE"},
    "name": {"S": "Admin Name"},
    "is_admin": {"BOOL": true}
  }' \
  --region us-east-1
```

---

### 3. Scores Table

```bash
aws dynamodb create-table \
  --table-name aais-hackathon-scores \
  --attribute-definitions \
    AttributeName=team_id,AttributeType=S \
    AttributeName=panelist_id,AttributeType=S \
  --key-schema \
    AttributeName=team_id,KeyType=HASH \
    AttributeName=panelist_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

**Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `team_id` | String (PK) | Team being scored |
| `panelist_id` | String (SK) | Panelist submitting score |
| `presentation` | Number | Score 1-5 |
| `innovation` | Number | Score 1-5 |
| `functionality` | Number | Score 1-5 |
| `aws_well_architected` | Number | Score 1-5 |
| `total` | Number | Sum of all scores |
| `comments` | String | Optional feedback |
| `created_at` | String | ISO 8601 timestamp |
| `updated_at` | String | ISO 8601 timestamp |

---

### 4. Use Cases Table

```bash
aws dynamodb create-table \
  --table-name aais-hackathon-use-cases \
  --attribute-definitions AttributeName=use_case_id,AttributeType=N \
  --key-schema AttributeName=use_case_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

**Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `use_case_id` | Number (PK) | Unique identifier (1, 2, 3...) |
| `name` | String | Company name (e.g., "Vault-Tec Corporation") |
| `archetype` | String | Use case type (e.g., "Secrecy-Driven") |
| `quote` | String | Tagline quote |
| `background` | String | Company background |
| `reality` | String | Business challenges |
| `persona` | String | User persona description |
| `tension` | String | Stakeholder conflicts |
| `focus` | String | Evaluation focus area |
| `challenges` | List | Array of challenge strings |
| `values` | List | Array of value strings |
| `closing` | String | Closing statement |
| `ascii_logo` | String | ASCII art logo |
| `loading_message` | String | Custom loading message |
| `sort_order` | Number | Display order |
| `active` | Boolean | Whether use case is visible |

**Seed use cases:**
```bash
cd lambda-api
python3 seed_use_cases.py
```

---

### 5. Judging Criteria Table

```bash
aws dynamodb create-table \
  --table-name aais-hackathon-judging-criteria \
  --attribute-definitions AttributeName=criteria_id,AttributeType=S \
  --key-schema AttributeName=criteria_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

**Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `criteria_id` | String (PK) | Always "main" (single document) |
| `intro` | String | Introduction text |
| `categories` | List | Scoring categories with descriptions |
| `required_tool` | Map | Required tool info (name, description, features) |
| `expected_services` | Map | Expected AWS services info |
| `closing` | String | Closing statement |
| `updated_at` | String | ISO 8601 timestamp |

**Seed judging criteria:**
```bash
aws dynamodb put-item \
  --table-name aais-hackathon-judging-criteria \
  --item '{
    "criteria_id": {"S": "main"},
    "intro": {"S": "Each team will be scored from 1 to 5 points (5 being the highest) across four categories. Maximum possible score: 20 points."},
    "closing": {"S": "Remember: The best solutions balance all four categories. Strive for excellence across the board."}
  }' \
  --region us-east-1
```

---

## ⚡ Lambda Function

### Create Execution Role

```bash
# Create the role
aws iam create-role \
  --role-name aais-hackathon-lambda-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach DynamoDB policy
aws iam put-role-policy \
  --role-name aais-hackathon-lambda-role \
  --policy-name DynamoDBAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Scan",
        "dynamodb:Query"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-east-1:*:table/aais-hackathon-*"
      ]
    }]
  }'

# Attach CloudWatch Logs policy
aws iam attach-role-policy \
  --role-name aais-hackathon-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### Create Lambda Function

```bash
# Package the code
cd lambda-api && zip -r ../lambda-deploy.zip .

# Create the function
aws lambda create-function \
  --function-name aais-hackathon-api \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/aais-hackathon-lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://../lambda-deploy.zip \
  --timeout 30 \
  --memory-size 256 \
  --region us-east-1
```

### Set Environment Variables (Optional)

```bash
aws lambda update-function-configuration \
  --function-name aais-hackathon-api \
  --environment "Variables={JWT_SECRET=your-secret-key-here}" \
  --region us-east-1
```

---

## 🌐 API Gateway

### Create REST API

```bash
# Create API
aws apigateway create-rest-api \
  --name aais-hackathon-api \
  --endpoint-configuration types=REGIONAL \
  --region us-east-1

# Note the API ID from the output, then create a proxy resource
# This is typically easier to do via the AWS Console:
# 1. Create a proxy resource: /{proxy+}
# 2. Create ANY method pointing to Lambda
# 3. Enable CORS
# 4. Deploy to 'prod' stage
```

**API Endpoint Format:** `https://{api-id}.execute-api.us-east-1.amazonaws.com/prod`

---

## 🪣 S3 + CloudFront (Static Hosting)

### Create S3 Bucket

```bash
aws s3 mb s3://aais2026euchackathon.com --region us-east-1

# Enable static website hosting
aws s3 website s3://aais2026euchackathon.com \
  --index-document index.html \
  --error-document index.html

# Set bucket policy for public read
aws s3api put-bucket-policy \
  --bucket aais2026euchackathon.com \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::aais2026euchackathon.com/*"
    }]
  }'
```

### Upload Frontend Files

```bash
aws s3 cp terminal.html s3://aais2026euchackathon.com/terminal.html --content-type "text/html"
aws s3 cp terminal.html s3://aais2026euchackathon.com/index.html --content-type "text/html"
aws s3 cp login.html s3://aais2026euchackathon.com/login.html --content-type "text/html"
aws s3 cp team-dashboard.html s3://aais2026euchackathon.com/team-dashboard.html --content-type "text/html"
aws s3 cp panelist-dashboard.html s3://aais2026euchackathon.com/panelist-dashboard.html --content-type "text/html"
aws s3 cp favicon-32x32.png s3://aais2026euchackathon.com/favicon-32x32.png --content-type "image/png"
aws s3 cp apple-touch-icon.png s3://aais2026euchackathon.com/apple-touch-icon.png --content-type "image/png"
aws s3 cp pre-war-new-vegas-is-absolutely-stunning-i-am-in-sheer-awe-v0-gqg29pm5z0kf1.jpg.webp s3://aais2026euchackathon.com/ --content-type "image/webp"
```

### Create CloudFront Distribution

Create via AWS Console or CLI with:
- Origin: S3 bucket
- Default root object: `index.html`
- HTTPS redirect enabled
- Cache invalidation on deploy

---

## ✅ Deployment Checklist

```
[ ] DynamoDB tables created (5 tables)
[ ] Admin panelist seeded
[ ] Use cases seeded (run seed_use_cases.py)
[ ] Judging criteria seeded
[ ] IAM role created with DynamoDB permissions
[ ] Lambda function deployed
[ ] API Gateway configured with proxy integration
[ ] S3 bucket created with static hosting
[ ] Frontend files uploaded
[ ] CloudFront distribution created
[ ] DNS configured (if using custom domain)
```

---

```
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   "Patrolling the AWS Console almost makes you wish for a         ║
║    nuclear winter."                                                ║
║                                                                    ║
║                              — Courier Six, Cloud Architect        ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```
