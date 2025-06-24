#!/bin/bash
set -e

EXTERNAL_DIR="external"
MICROPYTHON_DIR="${EXTERNAL_DIR}/micropython"
MICROPYTHON_REPO="https://github.com/micropython/micropython.git"
MICROPYTHON_TAG="v1.22.2"

# Verifica se o submódulo já foi inicializado
if [ ! -d "${MICROPYTHON_DIR}/.git" ]; then
    echo "Inicializando submódulo do MicroPython..."
    git submodule init "${MICROPYTHON_DIR}"
    git submodule update --recursive --remote "${MICROPYTHON_DIR}"
fi

# Faz checkout da tag e atualiza submódulos
echo "Configurando versão do MicroPython..."
cd "${MICROPYTHON_DIR}"
git fetch --tags
git checkout "${MICROPYTHON_TAG}"
git submodule update --init --recursive
cd -