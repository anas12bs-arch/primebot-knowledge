#!/bin/bash
# Sync local: hace pull del repo GitHub (cache fuera de la boveda) y copia
# solo las notas nuevas/cambiadas a wiki/auto-research/ dentro de la boveda.
# La boveda de Obsidian NUNCA se convierte en repo git -- se queda intacta,
# solo recibe archivos .md ya generados.
set -euo pipefail

REPO_URL="https://github.com/anas12bs-arch/primebot-knowledge.git"
CACHE_DIR="$HOME/.primebot-knowledge-cache"
VAULT_DIR="/Users/anasahmadouch/Library/Mobile Documents/iCloud~md~obsidian/Documents/Anas second brain/wiki/auto-research"

if [ ! -d "$CACHE_DIR/.git" ]; then
  echo "[sync] Clonando repo por primera vez..."
  git clone --quiet "$REPO_URL" "$CACHE_DIR"
fi

cd "$CACHE_DIR"
git pull --quiet

mkdir -p "$VAULT_DIR"
rsync -a --update "$CACHE_DIR/notes/" "$VAULT_DIR/"

COUNT=$(find "$CACHE_DIR/notes" -name "*.md" -newer "$VAULT_DIR/.last_sync" 2>/dev/null | wc -l | tr -d ' ' || echo "?")
touch "$VAULT_DIR/.last_sync"

echo "[sync] $(date -u '+%Y-%m-%d %H:%M UTC') - sync completado"
