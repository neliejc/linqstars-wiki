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
- Root bundled dependencies are retained. Extension-level ignore rules exclude
  some dependencies, including GoogleLogin and Widgets vendor directories.
  Install those dependencies from their Composer manifests/lockfiles when
  preparing deployment; a fresh clone is not yet a complete runnable server.

## Deployment

The GitHub Actions workflow in `.github/workflows/deploy.yml` deploys pushes to
`main` through FTPS once hosting credentials and `DEPLOY_ENABLED=true` are set.
See [deployment setup](docs/deployment.md) for the required secrets, variables,
first-run preview, and initial cleanup of old server files. Deployment is disabled
until configured. Live `LocalSettings.php`, uploaded files, and the database are
preserved.

Google OAuth must allow the production wiki callback URL. Review the example
configuration before using it on a new server.

## Reduced deployment size

GoogleLogin's Composer configuration retains only the `Oauth2` service wrapper.
The Google client, authentication library, and their dependencies remain installed.
Run `composer install --no-dev` inside `extensions/GoogleLogin` when preparing a
deployment; its `pre-autoload-dump` hook removes unused Google service wrappers.
If another Google API is needed later, add its service to the Composer allowlist
and reinstall `google/apiclient-services` to restore the missing wrappers.

Extensions retained from the current configuration: BlueSpiceFoundation,
DrawioEditor, GoogleLogin, InputBox, OOJSPlus, PageApprovals, VisualEditor, Widgets,
and WikiEditor. Their declared extension dependencies are included.
Inactive extensions removed: CiteThisPage, CodeEditor, Echo, ImageMap, Linter,
MultimediaViewer, NativeSvgHandler, Nuke, OATHAuth, PageImages, PdfHandler,
ReplaceText, SecureLinkFixer, SpamBlacklist, TextExtracts, and TitleBlacklist.
Reinstall an extension before enabling it in the server configuration.
