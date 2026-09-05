export interface ToolCheckResult {
  allowed: boolean;
  reason: string;
}

export interface ScrubResult<T = any> {
  data: T;
  redactionCount: number;
}

export interface LicenseStatus {
  licensed: boolean;
  tier: 'COMMUNITY' | 'PRO' | 'ENTERPRISE';
  status: string;
}

export function evaluateToolCall(toolName: string, args: Record<string, any>): ToolCheckResult;
export function scrubSecrets<T = any>(data: T): ScrubResult<T>;
export function loadLicense(): LicenseStatus;
