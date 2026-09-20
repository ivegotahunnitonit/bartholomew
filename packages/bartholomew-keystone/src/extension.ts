declare const require: any;
const fs = require('fs');
const path = require('path');
import { KeystoneEngine, KeystonePasskey } from './keystone_passkey';

export interface ExtensionContext {
  subscriptions: { push: (...items: any[]) => void };
}

export function activate(context: ExtensionContext) {
  let vscode: any;
  try {
    vscode = require('vscode');
  } catch {
    return;
  }

  const engine = new KeystoneEngine();

  // 1. Status Bar Item
  const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 105);
  statusBarItem.command = 'keystone.inspectClearance';
  statusBarItem.text = `$(key) KEYSTONE: ARMED`;
  statusBarItem.tooltip = `Bartholomew Keystone — Agent Capability Passkey Active | Click to inspect clearance`;
  context.subscriptions.push(statusBarItem);
  statusBarItem.show();

  function getPasskeyPath(): string {
    const rootPath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '.';
    return path.join(rootPath, '.btp_keystone.json');
  }

  function getActivePasskey(): KeystonePasskey | null {
    try {
      const p = getPasskeyPath();
      if (fs.existsSync(p)) {
        return JSON.parse(fs.readFileSync(p, 'utf-8'));
      }
    } catch {}
    return null;
  }

  // 2. Command: Issue Agent Capability Passkey
  const issueCmd = vscode.commands.registerCommand('keystone.issuePasskey', async () => {
    const agentId = await vscode.window.showInputBox({
      prompt: 'Enter Autonomous Agent ID or Name',
      value: 'agent-worker-01'
    });
    if (!agentId) return;

    const allowedWrite = await vscode.window.showInputBox({
      prompt: 'Allowed File Write Scopes (comma-separated globs)',
      value: 'src/components, site/'
    });

    const maxSpendStr = await vscode.window.showInputBox({
      prompt: 'Max Spend Limit USD ($)',
      value: '50.00'
    });

    const spendUsd = parseFloat(maxSpendStr || '50.00');
    const writeGlobs = (allowedWrite || 'src/').split(',').map((s: string) => s.trim()).filter(Boolean);

    const passkey = engine.issuePasskey(agentId, {
      files: {
        allow_read: ['**/*'],
        allow_write: writeGlobs,
        deny: ['.env', 'secrets', 'credentials.json', 'id_rsa']
      },
      commands: {
        allow_exec: ['npm test', 'npm run build', 'python -m unittest', 'pytest'],
        deny_exec: ['rm', 'curl', 'wget', 'sudo', 'mkfs']
      },
      network: {
        allow_domains: ['github.com', 'npmjs.com', 'pypi.org', 'docs.python.org'],
        allow_search: true
      },
      budget: {
        max_spend_usd: spendUsd
      }
    }, 120);

    const savePath = getPasskeyPath();
    fs.writeFileSync(savePath, JSON.stringify(passkey, null, 2), 'utf-8');

    vscode.window.showInformationMessage(
      `Keystone Passkey issued for '${agentId}'! Clearance active for 2 hours.`,
      'Copy Token ID',
      'Inspect Scopes'
    ).then((choice: string) => {
      if (choice === 'Copy Token ID') {
        vscode.env.clipboard.writeText(passkey.passkey_id);
      } else if (choice === 'Inspect Scopes') {
        vscode.commands.executeCommand('keystone.inspectClearance');
      }
    });

    statusBarItem.text = `$(key) KEYSTONE: ${agentId} ARMED`;
  });

  // 3. Command: Inspect Active Agent Clearance
  const inspectCmd = vscode.commands.registerCommand('keystone.inspectClearance', () => {
    const passkey = getActivePasskey();
    if (!passkey) {
      vscode.window.showInformationMessage(
        'No active Keystone Passkey found in this workspace.',
        'Issue New Passkey'
      ).then((choice: string) => {
        if (choice === 'Issue New Passkey') {
          vscode.commands.executeCommand('keystone.issuePasskey');
        }
      });
      return;
    }

    const isValid = engine.verifyPasskey(passkey);
    const status = isValid ? 'VALID & ACTIVE' : 'EXPIRED / INVALID';
    const writeScopes = passkey.scopes.files?.allow_write?.join(', ') || 'None';
    const spend = passkey.scopes.budget?.max_spend_usd ?? 0;

    vscode.window.showInformationMessage(
      `Keystone Clearance [${status}]\n\n• Agent: ${passkey.agent_id}\n• Token: ${passkey.passkey_id}\n• Expires: ${new Date(passkey.expires_at).toLocaleTimeString()}\n• Write Scopes: ${writeScopes}\n• Spend Ceiling: $${spend.toFixed(2)}`,
      'Revoke Key',
      'Renew Key'
    ).then((choice: string) => {
      if (choice === 'Revoke Key') {
        vscode.commands.executeCommand('keystone.revokePasskey');
      } else if (choice === 'Renew Key') {
        vscode.commands.executeCommand('keystone.issuePasskey');
      }
    });
  });

  // 4. Command: Revoke Agent Passkey
  const revokeCmd = vscode.commands.registerCommand('keystone.revokePasskey', () => {
    const p = getPasskeyPath();
    if (fs.existsSync(p)) {
      fs.unlinkSync(p);
      vscode.window.showInformationMessage('Keystone Passkey revoked. Agent privileges stripped.');
      statusBarItem.text = `$(key) KEYSTONE: STANDBY`;
    }
  });

  // 5. Command: Validate Agent Action against Passkey
  const validateCmd = vscode.commands.registerCommand('keystone.validateAction', async () => {
    const passkey = getActivePasskey();
    if (!passkey) {
      vscode.window.showErrorMessage('Cannot validate action: No active Keystone Passkey.');
      return;
    }

    const testCmd = await vscode.window.showInputBox({
      prompt: 'Enter command or file target to test against passkey clearance',
      value: 'rm -rf /'
    });
    if (!testCmd) return;

    const res = engine.evaluateAction(passkey, 'COMMAND_EXEC', testCmd);
    if (res.verdict === 'ALLOW') {
      vscode.window.showInformationMessage(`[CLEARANCE GRANTED] Action permitted (${res.latency_us}µs).`);
    } else {
      vscode.window.showErrorMessage(`[OUT OF SCOPE] Blocked: ${res.reason} (${res.latency_us}µs).`);
    }
  });

  context.subscriptions.push(issueCmd, inspectCmd, revokeCmd, validateCmd);
}

export function deactivate() {}
