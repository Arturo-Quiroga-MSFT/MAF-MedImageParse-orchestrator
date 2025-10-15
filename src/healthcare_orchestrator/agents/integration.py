"""
Integration Agent for PACS/EHR systems
"""

from typing import AsyncIterator
from agent_framework import ChatAgent, ChatMessage, AgentRunResponse, AgentRunResponseUpdate
from azure.identity.aio import AzureCliCredential, DefaultAzureCredential

from ..config.settings import Settings
from ..models.schemas import ProcessingResult, ClinicalReport
from ..models.prompts import INTEGRATION_AGENT_INSTRUCTIONS


class IntegrationAgent:
    """
    Agent responsible for integrating with external systems.
    Handles PACS, EHR, and other healthcare system integrations.
    """
    
    def __init__(self, settings: Settings):
        """Initialize the integration agent."""
        self.settings = settings
        self.agent: ChatAgent | None = None
        self.credential = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        if self.settings.use_azure_cli_auth:
            self.credential = AzureCliCredential()
        else:
            self.credential = DefaultAzureCredential()
            
        from agent_framework.azure import AzureChatClient
        
        chat_client = AzureChatClient(
            credential=self.credential,
            azure_endpoint=self.settings.azure_openai_endpoint,
            api_version=self.settings.azure_openai_api_version
        )
        
        self.agent = chat_client.create_agent(
            name="IntegrationAgent",
            instructions=INTEGRATION_AGENT_INSTRUCTIONS,
            ai_model_id=self.settings.azure_openai_deployment
        )
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.credential:
            await self.credential.close()
            
    async def send_to_pacs(
        self, 
        processing_result: ProcessingResult,
        report: ClinicalReport
    ) -> AgentRunResponse:
        """
        Send results back to PACS system.
        
        Args:
            processing_result: Processing results to send
            report: Generated clinical report
            
        Returns:
            Agent response with integration status
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Use 'async with' context manager.")
            
        message = ChatMessage(
            role="user",
            text=f"""
            Integrate results with PACS:
            - Study ID: {processing_result.study_id}
            - PACS AE Title: {self.settings.pacs_ae_title}
            - PACS Host: {self.settings.pacs_host}:{self.settings.pacs_port}
            - Report: {report.report_text[:200]}...
            
            Integration tasks:
            1. Convert segmentation masks to DICOM RT-STRUCT format
            2. Attach report as DICOM SR (Structured Report)
            3. Send to PACS using DICOM C-STORE
            4. Verify successful storage
            5. Log integration audit trail
            
            Ensure HIPAA compliance and proper DICOM metadata.
            """
        )
        
        response = await self.agent.run(message)
        return response
        
    async def store_in_azure(
        self,
        processing_result: ProcessingResult
    ) -> AgentRunResponse:
        """
        Store results in Azure Storage.
        
        Args:
            processing_result: Processing results to store
            
        Returns:
            Agent response with storage status
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Use 'async with' context manager.")
            
        message = ChatMessage(
            role="user",
            text=f"""
            Store results in Azure Blob Storage:
            - Study ID: {processing_result.study_id}
            - Container: {self.settings.azure_storage_container_name}
            - Status: {processing_result.status}
            
            Storage tasks:
            1. Upload segmentation masks as PNG/NRRD
            2. Store metadata as JSON
            3. Upload clinical report as PDF/HTML
            4. Create searchable index entry
            5. Generate SAS token for secure access
            
            Return storage URLs and access tokens.
            """
        )
        
        response = await self.agent.run(message)
        return response
