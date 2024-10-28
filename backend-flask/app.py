from flask import Flask
from flask import request
from flask_cors import CORS
import os
from lib.cognito_jwt_middleware import middleware # For JWT verification

import routes.activities
import routes.general
import routes.message
import routes.users
import routes.logger

from lib.cognito_jwt_token import CognitoJwtToken, TokenVerifyError
from lib.cors import init_cors
#--------Cloudwatch--------
from lib.logging import init_cloudwatch

#--------Cloudwatch--------

#--------Honeycomb, XRay, Rollbar--------
from lib.telemetry import init_honeycomb, init_xray, init_rollbar
#--------Honeycomb, XRay, Rollbar--------

# Configuring Logger to Use CloudWatch
LOGGER = init_cloudwatch('cruddur')
LOGGER.info("Test log")
#--------Cloudwatch--------

app = Flask(__name__)

# Configure middleware for JWT token verification
# Requires ENV:
# AWS_COGNITO_USER_POOL_ID
# AWS_COGNITO_USER_POOL_CLIENT_ID
# AWS_DEFAULT_REGION
app.wsgi_app = middleware(app.wsgi_app)

# Initialize telemetry and CORS
xray_url = os.getenv("AWS_XRAY_URL")
rollbar_access_token = os.getenv('ROLLBAR_ACCESS_TOKEN')
init_xray(app, xray_url)
init_honeycomb(app)
init_rollbar(app, rollbar_access_token)
init_cors(app)

routes.activities.load(app)
routes.general.load(app)
routes.message.load(app)
routes.users.load(app)
routes.logger.load(app, LOGGER)

if __name__ == "__main__":
  app.run(debug=True)