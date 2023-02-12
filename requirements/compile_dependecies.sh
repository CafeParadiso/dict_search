#!/bin/bash

pip list --not-required --format freeze > dev-requirements.in && \
pip install pip-tools && \
pip-compile dev-requirements.in -o dev-requirements.txt --generate-hashes