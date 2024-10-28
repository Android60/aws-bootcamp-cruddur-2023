from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
import os
from lib.cognito_jwt_middleware import middleware # For JWT verification

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
#--------Honeycomb--------
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
#--------Honeycomb--------

#--------X-RAY--------
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
#--------X-RAY--------

#--------Rollbar--------
import rollbar
import rollbar.contrib.flask
from flask import got_request_exception
#--------Rollbar--------


# Configuring Logger to Use CloudWatch
LOGGER = init_cloudwatch('cruddur')
LOGGER.info("Test log")
#--------Cloudwatch--------

# Initialize tracing and an exporter that can send data to Honeycomb
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
simple_processor = SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
# provider.add_span_processor(simple_processor) # Debugging
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# X-Ray
xray_url = os.getenv("AWS_XRAY_URL")
xray_recorder.configure(service='backend-flask', dynamic_naming=xray_url)

app = Flask(__name__)

cognito_jwt_token = CognitoJwtToken(
  user_pool_id=os.getenv("AWS_COGNITO_USER_POOL_ID"),
  user_pool_client_id=os.getenv("AWS_COGNITO_USER_POOL_CLIENT_ID"),
  region=os.getenv("AWS_DEFAULT_REGION")
)

# Configure middleware for JWT token verification
app.wsgi_app = middleware(app.wsgi_app)

# Initialize X-Ray
XRayMiddleware(app, xray_recorder)

# Initialize automatic instrumentation with Flask
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# Initialize Rollbar
rollbar_access_token = os.getenv('ROLLBAR_ACCESS_TOKEN')
with app.app_context():
  rollbar.init(
      # access token
      rollbar_access_token,
      # environment name
      'production',
      # server root directory, makes tracebacks prettier
      root=os.path.dirname(os.path.realpath(__file__)),
      # flask already sets up logging
      allow_logging_basic_config=False)
  # send exceptions from `app` to rollbar, using flask's signal system.
  got_request_exception.connect(rollbar.contrib.flask.report_exception, app)

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

def check_errors(model):
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200

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

@app.route("/api/activities/home", methods=['GET'])
def data_home():
  access_token = CognitoJwtToken.extract_access_token(request.headers)
  try:
    # Request is authenticated
    claims = cognito_jwt_token.verify(access_token)
    app.logger.debug("This request is authenticated")
    #---Decouple JWT verification with middleware---
    app.logger.debug("Got from Middleware: User auth is")
    app.logger.debug(request.environ["isAuthenticated"])
    app.logger.debug(request.environ["sub"]) # Log current userid
    #---Decouple JWT verification with middleware---
    # app.logger.debug(claims)
    # app.logger.debug(claims['username'])
    data = HomeActivities.run(cognito_user_id=claims['username'])
  except TokenVerifyError as e:
    # Request is not authenticated
    # app.logger.debug("This request is not authenticated")
    _ = request.data
    data = HomeActivities.run()
  return data, 200

@app.route("/api/activities/notifications", methods=['GET'])
def data_notifications():
  data = NotificationsActivities.run()
  return data, 200

@app.route("/api/users/@<string:handle>/short", methods=['GET'])
def data_users_short(handle):
  data = UsersShort.run(handle)
  return data, 200

@app.route("/api/activities/@<string:handle>", methods=['GET'])
def data_handle(handle):
  model = UserActivities.run(handle)
  return check_errors(model)

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

@app.route("/api/activities/<string:activity_uuid>", methods=['GET'])
def data_show_activity(activity_uuid):
  data = ShowActivity.run(activity_uuid=activity_uuid)
  return data, 200

@app.route("/api/activities/<string:activity_uuid>/reply", methods=['POST','OPTIONS'])
@cross_origin()
def data_activities_reply(activity_uuid):
  user_handle  = 'andrewbrown'
  message = request.json['message']
  model = CreateReply.run(message, user_handle, activity_uuid)
  return check_errors(model)

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