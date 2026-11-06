#!/usr/bin/env bash
# Tile N evenly spaced frames of a video into one image, each stamped with its timestamp.
# Usage: scripts/contact_sheet.sh VIDEO OUT.png [N=12] [COLS=4]
set -euo pipefail
video=$1 out=$2 n=${3:-12} cols=${4:-4}
rows=$(( (n + cols - 1) / cols ))
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$video")
# Sample at the midpoint of each of n equal slices so we skip the black first frame.
fps=$(python3 -c "print($n / $dur)")
# The fps filter labels each frame with its slice start; add half a slice so the stamp is the real time.
half=$(python3 -c "print($dur / $n / 2)")
ffmpeg -v error -y -i "$video" -vf "fps=$fps,scale=480:-2,drawtext=text='%{pts\:hms\:$half}':x=8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,tile=${cols}x${rows}:padding=4:color=gray" -frames:v 1 "$out"
echo "$out ($n frames from ${dur}s)"
