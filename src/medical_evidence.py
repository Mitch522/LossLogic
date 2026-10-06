import json
from datetime import date
from pathlib import Path
from typing import Any

from medical_timeline import build_medical_timeline, load_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLAIM_FILE = PROJECT_ROOT / "data" / "coverage" / "claim.json"


def load_claim() -> dict[str, Any]:
    with open(CLAIM_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def build_diagnosis_evidence() -> dict[str, dict[str, Any]]:
    claim = load_claim()
    loss_date = date.fromisoformat(claim["loss_date"])

    diagnoses = load_json("diagnoses.json")["diagnoses"]
    timeline = build_medical_timeline()

    evidence: dict[str, dict[str, Any]] = {}

    for diagnosis in diagnoses:
        diagnosis_id = diagnosis["diagnosis_id"]
        body_region = diagnosis["body_region"]
        records = timeline.get(body_region, [])

        pre_loss_records = [
            record for record in records
            if record["period"] == "pre_loss"
        ]
        post_loss_records = [
            record for record in records
            if record["period"] == "post_loss"
        ]

        separate_event_records = [
            record for record in post_loss_records
            if record["separate_event"]
        ]

        first_post_loss_date = None
        days_to_first_post_loss_record = None

        if post_loss_records:
            first_post_loss_date = min(
                date.fromisoformat(record["date"])
                for record in post_loss_records
            )
            days_to_first_post_loss_record = (
                first_post_loss_date - loss_date
            ).days

        condition_pre_loss_ids = diagnosis.get(
            "pre_loss_condition_record_ids", []
        )

        evidence[diagnosis_id] = {
            "condition": diagnosis["condition"],
            "body_region": body_region,
            "pre_loss_documented": bool(condition_pre_loss_ids),
            "post_loss_documented": bool(post_loss_records),
            "separate_post_loss_event": bool(separate_event_records),
            "pre_loss_condition_record_ids": condition_pre_loss_ids,
            "pre_loss_body_region_record_ids": [
                record["record_id"] for record in pre_loss_records
            ],
            "post_loss_record_ids": [
                record["record_id"] for record in post_loss_records
            ],
            "separate_event_record_ids": [
                record["record_id"] for record in separate_event_records
            ],
            "days_to_first_post_loss_record": days_to_first_post_loss_record,
        }

    return evidence


if __name__ == "__main__":
    print(json.dumps(build_diagnosis_evidence(), indent=2))
