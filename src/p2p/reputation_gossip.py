"""
BTP Decentralized P2P Peer Reputation Gossip Protocol.
Implements Byzantine-resistant peer reputation scoring with
EigenTrust transitive trust attenuation and fast-path slashing broadcasts.
"""

import os
import json
import time
import hmac
import hashlib
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional, Tuple


DEFAULT_GOSSIP_STORE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", ".btp_gossip_ledger.json"
)

SIGNING_SECRET_KEY = "btp_p2p_gossip_shared_sec_key"


@dataclass
class ReputationGossipMessage:
    message_id: str
    rater_agent_id: str
    target_agent_id: str
    score: float  # 0.0 to 1.0
    task_contract_id: str
    epoch: int
    timestamp: float = field(default_factory=time.time)
    signature: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def create(
        cls,
        rater_agent_id: str,
        target_agent_id: str,
        score: float,
        task_contract_id: str,
        epoch: int = 1
    ) -> "ReputationGossipMessage":
        entropy = f"{rater_agent_id}:{target_agent_id}:{score}:{task_contract_id}:{time.time_ns()}"
        msg_id = f"GOSSIP-{hashlib.sha256(entropy.encode()).hexdigest()[:12].upper()}"

        sign_payload = f"{msg_id}:{rater_agent_id}:{target_agent_id}:{score}:{epoch}"
        sig = hmac.new(SIGNING_SECRET_KEY.encode(), sign_payload.encode(), hashlib.sha256).hexdigest()

        return cls(
            message_id=msg_id,
            rater_agent_id=rater_agent_id,
            target_agent_id=target_agent_id,
            score=max(0.0, min(1.0, score)),
            task_contract_id=task_contract_id,
            epoch=epoch,
            timestamp=time.time(),
            signature=f"btp_gossip_sig_{sig[:32]}"
        )

    def verify(self) -> bool:
        sign_payload = f"{self.message_id}:{self.rater_agent_id}:{self.target_agent_id}:{self.score}:{self.epoch}"
        expected = "btp_gossip_sig_" + hmac.new(SIGNING_SECRET_KEY.encode(), sign_payload.encode(), hashlib.sha256).hexdigest()[:32]
        return self.signature == expected


@dataclass
class PeerNode:
    node_id: str
    address: str
    direct_trust: float = 0.5
    global_trust: float = 0.5
    vector_clock: int = 0
    jobs_audited: int = 0
    is_pretrusted: bool = False
    last_seen: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PeerReputationMesh:
    """
    Decentralized peer reputation coordinator implementing EigenTrust
    attenuation to suppress Sybil voting rings and propagate fast slashing.
    """

    def __init__(self, store_path: Optional[str] = None):
        self.store_path = os.path.abspath(store_path or DEFAULT_GOSSIP_STORE_PATH)
        self.peers: Dict[str, PeerNode] = {}
        self.gossip_history: List[ReputationGossipMessage] = []
        self.trust_matrix: Dict[str, Dict[str, float]] = {}  # rater -> target -> score
        self._init_default_mesh()
        self._load()

    def _init_default_mesh(self):
        defaults = [
            PeerNode(node_id="agent-code-auditor-99", address="p2p://node-1.btp.network:9001", direct_trust=0.98, global_trust=0.98, jobs_audited=289, is_pretrusted=True),
            PeerNode(node_id="agent-risk-oracle-01", address="p2p://node-2.btp.network:9002", direct_trust=0.99, global_trust=0.99, jobs_audited=142, is_pretrusted=True),
            PeerNode(node_id="agent-liquidity-arbiter-07", address="p2p://node-3.btp.network:9003", direct_trust=0.95, global_trust=0.95, jobs_audited=88, is_pretrusted=False),
            PeerNode(node_id="agent-cloudscale-worker-12", address="p2p://node-4.btp.network:9004", direct_trust=0.92, global_trust=0.92, jobs_audited=45, is_pretrusted=False),
        ]
        for p in defaults:
            self.peers[p.node_id] = p
            self.trust_matrix[p.node_id] = {}

    def _load(self):
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.get("peers", {}).items():
                        self.peers[k] = PeerNode(**v)
                    for msg in data.get("gossip_history", []):
                        self.gossip_history.append(ReputationGossipMessage(**msg))
            except Exception:
                pass

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
            with open(self.store_path, "w", encoding="utf-8") as f:
                json.dump({
                    "version": "5.4.0",
                    "peers": {k: v.to_dict() for k, v in self.peers.items()},
                    "gossip_history": [m.to_dict() for m in self.gossip_history[-100:]]
                }, f, indent=2)
        except Exception:
            pass

    def register_peer(self, node_id: str, address: str, is_pretrusted: bool = False) -> PeerNode:
        if node_id not in self.peers:
            self.peers[node_id] = PeerNode(
                node_id=node_id,
                address=address,
                direct_trust=0.5,
                global_trust=0.5,
                is_pretrusted=is_pretrusted
            )
            self.trust_matrix[node_id] = {}
            self._save()
        return self.peers[node_id]

    def broadcast_rating(
        self,
        rater_agent_id: str,
        target_agent_id: str,
        score: float,
        task_contract_id: str
    ) -> Tuple[bool, str, ReputationGossipMessage]:
        if rater_agent_id not in self.peers:
            self.register_peer(rater_agent_id, f"p2p://{rater_agent_id}.local")
        if target_agent_id not in self.peers:
            self.register_peer(target_agent_id, f"p2p://{target_agent_id}.local")

        msg = ReputationGossipMessage.create(
            rater_agent_id=rater_agent_id,
            target_agent_id=target_agent_id,
            score=score,
            task_contract_id=task_contract_id,
            epoch=self.peers[rater_agent_id].vector_clock + 1
        )

        if not msg.verify():
            return False, "Gossip message cryptographic verification failed.", msg

        self.gossip_history.append(msg)
        self.peers[rater_agent_id].vector_clock += 1

        # Update direct trust matrix
        if rater_agent_id not in self.trust_matrix:
            self.trust_matrix[rater_agent_id] = {}
        self.trust_matrix[rater_agent_id][target_agent_id] = msg.score

        # Re-compute global trust vector via EigenTrust
        self.compute_eigentrust()
        self._save()
        return True, "Reputation rating successfully broadcast and aggregated across mesh.", msg

    def compute_eigentrust(self, alpha: float = 0.85, max_iterations: int = 20) -> Dict[str, float]:
        """
        Executes power-iteration EigenTrust calculation:
        t^(k+1) = (1 - alpha) * C^T * t^(k) + alpha * p
        where p is pre-trusted baseline distribution.
        Dampens Sybil rating clusters by weighting trust paths from pre-trusted peers.
        """
        all_nodes = list(self.peers.keys())
        n = len(all_nodes)
        if n == 0:
            return {}

        # Pre-trusted baseline vector p
        pretrusted_nodes = [node for node, p in self.peers.items() if p.is_pretrusted]
        if not pretrusted_nodes:
            pretrusted_nodes = all_nodes

        p_vec = {node: (1.0 / len(pretrusted_nodes) if node in pretrusted_nodes else 0.0) for node in all_nodes}
        t_vec = {node: p_vec[node] for node in all_nodes}

        # Normalize direct trust matrix C
        norm_matrix: Dict[str, Dict[str, float]] = {u: {} for u in all_nodes}
        for u in all_nodes:
            ratings = self.trust_matrix.get(u, {})
            total_sum = sum(ratings.values())
            if total_sum > 0:
                for v in all_nodes:
                    norm_matrix[u][v] = ratings.get(v, 0.0) / total_sum
            else:
                for v in all_nodes:
                    norm_matrix[u][v] = p_vec[v]

        # Power iteration
        for _ in range(max_iterations):
            new_t: Dict[str, float] = {node: 0.0 for node in all_nodes}
            for v in all_nodes:
                c_sum = sum(norm_matrix[u].get(v, 0.0) * t_vec[u] for u in all_nodes)
                new_t[v] = ((1.0 - alpha) * c_sum) + (alpha * p_vec[v])
            t_vec = new_t

        # Update peer global trust records
        max_t = max(t_vec.values()) if t_vec and max(t_vec.values()) > 0 else 1.0
        for node, score in t_vec.items():
            normalized_score = round(min(1.0, max(0.01, score / max_t)), 4)
            self.peers[node].global_trust = normalized_score

        return t_vec

    def broadcast_slashing_penalty(self, target_agent_id: str, penalty_ratio: float = 0.5):
        """Fast-path slashing propagation across peer network upon Byzantine breach."""
        if target_agent_id in self.peers:
            peer = self.peers[target_agent_id]
            peer.direct_trust = max(0.0, peer.direct_trust * (1.0 - penalty_ratio))
            peer.global_trust = max(0.0, peer.global_trust * (1.0 - penalty_ratio))
            # Punish in direct trust matrix from all peers
            for u in self.peers:
                if target_agent_id in self.trust_matrix.get(u, {}):
                    self.trust_matrix[u][target_agent_id] *= (1.0 - penalty_ratio)
            self.compute_eigentrust()
            self._save()
