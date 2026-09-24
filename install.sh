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
sdl2path="/usr/lib64/pkgconfig:/usr/share/pkgconfig"
source .venv/bin/activate && \
#pip cache purge && \ # necessary on some reinstalls of kivy
pip install --upgrade pip && \
pip install --only-binary=:all: pillow && \
PKG_CONFIG_PATH=${sdl2path} USE_SDL2=1 pip install --no-binary :all: kivy[base] --no-deps -v 2>&1 | tee kivy_build.log && \
pip install . && \
pip freeze && \
cyclonedx-py environment -o /tmp/bom.xml && \
deactivate
