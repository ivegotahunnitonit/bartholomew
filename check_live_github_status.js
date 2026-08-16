import fetch from 'node-fetch';

const TOKEN = 'YOUR_GITHUB_TOKEN_HERE';
const HEADERS = {
  Authorization: `token ${TOKEN}`,
  Accept: 'application/vnd.github.v3+json',
  'User-Agent': 'Status-Checker/1.0'
};

async function checkStatus() {
  console.log('====================================================');
  console.log('  🔍 CHECKING LIVE GITHUB STATUS & DISPATCHES');
  console.log('====================================================\n');

  // 1. Check Crystal-PDF PR #71
  try {
    const prRes = await fetch('https://api.github.com/repos/iii123iii/Crystal-PDF/pulls/71', { headers: HEADERS });
    if (prRes.ok) {
      const pr = await prRes.json();
      console.log(`✅ Crystal-PDF Bounty PR #71:`);
      console.log(`   - State: ${pr.state.toUpperCase()}`);
      console.log(`   - Title: ${pr.title}`);
      console.log(`   - URL  : ${pr.html_url}`);
      console.log(`   - Merged: ${pr.merged}`);
    } else {
      console.log(`⚠️ Crystal-PDF PR #71 status: ${prRes.status}`);
    }
  } catch (e) {
    console.error('Error checking PR:', e.message);
  }

  // 2. Check Crystal-PDF Issue #3 Comment
  try {
    const commentRes = await fetch('https://api.github.com/repos/iii123iii/Crystal-PDF/issues/3/comments?per_page=50', { headers: HEADERS });
    if (commentRes.ok) {
      const comments = await commentRes.json();
      const myComment = comments.find(c => c.user && c.user.login === 'ivegotahunnitonit');
      if (myComment) {
        console.log(`\n✅ Crystal-PDF Claim Comment on Issue #3:`);
        console.log(`   - Author: ${myComment.user.login}`);
        console.log(`   - Created At: ${myComment.created_at}`);
        console.log(`   - URL: ${myComment.html_url}`);
      } else {
        console.log(`\nℹ️ Total comments on Issue #3: ${comments.length}`);
      }
    }
  } catch (e) {
    console.error('Error checking comments:', e.message);
  }

  // 3. Check Public Agentic-Eval Repo
  try {
    const repoRes = await fetch('https://api.github.com/repos/ivegotahunnitonit/agentic-eval', { headers: HEADERS });
    if (repoRes.ok) {
      const repo = await repoRes.json();
      console.log(`\n✅ Public Agentic-Eval Repository:`);
      console.log(`   - Name: ${repo.full_name}`);
      console.log(`   - Visibility: ${repo.private ? 'Private' : 'PUBLIC'}`);
      console.log(`   - URL: ${repo.html_url}`);
      console.log(`   - Pushed At: ${repo.pushed_at}`);
    }
  } catch (e) {
    console.error('Error checking repository:', e.message);
  }

  console.log('\n====================================================');
}

checkStatus();
