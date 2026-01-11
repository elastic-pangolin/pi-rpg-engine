#!/usr/bin/env bash
rm -R build/
rm -R .venv/
rm -R *.egg-info/
if command -v python3 &> /dev/null; then
    python3 -m venv .venv
elif command -v python &> /dev/null; then
    python -m venv .venv
else
    echo "Python not installed. Please install Python and then rerun this script."
    exit 1
fi
source .venv/bin/activate && \
pip install --upgrade pip && \
pip install --only-binary=:all: pillow && \
pip install kivy[base] --no-deps && \
pip install . && \
pip freeze && \
cyclonedx-py environment -o /tmp/bom.xml && \
deactivate
