"""
TripMate AI - Configuration Module
====================================
Contains application constants, system prompts, suggested prompts,
model definitions, and custom dark-navy CSS styling.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application Identity
APP_NAME = "TripMate AI"
TAGLINE = "Ask Anything. Explore Everything."
APP_ICON = "🧭"

# Welcome Screen Text
WELCOME_TITLE = "Hey! I'm TripMate AI."
WELCOME_SUBTITLE = "Your intelligent assistant for learning, exploring and planning."

# Gemini Model Configuration
DEFAULT_MODEL = "gemini-3.8-flash"
AVAILABLE_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.8-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
    "gemini-2.5-pro",
]

# Suggested Prompts for Quick Exploration
SUGGESTED_PROMPTS = [
    {
        "title": "Explain a concept",
        "description": "Break down complex topics into simple terms",
        "icon": "💡",
        "prompt": "Explain quantum computing and superposition in simple terms using an everyday analogy.",
    },
    {
        "title": "Write Python code",
        "description": "Generate, debug or optimize programming code",
        "icon": "💻",
        "prompt": "Write a clean, asynchronous Python script to fetch data from multiple REST endpoints concurrently with error handling and rate limiting.",
    },
    {
        "title": "Plan my next trip",
        "description": "Create custom itineraries and budget estimates",
        "icon": "✈️",
        "prompt": "Plan a comprehensive 5-day budget-friendly trip to Manali under ₹15,000 including travel, stay, food, and daily activities breakdown.",
    },
    {
        "title": "Teach me something",
        "description": "Discover fascinating facts and insights",
        "icon": "🚀",
        "prompt": "Teach me something fascinating about the universe or deep space that most people don't know.",
    },
]

# Core System Instruction for Gemini
SYSTEM_INSTRUCTION = """You are TripMate AI, an intelligent, articulate, and versatile general-purpose AI assistant.
Your tagline is: "Ask Anything. Explore Everything."

CORE CAPABILITIES & PERSONALITY:
1. General-Purpose Intelligence:
   - You can answer questions on ANY topic: science, mathematics, literature, philosophy, history, geography, arts, everyday problem solving, and creative writing.
   - You provide clear, high-quality, well-structured answers tailored in length and depth to the user's intent.
   - You explain technical and academic concepts clearly, using analogies where helpful.
   - You excel at programming and debugging: write clean, modern, well-commented code blocks with syntax highlighting.
   - You maintain conversational context seamlessly across follow-up questions.

2. Travel & Exploration Specialty:
   - While you are a general-purpose assistant, travel planning is one of your superpowers.
   - When asked travel-related questions (e.g. trip planning, itineraries, budgets, destination comparisons, route suggestions, packing lists):
     * Provide structured, actionable, day-by-day itineraries (Morning, Afternoon, Evening, Stay & Food recommendations).
     * Calculate realistic, transparent budget breakdowns (Transportation, Accommodation, Food, Sightseeing, Miscellaneous, Emergency Buffer).
     * Use appropriate local currencies (e.g., ₹ INR for Indian destinations, $ USD, € EUR, etc.).
     * Compare destinations thoughtfully across weather, culture, budget, accessibility, and vibe (use markdown tables when comparing).
     * Dynamically adjust itineraries when constraints change (e.g., if the user says "reduce budget to ₹10,000" or "change to 3 days").
     * Include local travel tips, safety recommendations, and best seasons to visit.

3. Formatting & Style:
   - Use Markdown formatting: headers, bold text, bullet points, numbered lists, tables, and code blocks.
   - When writing code, always specify the language (e.g., ```python, ```javascript).
   - Be engaging, polite, professional, and directly address the user's inquiry without unnecessary fluff.
"""

# Custom CSS for Dark Navy & Cyan/Blue ChatGPT-style Theme
CUSTOM_CSS = """
<style>
/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #F1F5F9;
}

/* Base background */
.stApp {
    background-color: #0B1120;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #070D18;
    border-right: 1px solid #1E293B;
}

section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #F8FAFC;
}

/* Sidebar button styling */
section[data-testid="stSidebar"] .stButton > button {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.2s ease-in-out;
    width: 100%;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #0284C7;
    border-color: #38BDF8;
    color: #FFFFFF;
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.25);
}

/* Primary "New Chat" button */
.new-chat-btn button {
    background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
    border: 1px solid #38BDF8 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    padding: 0.6rem 1rem !important;
    border-radius: 8px !important;
}

.new-chat-btn button:hover {
    background: linear-gradient(135deg, #0369A1 0%, #0284C7 100%) !important;
    box-shadow: 0 0 16px rgba(56, 189, 248, 0.4) !important;
}

/* Welcome Screen Header */
.welcome-container {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem 1rem;
    max-width: 780px;
    margin: 0 auto;
}

.badge-tag {
    display: inline-block;
    padding: 0.35rem 0.9rem;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.35);
    color: #38BDF8;
    border-radius: 9999px;
    margin-bottom: 1rem;
}

.welcome-title {
    font-size: 2.4rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #F8FAFC;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, #FFFFFF 40%, #94A3B8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.welcome-subtitle {
    font-size: 1.1rem;
    color: #94A3B8;
    margin-bottom: 2rem;
    line-height: 1.6;
}

/* Suggestion Card styling */
.prompt-card {
    background: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 12px;
    padding: 1.1rem;
    cursor: pointer;
    transition: all 0.25s ease;
    height: 100%;
}

.prompt-card:hover {
    border-color: #38BDF8;
    background: #132238;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(2, 132, 199, 0.18);
}

.prompt-icon {
    font-size: 1.4rem;
    margin-bottom: 0.4rem;
}

.prompt-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #F1F5F9;
    margin-bottom: 0.25rem;
}

.prompt-desc {
    font-size: 0.8rem;
    color: #94A3B8;
    line-height: 1.4;
}

/* Chat Message Styling */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    padding: 1rem 0;
    border-bottom: 1px solid rgba(30, 41, 59, 0.4);
}

/* User Message bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: rgba(30, 41, 59, 0.35) !important;
    border-radius: 12px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.75rem;
    border: 1px solid rgba(56, 189, 248, 0.15);
}

/* Assistant Message bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: rgba(15, 23, 42, 0.55) !important;
    border-radius: 12px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.75rem;
    border: 1px solid rgba(30, 41, 59, 0.7);
}

/* Chat Input Styling */
[data-testid="stChatInput"] {
    background-color: #070D18 !important;
    border: 1px solid #1E293B !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35) !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #38BDF8 !important;
    box-shadow: 0 0 16px rgba(56, 189, 248, 0.3) !important;
}

[data-testid="stChatInputTextArea"] {
    color: #F8FAFC !important;
}

/* Code block styling */
pre {
    background-color: #070D18 !important;
    border: 1px solid #1E293B !important;
    border-radius: 8px !important;
}

code {
    color: #38BDF8 !important;
}

/* Tables */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 1rem 0;
}

th, td {
    border: 1px solid #1E293B;
    padding: 8px 12px;
    text-align: left;
}

th {
    background-color: #131E32;
    color: #38BDF8;
}

/* Alert boxes */
.alert-box {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
    color: #FCA5A5;
}

.success-box {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
    color: #86EFAC;
}

.info-box {
    background: rgba(56, 189, 248, 0.08);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
    color: #BAE6FD;
}

/* Hide streamlit header decorations */
header[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* Custom scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0B1120;
}
::-webkit-scrollbar-thumb {
    background: #1E293B;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #334155;
}
</style>
"""
