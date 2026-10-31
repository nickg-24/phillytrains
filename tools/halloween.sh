#!/usr/bin/env bash
# Flip Halloween mode on or off without restarting the display service.
# Usage: bash tools/halloween.sh on|off|status
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FLAG="$ROOT/halloween.on"

case "${1:-}" in
    on)
        touch "$FLAG"
        echo "Halloween mode ON. Takes effect within one slide (a few seconds)."
        ;;
    off)
        rm -f "$FLAG"
        echo "Halloween mode OFF. Takes effect within one slide (a few seconds)."
        ;;
    status)
        if [ -f "$FLAG" ]; then echo "Halloween mode: ON"; else echo "Halloween mode: OFF"; fi
        ;;
    *)
        echo "Usage: bash $0 on|off|status"
        exit 1
        ;;
esac
