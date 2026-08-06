import json
import sys
from pathlib import Path

import pytest
from PIL import Image

TOOL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_ROOT))

DEFAULT_ANALYSIS = {
    "handle": "test-product",
    "title": "Test Product",
    "product_category": "pet accessory",
    "reference_images": ["01-original.jpg", "02-original.jpg", "03-original.jpg"],
    "primary_reference": "01-original.jpg",
    "critical_visual_features": ["rectangular gray mat", "raised lip edge"],
    "critical_functional_features": ["raised lip contains spills"],
    "allowed_changes": ["swap background to clean studio backdrop"],
    "forbidden_changes": ["do not change the mat shape", "do not change the color"],
    "variant_constraints": ["depict the gray colorway only"],
    "scale_constraints": ["19 x 12 inch mat — plausible under a mid-size bowl"],
    "interaction_constraints": [],
    "risk_level": "low",
    "eligible_outputs": {"refined": True, "lifestyle": True, "in_use": False},
    "requires_human_review": True,
    "unknowns": ["exact material composition not stated"],
}


def make_product_dir(base: Path, *, handle: str = "test-product", n_images: int = 3, with_brief: bool = True) -> Path:
    product_dir = base / handle
    original_dir = product_dir / "original"
    original_dir.mkdir(parents=True)

    for i in range(1, n_images + 1):
        img = Image.new("RGB", (64, 64), color=(120, 120, 120))
        img.save(original_dir / f"{i:02d}-original.jpg", "JPEG")

    manifest = {
        "handle": handle,
        "title": "Test Product",
        "vendor": "Nima",
        "type": "",
        "image_count": n_images,
        "original_image_urls": [f"https://example.com/{i}.jpg" for i in range(1, n_images + 1)],
    }
    (product_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if with_brief:
        brief = {
            "handle": handle,
            "title": "Test Product",
            "description": "<p>A gray waterproof feeding mat with a raised lip.</p>",
            "vendor": "Nima",
            "type": "Feeding accessories",
            "variants": [{"Color": "Gray", "price": "9.99"}],
            "colors": ["Gray"],
            "materials": "Silicone",
            "dimensions": "19 x 12 in",
            "primary_image_candidate": "original/01-original.jpg",
            "critical_fidelity_notes": ["Keep raised lip", "Keep rectangular shape"],
            "ordered_files": [f"original/{i:02d}-original.jpg" for i in range(1, n_images + 1)],
        }
        (product_dir / "product-brief.json").write_text(json.dumps(brief, indent=2), encoding="utf-8")

    return product_dir


class FakeOpenAIClient:
    """Stand-in for src.openai_client.OpenAIClient — never touches the network.

    `structured_responses` lets a test queue specific JSON payloads; otherwise a
    reasonable default is returned by call type (detected by schema_name).
    `fidelity_decision` controls what evaluate_candidate gets back.
    """

    def __init__(self, *, fidelity_decision: str = "approved_candidate", analysis_overrides: dict | None = None):
        self.structured_calls = []
        self.edit_calls = []
        self.fidelity_decision = fidelity_decision
        self.analysis = {**DEFAULT_ANALYSIS, **(analysis_overrides or {})}

    def structured_json(self, *, model, system_prompt, user_text, image_paths, json_schema, schema_name):
        self.structured_calls.append(schema_name)
        if schema_name == "product_analysis":
            return dict(self.analysis)
        if schema_name == "fidelity_report":
            decision = self.fidelity_decision
            return {
                "decision": decision,
                "overall_score": 90 if decision == "approved_candidate" else 20,
                "visual_identity_score": 90,
                "functional_accuracy_score": 90,
                "interaction_score": 90,
                "anatomy_score": 90,
                "violations": [] if decision != "reject" else [
                    {
                        "category": "shape",
                        "severity": "critical",
                        "description": "mat shape changed to round",
                        "evidence": "candidate image, whole frame",
                    }
                ],
                "verified_preserved_features": ["rectangular gray mat"],
                "uncertain_features": [],
                "recommended_action": {
                    "approved_candidate": "accept_for_human_review",
                    "review": "accept_for_human_review",
                    "reject": "regenerate",
                }[decision],
            }
        raise ValueError(f"Unexpected schema_name in test: {schema_name}")

    def edit_image(self, *, model, prompt, image_paths, size, quality, mask_path=None):
        from src.openai_client import ImageEditResult

        self.edit_calls.append(
            {
                "model": model,
                "size": size,
                "quality": quality,
                "images": [p.name for p in image_paths],
                "mask": mask_path.name if mask_path else None,
            }
        )
        img = Image.new("RGB", (32, 32), color=(200, 200, 200))
        import io

        buf = io.BytesIO()
        img.save(buf, "PNG")
        return ImageEditResult(
            image_bytes=buf.getvalue(),
            request_id=f"fake-req-{len(self.edit_calls)}",
            usage={"input_tokens": 10, "output_tokens": 20},
            model=model,
            duration_seconds=0.01,
        )


@pytest.fixture
def product_dir(tmp_path):
    return make_product_dir(tmp_path)


@pytest.fixture
def fake_client():
    return FakeOpenAIClient()
