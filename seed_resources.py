from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

load_dotenv()

uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)
db = client["language-resources"]
resources = db["resources"]

# Optional: wipe only seed data (safe-ish)
# resources.delete_many({"source": "Seed"})

now = datetime.now(timezone.utc)
seed = [
    # --- Spanish ---
    {
        "title": "SpanishDict",
        "type": "Website",
        "target_language": "Spanish",
        "level": "Any",
        "price": "Free",
        "link": "https://www.spanishdict.com/",
        "description": "Dictionary, grammar guides, and practice tools.",
        "tags": ["Grammar", "Vocabulary", "Writing"],
        "rating": 4.5,
        "review_count": 120000,
        "source": "Seed",
        "created_at": now,
    },
    {
        "title": "Easy Spanish (YouTube)",
        "type": "Video",
        "target_language": "Spanish",
        "level": "Beginner",
        "price": "Free",
        "link": "https://www.youtube.com/@EasySpanish",
        "description": "Street interviews for listening and speaking practice.",
        "tags": ["Listening", "Speaking"],
        "rating": 4.8,
        "review_count": 85000,
        "source": "Seed",
        "created_at": now,
    },
    {
        "title": "Practice Makes Perfect: Spanish Grammar",
        "type": "Textbook",
        "target_language": "Spanish",
        "level": "Beginner",
        "price": "Paid",
        "link": "https://www.mheducation.com/",
        "description": "Workbook-style grammar practice with explanations.",
        "tags": ["Grammar", "Writing"],
        "rating": 4.6,
        "review_count": 40000,
        "source": "Seed",
        "created_at": now,
    },
    {
        "title": "Coffee Break Spanish",
        "type": "Podcast",
        "target_language": "Spanish",
        "level": "Beginner",
        "price": "Free",
        "link": "https://coffeebreaklanguages.com/",
        "description": "Short guided episodes for learners.",
        "tags": ["Listening", "Speaking"],
        "rating": 4.7,
        "review_count": 300000,
        "source": "Seed",
        "created_at": now,
    },

    # --- Japanese ---
    {
        "title": "Tae Kim's Guide to Learning Japanese",
        "type": "Website",
        "target_language": "Japanese",
        "level": "Beginner",
        "price": "Free",
        "link": "https://guidetojapanese.org/learn/",
        "description": "Clear beginner grammar guide.",
        "tags": ["Grammar", "Writing"],
        "rating": 4.7,
        "review_count": 90000,
        "source": "Seed",
        "created_at": now,
    },
    {
        "title": "JapanesePod101",
        "type": "Website",
        "target_language": "Japanese",
        "level": "Any",
        "price": "Freemium",
        "link": "https://www.japanesepod101.com/",
        "description": "Audio lessons and listening practice content.",
        "tags": ["Listening", "Speaking", "Vocabulary"],
        "rating": 4.3,
        "review_count": 110000,
        "source": "Seed",
        "created_at": now,
    },
    {
        "title": "Genki I (Textbook)",
        "type": "Textbook",
        "target_language": "Japanese",
        "level": "Beginner",
        "price": "Paid",
        "link": "https://www.amazon.com/",
        "description": "Popular beginner textbook with workbook.",
        "tags": ["Grammar", "Vocabulary", "Writing"],
        "rating": 4.7,
        "review_count": 60000,
        "source": "Seed",
        "created_at": now,
    },
    {
        "title": "Anki (Spaced Repetition Flashcards)",
        "type": "App",
        "target_language": "Japanese",
        "level": "Any",
        "price": "Freemium",
        "link": "https://apps.ankiweb.net/",
        "description": "Flashcard system for vocab and kanji decks.",
        "tags": ["Vocabulary"],
        "rating": 4.6,
        "review_count": 200000,
        "source": "Seed",
        "created_at": now,
    },

    # --- French ---
    {
        "title": "Lawless French",
        "type": "Website",
        "target_language": "French",
        "level": "Any",
        "price": "Free",
        "link": "https://www.lawlessfrench.com/",
        "description": "Grammar explanations, exercises, and tips.",
        "tags": ["Grammar", "Writing", "Vocabulary"],
        "rating": 4.6,
        "review_count": 50000,
        "source": "Seed",
        "created_at": now,
    },
    {
        "title": "InnerFrench (Podcast)",
        "type": "Podcast",
        "target_language": "French",
        "level": "Intermediate",
        "price": "Free",
        "link": "https://innerfrench.com/",
        "description": "Clear French for listening practice.",
        "tags": ["Listening", "Vocabulary"],
        "rating": 4.8,
        "review_count": 70000,
        "source": "Seed",
        "created_at": now,
    },
    {
        "title": "Assimil French (Textbook)",
        "type": "Textbook",
        "target_language": "French",
        "level": "Beginner",
        "price": "Paid",
        "link": "https://www.assimil.com/",
        "description": "Structured self-study coursebook.",
        "tags": ["Grammar", "Listening", "Speaking"],
        "rating": 4.4,
        "review_count": 25000,
        "source": "Seed",
        "created_at": now,
    },
    {
        "title": "TV5MONDE Learn French",
        "type": "Website",
        "target_language": "French",
        "level": "Beginner",
        "price": "Free",
        "link": "https://apprendre.tv5monde.com/",
        "description": "Videos and activities for learners.",
        "tags": ["Listening", "Vocabulary"],
        "rating": 4.5,
        "review_count": 45000,
        "source": "Seed",
        "created_at": now,
    },
]

result = resources.insert_many(seed)
print(f"Inserted {len(result.inserted_ids)} resources into '{"language-resources"}.resources'")