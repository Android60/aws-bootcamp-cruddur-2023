from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
import os
from lib.cognito_jwt_middleware import middleware # For JWT verification
from lib.helpers import check_errors

import routes.activities
import routes.general
import routes.message
import routes.users

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

# CloudWatch Logs
@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    LOGGER.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response

routes.activities.load(app)
routes.general.load(app)
routes.message.load(app)
routes.users.load(app)

if __name__ == "__main__":
  app.run(debug=True)