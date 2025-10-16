"""
Data models and schemas for Healthcare Agent Orchestrator
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class ImageModality(str, Enum):
    """DICOM imaging modalities"""
    CT = "CT"  # Computed Tomography
    MR = "MR"  # Magnetic Resonance
    DX = "DX"  # Digital Radiography
    CR = "CR"  # Computed Radiography
    MG = "MG"  # Mammography
    US = "US"  # Ultrasound
    PT = "PT"  # PET Scan
    NM = "NM"  # Nuclear Medicine
    XA = "XA"  # X-Ray Angiography
    RF = "RF"  # Radio Fluoroscopy
    SC = "SC"  # Secondary Capture
    OT = "OT"  # Other


class ProcessingStatus(str, Enum):
    """Processing status for medical images"""
    PENDING = "pending"
    PREPROCESSING = "preprocessing"
    GENERATING_PROMPTS = "generating_prompts"
    SEGMENTING = "segmenting"
    VALIDATING = "validating"
    POSTPROCESSING = "postprocessing"
    GENERATING_REPORT = "generating_report"
    INTEGRATING = "integrating"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"


class MedicalImageInput(BaseModel):
    """Input model for medical image processing"""
    image_path: str = Field(..., description="Path to the medical image file")
    modality: ImageModality = Field(..., description="DICOM modality")
    clinical_indication: Optional[str] = Field(None, description="Clinical reason for imaging")
    patient_id: Optional[str] = Field(None, description="Patient identifier (anonymized)")
    study_id: Optional[str] = Field(None, description="Study identifier")
    series_id: Optional[str] = Field(None, description="Series identifier")
    body_part: Optional[str] = Field(None, description="Body part examined")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class SegmentationMask(BaseModel):
    """Segmentation mask result"""
    mask_data: str = Field(..., description="Base64-encoded segmentation mask")
    shape: list[int] = Field(..., description="Mask dimensions")
    dtype: str = Field(..., description="Data type")
    labels: list[str] = Field(..., description="Biomedical category labels")
    confidence_scores: list[float] = Field(..., description="Confidence scores per label")


class ValidationResult(BaseModel):
    """Validation and QA result"""
    is_valid: bool = Field(..., description="Whether segmentation passed validation")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Overall quality score")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    anomalies: list[str] = Field(default_factory=list, description="Detected anomalies")
    warnings: list[str] = Field(default_factory=list, description="Warnings")
    requires_radiologist_review: bool = Field(..., description="Flag for radiologist review")
    validation_details: dict[str, Any] = Field(default_factory=dict, description="Detailed validation metrics")


class ClinicalReport(BaseModel):
    """Clinical report generated from findings"""
    findings: str = Field(..., description="Structured findings")
    impression: str = Field(..., description="Clinical impression")
    measurements: dict[str, float] = Field(default_factory=dict, description="Quantitative measurements")
    comparison: Optional[str] = Field(None, description="Comparison with prior studies")
    recommendations: list[str] = Field(default_factory=list, description="Clinical recommendations")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")


class ProcessingResult(BaseModel):
    """Complete processing result"""
    request_id: str = Field(..., description="Unique request identifier")
    status: ProcessingStatus = Field(..., description="Processing status")
    input_image: MedicalImageInput = Field(..., description="Input image metadata")
    
    # Processing results
    preprocessed_image_path: Optional[str] = Field(None, description="Path to preprocessed image")
    prompts_used: list[str] = Field(default_factory=list, description="Prompts used for segmentation")
    segmentation_masks: Optional[SegmentationMask] = Field(None, description="Segmentation results")
    validation_result: Optional[ValidationResult] = Field(None, description="Validation results")
    clinical_report: Optional[ClinicalReport] = Field(None, description="Generated clinical report")
    
    # Metadata
    processing_time: float = Field(..., description="Total processing time in seconds")
    agent_traces: list[dict[str, Any]] = Field(default_factory=list, description="Agent execution traces")
    errors: list[str] = Field(default_factory=list, description="Processing errors")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class AgentMessage(BaseModel):
    """Message passed between agents"""
    agent_name: str = Field(..., description="Agent name")
    message_type: str = Field(..., description="Message type")
    content: dict[str, Any] = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
