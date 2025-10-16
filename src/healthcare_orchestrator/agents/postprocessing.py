"""
Post-Processing Agent
"""

from typing import AsyncIterator
from agent_framework import ChatAgent, ChatMessage, AgentRunResponse, AgentRunResponseUpdate
from azure.identity.aio import AzureCliCredential, DefaultAzureCredential

from healthcare_orchestrator.config.settings import Settings
from healthcare_orchestrator.models.schemas import SegmentationMask, ImageModality
from healthcare_orchestrator.models.prompts import POSTPROCESSING_AGENT_INSTRUCTIONS


class PostProcessingAgent:
    """
    Agent responsible for post-processing segmentation masks.
    Applies cleanup, refinement, and format conversion operations.
    """
    
    def __init__(self, settings: Settings):
        """Initialize the post-processing agent."""
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
            name="PostProcessingAgent",
            instructions=POSTPROCESSING_AGENT_INSTRUCTIONS,
            ai_model_id=self.settings.azure_openai_deployment
        )
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.credential:
            await self.credential.close()
            
    async def refine_mask(
        self, 
        segmentation_mask: SegmentationMask,
        modality: ImageModality,
        apply_smoothing: bool = True
    ) -> AgentRunResponse:
        """
        Refine and post-process segmentation mask.
        
        Args:
            segmentation_mask: Raw segmentation mask
            modality: Image modality
            apply_smoothing: Whether to apply smoothing operations
            
        Returns:
            Agent response with refined mask
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Use 'async with' context manager.")
            
        message = ChatMessage(
            role="user",
            text=f"""
            Post-process segmentation mask:
            - Modality: {modality}
            - Original shape: {segmentation_mask.shape}
            - Apply smoothing: {apply_smoothing}
            
            Post-processing operations:
            1. Remove small disconnected components
            2. Fill internal holes
            3. Apply morphological operations (erosion/dilation)
            4. {'Smooth boundaries using Gaussian filter' if apply_smoothing else 'Skip smoothing'}
            5. Convert to clinical output format (DICOM RT-STRUCT or NIfTI)
            6. Calculate volume and surface area metrics
            
            Provide refined mask with quality metrics.
            """
        )
        
        response = await self.agent.run(message)
        return response
