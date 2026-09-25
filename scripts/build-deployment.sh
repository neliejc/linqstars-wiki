#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Core vendor dependencies are bundled in this snapshot. Check them without
# updating MediaWiki or changing the root dependency graph.
composer check-platform-reqs --no-dev

for extension in GoogleLogin Widgets BlueSpiceFoundation OOJSPlus DrawioEditor; do
  composer validate --working-dir="extensions/$extension" --no-check-publish
  composer install --working-dir="extensions/$extension" --no-dev --prefer-dist --no-interaction --no-progress
  composer check-platform-reqs --working-dir="extensions/$extension" --no-dev
done

php -r '
require "extensions/GoogleLogin/vendor/autoload.php";
$client = new Google_Client();
$client->setClientId("build-check");
$client->setRedirectUri("https://example.invalid/callback");
$client->addScope("email");
if (!str_contains($client->createAuthUrl(), "accounts.google.com")) {
    throw new RuntimeException("Google OAuth URL generation failed");
}
new Google\Service\Oauth2($client);
$services = glob("extensions/GoogleLogin/vendor/google/apiclient-services/src/*", GLOB_ONLYDIR);
if (array_map("basename", $services) !== ["Oauth2"]) {
    throw new RuntimeException("Unexpected Google API services in deployment");
}
echo "Google OAuth build check passed\n";
'
