from __future__ import annotations

import re
from typing import Any

from app.schemas import PrivacyDecision, PrivacyFinding, PrivacyReview, ToolCall


EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
API_KEY_RE = re.compile(r"(?i)\b(api[_-]?key|token|secret|password)\b\s*[:=]\s*['\"]?[^'\"\s]{8,}")
WINDOWS_PATH_RE = re.compile(r"C:\\Users\\[^\\\s]+\\[^\s]+", re.IGNORECASE)


class PrivacyFirewall:
    def review(self, call: ToolCall, strict: bool = True) -> PrivacyReview:
        findings: list[PrivacyFinding] = []
        safe_payload: dict[str, Any] = {}
        for key, value in call.payload.items():
            text = str(value)
            redacted = text
            if EMAIL_RE.search(text):
                findings.append(PrivacyFinding("email", "Email-like value found in tool payload.", key))
                redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", redacted)
            if API_KEY_RE.search(text):
                findings.append(PrivacyFinding("secret", "Secret-like value found in tool payload.", key))
                redacted = API_KEY_RE.sub("[REDACTED_SECRET]", redacted)
            if WINDOWS_PATH_RE.search(text):
                findings.append(PrivacyFinding("local_path", "Private local path found in tool payload.", key))
                redacted = WINDOWS_PATH_RE.sub("[REDACTED_LOCAL_PATH]", redacted)
            safe_payload[key] = redacted if isinstance(value, str) else value
        secret_found = any(finding.kind == "secret" for finding in findings)
        decision = PrivacyDecision.BLOCK if strict and secret_found else PrivacyDecision.REDACT if findings else PrivacyDecision.ALLOW
        return PrivacyReview(decision=decision, safe_payload=safe_payload, findings=tuple(findings), leak_count=len(findings))

