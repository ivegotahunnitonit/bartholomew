// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title BartholomewEscrowPool
 * @author Bartholomew AI (https://bartholomew.info)
 * @notice BTP v4.2 Decentralized Autonomous Multi-Agent Escrow & Slashing Pool.
 * @dev Implements EIP-712 typed structured data signing for micro-escrow collateral
 *      and cryptographic peer-quorum dispute slashing across EVM L2s (Base, Arbitrum One).
 */

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract BartholomewEscrowPool {
    // --- EIP-712 Domain Separator Constants ---
    bytes32 public constant DOMAIN_TYPEHASH = keccak256(
        "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
    );

    bytes32 public constant SLASHING_CLAIM_TYPEHASH = keccak256(
        "EscrowSlashingClaim(bytes32 escrowId,address agentId,address payeeAddress,uint256 amountUsd,string violatedInvariant,bytes32 proofHash,uint256 nonce,uint256 deadline)"
    );

    bytes32 public immutable DOMAIN_SEPARATOR;
    address public owner;
    bool public paused;

    enum EscrowStatus { UNINITIALIZED, LOCKED, RELEASED, SLASHED }

    struct EscrowDeposit {
        bytes32 escrowId;
        address agent;
        address collateralToken; // address(0) for native ETH
        uint256 amount;
        uint256 lockedAt;
        EscrowStatus status;
    }

    struct SlashingClaim {
        bytes32 escrowId;
        address agentId;
        address payeeAddress;
        uint256 amountUsd;
        string violatedInvariant;
        bytes32 proofHash;
        uint256 nonce;
        uint256 deadline;
    }

    mapping(bytes32 => EscrowDeposit) public escrows;
    mapping(address => bool) public registeredJurors;
    mapping(uint256 => bool) public usedNonces;

    uint256 public constant MIN_JUROR_QUORUM = 2;

    event EscrowLocked(bytes32 indexed escrowId, address indexed agent, uint256 amount, address collateralToken);
    event EscrowReleased(bytes32 indexed escrowId, address indexed agent, uint256 amount);
    event EscrowSlashed(bytes32 indexed escrowId, address indexed payee, uint256 amount, string violatedInvariant);
    event JurorUpdated(address indexed juror, bool status);

    modifier onlyOwner() {
        require(msg.sender == owner, "UNAUTHORIZED_OWNER");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "CONTRACT_PAUSED");
        _;
    }

    constructor() {
        owner = msg.sender;
        DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                DOMAIN_TYPEHASH,
                keccak256(bytes("BartholomewEscrowPool")),
                keccak256(bytes("4.2.0")),
                block.chainid,
                address(this)
            )
        );
    }

    function setJuror(address juror, bool status) external onlyOwner {
        registeredJurors[juror] = status;
        emit JurorUpdated(juror, status);
    }

    function setPaused(bool _paused) external onlyOwner {
        paused = _paused;
    }

    /**
     * @notice Locks collateral bond for an autonomous agent action.
     */
    function lockNativeEscrow(bytes32 escrowId) external payable whenNotPaused {
        require(msg.value > 0, "INVALID_ESCROW_AMOUNT");
        require(escrows[escrowId].status == EscrowStatus.UNINITIALIZED, "ESCROW_ALREADY_EXISTS");

        escrows[escrowId] = EscrowDeposit({
            escrowId: escrowId,
            agent: msg.sender,
            collateralToken: address(0),
            amount: msg.value,
            lockedAt: block.timestamp,
            status: EscrowStatus.LOCKED
        });

        emit EscrowLocked(escrowId, msg.sender, msg.value, address(0));
    }

    /**
     * @notice Releases locked escrow upon successful task completion.
     */
    function releaseEscrow(bytes32 escrowId) external whenNotPaused {
        EscrowDeposit storage deposit = escrows[escrowId];
        require(deposit.status == EscrowStatus.LOCKED, "ESCROW_NOT_LOCKED");
        require(msg.sender == deposit.agent || msg.sender == owner, "NOT_AUTHORIZED_TO_RELEASE");

        deposit.status = EscrowStatus.RELEASED;
        uint256 amount = deposit.amount;

        if (deposit.collateralToken == address(0)) {
            (bool success, ) = deposit.agent.call{value: amount}("");
            require(success, "ETH_TRANSFER_FAILED");
        } else {
            bool success = IERC20(deposit.collateralToken).transfer(deposit.agent, amount);
            require(success, "TOKEN_TRANSFER_FAILED");
        }

        emit EscrowReleased(escrowId, deposit.agent, amount);
    }

    /**
     * @notice Slashes escrow collateral driven by verified EIP-712 slashing claim and peer juror signatures.
     */
    function slashWithQuorum(
        SlashingClaim calldata claim,
        bytes[] calldata jurorSignatures
    ) external whenNotPaused {
        require(block.timestamp <= claim.deadline, "CLAIM_EXPIRED");
        require(!usedNonces[claim.nonce], "NONCE_ALREADY_USED");
        require(jurorSignatures.length >= MIN_JUROR_QUORUM, "INSUFFICIENT_JUROR_QUORUM");

        EscrowDeposit storage deposit = escrows[claim.escrowId];
        require(deposit.status == EscrowStatus.LOCKED, "ESCROW_NOT_LOCKED");

        // Hash EIP-712 structured data
        bytes32 structHash = keccak256(
            abi.encode(
                SLASHING_CLAIM_TYPEHASH,
                claim.escrowId,
                claim.agentId,
                claim.payeeAddress,
                claim.amountUsd,
                keccak256(bytes(claim.violatedInvariant)),
                claim.proofHash,
                claim.nonce,
                claim.deadline
            )
        );

        bytes32 digest = keccak256(
            abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash)
        );

        // Verify that minimum quorum of unique registered jurors signed the claim
        address[] memory verifiedSigners = new address[](jurorSignatures.length);
        uint256 validCount = 0;

        for (uint256 i = 0; i < jurorSignatures.length; i++) {
            address recovered = recoverSigner(digest, jurorSignatures[i]);
            require(registeredJurors[recovered], "INVALID_OR_UNREGISTERED_JUROR");
            require(recovered != claim.agentId, "TARGET_AGENT_CANNOT_BE_JUROR");

            // Ensure no duplicate signatures
            for (uint256 j = 0; j < validCount; j++) {
                require(verifiedSigners[j] != recovered, "DUPLICATE_JUROR_SIGNATURE");
            }
            verifiedSigners[validCount] = recovered;
            validCount++;
        }

        usedNonces[claim.nonce] = true;
        deposit.status = EscrowStatus.SLASHED;
        uint256 amountToLiquidate = deposit.amount;

        // Disburse liquidated indemnity to payee
        if (deposit.collateralToken == address(0)) {
            (bool sent, ) = claim.payeeAddress.call{value: amountToLiquidate}("");
            require(sent, "LIQUIDATION_PAYOUT_FAILED");
        } else {
            bool sent = IERC20(deposit.collateralToken).transfer(claim.payeeAddress, amountToLiquidate);
            require(sent, "TOKEN_LIQUIDATION_FAILED");
        }

        emit EscrowSlashed(claim.escrowId, claim.payeeAddress, amountToLiquidate, claim.violatedInvariant);
    }

    function recoverSigner(bytes32 digest, bytes memory signature) public pure returns (address) {
        require(signature.length == 65, "INVALID_SIGNATURE_LENGTH");
        bytes32 r;
        bytes32 s;
        uint8 v;
        assembly {
            r := mload(add(signature, 32))
            s := mload(add(signature, 64))
            v := byte(0, mload(add(signature, 96)))
        }
        if (v < 27) {
            v += 27;
        }
        require(v == 27 || v == 28, "INVALID_SIGNATURE_V");
        return ecrecover(digest, v, r, s);
    }

    receive() external payable {}
}
