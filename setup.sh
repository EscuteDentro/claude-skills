#!/bin/sh
# Instala o pre-commit hook de proteção contra dados pessoais.
# Rodar uma vez após clonar o repo.

git config core.hooksPath .githooks
chmod +x .githooks/pre-commit

echo "✓ Hook instalado. Qualquer commit com dados pessoais será bloqueado automaticamente."
