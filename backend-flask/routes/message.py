from flask import request
from flask_cors import CORS, cross_origin
from lib.helpers import check_errors

from services.message_groups import MessageGroups
from services.messages import Messages
from services.create_message import CreateMessage

def load(app):
    @app.route("/api/message_groups", methods=['GET'])
    def data_message_groups():
        if request.environ["isAuthenticated"]==True:
            cognito_user_id  = request.environ["sub"]
            model = MessageGroups.run(cognito_user_id=cognito_user_id)
            return check_errors(model)
        else:
            return {}, 401

    @app.route("/api/messages/<string:message_group_uuid>", methods=['GET'])
    def data_messages(message_group_uuid):
        if request.environ["isAuthenticated"]==True:
            cognito_user_id  = request.environ["sub"]
            model = Messages.run (cognito_user_id=cognito_user_id, message_group_uuid=message_group_uuid)
            return check_errors(model)
        else:
            return {}, 401
  
    @app.route("/api/messages", methods=['POST','OPTIONS'])
    @cross_origin()
    def data_create_message():
        if request.environ["isAuthenticated"]==True:
            cognito_user_id  = request.environ["sub"]
            message_group_uuid   = request.json.get('message_group_uuid',None)
            user_receiver_handle = request.json.get('handle',None)
            message = request.json['message']

            if message_group_uuid == None:
                # Create for the first time
                model = CreateMessage.run(
                    mode="create",
                    message=message,
                    cognito_user_id=cognito_user_id,
                    user_receiver_handle=user_receiver_handle
                )
            else:
                # Push onto existing Message Group
                model = CreateMessage.run(
                    mode="update",
                    message=message,
                    message_group_uuid=message_group_uuid,
                    cognito_user_id=cognito_user_id
                )
                return check_errors(model)
        else:
            return {}, 401