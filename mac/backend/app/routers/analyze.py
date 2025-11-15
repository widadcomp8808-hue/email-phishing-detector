from __future__ import annotations

from typing import Final

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from ..schemas import AnalysisResponse, AnalyzeTextRequest
from ..services.analyzer import EmailAnalyzer

router = APIRouter(prefix="/api", tags=["analysis"])

_MAX_FILE_SIZE_BYTES: Final[int] = 5 * 1024 * 1024  # 5 MB
_ACCEPTED_CONTENT_TYPES: Final[set[str]] = {
    "message/rfc822",
    "text/plain",
    "application/octet-stream",
}

_analyzer = EmailAnalyzer()


@router.post("/analyze/text", response_model=AnalysisResponse)
async def analyze_text(payload: AnalyzeTextRequest) -> AnalysisResponse:
    """
    Analyze the provided email body using the heuristic/ML pipeline.
    """

    return _analyzer.analyze_text(
        body=payload.body, subject=payload.subject, headers=payload.headers
    )


@router.post(
    "/analyze/file",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
async def analyze_file(file: UploadFile = File(...)) -> AnalysisResponse:
    """
    Accept an uploaded RFC822 (.eml) file and return the classification result.
    """

    if file.content_type not in _ACCEPTED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content type: {file.content_type}",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )
    if len(contents) > _MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds the maximum allowed size of 5 MB.",
        )

    try:
        return _analyzer.analyze_eml_bytes(contents)
    except Exception as exc:  # pragma: no cover - safety net for malformed files
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse email message: {exc}",
        ) from exc

