#!/usr/bin/env bash
# Poll the trusted deployment branch and install only images published for its
# exact commit. This script is installed once and is never executed from a CI
# checkout on the production VM.
set -Eeuo pipefail

readonly branch="refactor/vue3-fastapi-modernization"
readonly repository="https://github.com/thomas5566/workhour.git"
readonly state_dir="${WORKHOUR_RUNNER_STATE:-/opt/workhour/runner-state}"
readonly state_file="$state_dir/deployed-sha"
readonly deploy_script="/opt/workhour/deploy/ubuntu/deploy-application.sh"

for required in git docker flock bash; do
  command -v "$required" >/dev/null || {
    echo "Required command is missing: $required" >&2
    exit 1
  }
done
[[ -x "$deploy_script" ]] || {
  echo "The locally installed deployment script is missing." >&2
  exit 1
}

mkdir -p "$state_dir"
exec 9>"$state_dir/update.lock"
flock -n 9 || exit 0

release_sha="$(git ls-remote --exit-code --heads "$repository" "$branch" | awk 'NR == 1 {print $1}')"
[[ "$release_sha" =~ ^[0-9a-f]{40}$ ]] || {
  echo "The deployment branch did not return a valid commit SHA." >&2
  exit 1
}

if [[ -r "$state_file" && "$(<"$state_file")" == "$release_sha" ]]; then
  exit 0
fi

backend_remote="ghcr.io/thomas5566/workhour-backend:$release_sha"
frontend_remote="ghcr.io/thomas5566/workhour-frontend:$release_sha"
docker pull "$backend_remote"
docker pull "$frontend_remote"

for image in "$backend_remote" "$frontend_remote"; do
  revision="$(docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.revision"}}' "$image")"
  [[ "$revision" == "$release_sha" ]] || {
    echo "Container image revision label mismatch." >&2
    exit 1
  }
done

docker tag "$backend_remote" "workhour-backend:$release_sha"
docker tag "$frontend_remote" "workhour-frontend:$release_sha"
bash "$deploy_script" "$release_sha"

temporary_state="$(mktemp "$state_dir/.deployed-sha.XXXXXX")"
printf '%s\n' "$release_sha" >"$temporary_state"
chmod 0600 "$temporary_state"
mv -f "$temporary_state" "$state_file"
