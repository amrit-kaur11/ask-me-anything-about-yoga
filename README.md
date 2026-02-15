<<<<<<< HEAD
# Ask Me Anything About Yoga – RAG-Based AI Wellness Application

A full-stack AI wellness assistant built using **FastAPI**, **Local LLM (llama.cpp)**, **RAG (Vector Search)**, and deployed as both:

- 🌐 Web Application  
- 📱 Android APK (via Capacitor)

This project was built as an internship assignment and demonstrates a **real production-style AI system** with a primary focus on **RAG architecture, backend safety logic, and system-level AI design** and where mobile and web clients communicate with an AI backend.

The application allows users to ask questions related to yoga, wellness, and mindfulness while ensuring responses are **grounded in a structured knowledge base** and **safe for health-related queries**.

---

## 📌 Problem Statement

The goal of this project is to design and build a **real-world RAG-based AI micro-application** in the wellness domain that:

- Uses a structured yoga / wellness knowledge base
- Implements a complete RAG pipeline (chunking, embeddings, retrieval, generation)
- Includes backend safety logic for health-related and sensitive queries
- Logs user queries, retrieved context, generated responses, and safety flags
- Demonstrates system-level understanding rather than surface-level API usage

---

## 🧠 System Architecture

The application follows a **client–server architecture** where the frontend (Web + Android) acts as a thin client and all intelligence lives in the backend.

Web App (Vite) Android App (APK)
| 
| HTTP API Calls 
↓ ↓
FastAPI Backend (Python)
|
|── Safety Layer
|── RAG Pipeline
| ├─ Chunking
| ├─ Embeddings
| ├─ Vector Retrieval
| └─ LLM Generation
|
└── MongoDB (Logs)

The FastAPI backend must be running for the application to function.  
This mirrors how real-world mobile and web applications consume AI APIs.

---

## 🔍 RAG Pipeline Design

### Knowledge Base
The knowledge base consists of curated yoga and wellness documents provided in markdown format. These documents serve as the **ground truth** for answer generation.

### Chunking
Documents are split into semantically meaningful chunks to:
- Preserve contextual relevance
- Improve retrieval accuracy
- Reduce token usage during generation

### Embeddings
Each chunk is converted into a vector embedding and stored in a vector index.

### Retrieval
At query time:
1. The user query is embedded
2. Top-K relevant chunks are retrieved using similarity search
3. Retrieved chunks are injected into the LLM prompt as context

This ensures responses are **grounded in retrieved evidence**, not hallucinated.

---

## 🛡️ Backend Safety Logic (Health-Aware RAG)

Because the application operates in the wellness and health domain, **backend-level safety logic** is enforced.

The system:
- Detects health-related and sensitive queries
- Prevents unsafe medical or curative claims
- Uses **fail-safe behavior** for high-risk questions

Example:
- **Query:** “Can yoga cure cancer?”
- **Behavior:**  
  The system avoids curative claims and instead provides retrieved educational context with appropriate disclaimers.

This design ensures **responsible AI behavior** while still delivering useful information.

---

## 🗂️ Logging & Observability (MongoDB)

For every user query, the backend logs the following in MongoDB:

- User query
- Retrieved knowledge chunks
- Generated response
- Safety flags (if triggered)
- Timestamp

This logging enables:
- Auditing of RAG behavior
- Debugging incorrect retrievals
- Analysis of safety decisions
- Future system improvements

---

## 📁 GitHub Folder Structure

root/
│
backend/                           # AI backend (FastAPI + RAG + LLM)
│
├── app/                           # Core application logic
│   │
│   ├── rag/                       # Retrieval-Augmented Generation engine
│   │   ├── chunker.py             # Splits long documents into semantic chunks
│   │   ├── embedder.py            # Converts text → vector embeddings
│   │   ├── generator.py           # Uses the LLM to generate final responses
│   │   ├── index.py               # Builds and manages the vector index
│   │   ├── prompts.py             # System & wellness prompt templates
│   │   └── retriever.py           # Finds relevant knowledge via similarity search
│   │
│   ├── api.py                    # REST API used by Web UI and Android app
│   ├── db.py                     # Stores chat history and user sessions
│   ├── main.py                   # FastAPI application entry point
│   └── safety.py                 # Filters harmful or unsafe content
│
├── data/                          # Knowledge base used by RAG
│   │
│   ├── articles/                 # Mental-wellness articles (markdown files)
│   └── yoga_docs.txt             # Yoga & breathing techniques for grounding
│
├── scripts/                       # Data & vector processing tools
│   │
│   └── build_index.py            # Converts documents into vector embeddings
│                                # and builds the similarity search index
│
├── storage/                       # Auto-generated vector DB & embeddings
│   |                            # (ignored in GitHub – rebuilt at runtime)
│   |
|   └──requirements.txt               # Python dependencies for the backend
│
├── docs/                              # AI system documentation
|   │
|   └── ai_prompts.md                  # Prompt engineering used for the wellness AI
|
frontend/                         # Web UI + Android mobile app (Capacitor)
│
├── android/                      # Native Android project generated by Capacitor
│                                 # This folder is used to build the APK
│
├── src/                          # Frontend application source code
│   │
│   ├── App.jsx                   # Main React UI for the wellness app
│   ├── api.js                    # Handles API calls to FastAPI backend
│   └── main.jsx                  # React entry point that renders the app
│
├── capacitor.config.json         # Connects the web app to Android (Capacitor config)
├── index.html                    # Root HTML file loaded by Vite
├── package.json                  # Frontend dependencies & scripts
├── package-lock.json             # Exact dependency versions (auto-generated)
└── vite.config.js                # Vite build & dev server configuration

---

## 🛠 Tech Stack

- **Backend**: Python, FastAPI, Ollama (Local LLM), RAG, Vector Database
- **Frontend**: Vite + JavaScript
- **Database:** MongoDB (logs)
- **Mobile**: Android (Capacitor WebView)
- **Deployment**: Local / Render / Vercel

---

# ⚙️ How to Run (Windows – same as I built it)

## 1️⃣ Backend

Open terminal:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r storage/requirements.txt

Run the backend:
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Open API docs: http://127.0.0.1:8000/docs

2️⃣ Frontend (Web)
Open new terminal:

```bash
cd frontend
npm install
npm run dev
```
Open in browser: http://localhost:5173

3️⃣ Android APK
The Android app was built using Capacitor and lives in:

frontend/android/
To generate APK:

```bash
cd frontend
npm run build
npx cap sync
npx cap open android
Then build APK from Android Studio.
```

📱 How Recruiters Can Use the APK
Install the APK on Android phone

Run the FastAPI backend on laptop

Phone and laptop must be on same Wi-Fi

App connects to backend via:

cpp
http://<your-laptop-ip>:8000
This is how real mobile apps work with APIs.

---

⚠️ Important:

The APK is not standalone. The FastAPI backend must be running on the same network.

This mirrors real-world mobile–backend system design.

---

🚧 Limitations & Future Work

Safety logic is rule-based and can be extended with ML classifiers

Vector index can be migrated to a managed vector database

Streaming responses can improve UX

Multi-domain knowledge bases can be added

These trade-offs were intentional to prioritize RAG correctness and backend design.

---

🎯 What This Project Shows
Full-stack AI system

LLM + RAG

Real API-based mobile & web integration

Production-style architecture

Local LLM deployment

---

👩‍💻 Author
Amrit Kaur
AI & Data Science Engineer


=======
# Ask Me Anything About Yoga – RAG-Based AI Wellness Application

A full-stack AI wellness assistant built using **FastAPI**, **Local LLM (llama.cpp)**, **RAG (Vector Search)**, and deployed as both:

- 🌐 Web Application  
- 📱 Android APK (via Capacitor)

This project was built as an internship assignment and demonstrates a **real production-style AI system** with a primary focus on **RAG architecture, backend safety logic, and system-level AI design** and where mobile and web clients communicate with an AI backend.

The application allows users to ask questions related to yoga, wellness, and mindfulness while ensuring responses are **grounded in a structured knowledge base** and **safe for health-related queries**.

---

## 📌 Problem Statement

The goal of this project is to design and build a **real-world RAG-based AI micro-application** in the wellness domain that:

- Uses a structured yoga / wellness knowledge base
- Implements a complete RAG pipeline (chunking, embeddings, retrieval, generation)
- Includes backend safety logic for health-related and sensitive queries
- Logs user queries, retrieved context, generated responses, and safety flags
- Demonstrates system-level understanding rather than surface-level API usage

---

## 🧠 System Architecture

The application follows a **client–server architecture** where the frontend (Web + Android) acts as a thin client and all intelligence lives in the backend.

Web App (Vite) Android App (APK)
| 
| HTTP API Calls 
↓ ↓
FastAPI Backend (Python)
|
|── Safety Layer
|── RAG Pipeline
| ├─ Chunking
| ├─ Embeddings
| ├─ Vector Retrieval
| └─ LLM Generation
|
└── MongoDB (Logs)

The FastAPI backend must be running for the application to function.  
This mirrors how real-world mobile and web applications consume AI APIs.

---

## 🔍 RAG Pipeline Design

### Knowledge Base
The knowledge base consists of curated yoga and wellness documents provided in markdown format. These documents serve as the **ground truth** for answer generation.

### Chunking
Documents are split into semantically meaningful chunks to:
- Preserve contextual relevance
- Improve retrieval accuracy
- Reduce token usage during generation

### Embeddings
Each chunk is converted into a vector embedding and stored in a vector index.

### Retrieval
At query time:
1. The user query is embedded
2. Top-K relevant chunks are retrieved using similarity search
3. Retrieved chunks are injected into the LLM prompt as context

This ensures responses are **grounded in retrieved evidence**, not hallucinated.

---

## 🛡️ Backend Safety Logic (Health-Aware RAG)

Because the application operates in the wellness and health domain, **backend-level safety logic** is enforced.

The system:
- Detects health-related and sensitive queries
- Prevents unsafe medical or curative claims
- Uses **fail-safe behavior** for high-risk questions

Example:
- **Query:** “Can yoga cure cancer?”
- **Behavior:**  
  The system avoids curative claims and instead provides retrieved educational context with appropriate disclaimers.

This design ensures **responsible AI behavior** while still delivering useful information.

---

## 🗂️ Logging & Observability (MongoDB)

For every user query, the backend logs the following in MongoDB:

- User query
- Retrieved knowledge chunks
- Generated response
- Safety flags (if triggered)
- Timestamp

This logging enables:
- Auditing of RAG behavior
- Debugging incorrect retrievals
- Analysis of safety decisions
- Future system improvements

---

## 📁 GitHub Folder Structure

root/
│
backend/                           # AI backend (FastAPI + RAG + LLM)
│
├── app/                           # Core application logic
│   │
│   ├── rag/                       # Retrieval-Augmented Generation engine
│   │   ├── chunker.py             # Splits long documents into semantic chunks
│   │   ├── embedder.py            # Converts text → vector embeddings
│   │   ├── generator.py           # Uses the LLM to generate final responses
│   │   ├── index.py               # Builds and manages the vector index
│   │   ├── prompts.py             # System & wellness prompt templates
│   │   └── retriever.py           # Finds relevant knowledge via similarity search
│   │
│   ├── api.py                    # REST API used by Web UI and Android app
│   ├── db.py                     # Stores chat history and user sessions
│   ├── main.py                   # FastAPI application entry point
│   └── safety.py                 # Filters harmful or unsafe content
│
├── data/                          # Knowledge base used by RAG
│   │
│   ├── articles/                 # Mental-wellness articles (markdown files)
│   └── yoga_docs.txt             # Yoga & breathing techniques for grounding
│
├── scripts/                       # Data & vector processing tools
│   │
│   └── build_index.py            # Converts documents into vector embeddings
│                                # and builds the similarity search index
│
├── storage/                       # Auto-generated vector DB & embeddings
│   |                            # (ignored in GitHub – rebuilt at runtime)
│   |
|   └──requirements.txt               # Python dependencies for the backend
│
├── docs/                              # AI system documentation
|   │
|   └── ai_prompts.md                  # Prompt engineering used for the wellness AI
|
frontend/                         # Web UI + Android mobile app (Capacitor)
│
├── android/                      # Native Android project generated by Capacitor
│                                 # This folder is used to build the APK
│
├── src/                          # Frontend application source code
│   │
│   ├── App.jsx                   # Main React UI for the wellness app
│   ├── api.js                    # Handles API calls to FastAPI backend
│   └── main.jsx                  # React entry point that renders the app
│
├── capacitor.config.json         # Connects the web app to Android (Capacitor config)
├── index.html                    # Root HTML file loaded by Vite
├── package.json                  # Frontend dependencies & scripts
├── package-lock.json             # Exact dependency versions (auto-generated)
└── vite.config.js                # Vite build & dev server configuration

---

## 🛠 Tech Stack

- **Backend**: Python, FastAPI, Ollama (Local LLM), RAG, Vector Database
- **Frontend**: Vite + JavaScript
- **Database:** MongoDB (logs)
- **Mobile**: Android (Capacitor WebView)
- **Deployment**: Local / Render / Vercel

---

# ⚙️ How to Run (Windows – same as I built it)

## 1️⃣ Backend

Open terminal:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r storage/requirements.txt

Run the backend:
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Open API docs: http://127.0.0.1:8000/docs

2️⃣ Frontend (Web)
Open new terminal:

```bash
cd frontend
npm install
npm run dev
```
Open in browser: http://localhost:5173

3️⃣ Android APK
The Android app was built using Capacitor and lives in:

frontend/android/
To generate APK:

```bash
cd frontend
npm run build
npx cap sync
npx cap open android
Then build APK from Android Studio.
```

📱 How Recruiters Can Use the APK
Install the APK on Android phone

Run the FastAPI backend on laptop

Phone and laptop must be on same Wi-Fi

App connects to backend via:

cpp
http://<your-laptop-ip>:8000
This is how real mobile apps work with APIs.

---

⚠️ Important:

The APK is not standalone. The FastAPI backend must be running on the same network.

This mirrors real-world mobile–backend system design.

---

🚧 Limitations & Future Work

Safety logic is rule-based and can be extended with ML classifiers

Vector index can be migrated to a managed vector database

Streaming responses can improve UX

Multi-domain knowledge bases can be added

These trade-offs were intentional to prioritize RAG correctness and backend design.

---

🎯 What This Project Shows
Full-stack AI system

LLM + RAG

Real API-based mobile & web integration

Production-style architecture

Local LLM deployment

---

👩‍💻 Author
Amrit Kaur
AI & Data Science Engineer

>>>>>>> f9ae8cc (Removed Ollama and integrated Groq API for LLM generation)
