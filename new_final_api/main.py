from flask import Flask, render_template
from flask_restful import Api, Resource
from flask_cors import CORS

from new_final import fetch_apps
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

@app.errorhandler(404)
def invalid_route(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(port=8000)
    