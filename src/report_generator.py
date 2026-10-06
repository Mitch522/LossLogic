from claim_evaluator import evaluate_claim


CLASSIFICATION_LABELS = {
    "RELATED_NEW": "Related - New Condition",
    "AGGRAVATION": "Related - Aggravation",
    "PREEXISTING": "Pre-Existing",
    "DEGENERATIVE": "Degenerative",
    "UNRELATED": "Unrelated",
    "UNDETERMINED": "Requires Additional Review",
}


def money(value):
    return f"${value:,.2f}"


def generate_report():
    evaluation = evaluate_claim()

    claim = evaluation["claim"]
    coverage = evaluation["coverage"]
    liability = evaluation["liability"]
    causation = evaluation["medical_causation"]
    financials = evaluation["financials"]
    bi_damages = evaluation["bi_damages"]
    summary = evaluation["claim_summary"]

    lines = []

    lines.append("# ClaimIQ Claim Evaluation")
    lines.append("")
    lines.append(
        "> Demonstration report generated from entirely fictional, "
        "synthetic claim data."
    )
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"**Claim:** {claim['claim_id']}")
    lines.append(f"**Loss Date:** {claim['loss_date']}")
    lines.append(f"**Jurisdiction:** {claim['jurisdiction']}")
    lines.append(
        f"**Coverage:** "
        f"{'Applies' if summary['coverage_applies'] else 'Requires Review'}"
    )
    lines.append(
        f"**BI Limit:** {money(summary['per_person_bi_limit'])} per person"
    )
    lines.append(
        f"**Liability:** "
        f"{summary['insured_liability_percent']}% insured / "
        f"{summary['claimant_comparative_negligence_percent']}% claimant"
    )
    lines.append(
        f"**Financially Allowed Medical Expenses:** "
        f"{money(summary['allowed_medical_expenses'])}"
    )
    lines.append(
        f"**Causation-Supported BI Medical Expenses:** "
        f"{money(summary['accident_related_allowed_medical_expenses'])}"
    )
    lines.append(
        f"**PIP Paid on Causation-Supported Bills:** "
        f"{money(summary['accident_related_pip_paid'])}"
    )
    lines.append(
        f"**Remaining Causation-Supported Medical Specials:** "
        f"{money(summary['accident_related_remaining_medical_specials'])}"
    )
    lines.append("")

    # Coverage
    lines.append("## Coverage")
    lines.append("")
    lines.append(coverage["conclusion"])
    lines.append("")
    lines.append(
        f"- BI limits: "
        f"{money(coverage['limits']['per_person'])} per person / "
        f"{money(coverage['limits']['per_accident'])} per accident"
    )

    if coverage["failed_requirements"]:
        lines.append(
            "- Failed requirements: "
            + ", ".join(coverage["failed_requirements"])
        )
    else:
        lines.append("- No coverage requirements failed.")

    lines.append("")

    # Liability
    lines.append("## Liability")
    lines.append("")
    lines.append(
        f"**Assessment:** "
        f"{liability['assessment']['insured_liability_percent']}% insured / "
        f"{liability['assessment']['claimant_comparative_negligence_percent']}% claimant"
    )
    lines.append(
        f"**Confidence:** {liability['assessment']['confidence']}"
    )
    lines.append(
        f"**Assessment Type:** "
        f"{liability['assessment']['assessment_type'].replace('_', ' ').title()}"
    )
    lines.append("")
    lines.append(liability["conclusion"])
    lines.append("")

    lines.append("### Primary Contributing Conduct")
    lines.append("")
    for item in liability["primary_contributing_conduct"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("### Comparative Contributing Conduct")
    lines.append("")
    for item in liability["comparative_contributing_conduct"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("### Evidence Limitations")
    lines.append("")
    for item in liability["evidence_limitations"]:
        lines.append(f"- {item}")
    lines.append("")

    # Medical Causation
    lines.append("## Medical Causation")
    lines.append("")

    for diagnosis_id, result in causation.items():
        label = CLASSIFICATION_LABELS.get(
            result["classification"],
            result["classification"],
        )

        lines.append(
            f"### {result['condition'].replace('_', ' ').title()}"
        )
        lines.append("")
        lines.append(f"**Diagnosis ID:** {diagnosis_id}")
        lines.append(
            f"**Body Region:** "
            f"{result['body_region'].replace('_', ' ').title()}"
        )
        lines.append(f"**Classification:** {label}")
        lines.append("")
        lines.append("**Rationale:**")
        lines.append("")

        for reason in result["reasons"]:
            lines.append(f"- {reason}")

        lines.append("")
        lines.append(
            "**Supporting Records:** "
            + ", ".join(result["supporting_record_ids"])
        )
        lines.append("")

    # Financial Evaluation
    lines.append("## Financial Evaluation")
    lines.append("")
    lines.append(
        f"- Total submitted charges: "
        f"{money(financials['summary']['total_submitted_charges'])}"
    )
    lines.append(
        f"- Voided charges excluded: "
        f"{money(financials['summary']['excluded_voided_charges'])}"
    )
    lines.append(
        f"- Duplicate charges excluded: "
        f"{money(financials['summary']['excluded_duplicate_charges'])}"
    )
    lines.append(
        f"- Bundled charges excluded: "
        f"{money(financials['summary']['excluded_bundled_charges'])}"
    )
    lines.append(
        f"- Allowed medical expenses: "
        f"{money(financials['summary']['total_allowed_medical_expenses'])}"
    )
    lines.append(
        f"- PIP paid: "
        f"{money(financials['summary']['total_pip_paid'])}"
    )
    lines.append(
        f"- Remaining allowable medical specials: "
        f"{money(financials['summary']['remaining_allowable_medical_specials'])}"
    )
    lines.append(
        f"- Remaining PIP limit: "
        f"{money(financials['summary']['pip_limit_remaining'])}"
    )
    lines.append("")

    # Causation-Supported BI Medical Evaluation
    lines.append("## Causation-Supported BI Medical Evaluation")
    lines.append("")
    lines.append(
        "This analysis applies the medical causation findings to the "
        "financially reconciled bills. A financially valid charge is not "
        "automatically treated as causation-supported BI medical expense."
    )
    lines.append("")
    lines.append(
        f"- Causation-supported allowed medical expenses: "
        f"{money(summary['accident_related_allowed_medical_expenses'])}"
    )
    lines.append(
        f"- PIP paid on causation-supported bills: "
        f"{money(summary['accident_related_pip_paid'])}"
    )
    lines.append(
        f"- Remaining causation-supported medical specials: "
        f"{money(summary['accident_related_remaining_medical_specials'])}"
    )
    lines.append("")

    lines.append("### Causation Exclusions")
    lines.append("")

    causation_exclusions = [
        bill
        for bill in bi_damages["bills"]
        if bill["included_in_evaluation"]
        and not bill["accident_related"]
    ]

    if causation_exclusions:
        for bill in causation_exclusions:
            diagnosis_details = []

            for diagnosis_id in bill["diagnosis_ids"]:
                result = causation.get(diagnosis_id)

                if result:
                    condition = result["condition"].replace("_", " ").title()
                    classification = CLASSIFICATION_LABELS.get(
                        result["classification"],
                        result["classification"],
                    )
                    diagnosis_details.append(
                        f"{diagnosis_id} ({condition}: {classification})"
                    )
                else:
                    diagnosis_details.append(diagnosis_id)

            lines.append(
                f"- {bill['bill_id']} ({bill['provider']}, "
                f"{bill['date_of_service']}): "
                f"{money(bill['allowed_amount'])} is financially allowable "
                f"but excluded from the causation-supported BI medical "
                f"total. Linked diagnoses: "
                f"{'; '.join(diagnosis_details)}."
            )
    else:
        lines.append(
            "- No financially allowable bills were excluded based on "
            "the medical causation analysis."
        )

    lines.append("")

    # Review Status
    lines.append("## Review Status")
    lines.append("")

    if summary["requires_additional_review"]:
        lines.append("**Additional review required.**")
        lines.append("")
        for flag in summary["review_flags"]:
            lines.append(f"- {flag}")
    else:
        lines.append(
            "No automated validation or review flags were identified "
            "for this demonstration claim."
        )

    lines.append("")

    # Final Summary
    lines.append("## Evaluation Summary")
    lines.append("")
    lines.append(
        "ClaimIQ identified applicable bodily injury coverage and an "
        f"{summary['insured_liability_percent']}/"
        f"{summary['claimant_comparative_negligence_percent']} liability "
        "assessment based on the available evidence."
    )
    lines.append("")
    lines.append(
        "The medical causation analysis identified "
        f"{len(summary['related_diagnosis_ids'])} condition(s) as new or "
        "aggravated by the loss and "
        f"{len(summary['non_related_diagnosis_ids'])} condition(s) as "
        "pre-existing, degenerative, or unrelated."
    )
    lines.append("")
    lines.append(
        "Financial reconciliation identified "
        f"{money(summary['allowed_medical_expenses'])} in allowable medical "
        "expenses before application of the medical causation findings."
    )
    lines.append("")
    lines.append(
        "After applying those causation findings, "
        f"{money(summary['accident_related_allowed_medical_expenses'])} "
        "is supported by conditions classified as new or aggravated by "
        "the loss, with "
        f"{money(summary['accident_related_remaining_medical_specials'])} "
        "remaining after PIP payments on those bills."
    )
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_report())
