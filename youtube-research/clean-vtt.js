#!/usr/bin/env node
// Usage: node clean-vtt.js <path-to-vtt>
// Cleans YouTube auto-generated VTT: strips word-timing tags, takes the last
// line of each cue (most complete), removes consecutive duplicates.
const fs = require('fs');
const path = process.argv[2];
if (!path) { console.error('Usage: node clean-vtt.js <file.vtt>'); process.exit(1); }
const vtt = fs.readFileSync(path, 'utf8');
const out = [];
let prev = null;
for (const block of vtt.split(/\r?\n\r?\n/)) {
  const lines = block.split(/\r?\n/).filter(l =>
    !l.includes('-->') &&
    !/^(WEBVTT|Kind:|Language:|NOTE)/.test(l) &&
    !/^\d+$/.test(l) &&
    l.trim() !== ''
  );
  if (!lines.length) continue;
  const last = lines[lines.length - 1].replace(/<[^>]+>/g, '').trim();
  if (!last || last === prev) continue;
  out.push(last);
  prev = last;
}
process.stdout.write(out.join('\n') + '\n');
