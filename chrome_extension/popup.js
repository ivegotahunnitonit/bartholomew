document.addEventListener('DOMContentLoaded', () => {
  const sidepanelBtn = document.getElementById('open-sidepanel-btn');
  const serverBadge = document.getElementById('server-badge');

  // Check local server health
  fetch('http://127.0.0.1:8080/api/stats')
    .then(res => res.json())
    .then(data => {
      serverBadge.innerText = 'Connected (8080)';
      serverBadge.className = 'badge online';
    })
    .catch(err => {
      serverBadge.innerText = 'Standby';
      serverBadge.style.color = '#ffbd2e';
    });

  sidepanelBtn.addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs && tabs[0] && tabs[0].id) {
        if (chrome.sidePanel && chrome.sidePanel.open) {
          chrome.sidePanel.open({ tabId: tabs[0].id }).catch(() => {});
        }
      }
    });
  });
});
