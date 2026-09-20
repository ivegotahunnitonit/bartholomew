-- Bartholomew Cloud — BigQuery Telemetry & Compliance Schema
-- ============================================================
-- Optimized for Google Cloud BigQuery with Day Partitioning and
-- Multi-Tenant Workspace Clustering for sub-second audit queries.

CREATE SCHEMA IF NOT EXISTS `btp_telemetry`
OPTIONS (
  location = 'US',
  description = 'Bartholomew Cloud In-Process AI Agent Security Telemetry and SOC 2 Audit Ledger'
);

-- 1. High-Throughput Telemetry Events Table
CREATE TABLE IF NOT EXISTS `btp_telemetry.events`
(
  event_id STRING NOT NULL,
  workspace_id STRING NOT NULL,
  agent_id STRING NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  action_type STRING,
  verdict STRING NOT NULL, -- 'ALLOW' or 'DENY'
  rule_id STRING,          -- e.g. 'RULE-AST-001', 'RULE-SEC-003'
  reason STRING,
  latency_us FLOAT64,
  payload_hash STRING,
  receipt_signature STRING,
  merkle_root STRING,
  client_version STRING,
  metadata JSON
)
PARTITION BY DATE(timestamp)
CLUSTER BY workspace_id, verdict, rule_id
OPTIONS (
  description = 'Streaming telemetry events from btp-guard SDK instances across all enterprise agent fleets',
  require_partition_filter = FALSE
);

-- 2. Immutable Cryptographic Merkle Ledger Table
CREATE TABLE IF NOT EXISTS `btp_telemetry.merkle_ledger`
(
  block_id STRING NOT NULL,
  workspace_id STRING NOT NULL,
  merkle_root STRING NOT NULL,
  start_timestamp TIMESTAMP NOT NULL,
  end_timestamp TIMESTAMP NOT NULL,
  event_count INT64 NOT NULL,
  sealed_signature STRING NOT NULL,
  authority_pubkey STRING NOT NULL,
  soc2_attestation JSON
)
PARTITION BY DATE(end_timestamp)
CLUSTER BY workspace_id
OPTIONS (
  description = 'Hourly and daily sealed Merkle root checkpoints for SOC 2 Type II non-repudiation'
);

-- 3. Pre-Calculated Continuous Compliance View
CREATE OR REPLACE VIEW `btp_telemetry.v_continuous_compliance_summary` AS
SELECT
  workspace_id,
  DATE(timestamp) AS audit_date,
  COUNT(1) AS total_evaluations,
  COUNTIF(verdict = 'ALLOW') AS total_allowed,
  COUNTIF(verdict = 'DENY') AS total_intercepted,
  ROUND(AVG(latency_us), 2) AS avg_decision_latency_us,
  COUNT(DISTINCT agent_id) AS active_agents,
  APPROX_COUNT_DISTINCT(payload_hash) AS unique_tool_invocations
FROM
  `btp_telemetry.events`
GROUP BY
  workspace_id, audit_date;
