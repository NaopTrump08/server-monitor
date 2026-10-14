import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { pipeline } from 'node:stream/promises';

const outDir = 'C:/Users/BossYu/Documents/deepseek-harness/default-workspace/c-bmi';
const zstdPath = 'C:/Users/BossYu/.dsh/sessions/--C-Users-BossYu-Documents-deepseek-harness-default-workspace--/session-7d3454e7-97c8-416c-8da8-65706de08040/session.v4.jsonl.zstd';
const cachePath = 'C:/Users/BossYu/.dsh/storages/session_projcache/sessions/session-7d3454e7-97c8-416c-8da8-65706de08040.json';

function walk(v, cb, kp = '') {
  if (typeof v === 'string') { cb(v, kp); return; }
  if (Array.isArray(v)) { v.forEach((x, i) => walk(x, cb, `${kp}[${i}]`)); return; }
  if (v && typeof v === 'object') for (const [k, x] of Object.entries(v)) walk(x, cb, kp ? `${kp}.${k}` : k);
}

// ---- 1) authoritative session log: stream-decode ALL zstd frames ----
const chunks = [];
await pipeline(fs.createReadStream(zstdPath), zlib.createZstdDecompress(), async function* (src) {
  for await (const c of src) chunks.push(c);
});
const text = Buffer.concat(chunks).toString('utf8');
fs.writeFileSync(path.join(outDir, 'session-full.jsonl'), text, 'utf8');
console.log('session log decompressed chars:', text.length);
console.log('session log contains "your name":', text.includes('your name'));

const hits = [];
for (const line of text.split('\n')) {
  if (!line.includes('your name')) continue;
  let obj;
  try { obj = JSON.parse(line); } catch { continue; }
  walk(obj, (s, kp) => { if (s.includes('your name')) hits.push({ src: 'session', kp, text: s }); });
}

// ---- 2) fall back to the projection cache ----
if (hits.length === 0 && fs.existsSync(cachePath)) {
  const t = fs.readFileSync(cachePath, 'utf8');
  console.log('\nfalling back to projcache; chars:', t.length, 'contains:', t.includes('your name'));
  try { walk(JSON.parse(t), (s, kp) => { if (s.includes('your name')) hits.push({ src: 'projcache', kp, text: s }); }); }
  catch (e) { console.log('projcache parse failed:', e.message); }
}

console.log('\nhits:', hits.length);
hits.sort((a, b) => b.text.length - a.text.length);
hits.slice(0, 5).forEach((h, i) => console.log(`  [${i}] src=${h.src} kp=${h.kp} len=${h.text.length}`));

const main = hits[0];
if (!main) { console.log('NO USER MESSAGE FOUND'); process.exit(0); }

fs.writeFileSync(path.join(outDir, 'user_raw.txt'), main.text, 'utf8');
console.log('\nwrote user_raw.txt, length =', main.text.length);

// ---- character audit ----
const suspicious = [];
Array.from(main.text).forEach((ch, idx) => {
  const cp = ch.codePointAt(0);
  const ok = (cp >= 0x20 && cp <= 0x7e) || ch === '\n' || ch === '\r' || ch === '\t';
  if (!ok) suspicious.push({ idx, cp, hex: 'U+' + cp.toString(16).toUpperCase().padStart(4, '0'), ch });
});

console.log('\n=== non-ASCII / control characters:', suspicious.length, '===');
const counts = new Map();
for (const s of suspicious) {
  const key = `${s.hex} ${JSON.stringify(s.ch)}`;
  counts.set(key, (counts.get(key) ?? 0) + 1);
}
for (const [k, v] of [...counts.entries()].sort((a, b) => b[1] - a[1])) console.log(`  ${k}  x${v}`);

if (suspicious.length > 0) {
  console.log('\nfirst 30 occurrences:');
  for (const s of suspicious.slice(0, 30)) {
    const ctx = main.text.slice(Math.max(0, s.idx - 30), s.idx + 30).replace(/\n/g, '\\n');
    console.log(`  idx=${s.idx} ${s.hex} ${JSON.stringify(s.ch)}  ctx="...${ctx}..."`);
  }
}
