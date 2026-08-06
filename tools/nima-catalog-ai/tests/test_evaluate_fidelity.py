from src import evaluate_fidelity
from src.config import TOOL_ROOT

PROMPTS_DIR = TOOL_ROOT / "prompts"
SCHEMAS_DIR = TOOL_ROOT / "schemas"


def test_reject_decision_maps_to_rejected_state():
    assert evaluate_fidelity.state_for_decision("reject") == "rejected"
    assert evaluate_fidelity.state_for_decision("review") == "review"
    assert evaluate_fidelity.state_for_decision("approved_candidate") == "approved_candidate"


def test_evaluate_candidate_reject_flow(product_dir, fake_client, tmp_path):
    fake_client.fidelity_decision = "reject"
    candidate = tmp_path / "candidate.png"
    candidate.write_bytes(b"\x89PNG\r\n")

    from tests.conftest import DEFAULT_ANALYSIS

    plan_entry = {
        "type": "refined",
        "primary_reference": "01-original.jpg",
        "secondary_references": [],
        "goal": "g",
        "composition": "c",
        "background": "b",
        "lighting": "l",
        "aspect_ratio": "1:1",
        "mandatory_rules": ["Preserve shape"],
        "risks": [],
        "rejection_criteria": ["shape changed"],
    }
    report = evaluate_fidelity.evaluate_candidate(
        handle="test-product",
        output_type="refined",
        candidate_path=candidate,
        analysis=DEFAULT_ANALYSIS,
        plan_entry=plan_entry,
        input_dir=product_dir,
        prompts_dir=PROMPTS_DIR,
        schemas_dir=SCHEMAS_DIR,
        client=fake_client,
        model="gpt-5.6-sol",
    )
    assert report["decision"] == "reject"
    assert report["candidate_file"] == "candidate.png"
    assert report["output_type"] == "refined"


def test_in_use_never_auto_approved(product_dir, fake_client, tmp_path):
    fake_client.fidelity_decision = "approved_candidate"
    candidate = tmp_path / "candidate.png"
    candidate.write_bytes(b"\x89PNG\r\n")
    from tests.conftest import DEFAULT_ANALYSIS

    plan_entry = {
        "type": "in-use",
        "primary_reference": "01-original.jpg",
        "secondary_references": [],
        "goal": "g",
        "composition": "c",
        "background": "b",
        "lighting": "l",
        "aspect_ratio": "4:5",
        "mandatory_rules": ["Preserve shape"],
        "risks": [],
        "rejection_criteria": ["wrong interaction"],
    }
    report = evaluate_fidelity.evaluate_candidate(
        handle="test-product",
        output_type="in-use",
        candidate_path=candidate,
        analysis=DEFAULT_ANALYSIS,
        plan_entry=plan_entry,
        input_dir=product_dir,
        prompts_dir=PROMPTS_DIR,
        schemas_dir=SCHEMAS_DIR,
        client=fake_client,
        model="gpt-5.6-sol",
    )
    assert report["decision"] == "review"
