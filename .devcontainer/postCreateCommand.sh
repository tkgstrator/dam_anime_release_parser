#!/bin/zsh

sudo chown -R python:python node_modules
python -m pip install -r requirements.txt
curl -fsSL https://bun.sh/install | bash
echo 'export PATH=$PATH:$HOME/.bun/bin' >> ~/.zprofile