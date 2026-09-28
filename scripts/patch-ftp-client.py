"""Patch folder preparation and state-read recovery in the pinned FTP action.

Existing paths need two CWD commands, not MKD/CWD/CDUP for every ancestor.
Keep the manifest format, exclusions, TLS, uploads and deletions unchanged.
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
source = source[:start] + replacement + source[end:]
start = source.index('function getServerFiles(client, logger, timings, args) {')
end = source.index('exports.getServerFiles = getServerFiles;', start)
original = source[start:end]
old_download = '            const serverFiles = yield downloadFileList(client, logger, args["state-name"]);'
old_catch = '        catch (error) {\n            logger.all(`----------------------------------------------------------------`);'
if original.count(old_download) != 1 or original.count(old_catch) != 1:
    raise SystemExit('FTP state reader changed; review before deployment')
original = original.replace('function getServerFiles(', 'function getServerFilesOnce(', 1)
original = original.replace('        try {', '        let readingState = false;\n        try {', 1)
original = original.replace(old_download, '            readingState = true;\n            yield client.size(args["state-name"]);\n' + old_download)
original = original.replace(old_catch, '        catch (error) {\n            if (!readingState || client.closed || error.code !== 550) { throw error; }\n            logger.all(`----------------------------------------------------------------`);')
wrapper = '''async function getServerFiles(client, logger, timings, args) {
    const transientCodes = new Set(["ECONNRESET", "ETIMEDOUT", "EPIPE", "ECONNABORTED", 421, 425, 426]);
    for (let attempt = 1; attempt <= 3; attempt++) {
        try {
            return await getServerFilesOnce(client, logger, timings, args);
        } catch (error) {
            if (attempt === 3 || !(client.closed || transientCodes.has(error.code))) {
                throw error;
            }
            logger.all(`FTP tracking-file connection failed; reconnecting (${attempt}/2)`);
            client.close();
            await new Promise(resolve => setTimeout(resolve, 2000 * attempt));
            await connect(client, args, logger);
        }
    }
}
'''
source = source[:start] + wrapper + original + source[end:]
path.write_text(source)
print('FTP folder preparation optimized; certificate verification unchanged')
