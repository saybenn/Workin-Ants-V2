#!/usr/bin/env bash
# Install the exact 532445e-era Linux toolchain without rewriting the lockfile.
set -euo pipefail
umask 077

repository=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
cd -- "$repository"

node_version=$(cat .node-version)
npm_version=$(python3 -c 'import json; print(json.load(open("package.json"))["packageManager"].removeprefix("npm@"))')
tool_root=/workspace/scratch/workin-ants-phase0-toolchain-${node_version}-${npm_version}
cache_root=/workspace/scratch/workin-ants-phase0-npm-cache

test "$(uname -s)" = Linux
test "$(uname -m)" = x86_64
test "$node_version" = 24.22.1
test "$npm_version" = 11.9.0

if [[ ! -e $tool_root && ! -L $tool_root ]]; then
  stage=$(mktemp -d /workspace/scratch/workin-ants-phase0-toolchain.XXXXXX)
  npm install --prefix "$stage" --cache "$cache_root" --no-audit --no-fund --ignore-scripts --save-exact \
    "node-linux-x64@$node_version" "npm@$npm_version"
  test ! -e "$tool_root"
  mv -T -- "$stage" "$tool_root"
fi

node_bin=$tool_root/node_modules/node-linux-x64/bin/node
printf '%s  %s\n' e32e2d16081cf644f88392934288086e7662529d0d43277c34f7aad2207cfafb "$node_bin" |
  sha256sum --check --strict
export PATH="$tool_root/node_modules/node-linux-x64/bin:$tool_root/node_modules/.bin:$PATH"
test "$(node --version)" = "v$node_version"
test "$(npm --version)" = "$npm_version"
export NEXT_TELEMETRY_DISABLED=1
export npm_config_cache="$cache_root"
npm ci --no-audit --no-fund --fetch-retries=0 --fetch-timeout=20000
printf 'export PATH=%q:"$PATH" NEXT_TELEMETRY_DISABLED=1 npm_config_cache=%q\n' \
  "$tool_root/node_modules/node-linux-x64/bin:$tool_root/node_modules/.bin" "$cache_root"
