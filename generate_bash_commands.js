import fs from 'fs';

if (!fs.existsSync('B2B_AUDIT_LEADS.json')) {
  console.error('Error: B2B_AUDIT_LEADS.json not found.');
  process.exit(1);
}

const data = JSON.parse(fs.readFileSync('B2B_AUDIT_LEADS.json', 'utf8'));
const leads = data.leads || [];

console.log('# ====================================================');
console.log('# 🚀 B2B OUTREACH COMMAND LIST FOR ALL 45 TARGET LEADS');
console.log('# ====================================================\n');

leads.forEach((lead, i) => {
  console.log(`# Lead ${i + 1}: ${lead.owner_login} (${lead.fork_name})`);
  console.log(`node dispatch_single_lead.js ${lead.owner_login} --dry-run`);
  console.log('');
});
