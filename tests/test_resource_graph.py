import pytest
from bartholomew_eval.resource_graph import (
    ResourceNode,
    NeedNode,
    ResourceGraphEngine,
    create_simulated_exchange_graph
)


def test_resource_graph_direct_match():
    engine = ResourceGraphEngine()
    engine.add_resource(ResourceNode(
        resource_id="res_01",
        owner="Alice",
        resource_type="skill",
        capability="web_development",
        capacity="10_hours",
        availability="2026-09-01/2026-09-10"
    ))
    engine.add_need(NeedNode(
        need_id="need_01",
        owner="Bob",
        requirement_type="skill",
        requirement="web_development"
    ))

    matches = engine.find_direct_matches()
    assert len(matches) == 1
    assert matches[0]["match_type"] == "DIRECT_1_TO_1"
    assert matches[0]["provider"] == "Alice"
    assert matches[0]["receiver"] == "Bob"


def test_multi_party_cycle_discovery():
    engine = create_simulated_exchange_graph()

    cycles = engine.find_multi_party_cycles()
    assert len(cycles) >= 1

    found_4_way_cycle = False
    for cycle in cycles:
        if cycle["cycle_length"] == 4:
            found_4_way_cycle = True
            participants = cycle["participants"]
            assert "Entity_A_Developer" in participants
            assert "Entity_B_Accountant" in participants
            assert "Entity_C_EquipmentOwner" in participants
            assert "Entity_D_Landscaper" in participants
            assert len(cycle["observed_facts"]) >= 1
            assert len(cycle["estimates"]) >= 1

    assert found_4_way_cycle, "Expected a 4-party exchange cycle A -> B -> C -> D -> A"
