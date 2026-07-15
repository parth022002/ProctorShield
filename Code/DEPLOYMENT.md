# 🚀 Deploying ProctorShield to Vercel

This guide provides step-by-step instructions to deploy the ProctorShield Flask application to **Vercel** with a cloud-hosted database.

---

## 🛠️ Prerequisites & Requirements

### 1. Version Control (GitHub)
Ensure your code is pushed to a remote GitHub repository. Vercel connects directly to GitHub for continuous deployment (CI/CD).

### 2. Cloud PostgreSQL Database (Required)
SQLite (`site.db`) is serverless-incompatible for persistent writes because Vercel uses a read-only filesystem where SQLite file updates are lost on cold starts.
You **must** host your database on a cloud PostgreSQL provider.
- **Recommended Free Providers**: 
  - **Neon PostgreSQL** ([neon.tech](https://neon.tech/)) — Highly recommended for serverless.
  - **Supabase** ([supabase.com](https://supabase.com/))
- Create a database and copy the **Connection URI** (starts with `postgres://` or `postgresql://`).

---

## 🔑 Environment Variables

You must configure these variables in the **Vercel Dashboard** under **Project Settings > Environment Variables** before deploying:

| Variable | Description | Example / Fallback |
| :--- | :--- | :--- |
| `DATABASE_URL` | Your cloud PostgreSQL connection URI | `postgresql://user:password@host/dbname` |
| `SECRET_KEY` | A long, secure random string for sessions | `7c9270027a164800f09e52vb828q1384523667f` |
| `MAIL_SERVER` | SMTP host for registration verification emails | `smtp.gmail.com` or mailtrap host |
| `MAIL_PORT` | SMTP port | `587` or `465` |
| `MAIL_USE_SSL` | Set to `True` if using SSL/TLS port 465 | `False` (for 587) |
| `MAIL_USERNAME` | SMTP username | `your-email@gmail.com` |
| `MAIL_PASSWORD` | SMTP password (or App Password) | `your-app-password` |

---

## 🚀 Step-by-Step Deployment

### Step 1: Create Vercel Project
1. Log in to the [Vercel Dashboard](https://vercel.com/).
2. Click **Add New > Project**.
3. Import your GitHub repository.

### Step 2: Configure Settings
1. Keep the **Framework Preset** as **Other**.
2. Keep the **Root Directory** as `./` (or the default workspace root).
3. Expand **Environment Variables** and copy-paste the variables listed in the section above.

### Step 3: Click Deploy!
1. Click the **Deploy** button.
2. Vercel will install dependencies from `requirements.txt` and build the serverless functions.
3. Once completed, Vercel will provide your live deployment URL (e.g., `https://proctorshield.vercel.app`).

---

## 📂 Configuration Files Overview

- **`vercel.json`**: Located in the root directory. It tells Vercel's build engine to route all requests (`/(.*)`) to the serverless Python handler inside `run.py`.
- **`run.py`**: Instantiates the Flask WSGI instance `app = create_app()`. Vercel automatically detects this global variable `app` and runs it.
- **`requirements.txt`**: Declares package versions. We added `psycopg2-binary` which provides the database connector for your PostgreSQL database cloud URI.
