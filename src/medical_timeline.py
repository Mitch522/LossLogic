import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MEDICAL_DATA = PROJECT_ROOT / "data" / "medical"


def load_json(filename: str) -> dict[str, Any]:
    with open(MEDICAL_DATA / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def build_medical_timeline() -> dict[str, list[dict[str, Any]]]:
    pre_loss = load_json("pre_loss_records.json")["records"]
    post_loss = load_json("post_loss_records.json")["records"]

    timeline: dict[str, list[dict[str, Any]]] = {}

    for period, records in (("pre_loss", pre_loss), ("post_loss", post_loss)):
        for record in records:
            for body_region, findings in record.get("findings", {}).items():
                entry = {
                    "record_id": record["record_id"],
                    "date": record["date"],
                    "period": period,
                    "provider_type": record["provider_type"],
                    "reason_for_visit": record["reason_for_visit"],
                    "separate_event": record.get("separate_event", False),
                    "findings": findings,
                }
                timeline.setdefault(body_region, []).append(entry)

    for entries in timeline.values():
        entries.sort(key=lambda item: item["date"])

    return timeline


if __name__ == "__main__":
    timeline = build_medical_timeline()
    print(json.dumps(timeline, indent=2))
