# Automatic deployment from GitHub

After setup, pushing to `main` runs **Actions → Deploy wiki**. It builds the
extension dependencies (including trimmed Google APIs) and uploads code through
FTPS. SSH access is not required. This requires hosting with explicit FTPS and a
valid TLS certificate.

## One-time setup

1. In DirectAdmin **FTP Management**, create a dedicated deployment account
   restricted to the wiki directory. Confirm its FTPS hostname and port with
   the hosting provider. Do not share the password in chat or commit it.
2. In GitHub **Settings → Secrets and variables → Actions → Secrets**, add:

   | Repository secret | Value |
   | --- | --- |
   | `FTP_SERVER` | Hosting FTPS hostname, without a protocol prefix |
   | `FTP_USERNAME` | Dedicated deployment account username |
   | `FTP_PASSWORD` | Its password |

3. Under the **Variables** tab, add:

   | Repository variable | Value |
   | --- | --- |
   | `FTP_SERVER_DIR` | Wiki directory as seen by that FTP account, ending in `/` |
   | `FTP_PORT` | Usually `21`; confirm with hosting |
   | `DEPLOY_PHP_VERSION` | Live PHP version from DirectAdmin, e.g. `8.3` |
   | `DEPLOY_ENABLED` | Initially `false`; change to `true` after the first deployment |

   An FTP account restricted to the wiki folder usually sees `/` as its destination.
   An account with broader access might see `/domains/wiki.linqstars.com/public_html/`.
   Verify by listing the directory: it must contain the live `LocalSettings.php`,
   `index.php`, `extensions`, and `images`. Do not guess the path.

4. Back up the live website using DirectAdmin or Acronis. Check that its enabled
   extensions match those retained in this repository before deploying the cleanup.
5. In **Actions → Deploy wiki → Run workflow**, select `main` and leave **dry_run**
   checked. Inspect the destination and proposed file changes.
6. Run again with **dry_run** unchecked to deploy. The first upload is larger;
   subsequent deployments transfer changed files using a server-side sync state.
7. Check the live homepage, Google login, images, and editor. The workflow's HTTP
   check alone does not verify sign-in or editing.
8. Set `DEPLOY_ENABLED` to `true`. Future pushes to `main` deploy automatically.

## First deployment of the size cleanup

The sync action tracks files it has deployed. It does **not** remove pre-existing,
untracked server files on the first run. Consequently the initial upload alone
does not reclaim all the space from the earlier cleanup.

After verifying the live configuration and backup, the initial migration must
remove the 16 inactive extension folders listed in the README and the unused
Google service wrappers under `extensions/GoogleLogin/vendor/google/apiclient-services/src/`.
Keep `Oauth2/` and `Oauth2.php`. Compare with the built package rather than deleting
other Google client/authentication libraries. This initial cleanup can be performed
over FTPS once the server connection is configured; it is not needed on every push.
Never enable `dangerous-clean-slate` to do this.

## What is preserved

The workflow excludes the live `LocalSettings.php`, `images/`, `cache/`, compiled
Widgets templates, credentials, and local tooling from both upload and deletion.
It does not connect to the database, import the local dump, run schema migrations,
or copy the local read-only preview settings. Keep the server's
`.ftp-deploy-sync-state.json` so subsequent deploys can track changes and deletions.

FTPS updates files in place, so a deployment is not an atomic release switch.
Use a quiet period for the initial upload. For changes requiring database migrations
or new extensions, prepare those deployment steps separately before pushing.

If a deployment fails, inspect its Actions log; a partial upload is possible.
Restore the hosting backup when necessary, or revert the code commit and push
again to redeploy the previous tracked code. Set `DEPLOY_ENABLED=false` to pause
automatic deployment.

Action reference: https://github.com/SamKirkland/FTP-Deploy-Action
