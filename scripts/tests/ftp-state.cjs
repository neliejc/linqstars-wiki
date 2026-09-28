const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(process.argv[2], 'utf8');
const start = source.indexOf('async function getServerFiles(');
const end = source.indexOf('exports.getServerFiles = getServerFiles;', start);
assert(start >= 0 && end > start);
async function scenario({missing = false, failures = 0, malformed = false}) {
  let sizes = 0, downloads = 0, reconnects = 0;
  const client = {
    closed: false,
    close() { this.closed = true; },
    async size() {
      sizes++;
      if (sizes <= failures) {
        this.closed = true;
        throw Object.assign(new Error('reset'), {code: 'ECONNRESET'});
      }
      if (missing) { throw Object.assign(new Error('missing'), {code: 550}); }
    }
  };
  const context = {
    __awaiter: (_self, _args, _promise, fn) => new Promise((resolve, reject) => {
      const generator = fn();
      function advance(method, value) {
        try {
          const result = generator[method](value);
          if (result.done) { resolve(result.value); }
          else { Promise.resolve(result.value).then(v => advance('next', v), e => advance('throw', e)); }
        } catch (e) { reject(e); }
      }
      advance('next');
    }),
    syncProvider_1: {async ensureDir() {}},
    types_1: {syncFileDescription: 'test', currentSyncFileVersion: '1'},
    setTimeout: fn => fn(),
    async connect() { reconnects++; client.closed = false; },
    async downloadFileList() {
      downloads++;
      if (malformed) { throw new SyntaxError('Invalid state JSON'); }
      return {generatedTime: 0, data: [{name: 'index.php'}]};
    }
  };
  const get = vm.runInNewContext(source.slice(start, end) + '\ngetServerFiles', context);
  let state, error;
  try {
    state = await get(client, {all() {}}, {}, {'server-dir': '/', 'state-name': 'state.json', exclude: []});
  } catch (e) { error = e; }
  return {state, error, sizes, downloads, reconnects};
}
(async () => {
  let r = await scenario({missing: true});
  assert.equal(r.state.data.length, 0); assert.equal(r.downloads, 0);
  r = await scenario({failures: 1});
  assert.equal(r.reconnects, 1); assert.equal(r.state.data[0].name, 'index.php');
  r = await scenario({failures: 3});
  assert.equal(r.reconnects, 2); assert.equal(r.error.code, 'ECONNRESET'); assert.equal(r.state, undefined);
  r = await scenario({malformed: true});
  assert.equal(r.error.name, 'SyntaxError'); assert.equal(r.reconnects, 0);
  console.log('State checks passed: missing, reconnect, retry limit, invalid JSON');
})().catch(e => { console.error(e); process.exitCode = 1; });
