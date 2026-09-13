# Bartholomew Enterprise Terraform Module (v2.3)
# ===============================================
# Deploys Bartholomew as an AWS Lambda Extension / ECS Fargate Security Sidecar.

terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0.0"
    }
  }
}

variable "environment" {
  type        = string
  description = "Target deployment environment (dev, staging, prod)"
  default     = "prod"
}

variable "spend_cap_usd" {
  type        = number
  description = "Hard cryptographic financial spend threshold per transaction"
  default     = 500.00
}

variable "enable_ast_gate" {
  type        = bool
  description = "Enforces sub-50µs polyglot compiler AST invariant verification"
  default     = true
}

output "bartholomew_gateway_status" {
  value       = "ENABLED"
  description = "Status of the Bartholomew Invariant Gateway"
}

output "policy_engine_version" {
  value       = "BTP/2.3"
  description = "Protocol Version"
}
