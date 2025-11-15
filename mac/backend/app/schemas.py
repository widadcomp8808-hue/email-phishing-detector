from __future__ import annotations

from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field


class AnalyzeTextRequest(BaseModel):
    """
    Payload for analyzing a raw email message provided as plain text.
    """

    subject: Optional[str] = Field(
        default=None,
        description="Optional subject extracted from the email.",
    )
    body: str = Field(
        ...,
        min_length=1,
        description="Full raw body of the email (plain text or HTML).",
    )
    headers: Optional[str] = Field(
        default=None, description="Optional raw headers for additional context."
    )


class AnalysisInsight(BaseModel):
    """
    Light-weight explanation item produced by the model/heuristics.
    """

    name: str = Field(..., description="Human readable name of the inspected feature.")
    value: Union[str, float, int] = Field(
        ..., description="Value of the feature observed in the email."
    )
    weight: Optional[float] = Field(
        default=None,
        description="Relative importance (0..1) of this feature in the decision.",
        ge=0.0,
        le=1.0,
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional free-form explanation that can be shown to the user.",
    )


class EmailMetadata(BaseModel):
    """
    Structured metadata extracted from the message headers.
    """

    subject: Optional[str] = None
    from_address: Optional[str] = None
    reply_to: Optional[str] = None
    to_addresses: List[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    """
    Standard response returned by the analyzer endpoints.
    """

    verdict: Literal["phishing", "legitimate"] = Field(
        ..., description="Binary classification outcome of the analyzer."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for the predicted label.",
    )
    model_version: str = Field(
        ..., description="Semantic version or git sha identifying the model."
    )
    metadata: Optional[EmailMetadata] = Field(
        default=None, description="Metadata extracted from the incoming message."
    )
    highlights: List[str] = Field(
        default_factory=list,
        description="High-level reasons or risk factors surfaced to the analyst.",
    )
    insights: List[AnalysisInsight] = Field(
        default_factory=list,
        description="Detailed feature-level explanations that drove the decision.",
    )

