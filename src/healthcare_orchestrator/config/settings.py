"""
Configuration settings for Healthcare Agent Orchestrator
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Azure AI Foundry Configuration
    azure_ai_project_endpoint: str = Field(
        ...,
        description="Azure AI Foundry project endpoint"
    )
    azure_subscription_id: Optional[str] = Field(
        None,
        description="Azure subscription ID"
    )
    azure_resource_group: Optional[str] = Field(
        None,
        description="Azure resource group name"
    )
    model_deployment_name: str = Field(
        default="gpt-4o",
        description="Model deployment name for agents"
    )

    # MedImageParse Configuration
    medimageparse_endpoint: str = Field(
        ...,
        description="MedImageParse API endpoint"
    )
    medimageparse_api_key: Optional[str] = Field(
        None,
        description="MedImageParse API key"
    )

    # Azure Storage Configuration
    azure_storage_connection_string: Optional[str] = Field(
        None,
        description="Azure Storage connection string"
    )
    azure_storage_container_name: str = Field(
        default="medical-images",
        description="Azure Storage container for medical images"
    )

    # Azure AI Search Configuration
    azure_search_endpoint: Optional[str] = Field(
        None,
        description="Azure AI Search endpoint"
    )
    azure_search_api_key: Optional[str] = Field(
        None,
        description="Azure AI Search API key"
    )
    azure_search_index_name: str = Field(
        default="medical-knowledge-base",
        description="Azure AI Search index name"
    )

    # DICOM/PACS Configuration
    pacs_ae_title: str = Field(
        default="ORTHANC",
        description="PACS Application Entity title"
    )
    pacs_host: str = Field(
        default="localhost",
        description="PACS server hostname"
    )
    pacs_port: int = Field(
        default=4242,
        description="PACS server port"
    )

    # Application Insights Configuration
    applicationinsights_connection_string: Optional[str] = Field(
        None,
        description="Application Insights connection string"
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    enable_tracing: bool = Field(
        default=True,
        description="Enable OpenTelemetry tracing"
    )

    # Agent Configuration
    agent_timeout: int = Field(
        default=300,
        description="Agent execution timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed operations"
    )
    retry_delay: float = Field(
        default=1.0,
        description="Initial delay between retries in seconds"
    )

    # Image Processing Configuration
    target_image_size: int = Field(
        default=1024,
        description="Target image size for MedImageParse (1024x1024)"
    )
    supported_modalities: list[str] = Field(
        default=[
            "CT", "MR", "DX", "CR", "MG", "US", "PT", "NM", 
            "XA", "RF", "SC", "OT"
        ],
        description="Supported DICOM modalities"
    )

    # Validation Configuration
    min_confidence_score: float = Field(
        default=0.7,
        description="Minimum confidence score for auto-approval"
    )
    require_radiologist_review: bool = Field(
        default=True,
        description="Require radiologist review for all results"
    )


# Global settings instance
settings = Settings()
