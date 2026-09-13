/**
 * WorkflowEngine.ts
 * Enterprise Durable Workflow & Task State Engine for ACN.
 * 
 * Orchestrates multi-step workflow pipelines for:
 * - Circularity Feedstock Trade Matchmaking & Escrow
 * - 24/7 Freight & Logistics Dispatching
 * - DePIN & GPU Compute Job Allocations
 * - Cryptographic Digital Notary Attestations
 */

import { db } from '../database/db.ts';
import * as crypto from 'node:crypto';

export interface WorkflowInstance {
  id: string;
  name: string;
  type: 'circularity_trade' | 'freight_dispatch' | 'gpu_compute' | 'notary_attestation';
  status: 'pending' | 'running' | 'completed' | 'failed';
  current_step: string;
  step_index: number;
  total_steps: number;
  payload: string;
  result: string | null;
  error_message: string | null;
  created_at: number;
  updated_at: number;
}

// Ensure database table exists for workflows
db.exec(`
  CREATE TABLE IF NOT EXISTS workflows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    current_step TEXT NOT NULL,
    step_index INTEGER NOT NULL,
    total_steps INTEGER NOT NULL,
    payload TEXT NOT NULL,
    result TEXT,
    error_message TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
  );
`);

export class WorkflowEngine {
  /**
   * Start a new workflow instance
   */
  static startWorkflow(params: {
    name: string;
    type: WorkflowInstance['type'];
    initial_step: string;
    total_steps?: number;
    payload: any;
  }): WorkflowInstance {
    const id = 'wf-' + crypto.randomUUID().substring(0, 8);
    const created_at = Date.now();

    const instance: WorkflowInstance = {
      id,
      name: params.name,
      type: params.type,
      status: 'running',
      current_step: params.initial_step,
      step_index: 1,
      total_steps: params.total_steps || 3,
      payload: JSON.stringify(params.payload),
      result: null,
      error_message: null,
      created_at,
      updated_at: created_at,
    };

    db.prepare(`
      INSERT INTO workflows (id, name, type, status, current_step, step_index, total_steps, payload, result, error_message, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(id, instance.name, instance.type, instance.status, instance.current_step, instance.step_index, instance.total_steps, instance.payload, null, null, created_at, created_at);

    return instance;
  }

  /**
   * Advance a workflow to the next step
   */
  static advanceStep(id: string, nextStep: string, resultData?: any): WorkflowInstance | null {
    const row = db.prepare("SELECT * FROM workflows WHERE id = ?").get(id) as WorkflowInstance;
    if (!row) return null;

    const newIndex = row.step_index + 1;
    const isComplete = newIndex >= row.total_steps;
    const newStatus = isComplete ? 'completed' : 'running';
    const resultStr = resultData ? JSON.stringify(resultData) : row.result;
    const updatedAt = Date.now();

    db.prepare(`
      UPDATE workflows 
      SET current_step = ?, step_index = ?, status = ?, result = ?, updated_at = ? 
      WHERE id = ?
    `).run(nextStep, newIndex, newStatus, resultStr, updatedAt, id);

    return {
      ...row,
      current_step: nextStep,
      step_index: newIndex,
      status: newStatus,
      result: resultStr,
      updated_at: updatedAt,
    };
  }

  /**
   * Fetch active workflows and execution stats
   */
  static getStats() {
    const totalStmt = db.prepare("SELECT COUNT(*) as count FROM workflows").get() as any;
    const runningStmt = db.prepare("SELECT COUNT(*) as count FROM workflows WHERE status = 'running'").get() as any;
    const completedStmt = db.prepare("SELECT COUNT(*) as count FROM workflows WHERE status = 'completed'").get() as any;

    const recentWorkflows = db.prepare("SELECT * FROM workflows ORDER BY updated_at DESC LIMIT 15").all() as WorkflowInstance[];

    return {
      total_workflows: totalStmt?.count || 0,
      running_workflows: runningStmt?.count || 0,
      completed_workflows: completedStmt?.count || 0,
      recent_workflows: recentWorkflows,
    };
  }
}
