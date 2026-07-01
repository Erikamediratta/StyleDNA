from flask import Flask, render_template, request, redirect, url_for, session
import requests
import os
from dotenv import load_dotenv
from agent import ask_style_agent

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET")

BACKEND_URL = os.getenv("BACKEND_URL")


@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("chat"))
    return redirect(url_for("login"))

#SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        data = {
            "fullname": request.form["fullname"],
            "username": request.form["username"],
            "email": request.form["email"],
            "password": request.form["password"],
            "city": request.form["city"]
        }
        response = requests.post(f"{BACKEND_URL}/auth/signup", json=data)

        if response.status_code == 201:
            session["user"] = response.json()
            session["jwt"] = response.cookies.get("jwt")
            return redirect(url_for("chat"))
        else:
            error = response.json().get("error", "Signup failed")
            return render_template("signup.html", error=error)

    return render_template("signup.html")
#LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = {
            "username": request.form["username"],
            "password": request.form["password"]
        }
        response = requests.post(f"{BACKEND_URL}/auth/login", json=data)

        if response.status_code == 200:
            session["user"] = response.json()
            session["jwt"] = response.cookies.get("jwt")
            return redirect(url_for("chat"))
        else:
            error = response.json().get("error", "Login failed")
            return render_template("login.html", error=error)

    return render_template("login.html")

#WARDROBE
@app.route("/wardrobe", methods=["GET", "POST"])
def wardrobe():
    if "user" not in session:
        return redirect(url_for("login"))

    cookies = {"jwt": session.get("jwt")}

    if request.method == "POST":
        item_data = {
            "name": request.form["name"],
            "category": request.form["category"],
            "color": request.form["color"],
            "occasion": request.form.get("occasion", "casual"),
            "season": request.form.get("season", "all"),
            "emoji": request.form.get("emoji", "👕")
        }
        requests.post(f"{BACKEND_URL}/wardrobe/add", json=item_data, cookies=cookies)
        return redirect(url_for("wardrobe"))

    response = requests.get(f"{BACKEND_URL}/wardrobe", cookies=cookies)
    items = response.json() if response.status_code == 200 else []

    return render_template("wardrobe.html", items=items, user=session["user"])

#DELETE WARDROBE
@app.route("/wardrobe/delete/<item_id>")
def delete_wardrobe_item(item_id):
    if "user" not in session:
        return redirect(url_for("login"))

    cookies = {"jwt": session.get("jwt")}
    requests.delete(f"{BACKEND_URL}/wardrobe/{item_id}", cookies=cookies)
    return redirect(url_for("wardrobe"))

#CHAT
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "user" not in session:
        return redirect(url_for("login"))

    if "chat_history" not in session:
        session["chat_history"] = []

    if request.method == "POST":
        question = request.form["question"]
        
        session["chat_history"].append({"role": "user", "content": question})

        answer = ask_style_agent(
            question=question,
            jwt_token=session.get("jwt"),
            user_city=session["user"].get("city", "Delhi"),
            chat_history=session["chat_history"][:-1]
            # 01 excludes the question we just added
        )

        session["chat_history"].append({"role": "assistant", "content": answer})
        session.modified = True

    return render_template("chat.html", 
        chat_history=session.get("chat_history", []),
        user=session["user"])

#CLEAR CHAT
@app.route("/chat/clear")
def clear_chat():
    session["chat_history"] = []
    return redirect(url_for("chat"))

#LOGOUT
@app.route("/logout")
def logout():
    cookies = {"jwt": session.get("jwt")}
    requests.post(f"{BACKEND_URL}/auth/logout", cookies=cookies)
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)