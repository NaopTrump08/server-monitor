import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const outDir = 'C:/Users/BossYu/Documents/deepseek-harness/default-workspace/c-bmi';
const zstdPath = 'C:/Users/BossYu/.dsh/sessions/--C-Users-BossYu-Documents-deepseek-harness-default-workspace--/session-7d3454e7-97c8-416c-8da8-65706de08040/session.v4.jsonl.zstd';

const buf = fs.readFileSync(zstdPath);
console.log('file bytes:', buf.length);

// locate zstd frame magics: 28 B5 2F FD
const magics = [];
for (let i = 0; i + 3 < buf.length; i++) {
  if (buf[i] === 0x28 && buf[i + 1] === 0xb5 && buf[i + 2] === 0x2f && buf[i + 3] === 0xfd) magics.push(i);
}
console.log('zstd frame magics found:', magics.length);
console.log('first 10 offsets:', magics.slice(0, 10).join(', '));

const parts = [];
let ok = 0, fail = 0;
for (let i = 0; i < magics.length; i++) {
  const start = magics[i];
  const end = i + 1 < magics.length ? magics[i + 1] : buf.length;
  try {
    const out = zlib.zstdDecompressSync(buf.subarray(start, end));
    parts.push(out.toString('utf8'));
    ok++;
  } catch {
    fail++;
  }
}
const text = parts.join('');
console.log(`frames decoded ok=${ok} failed=${fail}`);
console.log('decompressed chars:', text.length);
fs.writeFileSync(path.join(outDir, 'session-full.jsonl'), text, 'utf8');

console.log('contains "your name":', text.includes('your name'));

function walk(v, cb, kp = '') {
  if (typeof v === 'string') { cb(v, kp); return; }
  if (Array.isArray(v)) { v.forEach((x, i) => walk(x, cb, `${kp}[${i}]`)); return; }
  if (v && typeof v === 'object') for (const [k, x] of Object.entries(v)) walk(x, cb, kp ? `${kp}.${k}` : k);
}

const hits = [];
for (const line of text.split('\n')) {
  if (!line.includes('your name')) continue;
  let obj;
  try { obj = JSON.parse(line); } catch { continue; }
  walk(obj, (s, kp) => { if (s.includes('your name')) hits.push({ kp, text: s }); });
}
hits.sort((a, b) => b.text.length - a.text.length);
console.log('\nhits:', hits.length);
hits.slice(0, 5).forEach((h, i) => console.log(`  [${i}] kp=${h.kp} len=${h.text.length}`));

const main = hits[0];
if (!main) { console.log('NO HIT'); process.exit(0); }
fs.writeFileSync(path.join(outDir, 'user_raw.txt'), main.text, 'utf8');
console.log('wrote user_raw.txt length =', main.text.length);

const suspicious = [];
Array.from(main.text).forEach((ch, idx) => {
  const cp = ch.codePointAt(0);
  const okc = (cp >= 0x20 && cp <= 0x7e) || ch === '\n' || ch === '\r' || ch === '\t';
  if (!okc) suspicious.push({ idx, cp, hex: 'U+' + cp.toString(16).toUpperCase().padStart(4, '0'), ch });
});
console.log('\n=== non-ASCII / control chars:', suspicious.length, '===');
const counts = new Map();
for (const s of suspicious) { const k = `${s.hex} ${JSON.stringify(s.ch)}`; counts.set(k, (counts.get(k) ?? 0) + 1); }
for (const [k, v] of [...counts.entries()].sort((a, b) => b[1] - a[1])) console.log(`  ${k}  x${v}`);
for (const s of suspicious.slice(0, 30)) {
  const ctx = main.text.slice(Math.max(0, s.idx - 30), s.idx + 30).replace(/\n/g, '\\n');
  console.log(`  idx=${s.idx} ${s.hex} ${JSON.stringify(s.ch)} ctx="...${ctx}..."`);
}
