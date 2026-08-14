#!/bin/sh
# Fonte única do padrão de dados pessoais bloqueados neste repo -- usado
# tanto pelo hook local (.githooks/pre-commit, roda no commit) quanto pelo
# GitHub Action (.github/workflows/scan-dados-pessoais.yml, roda no
# push/PR, server-side -- não depende de ninguém ter rodado setup.sh no
# clone local). NUNCA duplicar a lista de padrões em outro lugar -- editar
# só aqui, os dois consumidores chamam este script.
#
# Uso:
#   scan-dados-pessoais.sh <arquivo1> [arquivo2 ...]   -- escaneia só esses
#   scan-dados-pessoais.sh                              -- escaneia toda a
#                                                          árvore rastreada
#
# POSIX sh puro, sem grep -P nem extensões GNU -- precisa rodar igual no
# hook local (macOS, BSD grep/sed) e no runner do GitHub Action (Ubuntu,
# GNU grep/sed).

PATTERNS='escutedentro\|/Users/[a-z]\|Outputs Claude\|_edm_\|64\.115\.123\|@gmail\.com'

# Arquivos deste próprio mecanismo de proteção -- nunca escanear, ou o
# script se auto-bloqueia (a definição do padrão CONTÉM os literais que ele
# procura). Path relativo à raiz do repo.
EXCLUDE='scripts/scan-dados-pessoais.sh .githooks/pre-commit'

is_excluded() {
  for ex in $EXCLUDE; do
    [ "$1" = "$ex" ] && return 0
  done
  return 1
}

# Extensões cobertas: inclui .py e .gs -- gap real encontrado em 14/08, o
# hook original não cobria os scripts Python/Apps Script deste repo.
# Filtro aplicado sempre, tanto em lista de arquivos passada por argumento
# (hook local, arquivos staged) quanto em git ls-files (CI, árvore inteira)
# -- nunca rodar grep em arquivo binário/sem extensão reconhecida.
if [ "$#" -gt 0 ]; then
  CANDIDATES="$*"
else
  CANDIDATES=$(git ls-files)
fi
FILES=$(printf '%s\n' $CANDIDATES | grep -E '\.(md|json|js|ts|html|txt|sh|py|gs|yml|yaml)$')

FOUND=""
for file in $FILES; do
  [ -f "$file" ] || continue
  is_excluded "$file" && continue
  hits=$(grep -n "$PATTERNS" "$file" 2>/dev/null)
  if [ -n "$hits" ]; then
    FOUND="$FOUND\n  $file:\n$hits"
  fi
done

if [ -n "$FOUND" ]; then
  printf "\n🚫 Dados pessoais detectados:\n"
  printf "$FOUND\n"
  printf "\nSubstituir pelos placeholders antes de commitar.\n"
  printf "Padrões bloqueados: escutedentro, /Users/, _edm_, @gmail.com, CNPJ do Escute Dentro, Outputs Claude\n\n"
  exit 1
fi

exit 0
