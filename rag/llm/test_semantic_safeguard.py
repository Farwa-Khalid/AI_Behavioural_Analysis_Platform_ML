
import json
from unittest.mock import patch

from rag.llm import llm_evidence_extractor as extractor


class FakeGeminiResponse:
    def __init__(self, data):
        self.text = json.dumps(data)


class FakeModels:
    def __init__(self, data):
        self.data = data

    def generate_content(self, **kwargs):
        return FakeGeminiResponse(self.data)


class FakeClient:
    def __init__(self, data):
        self.models = FakeModels(data)


def run_test(user_response):
    fake_data = {
        "evidence": [
            {
                "construct": "stress_vulnerability",
                "attribute": "detected",
                "value": True,
                "evidence_state": "known",
                "evidence_text": user_response,
            }
        ],
        "clarification_question": None,
    }

    with (
        patch.object(
            extractor,
            "genai",
        ) as fake_genai,
        patch.object(
            extractor,
            "api_key",
            "FAKE_TEST_KEY",
            create=True,
        ),
    ):
        fake_genai.Client.return_value = FakeClient(fake_data)

        # Patch the environment-based API key lookup if needed.
        with patch.dict(
            "os.environ",
            {"GEMINI_API_KEY": "FAKE_TEST_KEY"},
        ):
            result = extractor.extract_semantic_evidence(
                user_response
            )

    print("\nRESPONSE:", user_response)
    print("STATUS:", result["status"])
    print("EVIDENCE:", result["evidence"])
    print("CLARIFICATION:", result["clarification_question"])


if __name__ == "__main__":
    run_test(
        "My final year project is really stressful."
    )

    run_test(
        "I often struggle to cope with stressful situations."
    )
