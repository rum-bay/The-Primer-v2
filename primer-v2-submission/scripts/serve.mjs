import { createReadStream, statSync } from 'node:fs';
import { createServer } from 'node:http';
import { extname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const port = Number(process.argv[2] || 4173);
const host = process.argv[3] || '127.0.0.1';
const mime = {
  '.html': 'text/html; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.onnx': 'application/octet-stream', '.csv': 'text/csv; charset=utf-8',
};

createServer((req, res) => {
  if (!['GET', 'HEAD'].includes(req.method || '')) {
    res.writeHead(405, { Allow: 'GET, HEAD' }).end();
    return;
  }
  let pathname;
  try { pathname = decodeURIComponent(new URL(req.url || '/', 'http://localhost').pathname); }
  catch { res.writeHead(400).end('Bad request'); return; }
  let file = resolve(root, `.${pathname}`);
  if (file !== root && !file.startsWith(root + sep)) { res.writeHead(403).end('Forbidden'); return; }
  try { if (statSync(file).isDirectory()) file = resolve(file, 'index.html'); }
  catch { /* handled by the regular file check below */ }
  try {
    const size = statSync(file).size;
    res.writeHead(200, { 'Content-Type': mime[extname(file).toLowerCase()] || 'application/octet-stream', 'Content-Length': size, 'X-Content-Type-Options': 'nosniff' });
    if (req.method === 'HEAD') res.end(); else createReadStream(file).pipe(res);
  } catch { res.writeHead(404).end('Not found'); }
}).listen(port, host, () => process.stdout.write(`The Primer at http://${host}:${port}/web/\n`));
