/**
 * Bartholomew AI Chrome Extension - Background Service Worker
 */

chrome.runtime.onInstalled.addListener(() => {
  console.log('[Bartholomew] Background service worker initialized.');

  // Create context menu items for code selection
  chrome.contextMenus.create({
    id: 'bartholomew-explain',
    title: ' Ask Bartholomew to Explain Code',
    contexts: ['selection']
  });

  chrome.contextMenus.create({
    id: 'bartholomew-refactor',
    title: ' Suggest Refactor & Fix with Bartholomew',
    contexts: ['selection']
  });

  chrome.contextMenus.create({
    id: 'bartholomew-diagnose-ci',
    title: ' Diagnose CI Failure on this page',
    contexts: ['page']
  });

  // Enable side panel on action click
  if (chrome.sidePanel && chrome.sidePanel.setPanelBehavior) {
    chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch((error) => console.error(error));
  }
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'bartholomew-explain' || info.menuItemId === 'bartholomew-refactor') {
    const selectedText = info.selectionText || '';
    const actionType = info.menuItemId === 'bartholomew-explain' ? 'EXPLAIN' : 'REFACTOR';

    // Store the context selection for the side panel to pick up
    chrome.storage.local.set({
      activeCodeSnippet: selectedText,
      activeAction: actionType,
      activeUrl: tab ? tab.url : '',
      timestamp: Date.now()
    }, () => {
      // Open sidepanel if supported
      if (chrome.sidePanel && tab && tab.id) {
        chrome.sidePanel.open({ tabId: tab.id }).catch(() => {});
      }
    });
  } else if (info.menuItemId === 'bartholomew-diagnose-ci') {
    if (tab && tab.id) {
      chrome.tabs.sendMessage(tab.id, { type: 'TRIGGER_CI_SCAN' }, (response) => {
        if (chrome.runtime.lastError) {
          console.log('[Bartholomew] Tab message error:', chrome.runtime.lastError.message);
        }
      });
    }
  }
});

// Message hub for communication between content scripts, sidepanel, and local server
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'QUERY_LOCAL_BARTHOLOMEW') {
    fetch('http://127.0.0.1:8080/api/stats')
      .then(res => res.json())
      .then(data => sendResponse({ success: true, data }))
      .catch(err => sendResponse({ success: false, error: err.message }));
    return true; // Keep message channel open for async response
  }

  if (request.type === 'SUBMIT_WEBHOOK_EVENT') {
    fetch('http://127.0.0.1:8080/api/github/webhook', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request.payload)
    })
      .then(res => res.json())
      .then(data => sendResponse({ success: true, data }))
      .catch(err => sendResponse({ success: false, error: err.message }));
    return true;
  }
});
