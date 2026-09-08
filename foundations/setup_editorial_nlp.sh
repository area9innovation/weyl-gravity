#!/usr/bin/env bash
set -euo pipefail
# Usage: bash foundations/setup_editorial_nlp.sh /absolute/path/to/environment
# Requires Python 3.12 with pip. No root permissions or GPU packages are needed.
editorial_env="${1:?Pass a new dedicated environment directory}"
editorial_root="$(cd "$(dirname "$0")/.." && pwd)"
python3 -m venv --without-pip "$editorial_env"
python3 -m pip --python "$editorial_env/bin/python" install -r "$editorial_root/foundations/editorial-nlp-requirements.txt"
python3 -m pip --python "$editorial_env/bin/python" install --no-deps keyphrase-vectorizers==0.0.13 'https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl#sha256=1932429db727d4bff3deed6b34cfc05df17794f4a52eeb26cf8928f7c1a0fb85'
