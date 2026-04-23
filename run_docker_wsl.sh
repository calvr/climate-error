#!/bin/bash
# vim: set fileencoding=utf-8 fileformat=unix :
# -*- coding: utf-8 -*-

set -eo pipefail

PYVER="python$(grep -E "requires-python[[:space:]]*=" pyproject.toml | sed -E 's/.*"([^"]+)".*/\1/')"

DOCKER_IMG=mambaorg/micromamba:2.3.1-debian11

docker run --rm --user root -v $PWD:$PWD -w $PWD --ipc=host -it $DOCKER_IMG /bin/bash -lc "
set -eo pipefail
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

export SHAREDIR=\"\$(realpath \"\${PWD}/shared\")\" 
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

export MPLBACKEND=Agg
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

uv pip install --system .[test]
python -m ruff check .
python -m pytest \\
  --junitxml=\$TESTDIR/test-results.xml \\
  --cov=climate_error --cov-branch --cov-report=term-missing \\
  --cov-report xml:\$TESTDIR/test-coverage-results.xml \\
  tests/

uv pip install --system build
python -m build -v --wheel --sdist --outdir \$PKGSDIR
uv pip install --system \$PKGSDIR/*.whl

#uv pip list --format freeze

mkdir -p \$SHAREDIR

cat <<'EOF'

########################################################################
##                                                                    ##
##          INSTRUCTIONS TO GET FIGURES AND OTHER OUTPUTS             ##
##                                                                    ##
########################################################################
##         If you want to save figures, plots, or any other           ##
##         output results, please copy or write them to:              ##
## 
##             \$SHAREDIR
##
##         which resolves to:
##
EOF
printf \"##             %s\\n\" \"\$SHAREDIR\"
cat <<'EOF'
##     
##         like:
##     
##             (base) #  cp experiment_realcase_*.png  \$SHAREDIR/
##     
##         Anything placed in this directory will be available        ##
##         on the host system outside the container.                  ##
##                                                                    ##
########################################################################

EOF

exec bash
"

