#!/usr/bin/env bash
# Run writer pipelines for a list of projects. Usage: run_writers.sh plain|skill P1 P2 ...
# Each project runs sequentially through its stages; projects run in parallel (max 3).
set -u
cd "$(dirname "$0")/../.." || exit 1
MODE=$1; shift
W="python evaluation/harness/writers.py"
one() {
  P=$1
  if [ "$MODE" = plain ]; then
    $W prep "$P" plain && $W plain "$P" && $W collect "$P" plain
  else
    $W prep "$P" skill && $W skill-draft "$P" && $W skill-review "$P" && $W skill-revise "$P" && $W collect "$P" skill
  fi
  echo "FINISHED $MODE $P rc=$?"
}
export -f one; export MODE W
printf "%s\n" "$@" | xargs -P 3 -I{} bash -c 'one {}'
