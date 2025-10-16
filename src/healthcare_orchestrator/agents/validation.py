"""
Validation & QA Agent
"""

from typing import AsyncIterator
from agent_framework import ChatAgent, ChatMessage, AgentRunResponse, AgentRunResponseUpdate
from azure.identity.aio import AzureCliCredential, DefaultAzureCredential

from healthcare_orchestrator.config.settings import Settings
from healthcare_orchestrator.models.schemas import SegmentationMask
from healthcare_orchestrator.models.prompts import VALIDATION_AGENT_INSTRUCTIONS


class ValidationAgent:
    """
    Agent responsible for validating segmentation results.
    Performs quality assurance checks on segmentation masks.
    """
    
    def __init__(self, settings: Settings):
        """Initialize the validation agent."""
        self.settings = settings
        self.agent: ChatAgent | None = None
        self.credential = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        if self.settings.use_azure_cli_auth:
            self.credential = AzureCliCredential()
        else:
            self.credential = DefaultAzureCredential()
            
        from agent_framework.azure import AzureOpenAIChatClient
        
        chat_client = AzureOpenAIChatClient(
            credential=self.credential,
            azure_endpoint=self.settings.azure_openai_endpoint,
            api_version=self.settings.azure_openai_api_version,
            deployment_name=self.settings.azure_openai_deployment
        )
        
        self.agent = chat_client.create_agent(
            name="ValidationAgent",
            instructions=VALIDATION_AGENT_INSTRUCTIONS,
            ai_model_id=self.settings.azure_openai_deployment
        )
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.credential:
            await self.credential.close()
            
    async def validate(
        self, 
        segmentation_mask: SegmentationMask,
        original_image_path: str
    ) -> AgentRunResponse:
        """
        Validate segmentation mask quality.
        
        Args:
            segmentation_mask: Segmentation mask to validate
            original_image_path: Path to original image
            
        Returns:
            Agent response with validation results
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Use 'async with' context manager.")
            
        message = ChatMessage(
            role="user",
            text=f"""
            Validate segmentation mask:
            - Mask shape: {segmentation_mask.shape}
            - Original image: {original_image_path}
            - Confidence score: {segmentation_mask.confidence_score}
            
            Validation checks:
            1. Mask dimensions match expected size
            2. Segmentation coverage is reasonable (not empty/full)
            3. Edge quality and smoothness
            4. Anatomical plausibility
            5. Confidence threshold met
            6. No obvious artifacts or errors
            
            Provide validation result with pass/fail and specific issues found.
            """
        )
        
        response = await self.agent.run(message)
        return response
