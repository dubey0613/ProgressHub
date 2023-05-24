from flask import Flask, render_template
from flask_restful import Api, Resource
from flask_cors import CORS
from flask import Flask, jsonify
import requests
from details_soup import UserData

# from new_final import fetch_apps
# from details_soup import UserData


app = Flask(__name__)
CORS(app)
api = Api(app)


# class Details(Resource):
#     def get(self, platform):

#         user_data = UserData(platform)

#         try:
#             return user_data.get_details(platform)
#         except:
#             return {'status': 'Failed', 'details': 'Oops Sorry'}
        


# api.add_resource(Details,'/api/<string:platform>/<string:username>')
@app.route("/username")
def fetch_apps():
    response=requests.get('http://127.0.0.1:5000/api/leetcode/dubey0613')

    if response.status_code == 200:
        apps =response.json()
        return jsonify(apps)
    else:
        return jsonify({"Error": "Oops Sorry"})

@app.errorhandler(404)
def invalid_route(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(port=8000)
    
