import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const outDir = 'C:/Users/BossYu/Documents/deepseek-harness/default-workspace/c-bmi';
const zstdPath = 'C:/Users/BossYu/.dsh/sessions/--C-Users-BossYu-Documents-deepseek-harness-default-workspace--/session-7d3454e7-97c8-416c-8da8-65706de08040/session.v4.jsonl.zstd';

// --- decode all frames ---
const buf = fs.readFileSync(zstdPath);
const magics = [];
for (let i = 0; i + 3 < buf.length; i++) if (buf[i] === 0x28 && buf[i + 1] === 0xb5 && buf[i + 2] === 0x2f && buf[i + 3] === 0xfd) magics.push(i);
const parts = [];
for (let i = 0; i < magics.length; i++) {
  const end = i + 1 < magics.length ? magics[i + 1] : buf.length;
  try { parts.push(zlib.zstdDecompressSync(buf.subarray(magics[i], end)).toString('utf8')); } catch { }
}
const text = parts.join('');
console.log('frames:', magics.length, ' decompressed chars:', text.length);

// --- collect message-shaped objects ---
function collect(node, out) {
  if (Array.isArray(node)) { node.forEach((n) => collect(n, out)); return; }
  if (node && typeof node === 'object') {
    if (typeof node.role === 'string' && (typeof node.content === 'string' || Array.isArray(node.content))) {
      let t = '';
      if (typeof node.content === 'string') t = node.content;
      else for (const b of node.content) if (b && typeof b.text === 'string') t += b.text;
      out.push({ role: node.role, text: t });
    }
    for (const v of Object.values(node)) collect(v, out);
  }
}

const msgs = [];
for (const line of text.split('\n')) {
  if (!line.includes('#include <stdio.h>')) continue;
  try { collect(JSON.parse(line), msgs); } catch { }
}

const uniq = new Map();
for (const m of msgs) uniq.set(`${m.role}|${m.text.length}|${m.text.slice(0, 40)}`, m);
const list = [...uniq.values()].sort((a, b) => b.text.length - a.text.length);
console.log('\nmessage objects containing the C code:');
list.slice(0, 8).forEach((m, i) => console.log(`  [${i}] role=${m.role} len=${m.text.length} head=${JSON.stringify(m.text.slice(0, 30))}`));

const user = list.find((m) => m.role === 'user' && m.text.includes('int main'));
if (!user) { console.log('NO USER MESSAGE FOUND'); process.exit(0); }
console.log('\n=== USER MESSAGE (len=' + user.text.length + ') ===');

// isolate the code region: from '#include' to the Chinese question line
const start = user.text.indexOf('#include <stdio.h>');
let end = user.text.indexOf('以上文本');
if (end < 0) end = user.text.length;
const code = user.text.slice(start, end);
fs.writeFileSync(path.join(outDir, 'user_raw_code.txt'), code, 'utf8');
console.log('code region chars:', code.length, '(written to user_raw_code.txt)');

// --- invisible / suspicious character scan over the CODE region ---
const INVISIBLE = /[\u00AD\u200B-\u200F\u202A-\u202E\u2060-\u2064\u2066-\u2069\uFEFF]/;
const SPACES = /[\u00A0\u2000-\u200A\u202F\u205F\u3000]/;
const rows = [];
Array.from(code).forEach((ch, idx) => {
  const cp = ch.codePointAt(0);
  if (cp <= 0x7e) {
    if (cp < 0x20 && ch !== '\n' && ch !== '\t' && ch !== '\r') rows.push({ idx, hex: 'U+' + cp.toString(16).toUpperCase().padStart(4, '0'), ch, kind: 'CONTROL' });
    return;
  }
  let kind = 'non-ASCII';
  if (INVISIBLE.test(ch)) kind = 'INVISIBLE';
  else if (SPACES.test(ch)) kind = 'SPACE-LIKE';
  rows.push({ idx, hex: 'U+' + cp.toString(16).toUpperCase().padStart(4, '0'), ch, kind });
});

console.log('\n=== characters in the code region that are not plain ASCII: ' + rows.length + ' ===');
const byKind = {};
for (const r of rows) byKind[r.kind] = (byKind[r.kind] ?? 0) + 1;
console.log('by kind:', JSON.stringify(byKind));
for (const r of rows.slice(0, 60)) {
  const line = code.slice(0, r.idx).split('\n').length;
  const ctx = code.slice(Math.max(0, r.idx - 20), r.idx + 20).replace(/\n/g, '\\n');
  console.log(`  ${r.kind.padEnd(11)} line=${line} idx=${r.idx} ${r.hex} ${JSON.stringify(r.ch)}  ctx="...${ctx}..."`);
}
