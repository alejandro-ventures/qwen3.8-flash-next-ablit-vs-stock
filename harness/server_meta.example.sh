#!/bin/bash
# Generic metadata capture: commit, image digest, serve-path suffix and optional sidecar hash only.
# Usage: REPO=<recipe-checkout> CONTAINER=<container-name> SIDECAR=<optional-file> bash harness/server_meta.example.sh A1
set -eu
: "${REPO:?set REPO to the recipe checkout}"
: "${CONTAINER:?set CONTAINER to the serving container}"
label="${1:?supply a session letter}"
case "$label" in A0|A1|A2|B1|B2|C1) ;; *) exit 2 ;; esac
mkdir -p "runs/$label"
{
  echo "repo commit: $(git -C "$REPO" rev-parse HEAD)"
  echo "image digest: $(docker image inspect "$(docker inspect "$CONTAINER" --format '{{.Image}}')" --format '{{json .RepoDigests}}' | sed -n 's/.*@\(sha256:[0-9a-f]\{64\}\).*/\1/p')"
  echo "serve-path suffix: $(docker inspect "$CONTAINER" --format '{{json .Config.Cmd}}' | sed -n 's/.*\(ablit-[0-9a-f]*-[0-9a-f]*\).*/\1/p')"
  if [ -n "${SIDECAR:-}" ]; then
    echo "sidecar sha256: $(sha256sum "$SIDECAR" | cut -d' ' -f1)"
  fi
} > "runs/$label/server_meta.txt"
