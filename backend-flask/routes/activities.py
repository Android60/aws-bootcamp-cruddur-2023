from flask import Flask
from flask import request
from flask_cors import cross_origin
from lib.helpers import check_errors

from services.home_activities import HomeActivities
from services.notifications_activities import NotificationsActivities
from services.create_activity import CreateActivity
from services.search_activities import SearchActivities
from services.create_reply import CreateReply


def load(app):
    @app.route("/api/activities/home", methods=['GET'])
    def data_home():
        if request.environ["isAuthenticated"]==True:
            # Request is authenticated
            cognito_user_id  = request.environ["sub"]
            app.logger.debug("Got from Middleware: User auth is")
            app.logger.debug(request.environ["isAuthenticated"])
            app.logger.debug(request.environ["sub"]) # Log current userid
            data = HomeActivities.run(cognito_user_id=cognito_user_id)
        else:
            # Request is not authenticated
            # app.logger.debug("This request is not authenticated: ")
            # app.logger.debug(request.environ["tokenVerifyError"])
            _ = request.data
            data = HomeActivities.run()
        return data, 200

    @app.route("/api/activities/notifications", methods=['GET'])
    def data_notifications():
        data = NotificationsActivities.run()
        return data, 200



    @app.route("/api/activities/search", methods=['GET'])
    def data_search():
        term = request.args.get('term')
        model = SearchActivities.run(term)
        return check_errors(model)

    @app.route("/api/activities", methods=['POST','OPTIONS'])
    @cross_origin()
    def data_activities():
        user_handle  = request.json['user_handle']
        message = request.json['message']
        ttl = request.json['ttl']
        model = CreateActivity.run(message, user_handle, ttl)
        return check_errors(model)


    @app.route("/api/activities/<string:activity_uuid>/reply", methods=['POST','OPTIONS'])
    @cross_origin()
    def data_activities_reply(activity_uuid):
        user_handle  = 'andrewbrown'
        message = request.json['message']
        model = CreateReply.run(message, user_handle, activity_uuid)
        return check_errors(model)