"""
Image Preprocessing Agent for DICOM and medical image processing
"""

from typing import AsyncIterator
from agent_framework import ChatAgent, ChatMessage, AgentRunResponse, AgentRunResponseUpdate
from azure.identity.aio import AzureCliCredential, DefaultAzureCredential

from ..config.settings import Settings
from ..models.schemas import MedicalImageInput, ProcessingStatus
from ..models.prompts import IMAGE_PREPROCESSING_AGENT_INSTRUCTIONS


class PreprocessingAgent:
    """
    Agent responsible for preprocessing medical images.
    Handles DICOM parsing, format conversion, resizing, and normalization.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the preprocessing agent.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.agent: ChatAgent | None = None
        self.credential = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        # Choose credential based on settings
        if self.settings.use_azure_cli_auth:
            self.credential = AzureCliCredential()
        else:
            self.credential = DefaultAzureCredential()
            
        # Import Azure chat client from MAF
        from agent_framework.azure import AzureChatClient
        
        # Create chat client
        chat_client = AzureChatClient(
            credential=self.credential,
            azure_endpoint=self.settings.azure_openai_endpoint,
            api_version=self.settings.azure_openai_api_version
        )
        
        # Create agent using the chat client
        self.agent = chat_client.create_agent(
            name="PreprocessingAgent",
            instructions=IMAGE_PREPROCESSING_AGENT_INSTRUCTIONS,
            ai_model_id=self.settings.azure_openai_deployment
        )
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.credential:
            await self.credential.close()
            
    async def process(self, image_input: MedicalImageInput) -> AgentRunResponse:
        """
        Process medical image for preprocessing.
        
        Args:
            image_input: Medical image input data
            
        Returns:
            Agent response with preprocessing results
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Use 'async with' context manager.")
            
        # Create message with image metadata
        message = ChatMessage(
            role="user",
            text=f"""
            Preprocess medical image:
            - Modality: {image_input.modality}
            - Study ID: {image_input.study_id}
            - Patient ID: {image_input.patient_id}
            - Source Path: {image_input.image_path}
            
            Tasks:
            1. Validate DICOM metadata if applicable
            2. Convert to PNG format (1024x1024)
            3. Apply appropriate windowing for modality
            4. Normalize intensity values
            5. Ensure image quality for segmentation
            """
        )
        
        # Run agent
        response = await self.agent.run(message)
        return response
        
    async def process_streaming(self, image_input: MedicalImageInput) -> AsyncIterator[AgentRunResponseUpdate]:
        """
        Process medical image with streaming responses.
        
        Args:
            image_input: Medical image input data
            
        Yields:
            Streaming agent response updates
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Use 'async with' context manager.")
            
        message = ChatMessage(
            role="user",
            text=f"""
            Preprocess medical image:
            - Modality: {image_input.modality}
            - Study ID: {image_input.study_id}
            
            Provide step-by-step preprocessing actions.
            """
        )
        
        async for update in self.agent.run_stream(message):
            yield update
