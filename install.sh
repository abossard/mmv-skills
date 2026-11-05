#!/bin/bash
# Link every mmv-* skill folder into a Claude Code skills directory (default ~/.claude/skills).
# Existing links are replaced; a real folder with the same name is left alone. Uninstall: delete the links.
set -e
here="$(cd "$(dirname "$0")" && pwd)"
dest="${1:-$HOME/.claude/skills}"
mkdir -p "$dest"
for d in "$here"/mmv-*/; do
  name="$(basename "$d")"
  if [ -e "$dest/$name" ] && [ ! -L "$dest/$name" ]; then
    echo "skipped $dest/$name (exists and is not a link)"
    continue
  fi
  ln -sfn "${d%/}" "$dest/$name"
  echo "linked $dest/$name"
done
