import json
from typing import Any

from liability_findings import build_liability_findings


def evaluate_liability() -> dict[str, Any]:
    evidence = build_liability_findings()
    findings = evidence["findings"]
    supporting_evidence = evidence["supporting_evidence"]

    primary_conduct = []
    comparative_conduct = []
    limitations = []

    if findings["insured_initiated_lane_change"]:
        primary_conduct.append(
            "The insured initiated the lane change during which contact occurred."
        )

    if findings["claimant_occupied_destination_lane"]:
        primary_conduct.append(
            "Independent witness evidence supports that the claimant already "
            "occupied the destination lane."
        )

    if findings["insured_saw_claimant_before_maneuver"]:
        primary_conduct.append(
            "The insured reported seeing the claimant before beginning the maneuver."
        )

    if findings["contact_during_lateral_movement"]:
        primary_conduct.append(
            "Scene evidence places the contact during the insured's lateral movement."
        )

    if findings["damage_consistent_with_sideswipe"]:
        primary_conduct.append(
            "The vehicle damage pattern is consistent with a sideswipe collision."
        )

    if findings["claimant_accelerated_during_merge"]:
        comparative_conduct.append(
            "The claimant acknowledged accelerating during the developing merge."
        )

    if findings["claimant_acceleration_corroborated_by_witness"]:
        comparative_conduct.append(
            "The independent witness also observed the claimant appearing to "
            "increase speed."
        )

    if findings["claimant_took_evasive_action"]:
        comparative_conduct.append(
            "The claimant reported braking and moving left once the conflict "
            "became apparent."
        )

    limitations.append(
        "The witness could not determine the exact spacing between the vehicles "
        "when the lane change began."
    )
    limitations.append(
        "The witness could not confirm whether the insured's turn signal was activated."
    )

    insured_primary = (
        findings["insured_initiated_lane_change"]
        and findings["claimant_occupied_destination_lane"]
        and findings["contact_during_lateral_movement"]
    )

    claimant_comparative = (
        findings["claimant_accelerated_during_merge"]
        and findings["claimant_acceleration_corroborated_by_witness"]
    )

    if insured_primary and claimant_comparative:
        assessment = {
            "insured_liability_percent": 80,
            "claimant_comparative_negligence_percent": 20,
            "confidence": "MODERATE_HIGH",
            "assessment_type": "professional_judgment",
        }
        conclusion = (
            "The insured's lane-change maneuver is the primary contributing "
            "cause of the collision. The claimant's acceleration during the "
            "developing merge supports comparative negligence."
        )
    else:
        assessment = {
            "insured_liability_percent": None,
            "claimant_comparative_negligence_percent": None,
            "confidence": "INSUFFICIENT",
            "assessment_type": "professional_judgment",
        }
        conclusion = (
            "The available findings do not support the demonstration liability "
            "allocation without additional professional review."
        )

    material_evidence = sorted({
        evidence_id
        for finding, is_supported in findings.items()
        if is_supported
        for evidence_id in supporting_evidence.get(finding, [])
    })

    return {
        "primary_contributing_conduct": primary_conduct,
        "comparative_contributing_conduct": comparative_conduct,
        "material_evidence": material_evidence,
        "evidence_limitations": limitations,
        "assessment": assessment,
        "conclusion": conclusion,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_liability(), indent=2))
