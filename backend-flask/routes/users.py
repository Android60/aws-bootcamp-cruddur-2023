from flask import request
from lib.helpers import check_errors
from flask_cors import cross_origin

from services.user_activities import UserActivities
from services.show_activity import ShowActivity
from services.users_short import UsersShort
from services.update_profile import UpdateProfile

def load(app):
    @app.route("/api/activities/@<string:handle>", methods=['GET'])
    def data_handle(handle):
        model = UserActivities.run(handle)
        return check_errors(model)

    @app.route("/api/activities/<string:activity_uuid>", methods=['GET'])
    def data_show_activity(activity_uuid):
        data = ShowActivity.run(activity_uuid=activity_uuid)
        return data, 200
    
    @app.route("/api/users/@<string:handle>/short", methods=['GET'])
    def data_users_short(handle):
        data = UsersShort.run(handle)
        return data, 200
    
    @app.route("/api/profile/update", methods=['POST','OPTIONS'])
    @cross_origin()
    def data_update_profile():
        bio          = request.json.get('bio',None)
        display_name = request.json.get('display_name',None)
        if request.environ["isAuthenticated"]==True:
            cognito_user_id = request.environ["sub"]
            model = UpdateProfile.run(
            cognito_user_id=cognito_user_id,
            bio=bio,
            display_name=display_name
            )
            return check_errors(model)
        else:
            return {}, 401