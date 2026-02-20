from flask import Flask, jsonify, render_template, Response
from pymongo import MongoClient
from bson import ObjectId
from bson.json_util import dumps

app = Flask(__name__)

# Replace with your MongoDB Atlas connection string
uri = "mongodb+srv://alltimegreats123_db_user:4I8TSszeEm0cmQcO@lunch-db.1g1rjal.mongodb.net/?appName=lunch-db"

# Connect to MongoDB
client = MongoClient(uri)

# Select database and collection
db = client["5-dollar"]
collection = db["food"]

@app.route("/")
def start_index():
    return render_template("index.html")

@app.route("/home")
def welcome():
    return "Welcome to this Demo"

@app.route("/search/<budget>")
def search_food_items(budget):
    budget = float(budget)
    
    foods = collection.find({"price": {"$lte": budget}})
    
    return Response(dumps(foods), mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=False)
