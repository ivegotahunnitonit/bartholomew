import fs from 'fs';

const content = fs.readFileSync('.env.remote', 'utf16le');
console.log('--- .env.remote ---');
console.log(content);
