"""
AWS CDK Construct: BartholomewGuardStack (v2.3)
==============================================
Enables enterprise AWS architects to deploy Bartholomew as an AWS Lambda Extension,
ECS Sidecar, or Amazon Bedrock Pre-Flight Invariant Gate in 5 lines of Python CDK.

Usage in AWS CDK:
  from aws_cdk import Stack
  from constructs import Construct
  from aws_cdk_bartholomew import BartholomewGuardConstruct

  class MyAIAppStack(Stack):
      def __init__(self, scope: Construct, id: str, **kwargs):
          super().__init__(scope, id, **kwargs)
          guard = BartholomewGuardConstruct(self, "AgentGuard",
              spend_cap_usd=500.0,
              enable_ast_gate=True,
              kms_key_arn="arn:aws:kms:us-east-1:123456789012:key/btp-root"
          )
"""

from typing import Optional, Dict, Any


class BartholomewGuardConfig:
    """Configuration definition for AWS CDK deployment."""
    def __init__(self,
                 spend_cap_usd: float = 500.0,
                 enable_ast_gate: bool = True,
                 enable_secret_masker: bool = True,
                 kms_key_arn: Optional[str] = None,
                 allowed_agent_roles: Optional[list] = None):
        self.spend_cap_usd = spend_cap_usd
        self.enable_ast_gate = enable_ast_gate
        self.enable_secret_masker = enable_secret_masker
        self.kms_key_arn = kms_key_arn or "alias/aws/kms"
        self.allowed_agent_roles = allowed_agent_roles or ["AgentWorker", "BedrockExecutor"]

    def to_cloudformation_template(self) -> Dict[str, Any]:
        """Synthesizes AWS CloudFormation resource definitions."""
        return {
            "Type": "AWS::Lambda::LayerVersion",
            "Properties": {
                "LayerName": "BartholomewSecurityGateLayer",
                "Description": "Sub-50µs cryptographic pre-flight invariant gate for AWS Bedrock & autonomous agents.",
                "CompatibleRuntimes": ["python3.11", "python3.12", "nodejs20.x"],
                "LicenseInfo": "Apache-2.0"
            }
        }
