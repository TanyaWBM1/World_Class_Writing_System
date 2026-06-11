from __future__ import annotations

from runtime.mode_system.mode_router import (
    ACF_REQUIRED_FIELDS,
    build_generation_guidance,
    detect_imagination_drift,
    mode_contract,
    resolve_operating_mode,
)


def evaluate_mode_enforcement(text: str, profile: dict) -> dict:
    selected_mode = resolve_operating_mode(profile)
    contract = mode_contract(selected_mode)
    guidance = build_generation_guidance(profile)
    flags = list(guidance["mode_violation_flags"])

    if selected_mode == "creative_writing":
        if contract["acf_enabled"]:
            flags.append("creative_writing_acf_enabled")
        if contract["strict_claims_required"]:
            flags.append("creative_writing_strict_claims_enabled")
        if not contract["imagination_allowed"]:
            flags.append("creative_writing_imagination_disabled")
    elif selected_mode == "acf_lite":
        if detect_imagination_drift(text):
            flags.append("acf_lite_imagination_drift")
        for field in ACF_REQUIRED_FIELDS:
            if not str(profile.get(field, "") or "").strip():
                flags.append(f"acf_lite_missing_{field}")

    score = 1.0 if not flags else 0.45 if selected_mode == "creative_writing" else 0.15
    status = "pass" if not flags else "warn" if selected_mode == "creative_writing" else "fail"
    return {
        "validator_id": "mode_enforcement_validator",
        "score": round(score, 3),
        "status": status,
        "primary_library": "system_design_library",
        "secondary_libraries": [
            "evaluation_library",
            "failure_mode_library",
        ],
        "evidence": {
            "selected_mode": selected_mode,
            "mode_contract_applied": contract,
            "acf_requirements_active": contract["acf_enabled"],
            "imagination_allowed": contract["imagination_allowed"],
            "human_texture_allowed": contract["human_texture_allowed"],
            "mode_violation_flags": flags,
        },
    }
