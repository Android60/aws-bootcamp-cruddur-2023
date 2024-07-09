FROM python:3.10-slim-buster AS builder

WORKDIR backend-flask
COPY . .
RUN pip3 install -r requirements.txt
RUN apt update && apt install -y curl

# FROM builder AS dev
ENV FLASK_ENV=development
EXPOSE ${PORT}
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]
