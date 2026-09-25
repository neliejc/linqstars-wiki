const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(process.argv[2], 'utf8');
const start = source.indexOf('    async createFolder(folderPath) {');
assert(start >= 0, 'Patched method must exist');
const end = source.indexOf('    removeFile(filePath) {', start);
const method = vm.runInNewContext('({' + source.slice(start, end) + '})').createFolder;

async function check(error, dryRun = false) {
    const calls = [];
    const context = {
        dryRun,
        logger: {verbose() {}},
        client: {
            closed: false,
            async pwd() { calls.push('pwd'); return '/wiki'; },
            async cd(path) {
                calls.push('cd ' + path);
                if (path !== '/wiki' && error) { throw error; }
            },
            async ensureDir(path) { calls.push('ensure ' + path); }
        }
    };
    if (error && error.code !== 550 && !dryRun) {
        await assert.rejects(() => method.call(context, 'extensions/example'), error);
    } else {
        await method.call(context, 'extensions/example');
    }
    return calls;
}
(async () => {
    assert.deepEqual(await check(null), ['pwd', 'cd extensions/example', 'cd /wiki']);
    assert.deepEqual(await check({code: 550}), ['pwd', 'cd extensions/example', 'ensure extensions/example', 'cd /wiki']);
    const disconnected = Object.assign(new Error('Disconnected'), {code: 'ECONNRESET'});
    assert.deepEqual(await check(disconnected), ['pwd', 'cd extensions/example', 'cd /wiki']);
    assert.deepEqual(await check(null, true), []);
    console.log('Folder checks passed: existing, missing, connection failure, dry run');
})().catch(error => { console.error(error); process.exitCode = 1; });
