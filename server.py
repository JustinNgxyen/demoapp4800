from flask import Flask, jsonify, render_template, request, redirect, abort, session, url_for, flash
from pymongo import MongoClient
from bson import ObjectId
from bson.json_util import dumps
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_key")

uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)
db = client["language-resources"]
resources_col = db["resources"]
users_col = db["users"]
favorites_col = db["favorites"]


# ─── Auth helpers ────────────────────────────────────────────────────────────

def current_user_id():
    """Return ObjectId of the logged-in user, or None."""
    uid = session.get("user_id")
    return ObjectId(uid) if uid else None

def login_required(f):
    """Simple decorator — redirects to /login if not logged in."""
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user_id():
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# ─── Public pages ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ─── Auth routes ──────────────────────────────────────────────────────────────

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in all fields.", "error")
            return render_template("signup.html")

        # Check if email already in use
        if users_col.find_one({"email": email}):
            flash("An account with that email already exists.", "error")
            return render_template("signup.html")

        user = {
            "name": name,
            "email": email,
            "password_hash": generate_password_hash(password),
            "created_at": datetime.utcnow()
        }
        result = users_col.insert_one(user)

        # Log them straight in after signing up
        session["user_id"] = str(result.inserted_id)
        session["user_name"] = name
        return redirect(url_for("browse_resources"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = users_col.find_one({"email": email})
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Incorrect email or password.", "error")
            return render_template("login.html")

        session["user_id"]   = str(user["_id"])
        session["user_name"] = user.get("name", "")
        return redirect(url_for("browse_resources"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/onboarding")
def onboarding():
    return render_template("onboarding.html")


# ─── Resources ────────────────────────────────────────────────────────────────

@app.route("/resources")
def browse_resources():
    q = {}

    languages = request.args.getlist("target_language")
    if languages:
        q["target_language"] = {"$in": languages}

    types = request.args.getlist("type")
    if types:
        q["type"] = {"$in": types}

    levels = request.args.getlist("level")
    if levels:
        q["level"] = {"$in": levels}

    prices = request.args.getlist("price")
    if prices:
        q["price"] = {"$in": prices}

    tags = request.args.getlist("tag")
    if tags:
        q["tags"] = {"$all": tags}

    min_ratings = request.args.getlist("min_rating")
    if min_ratings:
        lowest = min(float(r) for r in min_ratings)
        q["rating"] = {"$gte": lowest}

    search_text = request.args.get("q", "").strip()
    if search_text:
        q["$text"] = {"$search": search_text}

    sort = request.args.get("sort", "top_rated")
    sort_spec = [("rating", -1)]
    if sort == "most_reviewed":
        sort_spec = [("review_count", -1)]
    elif sort == "newest":
        sort_spec = [("created_at", -1)]

    items = list(resources_col.find(q).sort(sort_spec).limit(60))

    # Build a set of favorited resource IDs for the logged-in user
    # so the template can show filled vs. outline hearts
    favorited_ids = set()
    uid = current_user_id()
    if uid:
        favs = favorites_col.find({"user_id": uid}, {"resource_id": 1})
        favorited_ids = {str(f["resource_id"]) for f in favs}

    return render_template("resources.html", resources=items, favorited_ids=favorited_ids)


@app.route("/resources/<rid>")
def resource_detail(rid):
    try:
        obj_id = ObjectId(rid)
    except Exception:
        abort(404)

    item = resources_col.find_one({"_id": obj_id})
    if not item:
        abort(404)

    uid = current_user_id()
    is_favorited = False
    if uid:
        is_favorited = bool(favorites_col.find_one({"user_id": uid, "resource_id": obj_id}))

    return render_template("resource_detail.html", resource=item, is_favorited=is_favorited)


# ─── Favorites ────────────────────────────────────────────────────────────────

@app.route("/favorites")
@login_required
def favorites_page():
    uid = current_user_id()
    favs = list(favorites_col.find({"user_id": uid}))
    resource_ids = [f["resource_id"] for f in favs]
    items = list(resources_col.find({"_id": {"$in": resource_ids}})) if resource_ids else []
    favorited_ids = {str(r["_id"]) for r in items}
    return render_template("favorites.html", resources=items, favorited_ids=favorited_ids)


@app.route("/favorites/add/<rid>", methods=["POST"])
@login_required
def add_favorite(rid):
    uid = current_user_id()
    try:
        resource_id = ObjectId(rid)
    except Exception:
        abort(404)

    favorites_col.update_one(
        {"user_id": uid, "resource_id": resource_id},
        {"$setOnInsert": {"created_at": datetime.utcnow()}},
        upsert=True
    )
    return redirect(request.referrer or "/favorites")


@app.route("/favorites/remove/<rid>", methods=["POST"])
@login_required
def remove_favorite(rid):
    uid = current_user_id()
    try:
        resource_id = ObjectId(rid)
    except Exception:
        abort(404)

    favorites_col.delete_one({"user_id": uid, "resource_id": resource_id})
    return redirect(request.referrer or "/favorites")


# ─── Submit ───────────────────────────────────────────────────────────────────

@app.route("/submit")
def submit():
    return render_template("submit.html")


# ─── Starter packs ────────────────────────────────────────────────────────────

@app.route("/starter-packs")
def starter_packs_overview():
    return render_template("starter_packs.html")

def pick_top_by_type(language, level_choices, per_type=2):
    base_q = {
        "target_language": language.capitalize(),
        "level": {"$in": level_choices}
    }
    types = ["App", "Website", "Video", "Podcast", "Textbook"]
    picks = {}
    for t in types:
        docs = list(resources_col.find({**base_q, "type": t}).sort([("rating", -1), ("review_count", -1)]).limit(per_type))
        if docs:
            picks[t] = docs
    return picks

@app.route("/starter-pack/<language>")
def starter_pack_detail(language):
    language_clean = language.strip().lower()
    display_language = language_clean.capitalize()
    picks = pick_top_by_type(display_language, ["Beginner", "Any"], per_type=2)
    return render_template("starter_pack_detail.html", language=display_language, picks=picks)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)