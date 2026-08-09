from app.privacy_firewall import PrivacyFirewall
from app.schemas import PrivacyDecision, ToolCall


def test_privacy_firewall_blocks_secret_in_strict_mode() -> None:
    review = PrivacyFirewall().review(ToolCall("web", {"query": "token=sk-test-private"}, "test"), strict=True)
    assert review.decision == PrivacyDecision.BLOCK
    assert review.leak_count == 1

