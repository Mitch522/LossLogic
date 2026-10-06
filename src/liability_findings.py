import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LIABILITY_DATA = PROJECT_ROOT / "data" / "liability"


def load_json(filename: str) -> dict[str, Any]:
    with open(LIABILITY_DATA / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def build_liability_findings() -> dict[str, Any]:
    statements = load_json("driver_statements.json")["statements"]
    witness = load_json("witness_statement.json")
    damage = load_json("vehicle_damage.json")

    insured_statement = next(
        item for item in statements if item["party"] == "insured"
    )
    claimant_statement = next(
        item for item in statements if item["party"] == "claimant"
    )

    insured_account = insured_statement["account"]
    claimant_account = claimant_statement["account"]
    witness_observations = witness["observations"]
    scene = damage["scene_evidence"]

    findings = {
        "insured_initiated_lane_change": (
            insured_account["intended_movement"] == "merge_left"
            and scene["contact_occurred_during_lane_change"]
        ),
        "claimant_occupied_destination_lane": (
            witness_observations["claimant_vehicle_was_already_in_destination_lane"]
        ),
        "insured_saw_claimant_before_maneuver": (
            insured_account["claimant_seen_before_maneuver"]
        ),
        "claimant_accelerated_during_merge": (
            claimant_account["claimant_reported_speed_change"]
            == "slight_acceleration"
        ),
        "claimant_acceleration_corroborated_by_witness": (
            witness_observations["claimant_appeared_to_increase_speed"]
        ),
        "claimant_took_evasive_action": (
            claimant_account["evasive_action"] is not None
        ),
        "damage_consistent_with_sideswipe": (
            scene["impact_type"] == "sideswipe"
        ),
        "contact_during_lateral_movement": (
            scene["contact_occurred_during_lane_change"]
        ),
    }

    supporting_evidence = {
        "insured_initiated_lane_change": [
            insured_statement["statement_id"],
            "vehicle_damage.scene_evidence",
        ],
        "claimant_occupied_destination_lane": [
            witness["statement_id"],
        ],
        "insured_saw_claimant_before_maneuver": [
            insured_statement["statement_id"],
        ],
        "claimant_accelerated_during_merge": [
            claimant_statement["statement_id"],
        ],
        "claimant_acceleration_corroborated_by_witness": [
            witness["statement_id"],
        ],
        "claimant_took_evasive_action": [
            claimant_statement["statement_id"],
        ],
        "damage_consistent_with_sideswipe": [
            "vehicle_damage.scene_evidence",
        ],
        "contact_during_lateral_movement": [
            "vehicle_damage.scene_evidence",
        ],
    }

    return {
        "findings": findings,
        "supporting_evidence": supporting_evidence,
    }


if __name__ == "__main__":
    print(json.dumps(build_liability_findings(), indent=2))
