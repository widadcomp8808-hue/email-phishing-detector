from __future__ import annotations

import email
import re
from dataclasses import dataclass
from email.message import Message
from typing import Iterable, List, Tuple
from urllib.parse import urlparse
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import pickle
import os

from .. import schemas


SUSPICIOUS_KEYWORDS: Tuple[str, ...] = (
    "verify your account",
    "update your password",
    "urgent action required",
    "suspended",
    "click here",
    "login now",
    "bank account",
    "invoice attached",
    "verify identity",
    "account locked",
    "security alert",
    "confirm your identity",
    "act now",
    "limited time",
    "expires soon",
    "click below",
    "verify now",
    "unusual activity",
    "verify payment",
    "update payment",
)

TRUST_SIGNAL_KEYWORDS: Tuple[str, ...] = (
    "newsletter",
    "receipt",
    "schedule",
    "meeting",
    "thank you",
    "invoice number",
    "order confirmation",
    "shipping",
    "tracking",
    "delivery",
)

SUSPICIOUS_DOMAINS: Tuple[str, ...] = (
    ".tk",
    ".ml",
    ".ga",
    ".cf",
    ".gq",
    ".xyz",
    ".top",
    ".click",
    ".download",
)


@dataclass
class EmailContent:
    """
    Simple container holding the normalized email artefacts for analysis.
    """

    subject: str | None
    body: str
    raw_headers: str | None = None
    from_address: str | None = None
    reply_to: str | None = None
    to_addresses: List[str] | None = None
    html_body: str | None = None


@dataclass
class EmailFeatures:
    """
    Extracted features from email for ML model.
    """

    suspicious_keyword_count: int
    trust_keyword_count: int
    url_count: int
    suspicious_domain_count: int
    exclamation_count: int
    question_count: int
    uppercase_ratio: float
    body_length: int
    subject_length: int
    has_html: bool
    html_ratio: float
    link_text_mismatch: bool
    from_domain_suspicious: bool
    reply_to_different: bool
    urgency_words: int
    spelling_errors_estimate: float


class EmailAnalyzer:
    """
    Enhanced email analyzer with advanced features and ML model.
    """

    def __init__(self, model_version: str = "0.1.0-ml") -> None:
        self.model_version = model_version
        self.model = None
        self.vectorizer = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """
        Initialize a simple ML model. In production, this would load a pre-trained model.
        For now, we use a rule-based ensemble that mimics ML behavior.
        """
        # This is a placeholder - in production, load a trained model
        # For now, we use enhanced heuristics that behave like an ML model
        pass

    def analyze_text(
        self, body: str, subject: str | None = None, headers: str | None = None
    ) -> schemas.AnalysisResponse:
        content = EmailContent(
            subject=subject,
            body=body,
            raw_headers=headers,
            html_body=body if "<html" in body.lower() or "<body" in body.lower() else None,
        )
        return self._run_analysis(content)

    def analyze_eml_bytes(self, data: bytes) -> schemas.AnalysisResponse:
        """
        Accepts raw RFC822 bytes and extracts the relevant textual information.
        """

        message = email.message_from_bytes(data)
        body = self._extract_body(message)
        html_body = self._extract_html_body(message)
        headers = self._serialize_headers(message)
        content = EmailContent(
            subject=message.get("Subject"),
            body=body,
            raw_headers=headers,
            from_address=message.get("From"),
            reply_to=message.get("Reply-To"),
            to_addresses=message.get_all("To", []),
            html_body=html_body,
        )
        return self._run_analysis(content)

    def _run_analysis(self, content: EmailContent) -> schemas.AnalysisResponse:
        normalized_body = self._normalize_text(content.body)
        normalized_subject = self._normalize_text(content.subject or "")
        headers = (content.raw_headers or "").lower()

        # Extract advanced features
        features = self._extract_features(content, normalized_body, normalized_subject, headers)

        # Use enhanced ML-like scoring
        score, highlights, insights = self._ml_like_score(features, normalized_body, normalized_subject, headers)

        verdict = "phishing" if score >= 0.5 else "legitimate"
        metadata = schemas.EmailMetadata(
            subject=content.subject,
            from_address=content.from_address,
            reply_to=content.reply_to,
            to_addresses=content.to_addresses or [],
        )
        return schemas.AnalysisResponse(
            verdict=verdict,
            confidence=abs(score - 0.5) * 2,  # Normalize to 0-1 range
            model_version=self.model_version,
            metadata=metadata,
            highlights=highlights,
            insights=insights,
        )

    def _extract_features(
        self, content: EmailContent, body: str, subject: str, headers: str
    ) -> EmailFeatures:
        """Extract comprehensive features from email content."""

        # Count keywords
        suspicious_keyword_count = self._count_hits(body + " " + subject, SUSPICIOUS_KEYWORDS)
        trust_keyword_count = self._count_hits(body + " " + subject, TRUST_SIGNAL_KEYWORDS)

        # Extract URLs (use original body for URL extraction)
        original_body = content.body or ""
        urls = self._extract_urls(original_body)
        url_count = len(urls)
        suspicious_domain_count = sum(1 for url in urls if any(domain in url.lower() for domain in SUSPICIOUS_DOMAINS))

        # Text analysis
        exclamation_count = original_body.count("!") + (content.subject or "").count("!")
        question_count = original_body.count("?") + (content.subject or "").count("?")
        
        # Uppercase ratio
        text_sample = original_body[:1000]
        if text_sample:
            uppercase_ratio = sum(1 for c in text_sample if c.isupper()) / len(text_sample)
        else:
            uppercase_ratio = 0.0

        # Length features
        body_length = len(original_body)
        subject_length = len(content.subject or "")

        # HTML analysis
        has_html = content.html_body is not None or "<html" in original_body.lower()
        html_ratio = len(re.findall(r"<[^>]+>", original_body)) / max(1, body_length) if body_length > 0 else 0.0

        # Link analysis
        link_text_mismatch = self._check_link_text_mismatch(original_body)

        # Domain analysis
        from_domain_suspicious = self._is_domain_suspicious(content.from_address or "")
        reply_to_different = (
            content.reply_to is not None
            and content.from_address is not None
            and self._extract_domain(content.reply_to) != self._extract_domain(content.from_address)
        )

        # Urgency words
        urgency_words = self._count_urgency_words(body + " " + subject)

        # Spelling errors estimate (simple heuristic based on character patterns)
        spelling_errors_estimate = self._estimate_spelling_errors(body)

        return EmailFeatures(
            suspicious_keyword_count=suspicious_keyword_count,
            trust_keyword_count=trust_keyword_count,
            url_count=url_count,
            suspicious_domain_count=suspicious_domain_count,
            exclamation_count=exclamation_count,
            question_count=question_count,
            uppercase_ratio=uppercase_ratio,
            body_length=body_length,
            subject_length=subject_length,
            has_html=has_html,
            html_ratio=html_ratio,
            link_text_mismatch=link_text_mismatch,
            from_domain_suspicious=from_domain_suspicious,
            reply_to_different=reply_to_different,
            urgency_words=urgency_words,
            spelling_errors_estimate=spelling_errors_estimate,
        )

    def _ml_like_score(
        self, features: EmailFeatures, body: str, subject: str, headers: str
    ) -> tuple[float, list[str], list[schemas.AnalysisInsight]]:
        """
        ML-like scoring using weighted features. This mimics a trained model.
        """

        # Feature weights (these would be learned from training data)
        weights = {
            "suspicious_keywords": 0.15,
            "trust_keywords": -0.08,
            "url_count": 0.12,
            "suspicious_domains": 0.20,
            "exclamation": 0.05,
            "uppercase_ratio": 0.08,
            "html_ratio": 0.06,
            "link_mismatch": 0.15,
            "suspicious_from": 0.12,
            "reply_different": 0.10,
            "urgency": 0.10,
            "spelling": 0.05,
        }

        # Calculate weighted score
        score = 0.3  # Base score (slightly biased toward legitimate)

        # Positive indicators (increase phishing probability)
        score += min(1.0, features.suspicious_keyword_count / 5.0) * weights["suspicious_keywords"]
        score += min(1.0, features.url_count / 3.0) * weights["url_count"]
        score += min(1.0, features.suspicious_domain_count / 2.0) * weights["suspicious_domains"]
        score += min(1.0, features.exclamation_count / 5.0) * weights["exclamation"]
        score += min(1.0, features.uppercase_ratio * 2.0) * weights["uppercase_ratio"]
        score += min(1.0, features.html_ratio * 10.0) * weights["html_ratio"]
        if features.link_text_mismatch:
            score += weights["link_mismatch"]
        if features.from_domain_suspicious:
            score += weights["suspicious_from"]
        if features.reply_to_different:
            score += weights["reply_different"]
        score += min(1.0, features.urgency_words / 3.0) * weights["urgency"]
        score += min(1.0, features.spelling_errors_estimate) * weights["spelling"]

        # Negative indicators (decrease phishing probability)
        score -= min(1.0, features.trust_keyword_count / 3.0) * abs(weights["trust_keywords"])

        # Normalize score to 0-1 range
        score = max(0.0, min(1.0, score))

        # Generate highlights
        highlights = []
        if features.suspicious_keyword_count > 0:
            highlights.append(f"تم اكتشاف {features.suspicious_keyword_count} كلمة/عبارة مشبوهة في الرسالة.")
        if features.suspicious_domain_count > 0:
            highlights.append(f"تم اكتشاف {features.suspicious_domain_count} رابط يحتوي على نطاق مشبوه.")
        if features.url_count > 3:
            highlights.append(f"الرسالة تحتوي على عدد كبير من الروابط ({features.url_count}).")
        if features.link_text_mismatch:
            highlights.append("تم اكتشاف عدم تطابق بين نص الرابط والرابط الفعلي.")
        if features.from_domain_suspicious:
            highlights.append("نطاق المرسل مشبوه.")
        if features.reply_to_different:
            highlights.append("عنوان الرد يختلف عن عنوان المرسل.")
        if features.urgency_words > 2:
            highlights.append("الرسالة تحتوي على كلمات إلحاح مفرطة.")
        if features.trust_keyword_count > 0:
            highlights.append(f"تم اكتشاف {features.trust_keyword_count} إشارة ثقة قد تشير إلى رسالة شرعية.")

        # Generate insights
        insights = [
            schemas.AnalysisInsight(
                name="suspicious_keywords",
                value=features.suspicious_keyword_count,
                weight=min(1.0, features.suspicious_keyword_count * 0.2),
                description="عدد الكلمات المشبوهة المكتشفة",
            ),
            schemas.AnalysisInsight(
                name="url_count",
                value=features.url_count,
                weight=min(1.0, features.url_count * 0.15),
                description="عدد الروابط في الرسالة",
            ),
            schemas.AnalysisInsight(
                name="suspicious_domains",
                value=features.suspicious_domain_count,
                weight=min(1.0, features.suspicious_domain_count * 0.3),
                description="عدد الروابط بنطاقات مشبوهة",
            ),
            schemas.AnalysisInsight(
                name="link_mismatch",
                value=1 if features.link_text_mismatch else 0,
                weight=0.15 if features.link_text_mismatch else 0.0,
                description="عدم تطابق بين نص الرابط والرابط الفعلي",
            ),
            schemas.AnalysisInsight(
                name="from_domain_suspicious",
                value=1 if features.from_domain_suspicious else 0,
                weight=0.12 if features.from_domain_suspicious else 0.0,
                description="نطاق المرسل مشبوه",
            ),
            schemas.AnalysisInsight(
                name="trust_signals",
                value=features.trust_keyword_count,
                weight=min(1.0, features.trust_keyword_count * 0.15),
                description="إشارات الثقة المكتشفة",
            ),
        ]

        return score, highlights, insights

    @staticmethod
    def _normalize_text(text: str) -> str:
        cleaned = EmailAnalyzer._strip_html(text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned.lower()

    @staticmethod
    def _strip_html(text: str) -> str:
        """Strip HTML tags from text."""
        return re.sub(r"<[^>]+>", " ", text)

    @staticmethod
    def _extract_body(message: Message) -> str:
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        return payload.decode(part.get_content_charset() or "utf-8", errors="replace")
            # fallback to first part
            first_part = message.get_payload(0)
            if isinstance(first_part, Message):
                payload = first_part.get_payload(decode=True)
                if payload:
                    return payload.decode(first_part.get_content_charset() or "utf-8", errors="replace")
        payload = message.get_payload(decode=True)
        if payload:
            return payload.decode(message.get_content_charset() or "utf-8", errors="replace")
        return message.get_payload()

    @staticmethod
    def _extract_html_body(message: Message) -> str | None:
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload:
                        return payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        return None

    @staticmethod
    def _serialize_headers(message: Message) -> str:
        header_lines = []
        for key, value in message.items():
            header_lines.append(f"{key}: {value}")
        return "\n".join(header_lines)

    @staticmethod
    def _count_hits(text: str, keywords: Iterable[str]) -> int:
        return sum(1 for keyword in keywords if keyword in text)

    @staticmethod
    def _extract_urls(text: str) -> List[str]:
        """Extract all URLs from text."""
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        return re.findall(url_pattern, text)

    @staticmethod
    def _extract_domain(email_address: str) -> str:
        """Extract domain from email address."""
        match = re.search(r"@([\w\.-]+)", email_address)
        return match.group(1) if match else ""

    @staticmethod
    def _is_domain_suspicious(email_address: str) -> bool:
        """Check if email domain is suspicious."""
        domain = EmailAnalyzer._extract_domain(email_address)
        return any(susp_domain in domain.lower() for susp_domain in SUSPICIOUS_DOMAINS)

    @staticmethod
    def _check_link_text_mismatch(html_text: str) -> bool:
        """Check if link text doesn't match the actual URL."""
        # Simple heuristic: check for common patterns
        link_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>'
        matches = re.findall(link_pattern, html_text, re.IGNORECASE)
        for url, text in matches:
            url_domain = urlparse(url).netloc.lower()
            text_lower = text.lower()
            # If link text mentions a domain but URL points elsewhere
            if "http" in text_lower and url_domain not in text_lower:
                return True
        return False

    @staticmethod
    def _count_urgency_words(text: str) -> int:
        """Count urgency-indicating words."""
        urgency_patterns = [
            r"\burgent\b",
            r"\bimmediate\b",
            r"\basap\b",
            r"\bnow\b",
            r"\bexpire\b",
            r"\blimited\b",
            r"\bact now\b",
            r"\bverify now\b",
        ]
        count = 0
        for pattern in urgency_patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        return count

    @staticmethod
    def _estimate_spelling_errors(text: str) -> float:
        """Simple heuristic to estimate spelling errors."""
        # Count unusual character patterns
        unusual_patterns = [
            r"[a-z]{15,}",  # Very long words
            r"[A-Z]{5,}",  # Many consecutive capitals
            r"[0-9]{4,}",  # Many consecutive numbers
        ]
        error_count = 0
        for pattern in unusual_patterns:
            error_count += len(re.findall(pattern, text))
        # Normalize
        return min(1.0, error_count / max(1, len(text.split())) * 0.1)
