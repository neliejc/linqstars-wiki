# Linqstars Wiki

MediaWiki source snapshot, with the installed extensions, skin, static assets,
and bundled PHP dependencies from the existing wiki hosting files.

## Configuration and data

- `LocalSettings.php` is server-specific and intentionally ignored by Git.
  `LocalSettings.example.php` preserves the wiki configuration with placeholder
  database credentials, secret keys, and Google OAuth credentials.
- For a new installation, copy the example to `LocalSettings.php` and configure
  the real values privately on the server. For this migration, preserve the
  existing server configuration and secret keys; do not overwrite them with
  placeholders.
- The database and uploaded files in `images/` are managed separately. Wiki pages,
  accounts, and history live in the database and are not included in this repository.
- Runtime caches and compiled widget templates are excluded.
- Bundled dependencies are retained to preserve the uploaded source snapshot.

## Deployment

No automated deployment is configured by this import. Pushing to GitHub does not
publish the wiki. The server still needs PHP, the database, uploaded files,
private configuration, writable runtime directories, DNS, and HTTPS configured.
Future deployments must preserve `LocalSettings.php` and uploaded files.

Google OAuth must allow the production wiki callback URL. Review the example
configuration before using it on a new server.
