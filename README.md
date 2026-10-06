# ClaimIQ

**Explainable, AI-ready bodily injury claim evaluation using structured insurance data and deterministic business logic.**

ClaimIQ is an independently developed insurance technology portfolio project demonstrating how complex bodily injury claim information can be transformed into structured, traceable, and reproducible claim analysis.

It combines insurance domain expertise with Python-based evaluation logic to analyze coverage, liability, medical causation, billing, PIP payments, and causation-supported medical damages.

> **Important:** ClaimIQ uses entirely fictional, synthetic claim data. It is a portfolio demonstration and is not intended to provide legal, medical, or claims-handling advice.

## The Problem

Bodily injury claims require information from multiple sources to be evaluated together, including policy information, statements, accident mechanics, medical history, treatment records, diagnostic findings, bills, and payments.

ClaimIQ demonstrates how those sources can be converted into structured evidence while preserving the reasoning behind each conclusion.

## What ClaimIQ Evaluates

### Coverage
Evaluates policy period, covered vehicle, permissive use, bodily injury coverage, known exclusions, and applicable BI limits.

### Liability
Reconciles driver statements, independent witness evidence, accident mechanics, and vehicle damage. The synthetic demonstration produces an **80% insured / 20% claimant** comparative negligence assessment. Liability is identified as professional judgment rather than a mathematically generated score.

### Medical Causation
Compares pre-loss and post-loss evidence and classifies conditions as Related - New Condition, Related - Aggravation, Pre-Existing, Degenerative, Unrelated, or Requires Additional Review.

The analysis considers temporal relationship, pre-loss documentation, objective changes, neurologic findings, imaging changes, and separate causal events. Supporting medical record IDs are retained for traceability.

### Billing and PIP Reconciliation
Evaluates submitted charges, corrected and voided bills, duplicates, bundled services, reimbursement rules, PIP payments, and remaining allowable medical specials.

### Causation-Supported BI Medical Evaluation
ClaimIQ deliberately separates **financial validity** from **medical causation**. A financially valid medical charge is not automatically treated as causation-supported bodily injury expense.

| Measure | Amount |
| --- | ---: |
| Financially allowable medical expenses | $2,425.00 |
| Causation-supported BI medical expenses | $2,075.00 |
| PIP paid on causation-supported bills | $1,660.00 |
| Remaining causation-supported medical specials | $415.00 |

In the demonstration claim, a $350 orthopedic charge is financially allowable but excluded from the causation-supported BI total because its linked conditions are classified as pre-existing and degenerative.

## Architecture

ClaimIQ separates three concepts:

1. **Source evidence**: policy data, statements, medical records, bills, and payments.
2. **Derived findings**: coverage requirements, liability facts, medical evidence signals, and reconciled billing.
3. **Claim conclusions**: coverage determination, liability assessment, medical causation classifications, and causation-supported financial evaluation.

This separation makes the evaluation easier to test, audit, explain, and extend.

## Project Structure

```text
ClaimIQ/
├── data/
│   ├── billing/
│   ├── coverage/
│   ├── liability/
│   └── medical/
├── docs/
├── examples/
│   ├── claim_evaluation.json
│   └── claim_evaluation.md
├── src/
│   ├── billing_reconciliation.py
│   ├── causation_evaluator.py
│   ├── claim_evaluator.py
│   ├── coverage_evaluator.py
│   ├── liability_evaluator.py
│   ├── liability_findings.py
│   ├── medical_evidence.py
│   ├── medical_timeline.py
│   └── report_generator.py
└── tests/
    ├── test_billing.py
    ├── test_causation.py
    ├── test_claim_evaluator.py
    ├── test_coverage.py
    ├── test_liability.py
    └── test_report.py
```

## Explainability and Traceability

ClaimIQ is designed to show **why** a conclusion was reached. Liability conclusions link to source evidence, medical classifications link to supporting record IDs, billing decisions link to individual bills, and causation-supported expenses link to diagnosis classifications.

Evidence limitations are surfaced rather than silently ignored.

## AI-Ready Design

ClaimIQ produces structured output that could support claims decision-support tools, adjuster review interfaces, AI-assisted claim summaries, medical chronology generation, claim QA workflows, analytics dashboards, and API-based insurance applications.

The current version uses deterministic business rules so its behavior remains reproducible and explainable.

## Automated Testing

ClaimIQ includes automated tests covering coverage, liability, medical causation, billing and PIP reconciliation, end-to-end claim evaluation, and human-readable report generation.

## Example Outputs

`examples/claim_evaluation.md` contains the human-readable claim evaluation.

`examples/claim_evaluation.json` contains the corresponding structured output for downstream applications.

## Why I Built This

My background includes more than 15 years in insurance, including bodily injury liability, litigation, medical record review, coverage analysis, claim evaluation, and claims leadership.

I built ClaimIQ to demonstrate how insurance domain knowledge can be translated into structured data, deterministic business logic, explainable decision support, automated testing, and AI-ready workflows.

The goal is not simply to produce an answer. It is to preserve the evidence and reasoning a human claims professional would need to understand how that answer was reached.

## Disclaimer

ClaimIQ is an independent portfolio project built with fictional and synthetic data. It is not affiliated with any insurer, employer, client, or other claims technology project.

It is intended solely to demonstrate software design, insurance domain modeling, data transformation, automated testing, and explainable decision-support concepts.
