from werkzeug.wrappers import Request, Response, ResponseStream
import logging
import os
from lib.cognito_jwt_token import CognitoJwtToken, TokenVerifyError

class middleware():
    """
    Cognito JWT verification middleware
    """
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        LOGGER = logging.getLogger(__name__) # Initialize Logger
        LOGGER.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler() # Log to console
        LOGGER.addHandler(console_handler)
        # LOGGER.info("Middleware got the call")
        request = Request(environ)
        # LOGGER.info(request.environ)
        cognito_jwt_token = CognitoJwtToken(
        user_pool_id=os.getenv("AWS_COGNITO_USER_POOL_ID"),
        user_pool_client_id=os.getenv("AWS_COGNITO_USER_POOL_CLIENT_ID"),
        region=os.getenv("AWS_DEFAULT_REGION")
        )
        # LOGGER.info(request.headers)
        access_token = CognitoJwtToken.extract_access_token(request.headers)
        try:
            # Request is authenticated
            claims = cognito_jwt_token.verify(access_token)
            # LOGGER.info("Middleware: This request is authenticated")
            # LOGGER.info(claims)
            # LOGGER.info(claims['username'])
            environ["isAuthenticated"] = True
            environ["username"] = claims['username']
            environ["sub"] = claims['sub']
        except TokenVerifyError as e:
            # Request is not authenticated
            # LOGGER.info("Middleware: This request is not authenticated")
            LOGGER.info(e)
            environ["isAuthenticated"] = False
        return self.app(environ, start_response)
        # res = Response(u'Authorization failed', mimetype= 'text/plain', status=401)
        # return res(environ, start_response)