# 🧭 TripMate AI

> **"Ask Anything. Explore Everything."**

A modern, conversational AI assistant inspired by ChatGPT, powered by the official Google Gemini API (`google-genai` SDK) and built with Python & Streamlit.

---

## 🌟 Overview

**TripMate AI** is a general-purpose AI chatbot designed to converse naturally, explain complex concepts, write and debug code, solve problems, and retain multi-turn conversational context. While it can answer questions on **any topic**, it also has **specialized travel intelligence superpowers**—generating detailed day-by-day itineraries, calculating budget breakdowns, comparing destinations, and adapting plans on the fly.

---

## ✨ Features

- **🌐 General-Purpose AI Assistant**:
  - Technical and academic explanations.
  - Python coding, debugging, and system architecture.
  - Science, mathematics, geography, history, and creative writing.
  - Seamless follow-up questions using active conversation history.

- **✈️ Travel & Exploration Superpower**:
  - Detailed day-by-day itineraries (Morning, Afternoon, Evening).
  - Realistic budget breakdowns (stay, transit, food, activities) in local currencies (₹, $, €).
  - Destination comparisons (e.g. Goa vs Kerala, Manali vs Shimla).
  - Dynamic replanning when constraints or budgets change.

- **🎨 Premium ChatGPT-Style Dark Navy UI**:
  - Modern aesthetic with subtle blue and cyan accents (`#0B1120`, `#38BDF8`).
  - Clear user and assistant chat bubbles with avatars.
  - Full Markdown rendering: syntax-highlighted code blocks, tables, lists, and LaTeX formulas.
  - Real-time token streaming for an instant, responsive chat experience.

- **💬 Multi-Session Chat Management**:
  - **New Chat** button to start fresh conversations.
  - Session history sidebar to easily switch between previous chats.
  - Auto-generated conversation titles based on your first query.
  - Clear current chat or export conversation as Markdown.

- **🔒 Secure & Robust Gemini Integration**:
  - Powered by the official `google-genai` Python SDK.
  - Environment variable support via `python-dotenv` (`.env` / `.env.example`).
  - Secure in-app API key configuration with one-click connection testing.
  - Graceful handling for missing keys, rate limits, invalid keys, and network disconnects.

---

## 📁 Project Structure

```
TripMate-AI/
├── .streamlit/
│   └── config.toml       # Streamlit dark navy theme configuration
├── app.py                # Main Streamlit web app & chat interface
├── chatbot.py            # Gemini API wrapper, streaming engine & error handler
├── config.py             # System prompts, suggested prompts, and CSS styling
├── requirements.txt      # Python dependencies
├── .env                  # Local environment file (API keys)
├── .env.example          # Environment template with instructions
└── README.md             # Project documentation & launch guide
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (or Anaconda / Miniconda)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Gemini API Key
Obtain your free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

Then either:
- Copy `.env.example` to `.env` and set your key:
  ```bash
  cp .env.example .env
  ```
  Edit `.env`:
  ```env
  GEMINI_API_KEY=AIzaSyYourActualKeyHere
  ```
- **Or** launch the app and enter your key directly into the **⚙️ Gemini API Configuration** expander in the sidebar!

### 4. Run the Application
```bash
streamlit run app.py
```
The application will open in your browser at `http://localhost:8501`.

---

## 💡 Example Prompts to Try

### General Knowledge & Learning
> "Explain quantum computing and superposition in simple terms with an everyday analogy."

### Programming & Debugging
> "Write a clean Python script using asyncio to scrape web data concurrently with error handling."

### Travel Planning & Itinerary
> "Plan a 5-day budget-friendly trip to Manali under ₹15,000 including stay, food, and daily activities."

### Travel Follow-Up & Budget Adjustment
> "Now reduce the budget to ₹10,000 and adjust the stay and activities accordingly."

### Destination Comparison
> "Compare Goa and Kerala for a 4-day vacation in December in terms of beaches, budget, vibe, and food."

---

## 🛡️ Error Handling
TripMate AI never fabricates or simulates AI responses if the API key is missing. Instead, it provides clear setup instructions right in the UI so you can configure your key in seconds and start chatting.
