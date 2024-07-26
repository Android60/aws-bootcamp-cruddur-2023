# Week 3 — Decentralized Authentication

## Homework Challenges

### Decouple the JWT verify from the application code by writing a  [Flask Middleware](../backend-flask/cognito_jwt_middleware.py)
I've used [JWT verify library](../backend-flask/lib/cognito_jwt_token.py) that was created during this week to write Middleware. It will validate JWT of request and set the appropriate value in `environ` dictionary:
```.py
try:
    # Request is authenticated
    claims = cognito_jwt_token.verify(access_token)
    environ["isAuthenticated"] = True
    environ["username"] = claims['username']
except TokenVerifyError as e:
    # Request is not authenticated
    environ["isAuthenticated"] = False
```

Inside app we can get values from `request.environ` like this:
```.py
app.logger.debug(request.environ["isAuthenticated"])
app.logger.debug(request.environ["username"])
```