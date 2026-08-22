#!/usr/bin/env node
/**
 * Submit Crystal-PDF mobile responsiveness PR for the $100 bounty
 * Issue: https://github.com/iii123iii/Crystal-PDF/issues/3
 */

const GITHUB_TOKEN = 'YOUR_GITHUB_TOKEN_HERE';
const UPSTREAM_OWNER = 'iii123iii';
const UPSTREAM_REPO = 'Crystal-PDF';
const MY_USER = 'ivegotahunnitonit';
const BRANCH_NAME = 'fix/mobile-responsive-landing-page';
const FILE_PATH = 'frontend/src/pages/LandingPage.tsx';

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
  if (!r.ok) {
    console.error(`API ${method} ${path} failed: ${r.status}`, JSON.stringify(data, null, 2));
    throw new Error(`GitHub API error ${r.status}: ${data.message || JSON.stringify(data)}`);
  }
  return data;
}

const LANDING_PAGE_CONTENT = `import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Scissors,
  Shield,
  Minimize2,
  ScanText,
  Image,
  Merge,
  ArrowRight,
  Layers,
  Upload,
  Wand2,
  Download,
  Gem,
  Pen,
  FileOutput,
  Menu,
  X,
} from 'lucide-react'

const tools = [
  { icon: Merge, name: 'Merge', desc: 'Combine multiple documents into one' },
  { icon: Scissors, name: 'Split', desc: 'Extract pages or divide by range' },
  { icon: Minimize2, name: 'Compress', desc: 'Shrink file size, keep quality' },
  { icon: Shield, name: 'Protect', desc: 'Encrypt with password protection' },
  { icon: ScanText, name: 'OCR', desc: 'Extract text from scanned pages' },
  { icon: Image, name: 'Convert', desc: 'PDF to image, image to PDF' },
  { icon: Pen, name: 'Annotate', desc: 'Draw, highlight, and add text' },
  { icon: FileOutput, name: 'Export', desc: 'Word, image, and format tools' },
]

const steps = [
  { num: '01', icon: Upload, title: 'Upload', body: 'Drop any PDF into your workspace. Stored securely under your account.' },
  { num: '02', icon: Wand2, title: 'Process', body: 'Pick a tool — merge, split, compress, protect, annotate, convert, and more.' },
  { num: '03', icon: Download, title: 'Download', body: 'Every operation creates a new file. Your originals are never modified.' },
]

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-[#050e18] text-slate-200 relative">
      {/*  CSS  */}
      <style>{\`
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,500;1,600&display=swap');

        @keyframes reveal {
          from { opacity: 0; transform: translateY(24px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes fade {
          from { opacity: 0; }
          to   { opacity: 1; }
        }
        @keyframes rotate-slow {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
        @keyframes slideDown {
          from { opacity: 0; transform: translateY(-8px); }
          to   { opacity: 1; transform: translateY(0); }
        }

        .anim-reveal { animation: reveal .8s cubic-bezier(.16,1,.3,1) both; }
        .anim-d1 { animation-delay: .08s; }
        .anim-d2 { animation-delay: .16s; }
        .anim-d3 { animation-delay: .24s; }
        .anim-d4 { animation-delay: .36s; }
        .anim-fade { animation: fade .6s ease both; }
        .anim-slide-down { animation: slideDown .2s ease both; }

        /* Dot grid texture */
        .dot-grid {
          background-image: radial-gradient(rgba(148,163,184,.07) 1px, transparent 1px);
          background-size: 24px 24px;
        }

        /* Crystal prism – scales down on mobile */
        .prism {
          width: 220px;
          height: 220px;
          position: relative;
        }
        @media (min-width: 768px) {
          .prism { width: 340px; height: 340px; }
        }
        .prism::before {
          content: '';
          position: absolute;
          inset: 0;
          background: conic-gradient(
            from 160deg,
            rgba(45,98,255,.18),
            rgba(96,165,250,.12),
            rgba(56,189,248,.08),
            rgba(45,98,255,.04),
            rgba(96,165,250,.14),
            rgba(45,98,255,.18)
          );
          clip-path: polygon(50% 4%, 93% 28%, 93% 72%, 50% 96%, 7% 72%, 7% 28%);
          animation: rotate-slow 40s linear infinite;
        }
        .prism::after {
          content: '';
          position: absolute;
          inset: 30px;
          background: conic-gradient(
            from 220deg,
            rgba(96,165,250,.1),
            transparent,
            rgba(56,189,248,.06),
            transparent,
            rgba(96,165,250,.1)
          );
          clip-path: polygon(50% 6%, 91% 29%, 91% 71%, 50% 94%, 9% 71%, 9% 29%);
          animation: rotate-slow 60s linear infinite reverse;
        }

        /* Feature card */
        .tool-card {
          background: rgba(255,255,255,.02);
          border: 1px solid rgba(255,255,255,.05);
          transition: all .25s ease;
        }
        .tool-card:hover {
          background: rgba(255,255,255,.04);
          border-color: rgba(96,165,250,.18);
          transform: translateY(-2px);
          box-shadow: 0 16px 48px -12px rgba(0,0,0,.5), 0 0 0 1px rgba(96,165,250,.08);
        }

        /* Mobile nav links */
        .mobile-nav-link {
          display: block;
          padding: 0.875rem 1.5rem;
          font-size: 1rem;
          font-weight: 500;
          color: rgba(148,163,184,1);
          border-bottom: 1px solid rgba(255,255,255,.04);
          transition: color .15s ease, background .15s ease;
        }
        .mobile-nav-link:hover {
          color: #fff;
          background: rgba(255,255,255,.03);
        }
      \`}</style>

      {/*  Ambient glow  */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden" aria-hidden>
        <div
          className="absolute -top-[30%] left-1/2 -translate-x-1/2 w-[600px] h-[600px] sm:w-[900px] sm:h-[900px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(45,98,255,.1) 0%, transparent 65%)' }}
        />
        <div
          className="absolute top-[55%] -right-[10%] w-[300px] h-[300px] sm:w-[500px] sm:h-[500px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(56,189,248,.05) 0%, transparent 65%)' }}
        />
      </div>

      {/*  Nav  */}
      <nav
        className="sticky top-0 z-50 backdrop-blur-xl border-b border-white/[.04]"
        style={{ background: 'rgba(5,14,24,.85)' }}
      >
        <div className="max-w-6xl mx-auto flex items-center justify-between px-4 sm:px-6 h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group shrink-0">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-blue-400 flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:shadow-blue-500/40 transition-shadow">
              <Gem size={14} className="text-white" />
            </div>
            <span className="font-semibold tracking-tight text-white text-lg">
              Crystal<span className="text-blue-400">PDF</span>
            </span>
          </Link>

          {/* Desktop nav links */}
          <div className="hidden sm:flex items-center gap-2">
            <Link
              to="/login"
              className="text-sm text-slate-400 hover:text-white px-4 py-2 transition-colors"
            >
              Sign in
            </Link>
            <Link
              to="/register"
              className="text-sm font-medium text-blue-300 bg-blue-500/15 hover:bg-blue-500/25 border border-blue-500/25 hover:border-blue-500/40 px-4 py-2 rounded-lg transition-all"
            >
              Get started
            </Link>
          </div>

          {/* Mobile hamburger button */}
          <button
            className="sm:hidden flex items-center justify-center w-9 h-9 rounded-lg text-slate-400 hover:text-white hover:bg-white/[.06] transition-all"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Mobile dropdown menu */}
        {mobileMenuOpen && (
          <div
            className="sm:hidden border-t border-white/[.04] anim-slide-down"
            style={{ background: 'rgba(5,14,24,.97)' }}
          >
            <Link
              to="/login"
              className="mobile-nav-link"
              onClick={() => setMobileMenuOpen(false)}
            >
              Sign in
            </Link>
            <div className="p-4">
              <Link
                to="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center justify-center gap-2 w-full px-4 py-3 rounded-xl text-sm font-medium text-white bg-gradient-to-b from-blue-600 to-blue-700 shadow-lg transition-all"
              >
                Get started free <ArrowRight size={14} strokeWidth={2.2} />
              </Link>
            </div>
          </div>
        )}
      </nav>

      {/*  Hero  */}
      <section className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 pt-14 pb-16 sm:pt-20 sm:pb-24 md:pt-32 md:pb-36 grid md:grid-cols-[1fr,auto] items-center gap-8 md:gap-12">
        {/* Text column */}
        <div className="max-w-2xl text-center md:text-left mx-auto md:mx-0">
          <h1 className="font-bold tracking-tight leading-[1.1] text-[clamp(2.4rem,8vw,4.8rem)] text-white anim-reveal">
            Every PDF tool<br className="hidden sm:block" /> you'll ever{' '}
            <em className="not-italic text-blue-400">need.</em>
          </h1>

          <p className="mt-5 sm:mt-7 text-[clamp(.95rem,2vw,1.2rem)] leading-relaxed text-slate-400 max-w-sm sm:max-w-md mx-auto md:mx-0 anim-reveal anim-d2">
            Merge, split, compress, protect, convert, and annotate&nbsp;&mdash;
            from one elegant workspace. No subscriptions, no upload limits.
          </p>

          <div className="mt-8 sm:mt-10 flex flex-col sm:flex-row flex-wrap justify-center md:justify-start gap-3 anim-reveal anim-d3">
            <Link
              to="/register"
              className="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl text-[15px] font-medium text-white bg-gradient-to-b from-blue-600 to-blue-700 shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 hover:-translate-y-px active:translate-y-0 transition-all"
            >
              Start for free <ArrowRight size={15} strokeWidth={2.2} />
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl text-[15px] font-medium text-slate-300 border border-white/10 hover:border-white/20 hover:bg-white/[.03] transition-all"
            >
              Sign in to workspace
            </Link>
          </div>
        </div>

        {/* Crystal visual */}
        <div className="flex items-center justify-center anim-fade anim-d4">
          <div className="prism">
            <div className="absolute inset-0 flex items-center justify-center">
              <Layers size={36} className="text-blue-400/30" strokeWidth={1} />
            </div>
          </div>
        </div>
      </section>

      {/*  Tools grid  */}
      <section className="relative z-10 dot-grid">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-16 sm:py-24 md:py-32">
          <div className="max-w-lg mb-10 sm:mb-14 text-center sm:text-left mx-auto sm:mx-0">
            <p className="text-xs font-medium tracking-[.15em] uppercase text-blue-400 mb-4">
              Toolkit
            </p>
            <h2 className="text-[clamp(2rem,6vw,3.5rem)] font-bold tracking-tight leading-[1.05] text-white">
              Everything in<br className="hidden sm:block" /> one workspace
            </h2>
            <p className="mt-4 text-slate-500 leading-relaxed text-[15px]">
              Every operation produces a new file — your originals stay untouched.
            </p>
          </div>

          {/* 1 col on xs, 2 on sm, 4 on md+ */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
            {tools.map((t) => (
              <div key={t.name} className="tool-card rounded-2xl p-5 cursor-default group">
                <div className="w-10 h-10 rounded-xl bg-blue-400/[.08] border border-blue-400/[.12] flex items-center justify-center mb-4 group-hover:bg-blue-400/[.12] group-hover:border-blue-400/[.2] transition-colors">
                  <t.icon size={18} className="text-blue-400" strokeWidth={1.8} />
                </div>
                <p className="text-[15px] font-semibold text-white tracking-tight mb-1">
                  {t.name}
                </p>
                <p className="text-[13px] text-slate-500 leading-snug">
                  {t.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/*  How it works  */}
      <section className="relative z-10 border-t border-white/[.04]">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-16 sm:py-24 md:py-32">
          <div className="text-center max-w-lg mx-auto mb-12 sm:mb-16">
            <p className="text-xs font-medium tracking-[.15em] uppercase text-blue-400 mb-4">
              How it works
            </p>
            <h2 className="text-[clamp(2rem,6vw,3.5rem)] font-bold tracking-tight leading-[1.05] text-white">
              Three steps, that's it
            </h2>
          </div>

          <div className="flex flex-col gap-0">
            {steps.map((s, i) => (
              <div key={s.num}>
                <div className="flex items-start gap-4 sm:gap-5">
                  <div className="shrink-0">
                    <div className="w-11 h-11 rounded-xl flex items-center justify-center bg-blue-500/10 border border-blue-500/20">
                      <s.icon size={20} className="text-blue-400" strokeWidth={1.6} />
                    </div>
                  </div>
                  <div className="pt-1 pb-4">
                    <p className="text-xs font-medium text-blue-400/60 tracking-wider mb-1">
                      Step {s.num}
                    </p>
                    <h3 className="text-base font-semibold text-white tracking-tight mb-1.5">
                      {s.title}
                    </h3>
                    <p className="text-sm text-slate-500 leading-relaxed max-w-xs sm:max-w-sm">
                      {s.body}
                    </p>
                  </div>
                </div>
                {i < steps.length - 1 && (
                  <div className="flex gap-4 sm:gap-5">
                    <div className="w-11 flex justify-center shrink-0">
                      <div className="w-px h-6 bg-gradient-to-b from-blue-500/20 to-transparent" />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/*  CTA  */}
      <section className="relative z-10 border-t border-white/[.04]">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-20 sm:py-28 md:py-36 text-center">
          <div
            className="absolute inset-x-0 top-0 h-64 pointer-events-none"
            style={{ background: 'radial-gradient(ellipse 50% 100% at 50% 0%, rgba(45,98,255,.06), transparent)' }}
          />
          <p className="text-sm text-slate-500 mb-4 relative">
            Free to use. No credit card required.
          </p>
          <h2 className="text-[clamp(2.2rem,7vw,4.5rem)] font-bold tracking-tight leading-[.95] text-white mb-8 sm:mb-10 relative">
            Start working with<br />
            your PDFs today.
          </h2>
          <div className="relative flex flex-col sm:flex-row flex-wrap justify-center gap-3">
            <Link
              to="/register"
              className="inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl text-[15px] font-medium text-white bg-gradient-to-b from-blue-600 to-blue-700 shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 hover:-translate-y-px transition-all"
            >
              Create free account <ArrowRight size={15} strokeWidth={2.2} />
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center justify-center px-7 py-3.5 text-[15px] text-slate-400 hover:text-slate-200 transition-colors"
            >
              or sign in
            </Link>
          </div>
        </div>
      </section>

      {/*  Footer  */}
      <footer className="relative z-10 border-t border-white/[.04]">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 flex flex-col sm:flex-row items-center sm:justify-between gap-3 text-center sm:text-left">
          <span className="font-semibold text-sm text-slate-600">
            Crystal<span className="text-blue-400/50">PDF</span>
          </span>
          <p className="text-xs text-slate-700">
            Secure, server-side processing. Your files never leave your account.
          </p>
        </div>
      </footer>
    </div>
  )
}
`;

async function main() {
  console.log(' Submitting Crystal-PDF mobile-responsive PR for $100 bounty...\n');

  // 1. Verify auth
  const me = await api('GET', '/user');
  console.log(` Authenticated as: ${me.login}`);

  // 2. Check if fork exists
  let fork;
  try {
    fork = await api('GET', `/repos/${me.login}/${UPSTREAM_REPO}`);
    console.log(` Fork exists: ${fork.full_name}`);
  } catch {
    console.log(' Forking repository...');
    fork = await api('POST', `/repos/${UPSTREAM_OWNER}/${UPSTREAM_REPO}/forks`, {
      default_branch_only: true
    });
    console.log(` Forked: ${fork.full_name}`);
    // Wait for fork to be ready
    await new Promise(r => setTimeout(r, 5000));
  }

  // 3. Get the SHA of the default branch (main)
  const upstreamRef = await api('GET', `/repos/${UPSTREAM_OWNER}/${UPSTREAM_REPO}/git/refs/heads/main`);
  const latestSha = upstreamRef.object.sha;
  console.log(` Latest main SHA: ${latestSha}`);

  // 4. Create or update the branch in our fork
  let branchExists = false;
  try {
    await api('GET', `/repos/${me.login}/${UPSTREAM_REPO}/git/refs/heads/${BRANCH_NAME}`);
    branchExists = true;
    console.log(` Branch already exists: ${BRANCH_NAME}`);
  } catch {
    // Branch doesn't exist, create it
  }

  if (!branchExists) {
    await api('POST', `/repos/${me.login}/${UPSTREAM_REPO}/git/refs`, {
      ref: `refs/heads/${BRANCH_NAME}`,
      sha: latestSha
    });
    console.log(` Created branch: ${BRANCH_NAME}`);
  }

  // 5. Get the current file SHA from upstream (needed for update)
  let fileSha;
  try {
    const fileInfo = await api('GET', `/repos/${me.login}/${UPSTREAM_REPO}/contents/${FILE_PATH}?ref=${BRANCH_NAME}`);
    fileSha = fileInfo.sha;
    console.log(` Got existing file SHA: ${fileSha}`);
  } catch {
    console.log(' File not in fork yet, will create it');
  }

  // 6. Commit the mobile-responsive LandingPage.tsx
  const fileContent = Buffer.from(LANDING_PAGE_CONTENT).toString('base64');
  const commitBody = {
    message: 'fix: make landing page fully responsive for mobile\n\nCloses #3\n\n## Changes\n- Added hamburger menu with animated dropdown for mobile nav\n- Hero: text centered on mobile, side-by-side on md+\n- Tool cards: 1-col xs, 2-col sm, 4-col md+\n- CTA/footer buttons stack vertically on mobile, row on sm+\n- Crystal prism scales down to 220px on mobile via CSS media query\n- All sections use responsive px-4 sm:px-6 and py-* values\n- clamp() for fluid typography across all breakpoints\n- Added useState for mobile menu toggle',
    content: fileContent,
    branch: BRANCH_NAME
  };
  if (fileSha) commitBody.sha = fileSha;

  const commit = await api('PUT', `/repos/${me.login}/${UPSTREAM_REPO}/contents/${FILE_PATH}`, commitBody);
  console.log(` Committed: ${commit.commit.sha}`);

  // 7. Check if PR already exists
  const existingPRs = await api('GET', `/repos/${UPSTREAM_OWNER}/${UPSTREAM_REPO}/pulls?state=open&head=${me.login}:${BRANCH_NAME}`);
  if (existingPRs.length > 0) {
    console.log(` PR already exists: ${existingPRs[0].html_url}`);
    return;
  }

  // 8. Create the PR
  const pr = await api('POST', `/repos/${UPSTREAM_OWNER}/${UPSTREAM_REPO}/pulls`, {
    title: 'fix: make landing page fully responsive for mobile',
    body: `Closes #3

## Summary

This PR makes the Crystal-PDF landing page fully responsive for mobile devices.

## Changes

### Navigation
- Added hamburger menu button (hidden on \`sm+\`, visible on mobile)
- Animated slide-down mobile dropdown with Sign in link + Get started CTA
- Hamburger toggles between \`Menu\` and \`X\` icons via React state

### Hero Section
- Text is centered on mobile, left-aligned on \`md+\`
- CTA buttons stack vertically on mobile (\`flex-col\`), row on \`sm+\` (\`sm:flex-row\`)
- Crystal prism scales down to 220px on mobile via CSS \`@media\` query (340px on \`md+\`)
- Fluid font sizes using \`clamp()\` for smooth scaling

### Tools Grid
- Changed from \`grid-cols-2 sm:grid-cols-4\` → \`grid-cols-1 sm:grid-cols-2 md:grid-cols-4\`
- Cards stack single-column on very small screens for better readability

### "How It Works" section
- Added responsive gap and padding (\`px-4 sm:px-6\`, \`py-16 sm:py-24 md:py-32\`)
- Section header centered on all breakpoints

### CTA Section
- Buttons stack vertically on mobile, row on \`sm+\`

### Footer
- Changed from \`flex justify-between\` → \`flex-col sm:flex-row\` to prevent overflow on narrow screens
- Text centered on mobile, aligned on \`sm+\`

### General
- All sections use \`px-4 sm:px-6\` padding (was \`px-6\` fixed, causing edge overflow on small screens)
- Ambient glow blobs scale with \`sm:\` variants`,
    head: `${me.login}:${BRANCH_NAME}`,
    base: 'main',
    maintainer_can_modify: true
  });

  console.log(`\n PR CREATED SUCCESSFULLY!`);
  console.log(` PR URL: ${pr.html_url}`);
  console.log(` PR #${pr.number}: ${pr.title}`);
}

main().catch(err => {
  console.error(' Error:', err.message);
  process.exit(1);
});
