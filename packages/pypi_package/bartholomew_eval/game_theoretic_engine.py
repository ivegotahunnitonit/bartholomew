"""
Bartholomew Game-Theoretic Mechanism Design Engine
===================================================
Provides Subgame Perfect Nash Equilibrium computation, dynamic collateral bonding,
challenger bounty allocation, and Grim Trigger reputation tracking for 100% autonomous
Agent-to-Agent (A2A) protocol execution.
"""

import time
import math
import random
from typing import Dict, Any, List, Optional, Tuple

class GameTheoreticStakeEngine:
    """
    Computes optimal collateral bonds, challenger audit bounties, payoff matrices,
    and Grim Trigger discount factors to ensure Honesty is the dominant Nash Equilibrium strategy.
    """
    def __init__(self, alpha_bounty_ratio: float = 0.85, default_discount_factor: float = 0.95):
        self.alpha = alpha_bounty_ratio  # Fraction of slashed Prover stake awarded to Challenger
        self.discount_factor = default_discount_factor  # Delta for repeated game horizon
        self.agent_history: Dict[str, Dict[str, Any]] = {}

    def calculate_required_bond(
        self,
        potential_exploit_value_usd: float,
        posterior_threat_prob: float,
        agent_did: str = "did:bth:default"
    ) -> float:
        """
        Calculates minimum required collateral bond S_P such that:
            S_P > R_exploit / alpha
        Dynamic multiplier increases if agent has high historical defect rate or high posterior risk.
        """
        history = self.agent_history.get(agent_did, {"defects": 0, "total_games": 0})
        defect_rate = (history["defects"] / max(history["total_games"], 1)) if history["total_games"] > 0 else 0.0

        # Base requirement for Nash stability
        base_stake = potential_exploit_value_usd / max(self.alpha, 0.1)

        # Risk scaling factor
        risk_multiplier = 1.0 + (posterior_threat_prob * 2.0) + (defect_rate * 3.0)
        required_bond = round(base_stake * risk_multiplier, 2)
        return max(required_bond, 1.0)  # Minimum $1.00 bond

    def calculate_challenger_bounty(self, prover_bond_usd: float) -> float:
        """
        Calculates the bounty payout earned by a Challenger upon detecting a tampered proof or constraint breach.
        """
        return round(self.alpha * prover_bond_usd, 2)

    def evaluate_payoff_matrix(
        self,
        prover_action: str,      # "HONEST" or "ADVERSARIAL"
        challenger_action: str,  # "AUDIT" or "PASS"
        prover_bond_usd: float,
        challenger_stake_usd: float,
        execution_reward_usd: float,
        potential_exploit_usd: float
    ) -> Dict[str, Any]:
        """
        Evaluates the 2x2 asymmetric game payoff matrix:

                     Challenger (Audit)            Challenger (Pass)
        Prover(H):   (R_exec - friction, -S_C)     (R_exec, 0)
        Prover(M):   (-S_P, S_C + alpha*S_P)       (R_exploit, 0)
        """
        p_act = prover_action.upper()
        c_act = challenger_action.upper()

        if p_act == "HONEST" and c_act == "PASS":
            payoff_prover = execution_reward_usd
            payoff_challenger = 0.0
            outcome = "NASH_OPTIMAL_PASS"

        elif p_act == "HONEST" and c_act == "AUDIT":
            friction = round(0.01 * prover_bond_usd, 2)
            payoff_prover = round(execution_reward_usd - friction, 2)
            payoff_challenger = round(-challenger_stake_usd, 2)
            outcome = "UNJUSTIFIED_CHALLENGE"

        elif p_act == "ADVERSARIAL" and c_act == "AUDIT":
            bounty = self.calculate_challenger_bounty(prover_bond_usd)
            payoff_prover = round(-prover_bond_usd, 2)
            payoff_challenger = round(challenger_stake_usd + bounty, 2)
            outcome = "DEFECT_CAUGHT_AND_SLASHED"

        else:  # ADVERSARIAL and PASS
            payoff_prover = potential_exploit_usd
            payoff_challenger = 0.0
            outcome = "PROTOCOL_EXPLOIT_LEAK"

        # Check Nash equilibrium stability condition
        is_nash_stable = (prover_bond_usd > (potential_exploit_usd / self.alpha)) if p_act == "HONEST" else False

        return {
            "prover_action": p_act,
            "challenger_action": c_act,
            "outcome": outcome,
            "payoff_prover_usd": payoff_prover,
            "payoff_challenger_usd": payoff_challenger,
            "prover_bond_usd": prover_bond_usd,
            "challenger_stake_usd": challenger_stake_usd,
            "is_nash_equilibrium": is_nash_stable,
        }

    def record_agent_game_outcome(self, agent_did: str, outcome: str) -> Dict[str, Any]:
        """
        Updates Grim Trigger reputation discount factor based on A2A game result.
        """
        if agent_did not in self.agent_history:
            self.agent_history[agent_did] = {
                "total_games": 0,
                "defects": 0,
                "clean_games": 0,
                "discount_factor": self.discount_factor,
                "grim_triggered": False,
            }

        hist = self.agent_history[agent_did]
        hist["total_games"] += 1

        if outcome in ["DEFECT_CAUGHT_AND_SLASHED", "PROTOCOL_EXPLOIT_LEAK"]:
            hist["defects"] += 1
            hist["grim_triggered"] = True
            hist["discount_factor"] = round(hist["discount_factor"] * 0.5, 4)  # Grim trigger penalty
        else:
            hist["clean_games"] += 1
            if not hist["grim_triggered"]:
                hist["discount_factor"] = min(round(hist["discount_factor"] * 1.01, 4), 0.999)

        return hist


class AgentToAgentGameSimulator:
    """
    Simulates autonomous multi-round Agent-to-Agent (A2A) interactions between
    Prover Agents, Challenger Red-Teams, and the Bartholomew Protocol Verifier.
    """
    def __init__(self, stake_engine: Optional[GameTheoreticStakeEngine] = None):
        self.engine = stake_engine or GameTheoreticStakeEngine()
        self.simulation_ledger: List[Dict[str, Any]] = []

    def run_a2a_cycle(
        self,
        prover_did: str,
        challenger_did: str,
        target_asset_value_usd: float,
        posterior_threat_prob: float,
        prover_honesty_prob: float = 0.95,
        challenger_audit_prob: float = 0.20
    ) -> Dict[str, Any]:
        """
        Executes a single autonomous A2A game cycle.
        """
        # Determine required bond
        required_bond = self.engine.calculate_required_bond(
            potential_exploit_value_usd=target_asset_value_usd,
            posterior_threat_prob=posterior_threat_prob,
            agent_did=prover_did
        )

        challenger_stake = round(required_bond * 0.1, 2)
        exec_reward = round(target_asset_value_usd * 0.05, 2)

        # Prover decides action based on probability
        is_honest = random.random() < prover_honesty_prob
        prover_action = "HONEST" if is_honest else "ADVERSARIAL"

        # Challenger decides action based on audit probability or high threat signal
        is_auditing = (random.random() < challenger_audit_prob) or (posterior_threat_prob > 0.40)
        challenger_action = "AUDIT" if is_auditing else "PASS"

        # Evaluate payoff
        payoff = self.engine.evaluate_payoff_matrix(
            prover_action=prover_action,
            challenger_action=challenger_action,
            prover_bond_usd=required_bond,
            challenger_stake_usd=challenger_stake,
            execution_reward_usd=exec_reward,
            potential_exploit_usd=target_asset_value_usd
        )

        # Update reputation
        prover_hist = self.engine.record_agent_game_outcome(prover_did, payoff["outcome"])

        cycle_record = {
            "cycle_id": f"cycle_a2a_{len(self.simulation_ledger) + 1:04d}",
            "timestamp": time.time(),
            "prover_did": prover_did,
            "challenger_did": challenger_did,
            "target_asset_value_usd": target_asset_value_usd,
            "posterior_threat_prob": posterior_threat_prob,
            "payoff": payoff,
            "prover_reputation": prover_hist,
        }

        self.simulation_ledger.append(cycle_record)
        return cycle_record

    def run_multi_round_simulation(
        self,
        num_rounds: int = 100,
        prover_did: str = "did:bth:agent_alpha",
        challenger_did: str = "did:bth:challenger_beta"
    ) -> Dict[str, Any]:
        """
        Executes a multi-round A2A simulation benchmark.
        """
        start_time = time.perf_counter()
        caught_defects = 0
        leaked_exploits = 0
        total_prover_net_usd = 0.0
        total_challenger_net_usd = 0.0

        for r in range(num_rounds):
            # Vary asset value and risk profile
            asset_val = float(random.randint(50, 500))
            # Inject an occasional adversarial attempt
            honesty_prob = 0.92 if r % 7 != 0 else 0.40
            threat_prob = round(random.uniform(0.01, 0.50), 3)

            rec = self.run_a2a_cycle(
                prover_did=prover_did,
                challenger_did=challenger_did,
                target_asset_value_usd=asset_val,
                posterior_threat_prob=threat_prob,
                prover_honesty_prob=honesty_prob,
                challenger_audit_prob=0.25
            )

            outcome = rec["payoff"]["outcome"]
            if outcome == "DEFECT_CAUGHT_AND_SLASHED":
                caught_defects += 1
            elif outcome == "PROTOCOL_EXPLOIT_LEAK":
                leaked_exploits += 1

            total_prover_net_usd += rec["payoff"]["payoff_prover_usd"]
            total_challenger_net_usd += rec["payoff"]["payoff_challenger_usd"]

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "total_rounds": num_rounds,
            "caught_defects": caught_defects,
            "leaked_exploits": leaked_exploits,
            "exploit_prevention_rate_pct": round(((num_rounds - leaked_exploits) / num_rounds) * 100, 2),
            "total_prover_net_usd": round(total_prover_net_usd, 2),
            "total_challenger_net_usd": round(total_challenger_net_usd, 2),
            "elapsed_ms": elapsed_ms,
            "throughput_cycles_per_sec": round(num_rounds / max(elapsed_ms / 1000, 0.001), 1)
        }
