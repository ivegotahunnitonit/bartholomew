#!/usr/bin/env node
// Post a comment on issue #3 linking to our PR to claim the bounty

const GITHUB_TOKEN = 'YOUR_GITHUB_TOKEN_HERE';

const headers = {
  Authorization: `Bearer ${GITHUB_TOKEN}`,
  Accept: 'application/vnd.github+json',
  'Content-Type': 'application/json',
  'X-GitHub-Api-Version': '2022-11-28',
  'User-Agent': 'ACN-BountyHunter/1.0'
};

async function api(method, path, body = null) {
  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch(`https://api.github.com${path}`, opts);
  const data = await r.json();
  if (!r.ok) throw new Error(`${r.status}: ${data.message}`);
  return data;
}

async function main() {
  const comment = await api('POST', '/repos/iii123iii/Crystal-PDF/issues/3/comments', {
    body: `Hey! I made the landing page fully responsive for mobile. Here's my PR: https://github.com/iii123iii/Crystal-PDF/pull/71

**What's fixed:**
- 🍔 Hamburger nav menu for mobile (animated slide-down dropdown)
- 📱 Hero text centered on mobile, buttons stack vertically then go side-by-side on larger screens
- 🃏 Tool cards: 1-col on phones, 2-col on tablets, 4-col on desktop
- 🔡 Fluid font sizes with \`clamp()\` across all breakpoints
- 💎 Crystal prism scales down on mobile via CSS \`@media\` query
- 🦶 Footer and CTA section stack properly on narrow screens

Ready for review!`
  });

  console.log(`✅ Comment posted: ${comment.html_url}`);
}

main().catch(e => { console.error(e.message); process.exit(1); });
