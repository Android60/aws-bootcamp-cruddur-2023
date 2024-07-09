# Week 1 — App Containerization

## Required homework

### Run the Dockerfile CMD as an external script

I've added "command" attribute with value "/frontend-react-js/entrypoint.sh" to Docker Compose file.

### Use multi-stage building for a Dockerfile build
Implementing multi-stage building was as easy as specifying multiple FROM statements in Dockerfile:
```
...
FROM python:3.10-slim-buster AS builder
# Stage 1
...
FROM builder AS dev
# Stage 2
```