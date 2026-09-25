"""Patch only folder preparation in the pinned FTP deployment action.

Existing paths need two CWD commands, not MKD/CWD/CDUP for every ancestor.
Keep the sync manifest, exclusions, TLS, uploads and deletions unchanged.
"""
import hashlib
import sys
from pathlib import Path

path = Path(sys.argv[1])
source = path.read_text()
start = source.index('    createFolder(folderPath) {')
end = source.index('    removeFile(filePath) {', start)
original = source[start:end]
# Fail closed if the upstream implementation differs from the tested version.
EXPECTED_HASH = 'e4b9b4a093fdc31c3fe45fde7e36e8eea6892c417abcbce9d41998385506bba9'
if hashlib.sha256(original.encode()).hexdigest() != EXPECTED_HASH:
    raise SystemExit('FTP folder implementation changed; review the patch before deployment')

replacement = '''    async createFolder(folderPath) {
        if (this.dryRun === true) { return; }
        const root = await this.client.pwd();
        try {
            try {
                await this.client.cd(folderPath);
            } catch (error) {
                if (error.code !== 550) { throw error; }
                await this.client.ensureDir(folderPath);
            }
        } finally {
            if (!this.client.closed) { await this.client.cd(root); }
        }
        this.logger.verbose(`  folder ready: ${folderPath}`);
    }
'''
path.write_text(source[:start] + replacement + source[end:])
print('FTP folder preparation optimized; certificate verification unchanged')
