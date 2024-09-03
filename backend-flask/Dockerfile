FROM 559077574210.dkr.ecr.us-east-1.amazonaws.com/cruddur-python:3.10-slim-buster AS builder

WORKDIR /backend-flask
COPY . .
RUN pip3 install -r requirements.txt

# FROM builder AS dev
ENV FLASK_DEBUG=1
ENV PYTHONUNBUFFERED=1
EXPOSE ${PORT}
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]
