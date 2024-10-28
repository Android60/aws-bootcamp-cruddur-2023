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
import os
#--------Rollbar--------


def init_honeycomb(app):
    # Initialize tracing and an exporter that can send data to Honeycomb
    provider = TracerProvider()
    processor = BatchSpanProcessor(OTLPSpanExporter())
    simple_processor = SimpleSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    # provider.add_span_processor(simple_processor) # Debugging
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(__name__)
    
    # Initialize automatic instrumentation with Flask
    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()

def init_xray(app, xray_url):
    xray_recorder.configure(service='backend-flask', dynamic_naming=xray_url)
    XRayMiddleware(app, xray_recorder)

def init_rollbar(app, rollbar_access_token):
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