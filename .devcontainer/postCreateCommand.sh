#!/bin/bash
sudo apt update
sudo apt install -y postgresql-client
pip3 install -r backend-flask/requirements.txt
pip3 install cfn-lint
npm install aws-cdk -g
cd thumbing-serverless-cdk
npm i
wget -P /tmp/ https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
unzip /tmp/aws-sam-cli-linux-x86_64.zip -d /tmp/sam-installation
sudo /tmp/sam-installation/install