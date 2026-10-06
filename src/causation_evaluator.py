import json
from pathlib import Path
from typing import Any

from medical_evidence import build_diagnosis_evidence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MEDICAL_DATA = PROJECT_ROOT / "data" / "medical"


def load_signals() -> dict[str, dict[str, Any]]:
    with open(
        MEDICAL_DATA / "evidence_signals.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def classify_diagnosis(
    evidence: dict[str, Any],
    signals: dict[str, Any]
) -> tuple[str, list[str]]:

    reasons = []

    # A separate documented event provides a more direct causal explanation.
    if signals.get("separate_causal_event"):
        reasons.append(
            "A separate post-loss event provides a direct causal explanation "
            "for the condition."
        )
        return "UNRELATED", reasons

    # Chronic degenerative evidence without material traumatic change.
    if (
        signals.get("degenerative_findings")
        and evidence["pre_loss_documented"]
        and not signals.get("new_objective_findings")
        and not signals.get("material_imaging_change")
    ):
        reasons.append(
            "The condition was documented before the loss and the post-loss "
            "records do not show a material acute objective or imaging change."
        )
        reasons.append(
            "The available findings are primarily degenerative in character."
        )
        return "DEGENERATIVE", reasons

    # Pre-existing condition with material post-loss objective change.
    if (
        evidence["pre_loss_documented"]
        and (
            signals.get("new_objective_findings")
            or signals.get("new_neurologic_findings")
            or signals.get("material_imaging_change")
        )
    ):
        reasons.append(
            "The condition existed before the loss, but the post-loss evidence "
            "shows a material change from the documented baseline."
        )

        if signals.get("new_neurologic_findings"):
            reasons.append(
                "New neurologic findings are documented after the loss."
            )

        if signals.get("material_imaging_change"):
            reasons.append(
                "Post-loss imaging demonstrates a material change from "
                "pre-loss imaging."
            )

        return "AGGRAVATION", reasons

    # Pre-existing condition without material objective change.
    if evidence["pre_loss_documented"]:
        reasons.append(
            "The condition was documented before the loss."
        )

        if signals.get("subjective_worsening"):
            reasons.append(
                "Subjective worsening is reported, but the available evidence "
                "does not demonstrate a material objective change."
            )
        else:
            reasons.append(
                "The available post-loss evidence does not demonstrate a "
                "material change from the pre-loss baseline."
            )

        return "PREEXISTING", reasons

    # New condition appearing promptly after the loss with supporting findings.
    if (
        not evidence["pre_loss_documented"]
        and evidence["post_loss_documented"]
        and signals.get("new_post_loss_symptoms")
        and (
            signals.get("new_objective_findings")
            or signals.get("material_imaging_change")
        )
    ):
        reasons.append(
            "The condition was not documented before the loss."
        )
        days = evidence["days_to_first_post_loss_record"]
        day_label = "day" if days == 1 else "days"
        reasons.append(
            f"Relevant post-loss evidence was documented "
            f"{days} {day_label} after the loss."
        )
        reasons.append(
            "The post-loss records contain supporting objective findings."
        )
        return "RELATED_NEW", reasons

    reasons.append(
        "The available evidence is insufficient for a supported classification."
    )
    return "UNDETERMINED", reasons


def evaluate_causation() -> dict[str, dict[str, Any]]:
    evidence = build_diagnosis_evidence()
    signals = load_signals()

    results = {}

    for diagnosis_id, diagnosis_evidence in evidence.items():
        diagnosis_signals = signals.get(diagnosis_id, {})

        classification, reasons = classify_diagnosis(
            diagnosis_evidence,
            diagnosis_signals
        )

        results[diagnosis_id] = {
            "condition": diagnosis_evidence["condition"],
            "body_region": diagnosis_evidence["body_region"],
            "classification": classification,
            "reasons": reasons,
            "supporting_record_ids": diagnosis_signals.get(
                "supporting_record_ids", []
            )
        }

    return results


if __name__ == "__main__":
    print(json.dumps(evaluate_causation(), indent=2))
