# -*- coding: utf-8 -*-
"""B2B Contract SLA Delivery Penalty Arbiter Skill for GenPark Agentic Commerce."""
import json
import hashlib
import time
from typing import Dict, Any

def calculate_sla_downtime_penalty(vendor_name: str, monthly_contract_value_usd: float, contracted_uptime_pct: float, actual_recorded_uptime_pct: float, total_outage_minutes: int) -> Dict[str, Any]:
    # Contracted monthly minutes (approx 43,200 mins in 30 days)
    total_month_mins = 43200
    allowed_downtime_mins = total_month_mins * (1.0 - (contracted_uptime_pct / 100.0))
    excess_downtime_mins = max(0, total_outage_minutes - int(allowed_downtime_mins))

    uptime_deficit = max(0.0, contracted_uptime_pct - actual_recorded_uptime_pct)

    # Standard enterprise tiered SLA rebate schedule
    if actual_recorded_uptime_pct < 98.0:
        credit_pct = 50.0  # Catastrophic breach
    elif actual_recorded_uptime_pct < 99.0:
        credit_pct = 30.0  # Major breach
    elif actual_recorded_uptime_pct < contracted_uptime_pct:
        credit_pct = 15.0  # Minor breach
    else:
        credit_pct = 0.0   # SLA Met

    penalty_amount_usd = round(monthly_contract_value_usd * (credit_pct / 100.0), 2)
    breach_flag = credit_pct > 0.0

    return {
        "vendor": vendor_name,
        "monthly_contract_fee_usd": monthly_contract_value_usd,
        "contracted_uptime_target_pct": contracted_uptime_pct,
        "actual_uptime_recorded_pct": actual_recorded_uptime_pct,
        "allowed_downtime_budget_mins": round(allowed_downtime_mins, 1),
        "total_unplanned_outage_mins": total_outage_minutes,
        "excess_outage_minutes": excess_downtime_mins,
        "sla_breach_detected": breach_flag,
        "contractual_credit_entitlement_pct": credit_pct,
        "enforceable_rebate_usd": penalty_amount_usd,
        "verdict": "LIQUIDATED_DAMAGES_ENFORCEABLE" if breach_flag else "SLA_MET_COMPLIANT",
        "arbiter": "GenPark Enterprise Legal FinOps Sentinel"
    }

def generate_sla_credit_demand_dossier(claim_id: str, vendor_name: str, penalty_credit_usd: float, outage_summary: str) -> Dict[str, Any]:
    hash_seed = f"{claim_id}_{vendor_name}_{penalty_credit_usd}_{time.time()}"
    dossier_hash = hashlib.sha256(hash_seed.encode()).hexdigest()[:16].upper()

    formal_notice = (
        f"FORMAL NOTICE OF SLA BREACH & DEBIT ADJUSTMENT\n\n"
        f"To: {vendor_name} Enterprise Account Management & Accounts Receivable\n"
        f"Claim Reference: SLA-{dossier_hash}\n"
        f"Breach Value: ${penalty_credit_usd:,.2f} USD\n\n"
        f"In accordance with Section 8.2 (Service Level Guarantees and Liquidated Remedies) of the governing Master Service Agreement, "
        f"notice is hereby served that {vendor_name} failed to maintain minimum contracted service availability:\n"
        f"Incident Abstract: {outage_summary}\n\n"
        f"Pursuant to the contract schedule, our enterprise has applied a billing credit of ${penalty_credit_usd:,.2f} USD "
        f"against the forthcoming billing cycle invoice. Written acknowledgement is requested within 10 business days.\n\n"
        f"Authorized Procurement Representative,\nGenPark Corporate Procurement Office"
    )

    return {
        "claim_id": claim_id,
        "dossier_token": f"SLA-{dossier_hash}",
        "vendor": vendor_name,
        "applied_credit_usd": penalty_credit_usd,
        "formal_demand_text": formal_notice,
        "status": "DEBIT_MEMO_COMPILED",
        "action": "Deduct credit from next month automated vendor AP disbursement."
    }
