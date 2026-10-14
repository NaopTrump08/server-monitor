import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const outDir = 'C:/Users/BossYu/Documents/deepseek-harness/default-workspace/c-bmi';
const zstdPath = 'C:/Users/BossYu/.dsh/sessions/--C-Users-BossYu-Documents-deepseek-harness-default-workspace--/session-7d3454e7-97c8-416c-8da8-65706de08040/session.v4.jsonl.zstd';

const buf = fs.readFileSync(zstdPath);
const magics = [];
for (let i = 0; i + 3 < buf.length; i++) if (buf[i] === 0x28 && buf[i + 1] === 0xb5 && buf[i + 2] === 0x2f && buf[i + 3] === 0xfd) magics.push(i);
const parts = [];
for (let i = 0; i < magics.length; i++) {
  const end = i + 1 < magics.length ? magics[i + 1] : buf.length;
  try { parts.push(zlib.zstdDecompressSync(buf.subarray(magics[i], end)).toString('utf8')); } catch { }
}
const text = parts.join('');

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
for (const m of msgs) uniq.set(`${m.role}|${m.text.length}`, m);
const user = [...uniq.values()].find((m) => m.role === 'user' && m.text.includes('int main'));

fs.writeFileSync(path.join(outDir, 'user_full.txt'), user.text, 'utf8');
console.log('user message chars:', user.text.length, '-> user_full.txt');

const audit = (label, s) => {
  const kinds = {
    'U+00A0 NBSP': /[\u00A0]/g,
    'zero-width/format/bidi': /[\u00AD\u200B-\u200F\u202A-\u202E\u2060-\u2064\u2066-\u2069\uFEFF]/g,
    'other space-like': /[\u2000-\u200A\u202F\u205F\u3000]/g,
    'ASCII control (non CR/LF/TAB)': /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g,
  };
  console.log(`\n=== ${label} (${s.length} chars) ===`);
  for (const [k, re] of Object.entries(kinds)) console.log(`  ${k}: ${(s.match(re) ?? []).length}`);
};

audit('FULL user message', user.text);
const codeOnly = user.text.slice(user.text.indexOf('#include <stdio.h>'), user.text.indexOf('以上文本'));
audit('code region only', codeOnly);
