const vscode = require('vscode');
const fs = require('fs');
const path = require('path');
const os = require('os');

function activate(context) {
    const config = vscode.workspace.getConfiguration('bartholomew');
    const apiKey = config.get('apiKey');
    const isTeamTier = config.get('teamTierSeat');

    // Status bar item
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'bartholomew.openDashboard';
    if (apiKey) {
        statusBarItem.text = `$(shield) BTP Guard: Cloud Active`;
        statusBarItem.tooltip = `Bartholomew Cloud Connected. Click to view dashboard.`;
    } else {
        statusBarItem.text = `$(shield) BTP Guard: Local`;
        statusBarItem.tooltip = `Running in local mode. Click to link Bartholomew Cloud.`;
    }
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Command 1: Setup MCP Gateway in Cursor / VS Code
    const setupMcpDisposable = vscode.commands.registerCommand('bartholomew.setupMcp', async () => {
        try {
            const cursorDir = path.join(os.homedir(), '.cursor');
            if (!fs.existsSync(cursorDir)) {
                fs.mkdirSync(cursorDir, { recursive: true });
            }
            const mcpConfigPath = path.join(cursorDir, 'mcp.json');
            let mcpData = { mcpServers: {} };
            if (fs.existsSync(mcpConfigPath)) {
                try {
                    mcpData = JSON.parse(fs.readFileSync(mcpConfigPath, 'utf8'));
                } catch (e) {}
            }

            mcpData.mcpServers = mcpData.mcpServers || {};
            mcpData.mcpServers['btp-guard'] = {
                command: 'python',
                args: ['-m', 'mcp_server'],
                env: {
                    BTP_ENFORCE_STRICT: config.get('enforceStrict') ? 'true' : 'false',
                    BTP_SPEND_CAP: String(config.get('spendCapUsd') || 500.0),
                    BTP_API_KEY: apiKey || ''
                }
            };

            fs.writeFileSync(mcpConfigPath, JSON.stringify(mcpData, null, 2), 'utf8');
            vscode.window.showInformationMessage('🛡️ Bartholomew Guard MCP Server successfully configured in ~/.cursor/mcp.json!');
        } catch (err) {
            vscode.window.showErrorMessage(`Failed to configure MCP: ${err.message}`);
        }
    });

    // Command 2: Generate SOC 2 Merkle Compliance Pack
    const soc2Disposable = vscode.commands.registerCommand('bartholomew.generateSoc2', async () => {
        const cloudUrl = config.get('cloudEndpoint') || 'https://bartholomew.info/cloud';
        vscode.env.openExternal(vscode.Uri.parse(`${cloudUrl}?action=soc2_export`));
    });

    // Command 3: Open Cloud Dashboard
    const openDashDisposable = vscode.commands.registerCommand('bartholomew.openDashboard', () => {
        vscode.env.openExternal(vscode.Uri.parse('https://bartholomew.info/cloud'));
    });

    // Command 4: Activate Team Tier License ($15/seat)
    const teamSeatDisposable = vscode.commands.registerCommand('bartholomew.activateTeamSeat', () => {
        vscode.env.openExternal(vscode.Uri.parse('https://bartholomew.info/store/'));
    });

    context.subscriptions.push(setupMcpDisposable, soc2Disposable, openDashDisposable, teamSeatDisposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
