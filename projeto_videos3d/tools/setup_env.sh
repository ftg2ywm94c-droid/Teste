#!/usr/bin/env bash
# Prepara um container novo para o pipeline (o ambiente da sessão é temporário).
# Testado em 2026-11-11: Ubuntu 24.04, 4 núcleos, sem GPU.
set -euo pipefail
BL=/opt/blender-4.2.3-linux-x64
if [ ! -x "$BL/blender" ]; then
  curl -sSfL -o /tmp/blender.tar.xz https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz
  tar xf /tmp/blender.tar.xz -C /opt && rm /tmp/blender.tar.xz
fi
ln -sf "$BL/blender" /usr/local/bin/blender
apt-get update -q && apt-get install -y -q libegl1 libgl1-mesa-dri libegl-mesa0   # Blender headless pede libEGL
pip install -q numpy scipy opencv-python-headless faster-whisper fonttools
blender --version | head -1
