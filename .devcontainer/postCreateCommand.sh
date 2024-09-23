#!/bin/bash
sudo apt update
sudo apt install -y postgresql-client
pip3 install -r backend-flask/requirements.txt
pip3 install cfn-lint
npm install aws-cdk -g
cd thumbing-serverless-cdk
npm i