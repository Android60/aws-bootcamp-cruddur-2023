from flask_cors import CORS
import os

def init_cors(app):
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