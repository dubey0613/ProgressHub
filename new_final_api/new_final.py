from flask import Flask, jsonify
import requests
app=Flask(__name__)
 
@app.route("/user_id")
def fetch_apps():
    response=requests.get('http://127.0.0.1:5000/api')

    if response.status_code == 200:
        apps =response.json()
        return jsonify(apps)
    else:
        return jsonify({"Error": "Oops Sorry"})
    
