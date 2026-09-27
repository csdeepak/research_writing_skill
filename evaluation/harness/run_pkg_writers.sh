#!/usr/bin/env bash
# Phase 6 downstream writers: same skill writer, evidence package only. Usage: run_pkg_writers.sh P1 P2 ...
set -u
cd "$(dirname "$0")/../.." || exit 1
W="python evaluation/harness/writers.py"
one() {
  P=$1; T=$2; C="skillpkg-$T"
  $W prep "$P" "$C" --package "evaluation/evidence_agent/packages/$T/$P" && \
  $W skill-draft "$P" --cond "$C" && $W skill-review "$P" --cond "$C" && \
  $W skill-revise "$P" --cond "$C" && $W collect "$P" "$C"
  echo "FINISHED $C $P rc=$?"
}
export -f one; export W
for P in "$@"; do printf "%s cheap\n%s strong\n" "$P" "$P"; done | xargs -P 3 -L 1 bash -c 'one $0 $1'
