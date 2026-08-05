#!/usr/bin/env bash
# Capture one sweep per channel.  ./FINAL_MEASUREMENTS/arduino-rig/sweep.sh
# Type the channel label, press enter, wait ~20 s. Blank label or Ctrl-C to stop.
set -u
PORT=${PORT:-/dev/ttyACM0}
OUT=$(cd "$(dirname "$0")/../data/R2_sweeps" && pwd)
sudo -n stty -F "$PORT" 115200 raw -echo
while true; do
  read -rp $'\nchannel label (e.g. s1_D1_G_seat1), blank to quit: ' L
  [ -z "$L" ] && { echo "done"; break; }
  # Labels go into a shell run under sudo and into a filename. Allow only
  # characters that are safe in both: no quotes, no slashes, no dots.
  if ! [[ $L =~ ^[A-Za-z0-9_-]{1,39}$ ]]; then
    echo "!! labels may use letters, digits, underscore and hyphen only (max 39)"
    continue
  fi
  f="$OUT/$L.csv"
  [ -e "$f" ] && { echo "!! $L.csv already exists, pick another name"; continue; }
  echo "sweeping... (~20 s)"
  sudo -n env LABEL="$L" PORT="$PORT" sh -c \
    '{ sleep 1; printf "%s\n" "$LABEL" > "$PORT"; } & timeout 45 cat "$PORT"' \
    > "$f" 2>/dev/null
  n=$(grep -cE '^[0-9]+,' "$f" || true)
  grep -E '^# i_max|WARNING' "$f" || true
  if [ "$n" -eq 63 ]; then echo "saved $L.csv  ($n points)"
  else echo "!! only $n points, NOT a clean sweep - check wiring and redo"; fi
done
