# ProctorShield - AI Proctoring & Examination Security Suite

ProctorShield is a security platform designed to preserve exam integrity. It replaces server-side video/audio processing loops with modern client-side browser analytics (utilizing MediaPipe FaceMesh) and processes anomalous violations using an intelligent Bayesian Risk Assessment Classifier.

---

## 👥 Seeded Test Credentials (Try Logging In!)

The database is pre-seeded with **5 active test accounts** (all passwords are set to `password123`). You can use these to test both student and teacher portals:

| Name | Role | Email | Password |
|---|---|---|---|
| **Dr. Alice Smith** | Teacher | `teacher1@example.com` | `password123` |
| **Prof. Bob Jones** | Teacher | `teacher2@example.com` | `password123` |
| **Charlie Brown** | Student | `teacher3@example.com` | `password123` |
| **Diana Prince** | Student | `student2@example.com` | `password123` |
| **Evan Wright** | Student | `student3@example.com` | `password123` |

To reset/reseed the database at any time, run:
```bash
python -c "import sys; sys.path.append(r'c:\Users\parth\OneDrive\Desktop\Code'); from Proctorshield import create_app, db, bcrypt; from Proctorshield.models import User, Student, Teacher; app = create_app(); ctx = app.app_context(); ctx.push(); db.drop_all(); db.create_all(); hashed = bcrypt.generate_password_hash('password123').decode('utf-8'); db.session.add(User(name='Dr. Alice Smith', email='teacher1@example.com', password=hashed, verified=True)); db.session.commit(); t1=Teacher(user_id=1); db.session.add(t1); db.session.add(User(name='Prof. Bob Jones', email='teacher2@example.com', password=hashed, verified=True)); db.session.commit(); t2=Teacher(user_id=3); db.session.add(t2); db.session.add(User(name='Charlie Brown', email='student1@example.com', password=hashed, verified=True)); db.session.commit(); s1=Student(user_id=5); db.session.add(s1); db.session.add(User(name='Diana Prince', email='student2@example.com', password=hashed, verified=True)); db.session.commit(); s2=Student(user_id=7); db.session.add(s2); db.session.add(User(name='Evan Wright', email='student3@example.com', password=hashed, verified=True)); db.session.commit(); s3=Student(user_id=9); db.session.add(s3); print('Database successfully re-seeded!')"
```

---

## 🛠️ Main Tech Stack
- **Backend**: Flask, Flask-SQLAlchemy (Modern SQLAlchemy 2.0 type annotated mapping), Flask-Bcrypt, Flask-Login, Flask-Mail.
- **Frontend**: HTML5, Vanilla CSS, JS, Bootstrap.
- **Theme**: Dark-modern glassmorphism with Outfits Typography.
- **Integrity AI**: MediaPipe FaceMesh, Web Audio Analyser API, Bayesian Threat Engine.
- **Performance Optimizations**: Browser Service Worker caches (CDN bypasses), frame rate throttling (FPS limits).

---

## 📂 Project Structure Overview
- `Proctorshield/`: Primary application packages (Controllers, Blueprints, Templates).
  - `models.py`: SQLAlchemy 2.0 type-safe database schemas.
  - `ai_engine.py`: Anomaly grader calculating joint probability risk scores.
  - `static/sw.js`: Service worker caching resources locally.
  - `static/theme.css`: High-end dark theme glassmorphism stylesheet.
- `run.py`: Entrypoint file mapping the WSGI instance.
- `vercel.json`: Configuration mapping for serverless hosting on Vercel.
- `Requirements.txt`: Pinning only essential web libraries for lightweight server deployments.
- `Monitoring System/`: Independent WebRTC live proctor webcam socket signaling and review channel.

---

## 🚀 Local Run Instructions (Flask Application)

Follow these steps to set up and run the main application locally:

### 1. Prerequisite Installations
Ensure you have **Python 3.8+** and **Pip** installed on your system.

### 2. Set Up a Virtual Environment (Optional but Recommended)
Open your terminal in the project root directory and run:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (Command Prompt)
venv\Scripts\activate
# On Windows (PowerShell)
.\venv\Scripts\activate.ps1
# On macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies
Install all required modules pinned in the requirements checklist:
```bash
pip install -r requirements.txt
```

### 4. Launch the Application Server
Run the startup script:
```bash
python run.py
```
Open your browser and navigate to:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## ⚠️ Troubleshooting Common Windows Issues

### 1. Error: `Microsoft Visual C++ 14.0 or greater is required` (Failed building wheel for greenlet)
This occurs because Python is trying to compile `greenlet` from C++ source files, which requires compiler build tools.
**Solution**: Bypass compilation by force-installing the precompiled binary wheel:
```powershell
python -m pip install --upgrade pip
pip install --only-binary :all: greenlet
pip install -r requirements.txt
```

### 2. Error: `script execution is disabled on this system` (PowerShell activate block)
PowerShell blocks execution of scripts by default.
**Solution**: Allow script execution in the current terminal scope:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\activate.ps1
```

### 3. Error: `ModuleNotFoundError: No module named 'cv2'`
OpenCV (`cv2`) is *not* required by the Flask application anymore, as all proctoring checks are computed in the browser. 
**Solution**: If you are using standalone test files (like `screen_recorder.py`) that require OpenCV, you can install it using:
```powershell
pip install opencv-python
```

---

## 📽️ Live WebRTC Proctor Monitoring Server (Optional Module)
If you wish to use the standalone P2P live video review channel (peer-to-peer webcam streaming):

1. **Install Node.js** (v14+) on your machine.
2. Navigate to the `Monitoring System` directory:
   ```bash
   cd "Monitoring System"
   ```
3. Install package dependencies:
   ```bash
   npm install
   ```
4. Start the socket.io signaling node server:
   ```bash
   node server.js
   ```
   *(Runs signaling channels on port 8000).*

5. Navigate to the client directory and run the React app:
   ```bash
   cd client
   npm install
   npm start
   ```
   *(Opens React P2P client on port 3000).*

---

## ☁️ Vercel Serverless Deployments
The workspace is pre-configured to be deployed serverless on Vercel:

1. Install Vercel CLI: `npm install -g vercel`
2. Login: `vercel login`
3. Run deployment build: `vercel`
   - *Note: `config.py` automatically detects Vercel environments and points SQLite writes to the read-write `/tmp/site.db` folder to prevent serverless file blockages.*
