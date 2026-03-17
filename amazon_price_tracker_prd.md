# Amazon Price Tracker (APT) - Product Requirements Document

## 1. Product Overview

**Name:** Amazon Price Tracker (APT)\
**Type:** Backend-first application (CLI + optional API)\
**Goal:** Track Amazon product prices, store history, and notify users when price conditions are met.

---

## 2. Functional Scope

### 2.1 Input Handling

**System Requirements:**

- Accept Amazon product URL
- Validate URL format
- Extract ASIN using regex

**Example Input:**

```
https://www.amazon.in/dp/B0XXXXX
```

**Expected Output:**

```
asin: B0XXXXX
```

---

### 2.2 Scraper Module

**Responsibilities:**

- Fetch HTML using `requests`
- Use headers:

```json
{
  "User-Agent": "Mozilla/5.0"
}
```

- Parse using `BeautifulSoup`

**Extract:**

- Product title
- Current price

**Selectors (with fallback logic):**

- `#productTitle`
- `.a-price-whole`
- `.a-offscreen`

**Edge Handling:**

- If price not found → return `None`
- Retry up to 3 times on failure

---

### 2.3 Database Layer

## 2.8 Backend Infrastructure (UPDATED)

**Database & Backend-as-a-Service:** Supabase

**Requirements:**
- Use Supabase PostgreSQL instead of SQLite
- Use Supabase client (JavaScript/Python) for DB interaction
- Store all tables in Supabase
- Enable REST or direct client access for frontend

**Authentication (Optional for now):**
- Supabase Auth (email-based)

**Tables (same schema, adapted to PostgreSQL):**
- products
- price_history
- tracking

**Why Supabase (MANDATORY):**
- Enables real frontend-backend integration
- Removes local DB limitations
- Makes project deployable

---

## 6. Non-Functional Requirements

**Schema:**

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asin TEXT UNIQUE,
    title TEXT,
    url TEXT
);

CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    price REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    target_price REAL,
    last_notified_price REAL,
    FOREIGN KEY(product_id) REFERENCES products(id)
);
```

---

### 2.4 Price Tracking Logic

**System Flow:**

1. Fetch current price
2. Retrieve last stored price
3. Compare:
   - If current < last → mark as drop
   - If current <= target\_price → trigger alert

---

### 2.5 Notification Module

**Primary Mode:** Telegram Bot

**Message Format:**

```
Price Drop Alert!
Product: <title>
Current Price: ₹XXXX
Target Price: ₹XXXX
Link: <url>
```

**Alternative:** Email via SMTP

---

### 2.6 Scheduler

**Options:**

- `schedule` library OR cron job

**Frequency:**

- Every 2 hours

**Task Responsibilities:**

- Iterate all tracked products
- Run scraper
- Update database
- Trigger alerts

---

### 2.7 CLI Interface

**Commands:**

```
add <url> <target_price>
list
track-now
remove <asin>
```

---

## 3. System Architecture

```
CLI Input
   ↓
URL Parser (ASIN)
   ↓
Scraper
   ↓
Database (SQLite)
   ↓
Tracking Engine
   ↓
Notification Service
   ↓
Scheduler
```

---

## 4. File Structure (MANDATORY)

```
amazon-price-tracker/
│
├── main.py
├── config.py
│
├── scraper/
│   └── amazon_scraper.py
│
├── database/
│   ├── models.py
│   └── db.py
│
├── services/
│   ├── tracker.py
│   └── notifier.py
│
├── utils/
│   └── parser.py
│
├── cli/
│   └── commands.py
│
└── requirements.txt
```

---

## 5. API Contracts (Internal)

### parse\_url(url)

```
Input: string
Output: asin (string)
```

### fetch\_product(asin)

```
Output:
{
  title: string,
  price: float
}
```

### store\_price(product\_id, price)

```
Output: success/failure
```

### check\_price\_drop(product\_id)

```
Output:
{
  is_drop: bool,
  is_target_hit: bool
}
```

---

## 6. Non-Functional Requirements

- Must handle at least 20 products
- Retry failed requests (max 3)
- Modular code structure
- No hardcoded product-specific logic

---

## 7. Environment Variables

```
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
EMAIL_USER=
EMAIL_PASS=
```

---

## 8. Dependencies

```
requests
beautifulsoup4
sqlite3
schedule
python-dotenv
```

---

## 9. Execution Flow

1. User runs:

```
python main.py add <url> <price>
```

2. System:

- Parses URL
- Stores product
- Adds tracking rule

3. Scheduler runs:

- Fetch price
- Store history
- Compare
- Notify if needed

---

## 10. Output Expectations (STRICT)

System must:

- Persist all prices
- Trigger alerts reliably
- Not crash on invalid input
- Log errors clearly

---

## 11. Deliverables

AI-generated output must include:

- Complete working codebase
- Modular architecture
- CLI interface
- Database setup
- Scraper implementation
- Notification system

---

## 12. Frontend Requirements (MANDATORY)

### 12.1 Overview

Add a lightweight but visually distinct frontend.

**Stack:**
- React (Vite)
- TailwindCSS (with custom theme)

---

### 12.2 Core Features

Frontend must allow:
- Add product URL + target price
- View tracked products
- View current price + last updated
- Visual indicator of price drop
- Trigger manual refresh

---

### 12.3 Pages

#### Dashboard
- List all tracked products
- Show:
  - Title
  - Current price
  - Target price
  - Status (↑ ↓ =)

#### Add Product
- Input: URL + target price
- Submit → calls backend API

---

### 12.4 UI Design System (STRICT — NO GENERIC GRADIENTS)

You are not building another generic SaaS dashboard. Avoid:
- Blue-purple gradients
- Glassmorphism overuse

#### Color Philosophy:
Dark, sharp, high-contrast, slightly industrial.

#### Primary Palette:
- Background: #0D0D0D (near black)
- Surface: #161616
- Accent: #FF6B00 (burnt orange)
- Secondary Accent: #00C2A8 (teal)
- Text Primary: #EAEAEA
- Text Secondary: #8A8A8A

#### Semantic Colors:
- Price Drop: #00E676 (neon green)
- Price Increase: #FF1744 (sharp red)

#### Typography:
- Font: Inter / Space Grotesk
- Bold, tight spacing

---

### 12.5 Component Requirements

- ProductCard
- AddProductForm
- PriceIndicatorBadge
- Navbar

Each component must be reusable and isolated.

---

### 12.6 API Integration

Frontend must consume backend endpoints:

```
GET /products
POST /products
GET /prices/<asin>
POST /track
```

---

### 12.7 Frontend File Structure

```
frontend/
│
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── styles/
│   └── App.jsx
│
├── index.html
└── package.json
```

---

### 12.8 UX Rules (NON-NEGOTIABLE)

- No clutter
- No unnecessary animations
- Data-first UI
- Everything actionable within 2 clicks

---

## 13. Updated Deliverables

AI-generated output must include:
- Backend system (as defined above)
- Fully functional React frontend
- API integration
- Clean UI with defined color system

---

## 14. Future Enhancements (Out of Scope)

- Web UI (Flask/React)
- Price history graphs
- Multi-user authentication

---

## 13. Instructions for AI Code Generation

Use the following directive when feeding into a vibecoding tool:

```
Generate a complete, production-ready Python project based on this PRD.

Requirements:
- Clean modular code
- No placeholders
- Fully runnable
- Proper error handling
- Meaningful comments
```

---

## Final Note

This PRD is designed to eliminate ambiguity and enforce a structured, system-level implementation. Any deviation from this structure will reduce reliability and scalability.

