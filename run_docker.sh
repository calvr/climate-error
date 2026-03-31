#!/bin/bash
# vim: set fileencoding=utf-8 fileformat=unix :
# -*- coding: utf-8 -*-

set -eo pipefail

PYVER="python$(grep -E "requires-python[[:space:]]*=" pyproject.toml | sed -E 's/.*"([^"]+)".*/\1/')"

DOCKER_IMG=mambaorg/micromamba:2.3.1-debian11

xhost +local:docker
#docker run --rm --user root --net=host -v $PWD:$PWD -w $PWD -it $DOCKER_IMG /bin/bash -lc "
docker run --rm --user root -p 127.0.0.1:42137:42137 \
  -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $PWD:$PWD -w $PWD \
  --ipc=host -it $DOCKER_IMG /bin/bash -lc "
eval \"\$(micromamba shell hook --shell bash)\"
micromamba activate base
micromamba config set --env always_copy True
micromamba config set --env allow_softlinks False
micromamba config set --env always_softlink False
micromamba config set --env offline False
micromamba config set --env override_channels_enabled True
micromamba config set --env channel_priority strict
micromamba config prepend --env channels conda-forge
micromamba config list 

export REPODIR=/opt/repo 
export PKGSDIR=/opt/dist
export TESTDIR=/opt/test

mkdir -p \$REPODIR
mkdir -p \$PKGSDIR
if [ \"\$(realpath \"\${REPODIR}\")\" != \"\$(realpath \"\${PWD}\")\" ]; then
  ( tar --exclude='./debug' -cf - . ) | ( cd \$REPODIR && tar -xf - )
  cd \$REPODIR
fi

PYVER=\"${PYVER}\"
[ -z \"\${PYVER}\" ] && PYVER=python
echo \"PYTHON VERSION: \${PYVER}\"

micromamba deactivate
micromamba activate base
micromamba install -y -c conda-forge \"\${PYVER}\" pip tk uv git jq curl gzip vim psutil
micromamba clean --all --yes
micromamba clean --force-pkgs-dirs --yes
micromamba deactivate
micromamba activate base

export MPLBACKEND=TkAgg
export PYTHONUNBUFFERED=1
export PYTHON_BASIC_REPL=1

mkdir -p \${HOME}/.pip
cat <<EOF > \${HOME}/.pip/pip.conf
[global]
index-url = https://pypi.org/simple
no-input = true
no-cache-dir = true

[install]
no-deps = false
upgrade-strategy = only-if-needed
EOF

git config --global --add safe.directory \"\${REPODIR}\"
python --version

uv pip install --system .

uv pip install --system build
python -m build -v --wheel --sdist --outdir \$PKGSDIR
uv pip install --system \$PKGSDIR/*.whl

uv pip list --format freeze

uv pip install --system .[test]
python -m ruff check .
python -m pytest \\
  --junitxml=\$TESTDIR/test-results.xml \\
  --cov=climate_error --cov-branch --cov-report=term-missing \\
  --cov-report xml:\$TESTDIR/test-coverage-results.xml \\
  tests/

exec bash
"

