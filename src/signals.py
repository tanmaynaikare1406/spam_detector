"""Rule-based message signals. Edit SIGNALS to tune."""
import re

SIGNALS = [
    ("urgency", r"\b(urgent|immediately|within \d+ ?(hours?|hrs?)|today only|last chance|final notice|act now|expires?)\b", 15, "Urgent wording pressures you to act fast"),
    ("credentials", r"\b(otp|password|pin|cvv|card number|login|verify your|confirm your|update your)\b", 20, "Asks for credentials or codes"),
    ("threat", r"\b(suspended|blocked|deactivated|locked|kyc|penalty|legal action)\b", 15, "Threatens your account"),
    ("reward", r"\b(won|winner|prize|lottery|reward|cashback|free gift|claim)\b", 15, "Offers a reward or prize"),
]

def clean(text):
    t = re.sub(r"<[^>]+>", " ", text.lower())
    t = re.sub(r"(https?://\S+|www\.\S+)", " urltoken ", t)
    t = re.sub(r"\d+", " numtoken ", t)
    return re.sub(r"\s+", " ", t).strip()

def find_signals(text):
    out = []
    for name, pat, w, why in SIGNALS:
        m = re.search(pat, text, re.I)
        if m:
            out.append({"name": name, "reason": f'{why}: "{m.group(0)}"', "matched_text": m.group(0), "weight": w})
    return out
