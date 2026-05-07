#!/bin/bash
# Build a snapshot .deb whose version embeds the current git commit.
#
# Produces a Debian version of the form:
#   <YYYYMMDD>.<short-sha>[.dirty]-1
# e.g. 20260506.c59f9f04-1
#
# debian/changelog is updated in place for the build and then restored,
# so the working tree is left clean (no spurious diff to commit).

set -euo pipefail

cd "$(dirname "$0")/.."

if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "error: not in a git working tree" >&2
    exit 1
fi

source=$(dpkg-parsechangelog -SSource)
date=$(git log -1 --format=%cs HEAD | tr -d -)
sha=$(git rev-parse --short=8 HEAD)
dirty=
if ! git diff --quiet HEAD -- . ':(exclude)debian/changelog'; then
    dirty=.dirty
fi
# Version is derived purely from git: <YYYYMMDD>.<short-sha>[.dirty]-1.
# The committed debian/changelog version is a static placeholder and is
# ignored here.
snapver="${date}.${sha}${dirty}-1"

name="${DEBFULLNAME:-$(git config user.name)}"
email="${DEBEMAIL:-$(git config user.email)}"
rfc_date=$(date -R)

backup=$(mktemp)
cp debian/changelog "$backup"
trap 'mv "$backup" debian/changelog' EXIT

{
    printf '%s (%s) UNRELEASED; urgency=medium\n\n' "$source" "$snapver"
    printf '  * Snapshot build from git %s.\n\n' "$sha"
    printf ' -- %s <%s>  %s\n\n' "$name" "$email" "$rfc_date"
    cat "$backup"
} >debian/changelog

echo "==> Building $snapver"
dpkg-buildpackage -uc -us -b -jauto "$@"
