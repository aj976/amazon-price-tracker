# Amazon Price Tracker (APT) 📈

APT is a full-stack, backend-first application designed to automatically track Amazon product prices, store historical data, and send real-time notifications (via Telegram/Email) when a product drops below your target price threshold.

It features a robust **Python FastAPI backend** with a clean, modular architecture and a sleek **React (Vite) frontend dashboard** styled with a dark, industrial TailwindCSS theme.

---

## 🏗 Architecture

The project is split into three decoupled services to ensure scalability and prevent the web server from blocking during scraping jobs:

1.  **FastAPI Backend (`api/` & `main.py`)**: Handles REST requests from the frontend and interacts with the database via the Repository layer.
2.  **Background Worker (`workers/scheduler.py` & `worker.py`)**: A standalone daemon that wakes up every 2 hours, scrapes the latest prices from Amazon for all tracked products, and dispatches alerts if targets are hit.
3.  **React Frontend (`frontend/`)**: A Vite-powered SPA that displays your tracked items, current prices, target prices, and provides a form to add new products.

All data is stored remotely in a **Supabase PostgreSQL** database.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
*   [Python 3.10+](https://www.python.org/downloads/)
*   [Node.js (v18+) & npm](https://nodejs.org/)
*   A [Supabase](https://supabase.com/) account and project
*   *(Optional)* A Telegram Bot Token and Chat ID for notifications

---

## 🚀 Setup Instructions

### 1. Database Setup (Supabase)
1. Create a new project in Supabase.
2. Go to the **SQL Editor** in your Supabase dashboard.
3. Copy the contents of `database/schema.sql` from this repository and run it to create the necessary `products`, `tracking`, and `price_history` tables.

### 2. Environment Variables
1. Rename the `.env_example` file in the root directory to `.env` (or create a new `.env` file).
2. Fill in your credentials:
    ```env
    # Supabase Configuration
    SUPABASE_URL=https://your-project.supabase.co
    SUPABASE_KEY=your-anon-key
    
    # Telegram Configuration (Required for alerts)
    TELEGRAM_BOT_TOKEN=your_bot_token
    TELEGRAM_CHAT_ID=your_chat_id
    ```

### 3. Backend Setup
1. Open a terminal in the root directory of the project.
2. Create and activate a Python virtual environment:
    ```bash
    python -m venv .venv
    # Windows:
    .\.venv\Scripts\activate
    # Mac/Linux:
    source .venv/bin/activate
    ```
3. Install the Python dependencies:
    ```bash
    pip install -r requirements.txt
    playwright install   # (If your scraper utilizes playwright internally)
    ```

### 4. Frontend Setup
1. Open a **new** terminal tab and navigate into the frontend directory:
    ```bash
    cd frontend
    ```
2. Install the Node modules:
    ```bash
    npm install
    ```

---

## 🏃‍♂️ Running the Application

To run the full application locally, you need to run the three components simultaneously. Open three separate terminal tabs:

**Terminal 1: Start the API Server**
```bash
# Ensure your virtual environment is activated!
uvicorn main:app --reload --port 8000
```

**Terminal 2: Start the Background Tracker Worker**
```bash
# Ensure your virtual environment is activated!
python worker.py
```

**Terminal 3: Start the React Dashboard**
```bash
cd frontend
npm run dev
```

Once everything is running, open your browser and go to **[http://localhost:5173](http://localhost:5173)** to access the dashboard!

---

## 📁 Directory Structure
```text
amazon-price-tracker/
├── api/                    # FastAPI route handlers
│   └── routes/             
├── cli/                    # Command-line interface logic
├── database/               # DB client and Repository pattern logic
├── frontend/               # React (Vite) SPA
├── scraper/                # Amazon web scraping logic
├── services/               # Core business logic (Tracking & Notifications)
├── utils/                  # Helper functions (URL parsing)
├── workers/                # Background scheduling logic
├── .env                    # Environment credentials
├── main.py                 # FastAPI Application Entry Point
├── worker.py               # Background Daemon Entry Point
└── requirements.txt        # Python dependencies
```
