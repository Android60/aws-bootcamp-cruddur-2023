#!/bin/bash
sudo apt install -y postgresql-client
pip3 install -r backend-flask/requirements.txt
npm install aws-cdk -g
cd thumbing-serverless-cdk
npm i