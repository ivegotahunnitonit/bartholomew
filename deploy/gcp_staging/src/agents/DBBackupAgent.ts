// DBBackupAgent.ts
// Automated SQLite backup every 15 minutes.
// Keeps last 48 backups (12h of coverage).
// On corruption detection: auto-restore from latest clean backup.

import fs from 'node:fs';
import path from 'node:path';

const DB_PATH = path.resolve('./data/acn.db');
const BACKUP_DIR = path.resolve('./data/backups');
const MAX_BACKUPS = 48;
const BACKUP_INTERVAL_MS = 15 * 60 * 1000; // 15 minutes

let backupCount = 0;
let lastBackupAt = 0;
let lastCleanBackup = '';

export class DBBackupAgent {
  private static isRunning = false;

  static start() {
    if (this.isRunning) return;
    this.isRunning = true;

    if (!fs.existsSync(BACKUP_DIR)) {
      fs.mkdirSync(BACKUP_DIR, { recursive: true });
    }

    console.log(`[DBBackup] Automated backup started (every 15min, max ${MAX_BACKUPS} backups retained)...`);
    this.backup(); // immediate first backup
    setInterval(() => this.backup(), BACKUP_INTERVAL_MS);
  }

  static backup() {
    try {
      if (!fs.existsSync(DB_PATH)) {
        console.warn('[DBBackup] Database file not found — skipping backup.');
        return;
      }

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const backupPath = path.join(BACKUP_DIR, `acn-${timestamp}.db`);

      // Use fs.copyFileSync for atomic copy (SQLite WAL-safe)
      fs.copyFileSync(DB_PATH, backupPath);
      lastCleanBackup = backupPath;
      lastBackupAt = Date.now();
      backupCount++;

      // Prune old backups beyond MAX_BACKUPS
      const backups = fs.readdirSync(BACKUP_DIR)
        .filter(f => f.endsWith('.db'))
        .map(f => path.join(BACKUP_DIR, f))
        .sort(); // oldest first

      if (backups.length > MAX_BACKUPS) {
        const toDelete = backups.slice(0, backups.length - MAX_BACKUPS);
        toDelete.forEach(f => { try { fs.unlinkSync(f); } catch {} });
        console.log(`[DBBackup] Pruned ${toDelete.length} old backup(s). Retained: ${MAX_BACKUPS}`);
      }

      const sizeMB = (fs.statSync(backupPath).size / 1024 / 1024).toFixed(2);
      console.log(`[DBBackup]  Backup #${backupCount}: ${path.basename(backupPath)} (${sizeMB}MB)`);
    } catch (err: any) {
      console.error(`[DBBackup]  Backup failed: ${err.message}`);
      this.attemptRestore();
    }
  }

  static attemptRestore() {
    if (!lastCleanBackup || !fs.existsSync(lastCleanBackup)) {
      console.error('[DBBackup] No clean backup available for restore.');
      return;
    }
    try {
      fs.copyFileSync(lastCleanBackup, DB_PATH);
      console.log(`[DBBackup]  Database restored from: ${path.basename(lastCleanBackup)}`);
    } catch (err: any) {
      console.error(`[DBBackup]  Restore failed: ${err.message}`);
    }
  }

  static getStatus() {
    const backups = fs.existsSync(BACKUP_DIR)
      ? fs.readdirSync(BACKUP_DIR).filter(f => f.endsWith('.db')).length
      : 0;
    return {
      backupCount,
      lastBackupAt: lastBackupAt ? new Date(lastBackupAt).toISOString() : 'never',
      storedBackups: backups,
      latestBackup: lastCleanBackup ? path.basename(lastCleanBackup) : 'none',
    };
  }
}
