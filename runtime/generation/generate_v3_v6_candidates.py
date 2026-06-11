from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.validation.validator_engine import evaluate_text


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_candidates(bundle: dict) -> list[dict]:
    protagonist = bundle["protagonist"]
    role = bundle["role"]
    artifact = bundle["artifact"]
    hidden_truth = bundle["hidden_truth"]
    pressure = bundle["pressure"]
    change = bundle["change"]
    setting = bundle["setting"]

    return [
        {
            "candidate_id": "v3v6_candidate_001",
            "strategy": "high_integrity_concrete_reveal",
            "text": (
                f"After midnight in {setting}, {protagonist}, a {role}, opened the {artifact} and found the detail that made the whole district lie collapse. "
                f"The number looked small until it touched the name beside it; then {pressure} stopped sounding like rumor and started sounding like proof.\n\n"
                f"People in the square did not lean closer because the moment was theatrical. They leaned closer because the page gave them something hard enough to carry: a date, a signature, a route, a missing payment. "
                f"{protagonist} understood that the real danger was no longer being wrong in private but leaving the truth unspoken in public.\n\n"
                f"So the scene turned on {change}. The {artifact} stopped functioning as paperwork and started functioning as witness."
            ),
        },
        {
            "candidate_id": "v3v6_candidate_002",
            "strategy": "generic_portable_motivation",
            "text": (
                "You are one decision away from the life you deserve. Stay strong. Trust the process. "
                "The people who change everything are the people who keep going when it gets hard. "
                "What matters is how you show up, why you keep believing, and what your mindset allows."
            ),
        },
        {
            "candidate_id": "v3v6_candidate_003",
            "strategy": "dialogue_hook_with_consequence",
            "text": (
                f"\"Read the fourth line,\" {protagonist} said.\n"
                f"\"It's only a receipt,\" the auditor answered.\n"
                f"\"No,\" {protagonist} said. \"It's the first time {hidden_truth} had to sign its own name.\"\n\n"
                f"The room changed because the page carried weight, not because anyone raised their voice. "
                f"In {setting}, even a small record could become a public lever once enough people saw what it connected."
            ),
        },
        {
            "candidate_id": "v3v6_candidate_004",
            "strategy": "identity_relay_with_specific_example",
            "text": (
                f"If you have ever watched one honest detail break a larger fraud, you know the pause that follows. "
                f"It is never only relief. It is embarrassment, anger, and the strange steadiness that arrives when a fact finally has a body.\n\n"
                f"Here that body was the {artifact}: not a slogan, not a leak without consequence, but a record with a route, a number, and a name. "
                f"That is why {change} lands. It gives the reader something more durable than mood."
            ),
        },
        {
            "candidate_id": "v3v6_candidate_005",
            "strategy": "motif_heavy_but_progressive",
            "text": (
                f"The {artifact} kept returning, but never as the same object. At first it was a tool of concealment. Then it became pressure. "
                f"By the time {protagonist} touched it in front of the room, it had turned into evidence.\n\n"
                f"That shift mattered because {pressure} was no longer abstract. The object carried a route, a time, and a person who could not explain it away."
            ),
        },
    ]


def objective_score(result: dict) -> float:
    validators = {item["validator_id"]: item for item in result["validator_results"]}
    viral = result["reader_metrics"]["viral_metrics"]
    weights = {
        "semantic_redundancy_detector": 0.16,
        "cadence_variance_checker": 0.08,
        "abstraction_ratio_checker": 0.08,
        "human_style_preference_validator": 0.08,
        "emotional_resonance_validator": 0.09,
        "memorability_validator": 0.09,
        "hook_strength_validator": 0.08,
        "novelty_validator": 0.08,
        "insight_density_validator": 0.13,
        "viral_integrity_validator": 0.13,
    }
    score = sum(validators[key]["score"] * weight for key, weight in weights.items())
    score += 0.1 * viral["viral_score"]
    if result["final_status"] == "accepted_with_warnings":
        score -= 0.03
    elif result["final_status"] == "rejected":
        score -= 0.2
    return round(score, 4)


def main() -> None:
    run_dir = ROOT / "runs" / "v3_v6_generator_demo"
    run_dir.mkdir(parents=True, exist_ok=True)
    input_bundle = load_json(run_dir / "input_bundle.json")
    registry = load_json(ROOT / "runtime" / "validation" / "validator_registry.json")
    thresholds = load_json(ROOT / "runtime" / "validation" / "evaluation_thresholds.json")

    candidates = []
    for candidate in build_candidates(input_bundle):
        result = evaluate_text(candidate["text"], {}, thresholds, registry)
        validators = {item["validator_id"]: item for item in result["validator_results"]}
        candidate["evaluation"] = {
            "final_status": result["final_status"],
            "objective_score": objective_score(result),
            "semantic_redundancy_score": validators["semantic_redundancy_detector"]["score"],
            "cadence_score": validators["cadence_variance_checker"]["score"],
            "abstraction_score": validators["abstraction_ratio_checker"]["score"],
            "human_style_score": validators["human_style_preference_validator"]["score"],
            "emotional_resonance_score": validators["emotional_resonance_validator"]["score"],
            "memorability_score": validators["memorability_validator"]["score"],
            "hook_strength_score": validators["hook_strength_validator"]["score"],
            "novelty_score": validators["novelty_validator"]["score"],
            "insight_density_score": validators["insight_density_validator"]["score"],
            "viral_integrity_score": validators["viral_integrity_validator"]["score"],
            "viral_score": result["reader_metrics"]["viral_metrics"]["viral_score"],
        }
        candidates.append(candidate)

    candidates.sort(key=lambda item: item["evaluation"]["objective_score"], reverse=True)
    selected = candidates[0]

    write_json(run_dir / "generated_candidates.json", {"run_id": input_bundle["run_id"], "candidates": candidates})
    (run_dir / "selected_output.txt").write_text(selected["text"], encoding="utf-8")
    write_json(
        run_dir / "selection_report.json",
        {
            "run_id": input_bundle["run_id"],
            "selected_candidate_id": selected["candidate_id"],
            "selected_strategy": selected["strategy"],
            "selected_status": selected["evaluation"]["final_status"],
            "selected_objective_score": selected["evaluation"]["objective_score"],
            "selection_basis": [
                "maximize v3 redundancy discipline and v6 viral value simultaneously",
                "prefer high insight density and viral integrity over portable genericity",
                "allow warnings when the combined objective remains strongest"
            ],
            "top_candidates": [
                {
                    "candidate_id": item["candidate_id"],
                    "strategy": item["strategy"],
                    "objective_score": item["evaluation"]["objective_score"],
                    "final_status": item["evaluation"]["final_status"],
                    "insight_density_score": item["evaluation"]["insight_density_score"],
                    "viral_integrity_score": item["evaluation"]["viral_integrity_score"],
                    "semantic_redundancy_score": item["evaluation"]["semantic_redundancy_score"],
                }
                for item in candidates[:3]
            ],
        },
    )


if __name__ == "__main__":
    main()
