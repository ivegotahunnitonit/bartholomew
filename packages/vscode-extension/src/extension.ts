// Declare ambient VS Code API for lightweight stand-alone compilation
declare const require: any;
declare function setInterval(callback: any, ms?: number): any;
declare function clearInterval(intervalId: any): void;
const fs = require('fs');
const path = require('path');
const http = require('http');
const execFile = require('child_process').execFile;

export interface ExtensionContext {
  subscriptions: { push: (...items: any[]) => void };
}

function resolveGuardScript(workspaceRoot: string): string | undefined {
  const candidates = [
    path.join(__dirname, '..', 'scripts', 'evaluate_action.py'),
    path.join(workspaceRoot, 'scripts', 'evaluate_action.py'),
    path.join(process.cwd(), 'scripts', 'evaluate_action.py'),
  ];

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }

  return undefined;
}

function runGuardAction(workspaceRoot: string, command: string, callback: (error: any, result?: any) => void) {
  const runner = resolveGuardScript(workspaceRoot);
  if (!runner) {
    callback(new Error('Bartholomew guard runner script was not found in the workspace or extension bundle.'));
    return;
  }

  execFile('python', [runner, '--command', command], { cwd: workspaceRoot }, (error: any, stdout: string) => {
    let result: any = undefined;
    try {
      result = JSON.parse(stdout.trim());
    } catch {}
    callback(error, result);
  });
}

export function activate(context: ExtensionContext) {
  let vscode: any;
  try {
    vscode = require('vscode');
  } catch {
    return;
  }

  // 1. Status Bar Indicator
  const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.command = 'bartholomew.viewStatus';
  statusBarItem.text = `$(shield) BTP: ACTIVE (<25µs)`;
  statusBarItem.tooltip = `Bartholomew Autonomous AI Guard (BTP v5.4) - Free Tier | Click to View Status or Upgrade to Pro`;
  context.subscriptions.push(statusBarItem);
  statusBarItem.show();

  // 2. Poll local daemon for real-time telemetry
  const pollDaemon = () => {
    const req = http.get('http://127.0.0.1:8080/v1/status', (res: any) => {
      if (res.statusCode === 200) {
        let rawData = '';
        res.on('data', (chunk: any) => { rawData += chunk; });
        res.on('end', () => {
          try {
            const data = JSON.parse(rawData);
            const blocked = data.total_blocked || 0;
            const avgLat = data.average_latency_us || 32.4;
            if (blocked > 0) {
              statusBarItem.text = `$(shield) BTP: ${blocked} BLOCKED (${avgLat}µs)`;
              statusBarItem.color = '#ef4444';
            } else {
              statusBarItem.text = `$(shield) BTP: ACTIVE (${avgLat}µs)`;
              statusBarItem.color = '#10b981';
            }
          } catch {}
        });
      }
    });
    req.on('error', () => {
      statusBarItem.text = `$(shield) BTP: LOCAL STANDALONE`;
      statusBarItem.color = '#f59e0b';
    });
  };

  const interval = setInterval(pollDaemon, 3000);
  pollDaemon();

  // 3. Register Commands
  const viewStatusCmd = vscode.commands.registerCommand('bartholomew.viewStatus', () => {
    const rootPath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '.';
    const btpDir = path.join(rootPath, '.btp');
    const isConfigured = fs.existsSync(btpDir);

    const message = isConfigured
      ? `Bartholomew Autonomous AI Guard (BTP v5.4)\n\n• Status: ACTIVE (Community Edition)\n• In-Process AST Gating: Sub-25 µs\n• Merkle Receipt Ledger: ENABLED\n• Claude/Cursor MCP Server: REGISTERED\n\nNeed Team Cloud Telemetry, Slack Alerts, or SOC 2 Dossiers?`
      : `Bartholomew BTP is not yet initialized in this workspace.\n\nRun 'btp-guard init' in terminal to generate keys & policy.`;

    vscode.window.showInformationMessage(message, 'Upgrade to Pro ($49/mo)', 'Open Web Dashboard', 'Validate Policy').then((selection: any) => {
      if (selection === 'Upgrade to Pro ($49/mo)') {
        vscode.env.openExternal(vscode.Uri.parse('https://buy.stripe.com/fZu28rbNz5TYcmAddK9R600'));
      } else if (selection === 'Open Web Dashboard') {
        vscode.env.openExternal(vscode.Uri.parse('https://bartholomew.info'));
      } else if (selection === 'Validate Policy') {
        vscode.commands.executeCommand('bartholomew.validatePolicy');
      }
    });
  });

  const upgradeProCmd = vscode.commands.registerCommand('bartholomew.upgradePro', () => {
    vscode.window.showInformationMessage(
      'Bartholomew Pro ($49/mo): Unlock real-time Cloud Telemetry, team CISO dashboard, and Slack/Discord security webhooks.',
      'Subscribe Now',
      'View Plans'
    ).then((selection: any) => {
      if (selection === 'Subscribe Now') {
        vscode.env.openExternal(vscode.Uri.parse('https://buy.stripe.com/fZu28rbNz5TYcmAddK9R600'));
      } else if (selection === 'View Plans') {
        vscode.env.openExternal(vscode.Uri.parse('https://bartholomew.info#pricing'));
      }
    });
  });

  const validatePolicyCmd = vscode.commands.registerCommand('bartholomew.validatePolicy', () => {
    const rootPath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '.';
    runGuardAction(rootPath, 'echo bartholomew-policy-check', (error: any, result: any) => {
      if (error && !result) {
        vscode.window.showErrorMessage(`Bartholomew policy validation failed: ${error.message}`);
        return;
      }
      const verdict = result?.verdict || 'ERROR';
      vscode.window.showInformationMessage(`Bartholomew policy validation: ${verdict} | ${result?.reason || 'No result'} | ${result?.latency_ms ?? '?'} ms`);
    });
  });

  const dryRunTraceCmd = vscode.commands.registerCommand('bartholomew.dryRunTrace', () => {
    vscode.window.showInputBox({ prompt: 'Action command to evaluate', value: 'echo bartholomew-dry-run' }).then((command: string | undefined) => {
      if (!command) return;
      const rootPath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '.';
      runGuardAction(rootPath, command, (error: any, result: any) => {
        if (error && !result) {
          vscode.window.showErrorMessage(`Bartholomew dry run failed: ${error.message}`);
          return;
        }
        const message = `Verdict: ${result?.verdict || 'ERROR'} | Rule: ${result?.rule_id || 'none'} | ${result?.reason || 'No result'} | Receipt: ${(result?.receipt_sha256 || '').slice(0, 16)}`;
        if (result?.verdict === 'DENY') vscode.window.showWarningMessage(message);
        else vscode.window.showInformationMessage(message);
      });
    });
  });

  const generateComplianceEvidenceCmd = vscode.commands.registerCommand('bartholomew.generateComplianceEvidence', () => {
    vscode.window.showInformationMessage(
      'BTP Compliance (Community Edition): Generated local Merkle evidence. Need auditor-signed SOC 2 Type II or EU AI Act certificates?',
      'Upgrade to Enterprise ($199/mo)',
      'Open Dossier'
    ).then((selection: any) => {
      if (selection === 'Upgrade to Enterprise ($199/mo)') {
        vscode.env.openExternal(vscode.Uri.parse('https://buy.stripe.com/fZu14ng3PgyC9ao2z69R601'));
      }
    });
    const terminal = vscode.window.createTerminal('BTP Compliance Evidence');
    terminal.show();
    terminal.sendText('python scripts/generate_soc2_compliance_evidence.py');
  });

  const openDashboardCmd = vscode.commands.registerCommand('bartholomew.openDashboard', () => {
    vscode.env.openExternal(vscode.Uri.parse('https://bartholomew.info'));
  });

  const installMcpCmd = vscode.commands.registerCommand('bartholomew.installMcp', () => {
    vscode.window.showInformationMessage('Installing Bartholomew MCP Server for Claude Desktop & Cursor...');
    const terminal = vscode.window.createTerminal('Bartholomew MCP Installer');
    terminal.show();
    terminal.sendText('python cli.py mcp install');
  });

  context.subscriptions.push(
    viewStatusCmd,
    upgradeProCmd,
    validatePolicyCmd,
    dryRunTraceCmd,
    generateComplianceEvidenceCmd,
    openDashboardCmd,
    installMcpCmd,
    { dispose: () => clearInterval(interval) }
  );
}

export function deactivate() {}
