from flask import Flask, render_template, jsonify
import requests
from key import key
app = Flask(__name__)

search_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/output?parameters"
details_url = "https://maps.googleapis.com/maps/api/place/details/output?parameters"

@app.route("/", methods=["GET"])
def retreive():
	return render_template('a.html')

@app.route("/sendRequest/<string:query>")
def results(query):
	url = "https://www.google.com"
	return jsonify({'result' :url})

if  __name__ == "__main__":
	app.run(debug=True)