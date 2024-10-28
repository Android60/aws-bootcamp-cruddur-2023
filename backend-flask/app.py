from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
import os
from lib.cognito_jwt_middleware import middleware # For JWT verification
from lib.helpers import check_errors

from services.users_short import *
from services.home_activities import *
from services.notifications_activities import *
from services.user_activities import *
from services.create_activity import *
from services.create_reply import *
from services.search_activities import *
from services.message_groups import *
from services.messages import *
from services.create_message import *
from services.show_activity import *
from services.update_profile import *

from lib.cognito_jwt_token import CognitoJwtToken, TokenVerifyError
#--------Cloudwatch--------
from lib.logging import init_cloudwatch
from time import strftime
#--------Cloudwatch--------

#--------Honeycomb, XRay, Rollbar--------
from lib.telemetry import init_honeycomb, init_xray, init_rollbar
#--------Honeycomb, XRay, Rollbar--------



# Configuring Logger to Use CloudWatch
LOGGER = init_cloudwatch('cruddur')
LOGGER.info("Test log")
#--------Cloudwatch--------

import routes.activities

app = Flask(__name__)

cognito_jwt_token = CognitoJwtToken(
  user_pool_id=os.getenv("AWS_COGNITO_USER_POOL_ID"),
  user_pool_client_id=os.getenv("AWS_COGNITO_USER_POOL_CLIENT_ID"),
  region=os.getenv("AWS_DEFAULT_REGION")
)

# Configure middleware for JWT token verification
app.wsgi_app = middleware(app.wsgi_app)

# Initialize X-Ray
xray_url = os.getenv("AWS_XRAY_URL")
init_xray(app, xray_url)

# Initialize Honeycomb automatic instrumentation with Flask
init_honeycomb(app)

# Initialize Rollbar
rollbar_access_token = os.getenv('ROLLBAR_ACCESS_TOKEN')
init_rollbar(app, rollbar_access_token)

frontend = os.getenv('FRONTEND_URL')
backend = os.getenv('BACKEND_URL')
origins = [frontend, backend]
cors = CORS(
  app, 
  resources={r"/api/*": {"origins": origins}},
  expose_headers="location,link",
  allow_headers=['content-type','if-modified-since','traceparent','tracesttate','Authorization'],
  methods="OPTIONS,GET,HEAD,POST"
)

@app.route('/api/health')
def health_check():
  return {'success': True}, 200

# @app.route('/rollbar/test')
# def rollbar_test():
#     rollbar.report_message('Hello World!', 'warning')
#     return "Hello World!"

# CloudWatch Logs
@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    LOGGER.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response

routes.activities.load(app)

@app.route("/api/message_groups", methods=['GET'])
def data_message_groups():
  try:
    cognito_user_id  = request.environ["sub"]
    model = MessageGroups.run(cognito_user_id=cognito_user_id)
    return check_errors(model)
  except TokenVerifyError as e:
    return {}, 401

@app.route("/api/messages/<string:message_group_uuid>", methods=['GET'])
def data_messages(message_group_uuid):
  try:
    cognito_user_id  = request.environ["sub"]
    model = Messages.run (cognito_user_id=cognito_user_id, message_group_uuid=message_group_uuid)
    return check_errors(model)
  except TokenVerifyError as e:
    return {}, 401
  
@app.route("/api/messages", methods=['POST','OPTIONS'])
@cross_origin()
def data_create_message():
  try:
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
  except TokenVerifyError as e:
    return {}, 401


@app.route("/api/users/@<string:handle>/short", methods=['GET'])
def data_users_short(handle):
  data = UsersShort.run(handle)
  return data, 200



@app.route("/api/profile/update", methods=['POST','OPTIONS'])
@cross_origin()
def data_update_profile():
  bio          = request.json.get('bio',None)
  display_name = request.json.get('display_name',None)
  try:
    cognito_user_id = request.environ["sub"]
    model = UpdateProfile.run(
      cognito_user_id=cognito_user_id,
      bio=bio,
      display_name=display_name
    )
    return check_errors(model)
  except TokenVerifyError as e:
    # unauthenicatied request
    app.logger.debug(e)
    return {}, 401

if __name__ == "__main__":
  app.run(debug=True)