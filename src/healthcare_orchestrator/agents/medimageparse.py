"""
MedImageParse Inference Agent
"""

from typing import AsyncIterator
from agent_framework import ChatAgent, ChatMessage, AgentRunResponse, AgentRunResponseUpdate
from azure.identity.aio import AzureCliCredential, DefaultAzureCredential

from ..config.settings import Settings
from ..models.prompts import MEDIMAGEPARSE_INFERENCE_AGENT_INSTRUCTIONS


class MedImageParseAgent:
    """
    Agent responsible for calling MedImageParse API and managing inference.
    Handles API interactions, error handling, and result processing.
    """
    
    def __init__(self, settings: Settings):
        """Initialize the MedImageParse inference agent."""
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
            name="MedImageParseAgent",
            instructions=MEDIMAGEPARSE_INFERENCE_AGENT_INSTRUCTIONS,
            ai_model_id=self.settings.azure_openai_deployment
        )
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.credential:
            await self.credential.close()
            
    async def run_inference(
        self, 
        image_path: str,
        prompt: str,
        study_id: str
    ) -> AgentRunResponse:
        """
        Run MedImageParse inference.
        
        Args:
            image_path: Path to preprocessed image
            prompt: Segmentation prompt
            study_id: Study identifier
            
        Returns:
            Agent response with inference results
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Use 'async with' context manager.")
            
        message = ChatMessage(
            role="user",
            text=f"""
            Execute MedImageParse segmentation:
            - Image: {image_path}
            - Prompt: {prompt}
            - Study ID: {study_id}
            - Endpoint: {self.settings.medimageparse_endpoint}
            
            Tasks:
            1. Prepare API request with base64-encoded image
            2. Call MedImageParse endpoint
            3. Handle response and decode segmentation mask
            4. Validate mask format and quality
            5. Return structured results
            """
        )
        
        response = await self.agent.run(message)
        return response
