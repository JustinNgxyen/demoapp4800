from flask import Flask, jsonify, render_template, Response
from pymongo import MongoClient
from bson import ObjectId
from bson.json_util import dumps
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Replace with your MongoDB Atlas connection string
uri = os.getenv("MONGODB_URI")
print(uri)
# Connect to MongoDB
client = MongoClient(uri)

# Select database and collection
db = client["premier-league"]
collection = db["stats"]

# collection.insert_one({"team": "Liverpool", "name": " Hugo Ekitike", "Goals": 10, "Assists": 2, "Rating": 7.03, "img": "https://cdn-img.zerozero.pt/img/jogadores/new/00/07/820007_hugo_ekitike_20250920114821.png"})
# collection.insert_one({"team": "Liverpool", "name": "Cody Gakpo", "Goals": 5, "Assists": 3, "Rating": 7.26, "img": "https://cdn-img.zerozero.pt/img/jogadores/new/85/87/528587_cody_gakpo_20251022235835.png"})
# collection.insert_one({"team": "Liverpool", "name": "Dominik Szoboszlai", "Goals": 4, "Assists": 2, "Rating": 7.42, "img": "https://img.uefa.com/imgml/TP/players/17/2026/324x324/250104066.jpg"})
# collection.insert_one({"team": "Liverpool", "name": "Mohamed Salah", "Goals": 4, "Assists": 6, "Rating": 7.06, "img": "https://img.uefa.com/imgml/TP/players/1/2026/324x324/250052469.jpg"})
# collection.insert_one({"team": "Liverpool", "name": "Ryan Gravenberch", "Goals": 4, "Assists": 2, "Rating": 7.45, "img": "https://cdn-img.zerozero.pt/img/jogadores/new/66/31/596631_ryan_gravenberch_20251102003135.png"})

@app.route("/")
def start_index():
    return render_template("index.html")

def to_player(doc, stat_key):
    if not doc:
        return None
    return {
        "name": doc.get("name"),
        "value": doc.get(stat_key),
        "image_url": doc.get("img"),
    }

def top_n(team_q, sort_key, n=3):
    docs = list(collection.find(team_q).sort(sort_key, -1).limit(n))
    return [
        {
            "name": d.get("name"),
            "value": d.get(sort_key),
            "image_url": d.get("img"),
        }
        for d in docs
    ]

@app.route("/search/<team>")
def search_team(team):
    team_q = {"team": {"$regex": f"^{team}$", "$options": "i"}}

    return jsonify({
        "team": team,
        "top_goalscorers": top_n(team_q, "Goals", 3),
        "top_assisters": top_n(team_q, "Assists", 3),
        "top_rated": top_n(team_q, "Rating", 3),
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
