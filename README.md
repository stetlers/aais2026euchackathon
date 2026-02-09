# ☢️ AAIS 2026 EUC HACKATHON ☢️

**VAULT-TEC APPROVED • CLASSIFIED CLEARANCE LEVEL: TEAM EYES ONLY**

```
    ╔══════════════════════════════════════════════════════════════╗
    ║  >>> WELCOME TO THE FUTURE OF INNOVATION, VAULT DWELLER <<<  ║
    ║                                                              ║
    ║     War never changes. But your cloud architecture can.      ║
    ╚══════════════════════════════════════════════════════════════╝
```

## 📺 What Is This Terminal?

This is the official command center for the **AAIS 2026 End User Computing Hackathon** — a Fallout-themed development competition where teams compete to build the most innovative solutions using AWS services.

Why Fallout? Because Amazon Prime Video's adaptation became a wasteland-sized hit with over 65 million viewers in its first 16 days. We figured if the world's going to end, we might as well have good infrastructure.

**Live Site:** [aais2026euchackathon.com](https://aais2026euchackathon.com)

## 🎮 Features

### For Teams (Vault Dwellers)
- **Use Case Selection** — Choose from 6 pre-war corporate scenarios, each with unique challenges
- **Team Registration** — Assemble your squad and register your solution
- **AI Catchphrase Generator** — Let Bedrock create a Fallout-themed team motto
- **AI Solution Enhancement** — Rewrite your solution with Wasteland flair
- **Solution Submission** — Document your AWS services and approach
- **Vault ID Card** — Shareable team identity card with QR code
- **Dot-Matrix Printouts** — Press 'P' to generate retro-style briefing documents

### For Panelists (Overseers)
- **Scoring Dashboard** — Rate teams across 4 categories (max 20 points)
- **Live Leaderboard** — Track standings in real-time
- **Team Management** — View all registered teams and their solutions

### For Admins (Enclave Officers)
- **Use Case Management** — Full CRUD operations on hackathon scenarios
- **Judging Criteria Editor** — Modify scoring guidelines on the fly
- **ASCII Logo Management** — Because every corporation needs branding

## 🏗️ Architecture

*"They asked me how well I understood theoretical physics. I said I had a theoretical degree in physics."*

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   CloudFront    │────▶│    S3 Bucket     │     │   DynamoDB      │
│   (CDN Layer)   │     │  (Static HTML)   │     │   (5 Tables)    │
└─────────────────┘     └──────────────────┘     └────────▲────────┘
                                                          │
┌─────────────────┐     ┌──────────────────┐              │
│     Teams &     │────▶│   API Gateway    │────▶┌───────┴────────┐
│    Panelists    │     │    (REST API)    │     │  Lambda (Python)│
└─────────────────┘     └──────────────────┘     └───────┬────────┘
                                                          │
                                                 ┌────────▼────────┐
                                                 │ Amazon Bedrock  │
                                                 │ (Claude Haiku)  │
                                                 └─────────────────┘
```

### Tech Stack
| Layer | Technology | Fallout Equivalent |
|-------|------------|-------------------|
| Frontend | Static HTML/CSS/JS | Pip-Boy Interface |
| API | AWS Lambda + API Gateway | Mr. Handy's Neural Network |
| AI | Amazon Bedrock (Claude Haiku) | ROBCO Personality Matrix |
| Database | DynamoDB | Vault-Tec Records Division |
| Hosting | S3 + CloudFront | Brotherhood of Steel Broadcast Tower |
| Auth | Custom JWT | Vault Security Clearance |

## 🚀 Deployment

### Deploy Lambda (The Nuclear Option)
```bash
cd lambda-api && zip -r ../lambda-deploy.zip . && \
aws lambda update-function-code --function-name aais-hackathon-api \
  --zip-file fileb://../lambda-deploy.zip --region us-east-1
```

### Deploy Frontend (Broadcast to the Wasteland)
```bash
aws s3 cp terminal.html s3://aais2026euchackathon.com/terminal.html --content-type "text/html"
aws s3 cp terminal.html s3://aais2026euchackathon.com/index.html --content-type "text/html"
```

### Invalidate Cache (Clear the Radiation)
```bash
aws cloudfront create-invalidation --distribution-id E2K0ALSZE884A6 --paths "/*"
```

## 🗄️ Infrastructure Setup

*"Building for the future, even if that future is a wasteland."*

Setting up a new environment? See **[INFRASTRUCTURE.md](INFRASTRUCTURE.md)** for complete deployment instructions including:

- **DynamoDB Tables** — 5 tables with full schemas and creation commands
  - `aais-hackathon-teams` — Team registrations (PK: `team_id`)
  - `aais-hackathon-panelists` — Panelist credentials (PK: `panelist_id`)
  - `aais-hackathon-scores` — Scoring data (PK: `team_id`, SK: `panelist_id`)
  - `aais-hackathon-use-cases` — Hackathon scenarios (PK: `use_case_id`)
  - `aais-hackathon-judging-criteria` — Single document (PK: `criteria_id="main"`)
- **IAM Permissions** — Lambda execution role with DynamoDB access
- **Lambda Function** — Python 3.11 runtime setup
- **API Gateway** — REST API with proxy integration
- **S3 + CloudFront** — Static hosting configuration

## 📊 Judging Criteria

Teams are scored like S.P.E.C.I.A.L. stats, but for cloud solutions:

| Category | Points | What We're Looking For |
|----------|--------|----------------------|
| **Presentation** | 1-5 | Charisma isn't a dump stat |
| **Innovation** | 1-5 | Intelligence and creativity |
| **Functionality** | 1-5 | Does it actually work? (Perception check) |
| **AWS Well-Architected** | 1-5 | Endurance of your infrastructure |

**Maximum Score: 20 points** *(Luck not included)*

## 🎨 Design Philosophy

The interface is designed to look like a pre-war terminal from the Fallout universe:

- **Font:** VT323 (Google Fonts) — That authentic CRT terminal feel
- **Colors:** Green phosphor (#33ff33) with amber highlights (#ffcc66)
- **Effects:** CSS scanlines, CRT curvature, subtle text-shadow glow
- **Aesthetic:** "What if IBM and Atomic Age optimism had a baby?"

## 📁 Project Structure

```
aais2026euchackathon/
├── terminal.html          # Main menu (Pip-Boy home screen)
├── index.html             # Copy of terminal.html
├── login.html             # Authentication portal
├── team-dashboard.html    # Team management interface
├── panelist-dashboard.html # Overseer command center
├── vault-id-card.html     # Shareable team ID card
├── lambda-api/
│   ├── lambda_function.py # All API routes (711 lines of destiny)
│   ├── seed_use_cases.py  # Initial data population
│   └── stream_handler.py  # Event streaming utilities
├── backups/               # DynamoDB snapshots
├── AGENTS.md              # Warp AI guidance file
└── INFRASTRUCTURE.md      # AWS deployment guide
```

## 🤝 Contributing

*"The way I see it, you and I are partners in this little venture."*

Found a bug? Want to add a feature? Feel free to:
1. Check the [Issues](https://github.com/stetlers/aais2026euchackathon/issues) for existing tasks
2. Fork the repository
3. Make your changes
4. Submit a pull request

## 📜 License

This project is property of the AAIS 2026 EUC Hackathon organizing committee.

---

```
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   "In the post-apocalyptic wasteland of legacy systems,           ║
║    only the well-architected shall survive."                       ║
║                                                                    ║
║                              — Ancient AWS Proverb, circa 2077     ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

**Built with 💚 and radioactive enthusiasm**
