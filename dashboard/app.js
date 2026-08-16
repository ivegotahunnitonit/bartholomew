// ═══════════════════════════════════════════════════════
// ACN Operator Dashboard — app.js
// ═══════════════════════════════════════════════════════
const API_BASE = window.location.origin;

// Global state
let nodeCoords       = { lat: 40.7128, lng: -74.0060 };
let activeMatch      = null;
let selectedNetwork  = 'lightning';
let knownLogs        = new Set();
let currentPage      = 'dashboard';
let ledgerFilter     = 'all';
let allTransactions  = [];
let rotateCounter    = 0;
window.networkMode   = localStorage.getItem('acn-network-mode') || 'mainnet';

// ─────────────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  initRouter();
  initApp();
  fetchPayPalSettings();
  setInterval(refreshDynamicData, 6000);
  setInterval(pollSystemLogs, 3000);
});

async function initApp() {
  await fetchStatus();
  await fetchListings();
  await fetchMatches();
  await fetchTransactions();
  await fetchPeers();
  await fetchScoutStats();
  await fetchApiKeys();
  await fetchArbitrageStatus();
  await pollSystemLogs();

  document.getElementById('listing-form').addEventListener('submit', handleFormSubmit);
  document.getElementById('btn-fill-loc').addEventListener('click', fillNodeLocation);
  document.getElementById('peer-connect-form').addEventListener('submit', handleConnectPeer);

  // Bartholomew Pricing Trend Analysis listeners
  document.getElementById('listing-resource').addEventListener('input', updatePricingRecommendation);
  document.getElementById('listing-price').addEventListener('input', updatePricingRecommendation);
  document.getElementById('listing-type').addEventListener('change', updatePricingRecommendation);
}

async function refreshDynamicData() {
  await fetchStatus();
  await fetchMatches();
  await fetchTransactions();
  await fetchPeers();
  await fetchScoutStats();
  await fetchApiKeys();
  await fetchArbitrageStatus();
  if (currentPage === 'orchestrator') {
    await fetchCluster();
  }
}

async function updatePricingRecommendation() {
  const resource = document.getElementById('listing-resource').value.trim();
  const price = parseFloat(document.getElementById('listing-price').value) || 0;
  const type = document.getElementById('listing-type').value;
  const recEl = document.getElementById('pricing-recommendation');

  if (!resource || price <= 0) {
    recEl.style.display = 'none';
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/analysis?resource=${encodeURIComponent(resource)}&type=${type}&price=${price}`);
    if (res.ok) {
      const data = await res.json();
      if (data.recommended) {
        recEl.innerHTML = `<span style="color:#ef4444; font-weight:700;">💡 Bartholomew Recommendation:</span> <span style="color:var(--text-muted);">${data.message}</span>`;
        recEl.style.display = 'block';
      } else {
        recEl.innerHTML = `<span style="color:#10b981; font-weight:700;">✓ Competitively Priced:</span> <span style="color:var(--text-muted);">${data.message}</span>`;
        recEl.style.display = 'block';
      }
    } else {
      recEl.style.display = 'none';
    }
  } catch (err) {
    recEl.style.display = 'none';
  }
}

// ─────────────────────────────────────────────────────
// CLIENT-SIDE PAGE ROUTER
// ─────────────────────────────────────────────────────
const PAGE_TITLES = {
  dashboard:    { title: 'Circularity Command',     crumb: 'ACN / Command' },
  marketplace:  { title: 'Resource Marketplace',   crumb: 'ACN / Marketplace' },
  matches:      { title: 'Matchmaker Engine',      crumb: 'ACN / Matchmaker' },
  wallet:       { title: 'Bartholomew Treasury',   crumb: 'ACN / Treasury' },
  orchestrator: { title: 'Cluster Orchestrator',   crumb: 'ACN / Orchestrator' },
  network:      { title: 'P2P Peering Hub', crumb: 'ACN / Peering' },
};

function initRouter() {
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const page = link.getAttribute('data-page');
      navigateTo(page);
    });
  });

  // Handle hash changes
  const hash = window.location.hash.replace('#', '');
  if (hash && PAGE_TITLES[hash]) navigateTo(hash);
}

function navigateTo(page) {
  if (!PAGE_TITLES[page]) return;
  currentPage = page;

  // Update page visibility
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const target = document.getElementById(`page-${page}`);
  if (target) target.classList.add('active');

  // Update nav active state
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  const navLink = document.getElementById(`nav-${page}`);
  if (navLink) navLink.classList.add('active');

  // Update topbar
  document.getElementById('page-title').textContent = PAGE_TITLES[page].title;
  document.getElementById('page-breadcrumb').textContent = PAGE_TITLES[page].crumb;

  window.location.hash = page;

  // Lazy-load page data
  if (page === 'marketplace') fetchListings();
  if (page === 'matches') fetchMatches();
  if (page === 'wallet') { fetchTransactions(); fetchStatus(); refreshPayPalBalances(); }
  if (page === 'orchestrator') { fetchCluster(); }
  if (page === 'network') { fetchPeers(); pollSystemLogs(); }
}
window.navigateTo = navigateTo;

// ─────────────────────────────────────────────────────
// FETCH: STATUS
// ─────────────────────────────────────────────────────
async function fetchStatus() {
  try {
    const res = await fetch(`${API_BASE}/api/status`);
    if (!res.ok) throw new Error('Status unavailable');
    const data = await res.json();
    fetchApiKeys();

    nodeCoords.lat = data.lat;
    nodeCoords.lng = data.lng;

    const nodeShort = `Node: ${data.node_id.substring(0, 16)}...`;
    document.getElementById('header-node-id').textContent = nodeShort;
    document.getElementById('sidebar-node-id').textContent = data.node_id.substring(0, 20) + '...';

    const wallets = data.wallet.wallets;
    const totalConf    = wallets.lightning.confirmed_balance + wallets.base.confirmed_balance + (wallets.bitcoin ? wallets.bitcoin.confirmed_balance : 0) + (wallets.paypal ? wallets.paypal.confirmed_balance : 0);
    const totalPending = wallets.lightning.pending_balance + wallets.base.pending_balance + (wallets.bitcoin ? wallets.bitcoin.pending_balance : 0) + (wallets.paypal ? wallets.paypal.pending_balance : 0);

    // Stats
    document.getElementById('stat-earnings').textContent = `$${totalConf.toFixed(2)}`;
    document.getElementById('stat-savings').textContent  = `$${data.statistics.total_savings_usd.toFixed(2)}`;
    document.getElementById('stat-listings').textContent = data.statistics.listings_registered;
    document.getElementById('stat-matches').textContent  = data.statistics.active_proposed_matches;
    document.getElementById('stat-pending-earnings').textContent = `$${totalPending.toFixed(2)}`;

    // Sidebar
    document.getElementById('sf-earnings').textContent = `$${totalConf.toFixed(2)}`;
    document.getElementById('sf-savings').textContent  = `$${data.statistics.total_savings_usd.toFixed(2)}`;

    // Nav badge
    const matchBadge = document.getElementById('nav-matches-badge');
    if (data.statistics.active_proposed_matches > 0) {
      matchBadge.textContent = data.statistics.active_proposed_matches;
      matchBadge.style.display = 'inline-block';
    } else {
      matchBadge.style.display = 'none';
    }

    // Treasury Balance Sheet
    const fmt = (v) => `$${(v || 0).toFixed(2)}`;
    const el = (id) => document.getElementById(id);
    if (el('pp-bal-lightning')) el('pp-bal-lightning').textContent = fmt(wallets.lightning.confirmed_balance);
    if (el('pp-bal-base'))      el('pp-bal-base').textContent      = fmt(wallets.base.confirmed_balance);
    if (el('pp-bal-bitcoin'))   el('pp-bal-bitcoin').textContent   = fmt(wallets.bitcoin ? wallets.bitcoin.confirmed_balance : 0);
    if (el('pp-bal-paypal'))    el('pp-bal-paypal').textContent    = fmt(wallets.paypal ? wallets.paypal.confirmed_balance : 0);
    if (el('pp-bal-total'))     el('pp-bal-total').textContent     = fmt(totalConf);

    // DeFi Yield metrics update
    if (wallets.base && wallets.base.yield_rate !== undefined) {
      if (el('defi-yield-rate'))      el('defi-yield-rate').textContent      = `${(wallets.base.yield_rate * 100).toFixed(2)}% APY`;
      if (el('defi-yield-earned'))    el('defi-yield-earned').textContent    = `$${(wallets.base.yield_earned || 0).toFixed(4)}`;
      if (el('defi-staked-balance'))  el('defi-staked-balance').textContent  = fmt(wallets.base.staked_balance);
      if (el('defi-auto-stake'))      el('defi-auto-stake').checked          = wallets.base.auto_stake === 1;
    }

    // Deposit Credentials
    if (el('wallet-addr-lightning')) el('wallet-addr-lightning').textContent = wallets.lightning.address;
    if (el('wallet-addr-base'))      el('wallet-addr-base').textContent      = wallets.base.address;
    if (el('wallet-addr-bitcoin'))   el('wallet-addr-bitcoin').textContent   = wallets.bitcoin ? wallets.bitcoin.address : 'loading...';

    // Real On-Chain Balances
    if (el('balance-real-base')) el('balance-real-base').textContent = `${(wallets.base.real_balance || 0).toFixed(4)} ETH`;
    if (el('balance-real-btc'))  el('balance-real-btc').textContent  = `${(wallets.bitcoin ? wallets.bitcoin.real_balance : 0).toFixed(4)} BTC`;

    // Intake Mode config (Command Center dropdown)
    const intakeModeSelect = document.getElementById('intake-mode');
    if (intakeModeSelect && data.intake_mode) {
      intakeModeSelect.value = data.intake_mode;
    }

    // Auto-Settle status
    const autoSettleCheck = document.getElementById('paypal-auto-settle');
    if (autoSettleCheck) {
      autoSettleCheck.checked = !!data.wallet.auto_settle;
    }

    // Miner updates
    if (data.miner) {
      const proxyAddrEl = document.getElementById('miner-proxy-address');
      if (proxyAddrEl) proxyAddrEl.textContent = data.miner.stratum_port;
      const threadsEl = document.getElementById('miner-threads');
      if (threadsEl) threadsEl.textContent = `${data.miner.threads} Cores`;
      const sharesEl = document.getElementById('miner-shares');
      if (sharesEl) sharesEl.textContent = `${data.miner.shares}`;
      const ipEl = document.getElementById('mining-ip-display');
      if (ipEl) ipEl.textContent = window.location.hostname || 'localhost';
      const portEl = document.getElementById('mining-port-display');
      if (portEl) portEl.textContent = data.miner.stratum_port;
    }

  } catch (err) {
    console.error('fetchStatus error:', err);
  }
}

// ─────────────────────────────────────────────────────
// FETCH: LISTINGS
// ─────────────────────────────────────────────────────
async function fetchListings() {
  try {
    const res = await fetch(`${API_BASE}/api/listings`);
    if (!res.ok) throw new Error('Listings unavailable');
    const listings = await res.json();

    const tbody = document.getElementById('listings-tbody');
    const badge = document.getElementById('listings-badge');
    if (badge) badge.textContent = listings.length;

    if (!listings || listings.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center"><div class="empty-state">No listings yet. Post one above.</div></td></tr>`;
      return;
    }

    tbody.innerHTML = listings.map(l => `
      <tr>
        <td><span class="entity-role ${l.type}">${l.type.toUpperCase()}</span></td>
        <td>${escapeHtml(l.resource)}</td>
        <td>${l.quantity} ${escapeHtml(l.unit)}</td>
        <td>$${l.price.toFixed(2)}</td>
        <td>${l.lat.toFixed(3)}, ${l.lng.toFixed(3)}</td>
        <td><span class="tx-status ${l.status}">${l.status}</span></td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('fetchListings error:', err);
  }
}

// ─────────────────────────────────────────────────────
// FETCH: MATCHES
// ─────────────────────────────────────────────────────
async function fetchMatches() {
  try {
    const res = await fetch(`${API_BASE}/api/matches`);
    if (!res.ok) throw new Error('Matches unavailable');
    const matches = await res.json();

    const proposed = matches.filter(m => m.status === 'proposed');
    const badge = document.getElementById('matches-badge');
    if (badge) badge.textContent = proposed.length;

    const container = document.getElementById('matches-container');
    if (!container) return;

    if (proposed.length === 0) {
      container.innerHTML = `<div class="empty-state">No matching opportunities found yet. Add listings to trigger the matchmaker.</div>`;
      return;
    }

    container.innerHTML = proposed.map(m => `
      <div class="match-card">
        <div class="match-entity">
          <span class="entity-role waste">Waste Source</span>
          <span class="entity-resource">${escapeHtml(m.waste_resource)}</span>
          <span class="entity-node">Node: ${escapeHtml(m.waste_node_id.substring(0, 8))}</span>
        </div>
        <div class="match-flow">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          <span>${m.distance_km.toFixed(1)} km</span>
        </div>
        <div class="match-entity">
          <span class="entity-role need">Buyer Target</span>
          <span class="entity-resource">${escapeHtml(m.need_resource)}</span>
          <span class="entity-node">Node: ${escapeHtml(m.need_node_id.substring(0, 8))}</span>
        </div>
        <div class="match-metrics">
          <div class="metric-row highlight"><span>Net Savings:</span><strong>$${m.savings_usd.toFixed(2)}</strong></div>
          <div class="metric-row"><span>Fee:</span><strong>$${m.fee_usd.toFixed(2)}</strong></div>
        </div>
        <div class="match-actions">
          <button class="btn btn-success btn-sm" onclick="openPaymentModal('${m.id}', ${m.savings_usd}, ${m.fee_usd})">Accept &amp; Settle</button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('fetchMatches error:', err);
  }
}

// ─────────────────────────────────────────────────────
// FETCH: TRANSACTIONS (with tab filtering)
// ─────────────────────────────────────────────────────
async function fetchTransactions() {
  try {
    const res = await fetch(`${API_BASE}/api/transactions`);
    if (!res.ok) throw new Error('Transactions unavailable');
    allTransactions = await res.json();
    renderTransactions();
  } catch (err) {
    console.error('fetchTransactions error:', err);
  }
}

function renderTransactions() {
  const container = document.getElementById('transactions-container');
  if (!container) return;

  const list = ledgerFilter === 'all'
    ? allTransactions
    : allTransactions.filter(t => t.status === ledgerFilter);

  if (!list || list.length === 0) {
    container.innerHTML = `<div class="empty-state">No ${ledgerFilter === 'all' ? '' : ledgerFilter + ' '}transactions yet.</div>`;
    return;
  }

  const icons = { lightning: '⚡', solana: '◎', base: '🛡' };

  container.innerHTML = list.map(t => `
    <div class="tx-item">
      <div class="tx-info">
        <span class="tx-details">${icons[t.payment_method] || '○'} Fee Settlement (Match: ${t.match_id.substring(0, 8)})</span>
        <span class="tx-id" onclick="openExplorerModal('${t.id}')">hash: ${t.tx_hash ? t.tx_hash.substring(0, 22) + '...' : 'processing...'}</span>
      </div>
      <div class="tx-status-amount">
        <div class="tx-amount">+$${t.amount_usd.toFixed(2)}</div>
        <span class="tx-status ${t.status}">${t.status}</span>
      </div>
    </div>
  `).join('');
}

function switchLedgerTab(filter, btn) {
  ledgerFilter = filter;
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderTransactions();
}
window.switchLedgerTab = switchLedgerTab;

// ─────────────────────────────────────────────────────
// FETCH: PEERS
// ─────────────────────────────────────────────────────
async function fetchPeers() {
  try {
    const res = await fetch(`${API_BASE}/api/peers`);
    if (!res.ok) return;
    const peers = await res.json();
    const badge = document.getElementById('peers-badge');
    if (badge) badge.textContent = peers.length;

    const container = document.getElementById('peers-container');
    if (!container) return;

    if (!peers || peers.length === 0) {
      container.innerHTML = `<div class="empty-state">No peers connected. Paste a peer URL above.</div>`;
      return;
    }

    container.innerHTML = peers.map(p => `
      <div class="peer-card">
        <div class="peer-info">
          <span class="peer-url">${escapeHtml(p.url)}</span>
          <span class="peer-id">ID: ${escapeHtml(p.node_id ? p.node_id.substring(0, 12) + '...' : 'unknown')}</span>
        </div>
        <span class="tx-status confirmed">Online</span>
      </div>
    `).join('');
  } catch (err) {
    console.error('fetchPeers error:', err);
  }
}

// ─────────────────────────────────────────────────────
// POLL: GOSSIP LOGS
// ─────────────────────────────────────────────────────
async function pollSystemLogs() {
  try {
    const res = await fetch(`${API_BASE}/api/logs`);
    if (!res.ok) return;
    const logs = await res.json();
    const container = document.getElementById('console-container');
    if (!container) return;

    logs.forEach(log => {
      if (knownLogs.has(log.id)) return;
      knownLogs.add(log.id);

      const categoryMap = {
        '[P2P]': 'p2p',
        '[Matchmaker]': 'matchmaker',
        '[Payment]': 'payment',
        '[Config]': 'system',
        '[Database]': 'system',
        '[SYSTEM]': 'system',
      };

      let category = 'system';
      for (const [prefix, cat] of Object.entries(categoryMap)) {
        if (log.message.includes(prefix)) { category = cat; break; }
      }

      const line = document.createElement('div');
      line.className = 'console-line';
      line.innerHTML = `
        <span class="console-timestamp">[${new Date(log.timestamp).toLocaleTimeString()}]</span>
        <span class="console-category ${category}">${category.toUpperCase()}</span>
        <span class="console-message">${escapeHtml(log.message)}</span>
      `;
      container.appendChild(line);
    });
    container.scrollTop = container.scrollHeight;
  } catch (_) {}
}

// ─────────────────────────────────────────────────────
// SETTINGS PAGE
// ─────────────────────────────────────────────────────
async function populateSettings() {
  try {
    const res = await fetch(`${API_BASE}/api/status`);
    if (!res.ok) return;
    const data = await res.json();
    document.getElementById('settings-node-id').textContent = data.node_id;
    document.getElementById('settings-port').textContent = data.port;
    document.getElementById('settings-lat').textContent = data.lat;
    document.getElementById('settings-lng').textContent = data.lng;
    document.getElementById('settings-radius').textContent = `${data.max_radius_km} km`;
    document.getElementById('settings-fee').textContent = `${(data.fee_rate * 100).toFixed(1)}%`;
    document.getElementById('settings-autoaccept').textContent = data.auto_accept_enabled ? 'Enabled' : 'Disabled';
    document.getElementById('settings-threshold').textContent = `$${data.auto_accept_threshold?.toFixed(2) || '10.00'}`;
  } catch (err) {
    console.error('populateSettings error:', err);
  }
}

// ─────────────────────────────────────────────────────
// FORM HANDLERS
// ─────────────────────────────────────────────────────
async function handleFormSubmit(e) {
  e.preventDefault();
  const btn = e.target.querySelector('[type=submit]');
  btn.disabled = true;
  btn.textContent = 'Submitting...';

  try {
    const payload = {
      type:     document.getElementById('listing-type').value,
      resource: document.getElementById('listing-resource').value.trim(),
      quantity: parseFloat(document.getElementById('listing-quantity').value),
      unit:     document.getElementById('listing-unit').value.trim(),
      price:    parseFloat(document.getElementById('listing-price').value),
      lat:      parseFloat(document.getElementById('listing-lat').value),
      lng:      parseFloat(document.getElementById('listing-lng').value),
    };

    const res = await fetch(`${API_BASE}/api/listings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      e.target.reset();
      await fetchListings();
      await fetchMatches();
    } else {
      const err = await res.json();
      alert('Error: ' + err.error);
    }
  } catch (err) {
    alert('Submit error: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Submit Listing';
  }
}

async function handleConnectPeer(e) {
  e.preventDefault();
  const urlInput = document.getElementById('peer-url');
  const url = urlInput.value.trim();
  if (!url) return;

  try {
    const res = await fetch(`${API_BASE}/api/peers/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    if (res.ok) { urlInput.value = ''; await fetchPeers(); }
    else { const e = await res.json(); alert(`Connection failed: ${e.error}`); }
  } catch (err) {
    alert(`Connection error: ${err.message}`);
  }
}



function fillNodeLocation() {
  document.getElementById('listing-lat').value = nodeCoords.lat;
  document.getElementById('listing-lng').value = nodeCoords.lng;
}

// ─────────────────────────────────────────────────────
// COPY TO CLIPBOARD
// ─────────────────────────────────────────────────────
function copyToClipboard(elementId) {
  const text = document.getElementById(elementId)?.textContent || '';
  navigator.clipboard.writeText(text).catch(() => {});
}
window.copyToClipboard = copyToClipboard;





// ─────────────────────────────────────────────────────
// MODAL HELPERS
// ─────────────────────────────────────────────────────
function openModal(id) { const m = document.getElementById(id); if (m) m.classList.add('active'); }
function closeModal(id) { const m = document.getElementById(id); if (m) m.classList.remove('active'); }
window.openModal = openModal;
window.closeModal = closeModal;



// ─────────────────────────────────────────────────────
// PAYMENT MODAL
// ─────────────────────────────────────────────────────
function openPaymentModal(matchId, savingsUsd, feeUsd) {
  activeMatch = { id: matchId, savings: savingsUsd, fee: feeUsd, step: 1, txId: null };
  selectedNetwork = 'lightning';

  // Reset UI
  document.getElementById('step-node-1').className = 'payment-step active';
  document.getElementById('step-node-2').className = 'payment-step';
  document.getElementById('step-node-3').className = 'payment-step';
  document.getElementById('network-selectors-container').style.display = 'block';
  document.getElementById('invoice-display-block').style.display = 'none';
  document.getElementById('modal-real-tx-hash-container').style.display = 'none';
  document.getElementById('btn-modal-action').disabled = false;
  document.getElementById('btn-modal-action').textContent = 'Broadcast Payment Transaction';

  document.getElementById('modal-savings-usd').textContent = `$${savingsUsd.toFixed(2)}`;
  document.getElementById('modal-fee-usd').textContent     = `$${feeUsd.toFixed(2)}`;

  ['lightning','solana','base','bitcoin','paypal'].forEach(n => {
    const el = document.getElementById(`net-btn-${n}`);
    if (el) el.className = 'network-select-btn' + (n === 'lightning' ? ' active' : '');
  });

  updateCryptoConversion();
  openModal('payment-modal');
}
window.openPaymentModal = openPaymentModal;

function selectNetwork(network) {
  selectedNetwork = network;
  ['lightning','solana','base','bitcoin','paypal'].forEach(n => {
    const el = document.getElementById(`net-btn-${n}`);
    if (el) el.className = 'network-select-btn' + (n === network ? ' active' : '');
  });
  updateCryptoConversion();
}
window.selectNetwork = selectNetwork;

function updateCryptoConversion() {
  const el    = document.getElementById('modal-crypto-value');
  const label = document.getElementById('modal-crypto-conv-row');
  const fee   = activeMatch?.fee || 0;
  if (selectedNetwork === 'lightning') {
    el.textContent = `${Math.round((fee / 65000) * 100000000000)} mSAT`;
    label.style.display = 'flex';
  } else if (selectedNetwork === 'solana') {
    el.textContent = `${(fee / 150).toFixed(6)} SOL`;
    label.style.display = 'flex';
  } else if (selectedNetwork === 'bitcoin') {
    el.textContent = `${(fee / 65000).toFixed(8)} BTC`;
    label.style.display = 'flex';
  } else if (selectedNetwork === 'paypal') {
    el.textContent = `$${fee.toFixed(2)} USD`;
    label.style.display = 'flex';
  } else {
    el.textContent = `${fee.toFixed(4)} USDC`;
    label.style.display = 'flex';
  }
}

async function simulatePaymentWorkflow() {
  const btn = document.getElementById('btn-modal-action');

  if (activeMatch.step === 1) {
    btn.disabled = true;
    btn.textContent = 'Accepting Match...';

    try {
      const res = await fetch(`${API_BASE}/api/matches/accept`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ match_id: activeMatch.id, payment_method: selectedNetwork }),
      });

      if (!res.ok) { const e = await res.json(); alert('Accept failed: ' + e.error); btn.disabled = false; btn.textContent = 'Broadcast Payment Transaction'; return; }

      const data = await res.json();
      activeMatch.txId = data.tx_id;
      activeMatch.step = 2;

      document.getElementById('step-node-1').className = 'payment-step completed';
      document.getElementById('step-node-2').className = 'payment-step active';
      document.getElementById('network-selectors-container').style.display = 'none';

      const displayBlock = document.getElementById('invoice-display-block');
      displayBlock.style.display = 'flex';

      const ta = document.getElementById('invoice-textarea');
      const hashContainer = document.getElementById('modal-real-tx-hash-container');
      const hashLabel = hashContainer ? hashContainer.querySelector('label') : null;
      const hashInput = document.getElementById('modal-input-tx-hash');

      if (selectedNetwork === 'lightning') {
        ta.value = data.invoice.bolt11;
        if (hashContainer) hashContainer.style.display = 'none';
      } else if (selectedNetwork === 'paypal') {
        ta.value = `Send payment to PayPal: ${data.invoice.destination_address}`;
        if (hashContainer) {
          hashContainer.style.display = 'block';
          if (hashLabel) hashLabel.textContent = 'Paste PayPal Transaction ID (Optional):';
          if (hashInput) hashInput.placeholder = 'e.g. PP-MOCK-...';
        }
      } else {
        ta.value = `Send to: ${data.invoice.destination_address}`;
        if (hashContainer) {
          hashContainer.style.display = 'block';
          if (hashLabel) hashLabel.textContent = 'Paste Blockchain Tx Hash (Base):';
          if (hashInput) hashInput.placeholder = 'e.g. 0x8a... (Base)';
        }
      }

      btn.disabled = false;
      btn.textContent = 'Verify Payment Transaction';

    } catch (err) {
      alert('Network error: ' + err.message);
      btn.disabled = false;
      btn.textContent = 'Broadcast Payment Transaction';
    }

  } else if (activeMatch.step === 2) {
    const txHash = document.getElementById('modal-input-tx-hash').value.trim();
    btn.disabled = true;
    btn.textContent = 'Broadcasting...';

    try {
      const res = await fetch(`${API_BASE}/api/transactions/pay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tx_id: activeMatch.txId, tx_hash: txHash }),
      });

      if (!res.ok) { const e = await res.json(); alert('Broadcast failed: ' + e.error); btn.disabled = false; btn.textContent = 'Verify Payment Transaction'; return; }

      activeMatch.step = 3;
      document.getElementById('modal-real-tx-hash-container').style.display = 'none';
      document.getElementById('step-node-2').className = 'payment-step completed';
      document.getElementById('step-node-3').className = 'payment-step active';
      document.getElementById('invoice-display-block').style.opacity = '0.5';

      let pollCount = 0;
      const interval = setInterval(async () => {
        pollCount++;
        try {
          const txRes = await fetch(`${API_BASE}/api/transactions/${activeMatch.txId}`);
          if (txRes.ok) {
            const txData = await txRes.json();
            if (txData.status === 'confirmed') {
              clearInterval(interval);
              document.getElementById('step-node-3').className = 'payment-step completed';
              btn.disabled = false;
              btn.textContent = 'Close Settlement';
            } else if (txData.status === 'failed') {
              clearInterval(interval);
              btn.disabled = false;
              btn.textContent = 'Verification Failed';
            } else {
              btn.textContent = `Confirming (${txData.confirmations}/${selectedNetwork === 'lightning' || selectedNetwork === 'paypal' ? 1 : 3})...`;
            }
          }
        } catch (_) {}
        if (pollCount > 15) { clearInterval(interval); btn.disabled = false; btn.textContent = 'Close (Timeout)'; }
      }, 1200);

    } catch (err) {
      alert('Broadcast error: ' + err.message);
      btn.disabled = false;
      btn.textContent = 'Verify Payment Transaction';
    }

  } else if (activeMatch.step === 3) {
    closeModal('payment-modal');
    await fetchTransactions();
    await fetchMatches();
  }
}
window.simulatePaymentWorkflow = simulatePaymentWorkflow;

// ─────────────────────────────────────────────────────
// BLOCKCHAIN EXPLORER MODAL
// ─────────────────────────────────────────────────────
async function openExplorerModal(txId) {
  try {
    const res = await fetch(`${API_BASE}/api/transactions/${txId}`);
    if (!res.ok) throw new Error('Transaction details unavailable');
    const tx = await res.json();

    document.getElementById('explorer-tx-id').textContent = tx.id;
    document.getElementById('explorer-status').innerHTML = `<span class="tx-status ${tx.status}">${tx.status}</span>`;

    const icons = { lightning: '⚡ Bitcoin Lightning', solana: '◎ Solana (Archived)', base: '🛡 Base L2', bitcoin: '₿ Bitcoin' };
    document.getElementById('explorer-network').textContent      = icons[tx.payment_method] || tx.payment_method;
    document.getElementById('explorer-tx-hash').textContent      = tx.tx_hash || 'Pending broadcast...';
    document.getElementById('explorer-block-height').textContent = tx.block_number || 'Awaiting inclusion...';
    document.getElementById('explorer-confirmations').textContent = `${tx.confirmations} block(s)`;
    document.getElementById('explorer-gas-fee').textContent       = tx.network_gas_fee || 'estimating...';
    document.getElementById('explorer-match-id').textContent      = tx.match_id;
    document.getElementById('explorer-value').textContent         = `$${tx.amount_usd.toFixed(4)} USD`;
    document.getElementById('explorer-time').textContent          = tx.timestamp_settled ? new Date(tx.timestamp_settled).toLocaleString() : 'Processing...';

    openModal('explorer-modal');
  } catch (err) {
    alert('Explorer error: ' + err.message);
  }
}
window.openExplorerModal = openExplorerModal;

// ─────────────────────────────────────────────────────
// UTILITY
// ─────────────────────────────────────────────────────
function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Match page: Proposed vs Receipts tabs
let matchTabActive = 'matches';
function switchMatchTab(tab, btn) {
  matchTabActive = tab;
  document.getElementById('match-tab-matches')?.classList.remove('active');
  document.getElementById('match-tab-receipts')?.classList.remove('active');
  btn.classList.add('active');
  const mc = document.getElementById('matches-container');
  const rc = document.getElementById('receipts-container');
  if (mc) mc.style.display = tab === 'matches' ? 'block' : 'none';
  if (rc) rc.style.display = tab === 'receipts' ? 'block' : 'none';
  if (tab === 'receipts') fetchReceipts();
}
window.switchMatchTab = switchMatchTab;

// ---------------------------------------- FETCH: SOURCE RECEIPTS
async function fetchReceipts() {
  try {
    const res = await fetch(`${API_BASE}/api/receipts`);
    if (!res.ok) return;
    const receipts = await res.json();
    renderReceipts(receipts);
  } catch (err) { console.error('fetchReceipts error:', err); }
}

function renderReceipts(receipts) {
  const container = document.getElementById('receipts-container');
  if (!container) return;
  if (!receipts || receipts.length === 0) {
    container.innerHTML = '<div class="empty-state">No discovery receipts yet. Scout cycles every 45s.</div>';
    return;
  }
  const srcIcons = { peer_node: '🌐', task: '⚙️', material: '♻️', challenge: '🧩', compute: '🧠' };
  container.innerHTML = receipts.map(r => `
    <div class="receipt-card">
      <div class="receipt-header">
        <div class="receipt-source">
          <span class="receipt-icon">${srcIcons[r.source_type] || '❓'}</span>
          <div>
            <span class="receipt-source-label">${escapeHtml(r.source_label)}</span>
            <span class="receipt-agent"> via ${escapeHtml(r.agent)}</span>
          </div>
        </div>
        <div class="receipt-meta">
          <span class="receipt-time">${new Date(r.discovered_at).toLocaleString()}</span>
          <span class="tx-status ${r.match_id ? 'confirmed' : 'pending'}">${r.match_id ? 'Matched' : 'Scouted'}</span>
        </div>
      </div>
      <div class="receipt-body">
        <div class="receipt-row">
          <span class="entity-role ${r.listing_type}">${r.listing_type.toUpperCase()}</span>
          <strong>${escapeHtml(r.resource)}</strong>
          <span class="receipt-qty">${r.quantity} ${escapeHtml(r.unit)} @ $${r.price_per_unit.toFixed(3)}/${escapeHtml(r.unit)}</span>
        </div>
        <div class="receipt-row receipt-location">
          📍 ${r.lat.toFixed(4)}, ${r.lng.toFixed(4)}
          ${r.match_id ? ' | Match: ' + r.match_id.substring(0,8) + '...' : ''}
        </div>
        ${r.notes ? '<div class="receipt-notes">' + escapeHtml(r.notes) + '</div>' : ''}
      </div>
    </div>
  `).join('');
}

// ─────────────────────────────────────────────────────
// INTAKE DIAGNOSTICS & UPDATES
// ─────────────────────────────────────────────────────
async function fetchScoutStats() {
  try {
    const res = await fetch(`${API_BASE}/api/scout/stats`);
    if (!res.ok) return;
    const stats = await res.json();

    const processedEl = document.getElementById('diag-processed');
    const filteredEl = document.getElementById('diag-filtered');
    const convertedEl = document.getElementById('diag-converted');
    const rateEl = document.getElementById('diag-rate');

    if (processedEl) processedEl.textContent = stats.processed;
    if (filteredEl) filteredEl.textContent = stats.filtered;
    if (convertedEl) convertedEl.textContent = stats.converted;

    const rate = stats.processed > 0 ? ((stats.converted / stats.processed) * 100).toFixed(1) : '0.0';
    if (rateEl) rateEl.textContent = `${rate}%`;

    // Category breakdown
    const categories = ['task', 'material', 'challenge', 'compute'];
    const pluralMap = {
      task: 'tasks',
      material: 'materials',
      challenge: 'challenges',
      compute: 'compute'
    };

    categories.forEach(cat => {
      const catStats = stats.byCategory[cat] || { processed: 0, filtered: 0, converted: 0 };
      const plur = pluralMap[cat];
      
      const pEl = document.getElementById(`diag-${plur}-processed`);
      const fEl = document.getElementById(`diag-${plur}-filtered`);
      const cEl = document.getElementById(`diag-${plur}-converted`);

      if (pEl) pEl.textContent = catStats.processed;
      if (fEl) fEl.textContent = catStats.filtered;
      if (cEl) cEl.textContent = catStats.converted;
    });

  } catch (err) {
    console.error('fetchScoutStats error:', err);
  }
}
window.fetchScoutStats = fetchScoutStats;

async function saveIntakeMode() {
  const selectEl = document.getElementById('intake-mode');
  if (!selectEl) return;
  const mode = selectEl.value;

  try {
    const res = await fetch(`${API_BASE}/api/settings/intake`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ intake_mode: mode }),
    });

    if (res.ok) {
      await fetchStatus();
      await fetchScoutStats();
    } else {
      const err = await res.json();
      alert(`Failed to update intake mode: ${err.error}`);
    }
  } catch (err) {
    alert(`Connection error: ${err.message}`);
  }
}
window.saveIntakeMode = saveIntakeMode;

// ─────────────────────────────────────────────────────
// PAYPAL PAGE FUNCTIONS
// ─────────────────────────────────────────────────────

async function refreshPayPalBalances() {
  try {
    const res = await fetch(`${API_BASE}/api/settle`);
    if (!res.ok) return;
    const data = await res.json();
    const w = data.wallet;
    if (w && w.wallets) {
      const fmt = (v) => `$${(v || 0).toFixed(2)}`;
      const el = (id) => document.getElementById(id);
      if (el('pp-bal-lightning')) el('pp-bal-lightning').textContent = fmt(w.wallets.lightning.confirmed_balance);
      if (el('pp-bal-solana'))    el('pp-bal-solana').textContent    = fmt(w.wallets.solana.confirmed_balance);
      if (el('pp-bal-base'))      el('pp-bal-base').textContent      = fmt(w.wallets.base.confirmed_balance);
      if (el('pp-bal-bitcoin'))   el('pp-bal-bitcoin').textContent   = fmt(w.wallets.bitcoin.confirmed_balance);
      if (el('pp-bal-paypal'))    el('pp-bal-paypal').textContent    = fmt(w.wallets.paypal ? w.wallets.paypal.confirmed_balance : 0);
      const total = (w.wallets.lightning.confirmed_balance || 0)
        + (w.wallets.base.confirmed_balance || 0)
        + (w.wallets.bitcoin.confirmed_balance || 0)
        + (w.wallets.paypal ? w.wallets.paypal.confirmed_balance : 0);
      if (el('pp-bal-total')) el('pp-bal-total').textContent = fmt(total);
    }

    // Sync auto-settle checkbox
    const statusRes = await fetch(`${API_BASE}/api/status`);
    if (statusRes.ok) {
      const statusData = await statusRes.json();
      const checkbox = document.getElementById('paypal-auto-settle');
      if (checkbox) {
        checkbox.checked = !!statusData.auto_settle_on_match;
      }
      
      const autoEnabledCheckbox = document.getElementById('auto-withdraw-enabled');
      const autoMethodSelect = document.getElementById('auto-withdraw-method');
      const autoThresholdInput = document.getElementById('auto-withdraw-threshold');
      if (autoEnabledCheckbox) autoEnabledCheckbox.checked = !!statusData.auto_withdraw_enabled;
      if (autoMethodSelect) autoMethodSelect.value = statusData.auto_withdraw_method || 'electrum';
      if (autoThresholdInput) autoThresholdInput.value = statusData.auto_withdraw_threshold !== undefined ? statusData.auto_withdraw_threshold : 10.00;
    }
  } catch (err) {
    console.warn('[PayPal] Balance refresh failed:', err);
  }
}

async function handlePayPalWithdraw() {
  const amountInput = document.getElementById('paypal-amount');
  const methodSelect = document.getElementById('paypal-method');
  const statusEl = document.getElementById('paypal-status');
  const btn = document.getElementById('btn-paypal-withdraw');

  const amount = parseFloat(amountInput.value);
  const method = methodSelect.value;

  if (!amount || amount <= 0) {
    statusEl.textContent = '⚠ Please enter a valid amount.';
    statusEl.className = 'paypal-status paypal-status-error';
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Processing...';
  statusEl.textContent = '';
  statusEl.className = 'paypal-status';

  try {
    const res = await fetch(`${API_BASE}/api/withdraw`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount_usd: amount, method }),
    });
    const contentType = res.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      statusEl.textContent = '✗ Server returned non-JSON response. Please restart the ACN server to load the new endpoints.';
      statusEl.className = 'paypal-status paypal-status-error';
      return;
    }
    const data = await res.json();
    if (data.success) {
      statusEl.textContent = `✓ Withdrawal of $${amount.toFixed(2)} via ${method} successful! TX: ${data.tx_id}`;
      statusEl.className = 'paypal-status paypal-status-success';
      amountInput.value = '';
      refreshPayPalBalances();
    } else {
      statusEl.textContent = `✗ ${data.error || 'Withdrawal failed.'}`;
      statusEl.className = 'paypal-status paypal-status-error';
    }
  } catch (err) {
    statusEl.textContent = `✗ Network error: ${err.message}`;
    statusEl.className = 'paypal-status paypal-status-error';
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 21h2l1.5-7H15c3.5 0 5.5-2.5 6-5.5S19.5 3 16 3H9L7 21z"/></svg> Withdraw Now';
  }
}
window.handlePayPalWithdraw = handlePayPalWithdraw;

async function handleProcessPending() {
  const statusEl = document.getElementById('paypal-settle-status');
  statusEl.textContent = 'Processing settlements...';
  statusEl.className = 'paypal-status';

  try {
    const res = await fetch(`${API_BASE}/api/settle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const contentType = res.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      statusEl.textContent = '✗ Server returned non-JSON response. Please restart the ACN server to load the new endpoints.';
      statusEl.className = 'paypal-status paypal-status-error';
      return;
    }
    const data = await res.json();
    if (data.success) {
      const w = data.wallet;
      statusEl.textContent = `✓ Settlements processed. ${w.pending_transactions} still pending, ${w.confirmed_transactions} confirmed.`;
      statusEl.className = 'paypal-status paypal-status-success';
      refreshPayPalBalances();
    } else {
      statusEl.textContent = `✗ ${data.error || 'Settlement processing failed.'}`;
      statusEl.className = 'paypal-status paypal-status-error';
    }
  } catch (err) {
    statusEl.textContent = `✗ Network error: ${err.message}`;
    statusEl.className = 'paypal-status paypal-status-error';
  }
}
window.handleProcessPending = handleProcessPending;

function toggleAutoSettle() {
  const checkbox = document.getElementById('paypal-auto-settle');
  const enabled = checkbox.checked;
  // Persist to server settings
  fetch(`${API_BASE}/api/settings/intake`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ auto_settle_on_match: enabled }),
  }).catch(() => {});
  console.log(`[PayPal] Auto-settle ${enabled ? 'enabled' : 'disabled'}`);
}
window.toggleAutoSettle = toggleAutoSettle;

function saveAutoWithdrawSettings() {
  const enabled = document.getElementById('auto-withdraw-enabled').checked;
  const method = document.getElementById('auto-withdraw-method').value;
  const threshold = parseFloat(document.getElementById('auto-withdraw-threshold').value) || 10.0;
  
  const statusEl = document.getElementById('auto-withdraw-status');
  if (statusEl) {
    statusEl.textContent = 'Saving settings...';
    statusEl.className = 'paypal-status';
  }

  fetch(`${API_BASE}/api/settings/autowithdraw`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      auto_withdraw_enabled: enabled,
      auto_withdraw_method: method,
      auto_withdraw_threshold: threshold
    }),
  })
  .then(res => res.json())
  .then(data => {
    if (statusEl) {
      if (data.success) {
        statusEl.textContent = '✓ Auto-withdraw settings saved successfully.';
        statusEl.className = 'paypal-status paypal-status-success';
        setTimeout(() => { statusEl.textContent = ''; }, 3000);
      } else {
        statusEl.textContent = '✗ Failed to save settings: ' + (data.error || 'unknown');
        statusEl.className = 'paypal-status paypal-status-error';
      }
    }
  })
  .catch(err => {
    if (statusEl) {
      statusEl.textContent = '✗ Connection error: ' + err.message;
      statusEl.className = 'paypal-status paypal-status-error';
    }
  });
}
window.saveAutoWithdrawSettings = saveAutoWithdrawSettings;

// ─────────────────────────────────────────────────────
// PAYPAL CREDENTIALS
// ─────────────────────────────────────────────────────
async function fetchPayPalSettings() {
  try {
    const res = await fetch(`${API_BASE}/api/settings/paypal`);
    if (res.ok) {
      const data = await res.json();
      const meEl = document.getElementById('paypal-me-link');
      const idEl = document.getElementById('paypal-client-id');
      const secEl = document.getElementById('paypal-client-secret');
      if (meEl && data.paypal_me_link) meEl.value = data.paypal_me_link;
      if (idEl && data.paypal_client_id) idEl.value = data.paypal_client_id;
      if (secEl && data.paypal_client_secret) secEl.value = data.paypal_client_secret;
    }
  } catch (err) {
    console.error('Failed to fetch PayPal settings', err);
  }
}

async function savePayPalSettings() {
  const meLink = document.getElementById('paypal-me-link').value;
  const clientId = document.getElementById('paypal-client-id').value;
  const clientSecret = document.getElementById('paypal-client-secret').value;
  const statusEl = document.getElementById('paypal-settings-status');
  
  if (statusEl) {
    statusEl.textContent = 'Saving settings...';
    statusEl.className = 'paypal-status';
  }

  try {
    const res = await fetch(`${API_BASE}/api/settings/paypal`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        paypal_me_link: meLink,
        paypal_client_id: clientId,
        paypal_client_secret: clientSecret
      }),
    });
    const data = await res.json();
    if (statusEl) {
      if (data.success) {
        statusEl.textContent = '✓ PayPal settings saved successfully.';
        statusEl.className = 'paypal-status paypal-status-success';
        setTimeout(() => { statusEl.textContent = ''; }, 3000);
      } else {
        statusEl.textContent = '✗ Failed: ' + (data.error || 'unknown');
        statusEl.className = 'paypal-status paypal-status-error';
      }
    }
  } catch (err) {
    if (statusEl) {
      statusEl.textContent = '✗ Connection error: ' + err.message;
      statusEl.className = 'paypal-status paypal-status-error';
    }
  }
}
window.savePayPalSettings = savePayPalSettings;


// ─────────────────────────────────────────────────────
// CLUSTER ORCHESTRATOR ACTIONS
// ─────────────────────────────────────────────────────
async function fetchCluster() {
  try {
    const res = await fetch(`${API_BASE}/api/orchestrator/status`);
    if (!res.ok) throw new Error('Orchestrator API unavailable');
    const data = await res.json();
    
    if (data.success && data.cluster) {
      const tbody = document.getElementById('cluster-nodes-tbody');
      
      // Update statistics card values
      document.getElementById('orchestrator-nodes-count').textContent = data.cluster.length;
      document.getElementById('orchestrator-active-count').textContent = `${data.cluster.length} Nodes`;
      
      let totalShares = 0;
      let totalEarnings = 0;
      
      if (data.cluster.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="8" style="padding:20px; text-align:center; color:#718096;">No sub-nodes spawned yet. Enter a port and click Spawn Peer Node!</td>
          </tr>
        `;
      } else {
        let html = '';
        let totalPeers = 0;
        let totalMatches = 0;
        
        data.cluster.forEach(node => {
          const statusClass = node.status === 'running' ? 'badge-success' : 'badge-danger';
          const nodeShortId = node.nodeId.substring(0, 15) + '...';
          const peersCount = node.peersCount !== undefined ? node.peersCount : 0;
          const listingsCount = node.listingsCount !== undefined ? node.listingsCount : 0;
          const matchesCount = node.matchesCount !== undefined ? node.matchesCount : 0;
          
          totalPeers += peersCount;
          totalMatches += matchesCount;
          
          html += `
            <tr style="border-bottom:1px solid #2d3748; hover:background:#1a202c;">
              <td style="padding:10px; font-family:monospace;">${nodeShortId}<br><span style="color:#718096; font-size:11px;">PID: ${node.pid}</span></td>
              <td style="padding:10px;">${node.port}</td>
              <td style="padding:10px;"><span class="badge ${statusClass}">${node.status.toUpperCase()}</span></td>
              <td style="padding:10px; font-family:monospace;">${peersCount}</td>
              <td style="padding:10px; font-family:monospace;">${listingsCount}</td>
              <td style="padding:10px; font-family:monospace; color:var(--accent-green);">${matchesCount}</td>
              <td style="padding:10px;">${node.uptime}s</td>
              <td style="padding:10px; text-align:right;">
                <button class="btn btn-sm btn-danger" onclick="handleTerminateSubNode(${node.port})">Terminate</button>
              </td>
            </tr>
          `;
        });
        tbody.innerHTML = html;
        
        const avgPeers = data.cluster.length > 0 ? Math.round(totalPeers / data.cluster.length) : 0;
        const avgPeersEl = document.getElementById('orchestrator-avg-peers');
        if (avgPeersEl) avgPeersEl.textContent = avgPeers;
        
        const totalMatchesEl = document.getElementById('orchestrator-total-matches');
        if (totalMatchesEl) totalMatchesEl.textContent = totalMatches;
      }
    }
  } catch (err) {
    console.error('fetchCluster error:', err);
  }
}
window.fetchCluster = fetchCluster;

async function handleSpawnSubNode() {
  const portInput = document.getElementById('spawn-port-input');
  const port = parseInt(portInput.value, 10);
  if (!port || isNaN(port)) {
    alert('Please enter a valid port number.');
    return;
  }
  
  try {
    const res = await fetch(`${API_BASE}/api/orchestrator/spawn`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port })
    });
    const data = await res.json();
    if (data.success) {
      portInput.value = '';
      await fetchCluster();
    } else {
      alert(`Failed to spawn node: ${data.error}`);
    }
  } catch (err) {
    alert(`Error spawning node: ${err.message}`);
  }
}
window.handleSpawnSubNode = handleSpawnSubNode;

async function handleTerminateSubNode(port) {
  if (!confirm(`Are you sure you want to terminate sub-node on port ${port}?`)) return;
  
  try {
    const res = await fetch(`${API_BASE}/api/orchestrator/terminate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port })
    });
    const data = await res.json();
    if (data.success) {
      await fetchCluster();
    } else {
      alert(`Failed to terminate node: ${data.error}`);
    }
  } catch (err) {
    alert(`Error terminating node: ${err.message}`);
  }
}
window.handleTerminateSubNode = handleTerminateSubNode;

async function fetchApiKeys() {
  const tbody = document.getElementById('api-keys-table-body');
  const badge = document.getElementById('api-keys-badge');
  if (!tbody) return;

  try {
    const res = await fetch(`${API_BASE}/api/keys`);
    const keys = await res.json();
    
    badge.textContent = `${keys.length} Key${keys.length === 1 ? '' : 's'}`;

    if (keys.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" style="padding:12px 10px; text-align:center; color:var(--text-muted);">No active API credentials found.</td>
        </tr>
      `;
      return;
    }

    let html = '';
    keys.forEach(k => {
      const dateStr = new Date(k.created_at).toLocaleString();
      const statusClass = k.status === 'active' ? 'badge-success' : 'badge-danger';
      const actionButton = k.status === 'active' 
        ? `<button class="btn btn-sm btn-danger" onclick="revokeApiKey('${k.key}')" style="padding:0.25rem 0.5rem; font-size:0.7rem;">Revoke</button>`
        : `<span style="color:var(--text-muted); font-size:0.75rem;">None</span>`;

      html += `
        <tr style="border-bottom:1px solid var(--panel-border);">
          <td style="padding:10px; font-weight:500;">${k.label}</td>
          <td style="padding:10px; font-family:var(--font-mono); font-size:0.75rem; color:var(--accent-blue);">${k.key}</td>
          <td style="padding:10px; color:var(--text-muted); font-size:0.75rem;">${dateStr}</td>
          <td style="padding:10px; font-family:var(--font-mono); font-weight:bold; color:var(--accent-green);">${k.queries_count}</td>
          <td style="padding:10px; text-align:right;">${actionButton}</td>
        </tr>
      `;
    });
    tbody.innerHTML = html;
  } catch (err) {
    console.error('fetchApiKeys error:', err);
  }
}
window.fetchApiKeys = fetchApiKeys;

async function generateApiKey() {
  const labelInput = document.getElementById('api-key-label');
  const label = labelInput.value.trim();
  if (!label) {
    alert('Please enter a description for the API key.');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/keys/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ label })
    });
    const data = await res.json();
    if (data.success) {
      labelInput.value = '';
      await fetchApiKeys();
    } else {
      alert(`Failed to generate key: ${data.error}`);
    }
  } catch (err) {
    alert(`Error generating key: ${err.message}`);
  }
}
window.generateApiKey = generateApiKey;

async function revokeApiKey(key) {
  if (!confirm('Are you sure you want to revoke this API key? This action is permanent.')) return;

  try {
    const res = await fetch(`${API_BASE}/api/keys/revoke`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key })
    });
    const data = await res.json();
    if (data.success) {
      await fetchApiKeys();
    } else {
      alert(`Failed to revoke key: ${data.error}`);
    }
  } catch (err) {
    alert(`Error revoking key: ${err.message}`);
  }
}
window.revokeApiKey = revokeApiKey;

async function toggleAutoStake() {
  const checkbox = document.getElementById('defi-auto-stake');
  const enabled = checkbox.checked;

  try {
    const res = await fetch(`${API_BASE}/api/settings/autostake`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled })
    });
    const data = await res.json();
    if (!data.success) {
      checkbox.checked = !enabled;
      alert(`Failed to toggle auto stake: ${data.error}`);
    }
  } catch (err) {
    checkbox.checked = !enabled;
    alert(`Error toggling auto stake: ${err.message}`);
  }
}
window.toggleAutoStake = toggleAutoStake;

async function fetchArbitrageStatus() {
  const profitEl = document.getElementById('arbitrage-profit-usd');
  const allocatedEl = document.getElementById('arbitrage-allocated-usd');
  if (!profitEl || !allocatedEl) return;

  try {
    const res = await fetch(`${API_BASE}/api/arbitrage`);
    const data = await res.json();
    if (data.success) {
      profitEl.textContent = `$${(data.status.profit_earned || 0).toFixed(6)}`;
      allocatedEl.textContent = `$${(data.status.allocated_capital || 0).toFixed(2)}`;
    }
  } catch (err) {
    console.error('fetchArbitrageStatus error:', err);
  }
}
window.fetchArbitrageStatus = fetchArbitrageStatus;

async function allocateArbitrage() {
  const input = document.getElementById('arbitrage-amount');
  const amount = parseFloat(input.value);
  if (!amount || amount <= 0) {
    alert('Please enter a valid amount to allocate.');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/arbitrage/allocate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount_usd: amount })
    });
    const data = await res.json();
    if (data.success) {
      input.value = '';
      await fetchArbitrageStatus();
      await refreshPayPalBalances();
    } else {
      alert(`Failed to allocate: ${data.error}`);
    }
  } catch (err) {
    alert(`Error allocating capital: ${err.message}`);
  }
}
window.allocateArbitrage = allocateArbitrage;

async function deallocateArbitrage() {
  const input = document.getElementById('arbitrage-amount');
  const amount = parseFloat(input.value);
  if (!amount || amount <= 0) {
    alert('Please enter a valid amount to reclaim.');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/arbitrage/deallocate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount_usd: amount })
    });
    const data = await res.json();
    if (data.success) {
      input.value = '';
      await fetchArbitrageStatus();
      await refreshPayPalBalances();
    } else {
      alert(`Failed to reclaim: ${data.error}`);
    }
  } catch (err) {
    alert(`Error reclaiming capital: ${err.message}`);
  }
}
window.deallocateArbitrage = deallocateArbitrage;