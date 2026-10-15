#!/bin/sh
# Copie les fichiers partagés dans les skills qui s'en servent.
# shared/ est la source ; chaque dossier de skill garde sa copie pour marcher seul
# (installation par copie). tests/run.sh échoue si une copie a dérivé.
set -e
cd "$(dirname "$0")/.."
cp shared/hookscore_fr.py shared/hookscore_fr_poids.json skills/insta-reel/
cp shared/slop-fr.json skills/insta-humain/
echo "copies à jour"
