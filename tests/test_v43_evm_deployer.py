"""
Milestone 4.3 Tests: EVM Testnet Deployment & Verification Tooling.
Validates deploying BartholomewEscrowPool.sol to Base Sepolia, Arbitrum Sepolia,
and generating EIP-712 contract configurations.
"""

import pytest
import os
import json
from src.settlement.evm_deployer import EVMDeployer, NETWORK_CONFIGS


def test_evm_deployer_base_sepolia(tmp_path):
    deployer = EVMDeployer(network="base-sepolia")
    out_file = str(tmp_path / "base_sepolia_escrow.json")
    
    receipt = deployer.deploy(dry_run=True, output_file=out_file)

    assert receipt["status"] == "DEPLOYED"
    assert receipt["chain_id"] == 84532
    assert receipt["contract_address"].startswith("0x")
    assert len(receipt["contract_address"]) == 42
    assert "basescan.org" in receipt["explorer_url"]
    assert os.path.exists(out_file)

    with open(out_file, "r") as f:
        saved = json.load(f)
    assert saved["contract_address"] == receipt["contract_address"]


def test_evm_deployer_arbitrum_sepolia():
    deployer = EVMDeployer(network="arbitrum-sepolia")
    receipt = deployer.deploy(dry_run=True)

    assert receipt["chain_id"] == 421614
    assert "arbiscan.io" in receipt["explorer_url"]
    assert len(receipt["abi"]) > 0


def test_evm_deployer_unknown_network():
    with pytest.raises(ValueError, match="Unknown network"):
        EVMDeployer(network="unsupported-chain")
