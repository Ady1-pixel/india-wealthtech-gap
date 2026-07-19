"""Central configuration: app roster, category labels, paths, topic lexicons."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"

REVIEWS_PER_APP = 2500
LANG = "en"
COUNTRY = "in"

# firm: display name used to join against NSE active-client data
# segment: "broker" (maps to NSE active clients) or "platform" (MF/wealth only)
# category: "fintech" (digital-native) or "incumbent" (bank/legacy-affiliated)
APPS = [
    {"firm": "Groww",            "app_id": "com.nextbillion.groww",          "segment": "broker",   "category": "fintech"},
    {"firm": "Zerodha",          "app_id": "com.zerodha.kite3",              "segment": "broker",   "category": "fintech"},
    {"firm": "Angel One",        "app_id": "com.msf.angelmobile",            "segment": "broker",   "category": "fintech"},
    {"firm": "ICICIdirect",      "app_id": "com.icicidirect.idirectsuper",   "segment": "broker",   "category": "incumbent"},
    {"firm": "Upstox",           "app_id": "in.upstox.app",                  "segment": "broker",   "category": "fintech"},
    {"firm": "Kotak Neo",        "app_id": "com.kotak.neo",                  "segment": "broker",   "category": "incumbent"},
    {"firm": "HDFC Securities",  "app_id": "com.cloudtradetech.sky",         "segment": "broker",   "category": "incumbent"},
    {"firm": "SBI Securities",   "app_id": "com.msf.sbicap.securities",      "segment": "broker",   "category": "incumbent"},
    {"firm": "Dhan",             "app_id": "com.dhan.live",                  "segment": "broker",   "category": "fintech"},
    {"firm": "Motilal Oswal",    "app_id": "mosl.powerapp.com",              "segment": "broker",   "category": "incumbent"},
    {"firm": "Paytm Money",      "app_id": "com.paytmmoney",                 "segment": "broker",   "category": "fintech"},
    {"firm": "Mirae Asset Sharekhan", "app_id": "com.sharekhan.androidsharemobile", "segment": "broker", "category": "incumbent"},
    {"firm": "5paisa",           "app_id": "com.fivepaisa.trade",            "segment": "broker",   "category": "fintech"},
    # Wealth/MF platforms: benchmarked on experience, excluded from the growth model
    {"firm": "Coin by Zerodha",  "app_id": "com.zerodha.coin",               "segment": "platform", "category": "fintech"},
    {"firm": "ET Money",         "app_id": "com.smartspends",                "segment": "platform", "category": "fintech"},
    {"firm": "Kuvera",           "app_id": "com.gooogle.android.kuvera.app", "segment": "platform", "category": "fintech"},
    {"firm": "INDmoney",         "app_id": "in.indwealth",                   "segment": "platform", "category": "fintech"},
]

# Keyword lexicons for tagging what a review is talking about.
# Deliberately simple and auditable: a review is tagged with a theme if any
# pattern matches (case-insensitive, word-ish boundaries applied in code).
TOPIC_LEXICONS = {
    "ui_ux": [
        "ui", "ux", "interface", "design", "layout", "navigation", "confusing",
        "clean", "intuitive", "user friendly", "user-friendly", "easy to use",
        "clutter", "theme", "dark mode", "look and feel", "smooth experience",
    ],
    "performance": [
        "crash", "hang", "lag", "slow", "freeze", "stuck", "loading", "glitch",
        "bug", "not working", "doesn't work", "server down", "downtime",
        "technical issue", "error",
    ],
    "onboarding_kyc": [
        "kyc", "onboarding", "account opening", "signup", "sign up", "register",
        "verification", "documents", "aadhaar", "pan card", "activation",
    ],
    "customer_support": [
        "customer care", "customer support", "support team", "helpline",
        "no response", "ticket", "complaint", "call center", "chat support",
        "grievance", "no one responds",
    ],
    "charges_fees": [
        "charges", "brokerage", "fees", "hidden charges", "amc", "commission",
        "expensive", "pricing", "deducted", "annual charge",
    ],
    "ai_features": [
        "ai", "artificial intelligence", "chatbot", "bot", "recommendation",
        "advisory", "robo", "smart suggestion", "insights", "screener",
        "analytics", "prediction", "algo",
    ],
    "trust_security": [
        "fraud", "scam", "trust", "security", "otp", "unauthorised",
        "unauthorized", "data leak", "privacy", "safe", "blocked my account",
    ],
}
