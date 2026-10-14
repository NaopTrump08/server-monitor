import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const src = 'C:/Users/BossYu/.dsh/sessions/--C-Users-BossYu-Documents-deepseek-harness-default-workspace--/session-7d3454e7-97c8-416c-8da8-65706de08040/session.v4.jsonl.zstd';
const outDir = 'C:/Users/BossYu/Documents/deepseek-harness/default-workspace/c-bmi';

const dec = zlib.zstdDecompressSync(fs.readFileSync(src));
const text = dec.toString('utf8');
fs.writeFileSync(path.join(outDir, 'session-decompressed.jsonl'), text, 'utf8');
console.log('decompressed chars:', text.length);

const lines = text.split('\n').filter((l) => l.trim() !== '');
console.log('jsonl lines:', lines.length);

function walk(value, cb, keyPath = '') {
  if (typeof value === 'string') { cb(value, keyPath); return; }
  if (Array.isArray(value)) { value.forEach((v, i) => walk(v, cb, `${keyPath}[${i}]`)); return; }
  if (value && typeof value === 'object') {
    for (const [k, v] of Object.entries(value)) walk(v, cb, keyPath ? `${keyPath}.${k}` : k);
  }
}

const hits = [];
for (let i = 0; i < lines.length; i++) {
  if (!lines[i].includes('your name')) continue;
  let obj;
  try { obj = JSON.parse(lines[i]); } catch { hits.push({ line: i, keyPath: '(unparsed)', text: lines[i] }); continue; }
  walk(obj, (s, keyPath) => { if (s.includes('your name')) hits.push({ line: i, keyPath, text: s }); });
}

console.log('hits containing "your name":', hits.length);

// pick the longest hit = the full code paste
hits.sort((a, b) => b.text.length - a.text.length);
const main = hits[0];
if (!main) { console.log('NO HIT FOUND'); process.exit(0); }

console.log('\n=== longest hit ===');
console.log('line:', main.line, ' keyPath:', main.keyPath, ' length:', main.text.length);

fs.writeFileSync(path.join(outDir, 'user_raw.txt'), main.text, 'utf8');
console.log('wrote user_raw.txt (byte-exact as received)');

// character audit
const suspicious = [];
const cps = Array.from(main.text);
cps.forEach((ch, idx) => {
  const cp = ch.codePointAt(0);
  const isAsciiPrintable = cp >= 0x20 && cp <= 0x7e;
  const isNormalWs = ch === '\n' || ch === '\r' || ch === '\t';
  if (!isAsciiPrintable && !isNormalWs) {
    suspicious.push({ idx, cp, hex: 'U+' + cp.toString(16).toUpperCase().padStart(4, '0'), ch });
  }
});

console.log('\n=== non-ASCII / control characters found:', suspicious.length, '===');
const counts = new Map();
for (const s of suspicious) {
  const key = `${s.hex} ${JSON.stringify(s.ch)}`;
  counts.set(key, (counts.get(key) ?? 0) + 1);
}
for (const [k, v] of [...counts.entries()].sort((a, b) => b[1] - a[1])) console.log(`  ${k}  x${v}`);
console.log('\nfirst 40 occurrences (index / codepoint / context):');
for (const s of suspicious.slice(0, 40)) {
  const ctx = main.text.slice(Math.max(0, s.idx - 25), s.idx + 25).replace(/\n/g, '\\n');
  console.log(`  idx=${s.idx} ${s.hex} char=${JSON.stringify(s.ch)} ctx="...${ctx}..."`);
}
