import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_router import detect_pii, detect_code, classify


class TestPII:
    def test_phone_10digit(self):
        has_pii, _ = detect_pii("call me at 9876543210")
        assert has_pii is True

    def test_phone_formatted(self):
        has_pii, _ = detect_pii("call me at 123-456-7890")
        assert has_pii is True

    def test_email(self):
        has_pii, _ = detect_pii("my email is test@example.com")
        assert has_pii is True

    def test_secret_keyword(self):
        has_pii, _ = detect_pii("api_key=sk_test_1234567890abcdef")
        assert has_pii is True

    def test_no_pii(self):
        has_pii, _ = detect_pii("what is 2+2?")
        assert has_pii is False


class TestCode:
    def test_python_function(self):
        is_code, _ = detect_code("def hello(): return 'world'")
        assert is_code is True

    def test_javascript(self):
        is_code, _ = detect_code("const x = () => { return 1; }")
        assert is_code is True

    def test_sql(self):
        is_code, _ = detect_code("SELECT * FROM users WHERE id = 1")
        assert is_code is True

    def test_no_code(self):
        is_code, _ = detect_code("what is the weather today?")
        assert is_code is False


class TestClassify:
    def test_sensitive_routes_local(self):
        result = classify("my email is test@example.com")
        assert result == "sensitive"

    def test_coding_routes_coding(self):
        result = classify("def foo(): pass")
        assert result == "coding"

    def test_general_routes_cloud(self):
        result = classify("what is 2+2?")
        assert result == "general"

    def test_pii_priority_over_code(self):
        result = classify("email: test@example.com\ndef foo(): pass")
        assert result == "sensitive"
