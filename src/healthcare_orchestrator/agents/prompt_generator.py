"""
Prompt Generator Agent for MedImageParse
"""

from typing import AsyncIterator
from agent_framework import ChatAgent, ChatMessage, AgentRunResponse, AgentRunResponseUpdate
from azure.identity.aio import AzureCliCredential, DefaultAzureCredential

from ..config.settings import Settings
from ..models.schemas import MedicalImageInput, ImageModality
from ..models.prompts import PROMPT_GENERATION_AGENT_INSTRUCTIONS, MODALITY_PROMPT_TEMPLATES


class PromptGeneratorAgent:
    """
    Agent responsible for generating optimized prompts for MedImageParse.
    Creates modality-specific segmentation prompts based on clinical context.
    """
    
    def __init__(self, settings: Settings):
        """Initialize the prompt generator agent."""
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
            name="PromptGeneratorAgent",
            instructions=PROMPT_GENERATION_AGENT_INSTRUCTIONS,
            ai_model_id=self.settings.azure_openai_deployment
        )
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.credential:
            await self.credential.close()
            
    async def generate_prompt(
        self, 
        image_input: MedicalImageInput,
        clinical_context: str = ""
    ) -> AgentRunResponse:
        """
        Generate optimized segmentation prompt.
        
        Args:
            image_input: Medical image input data
            clinical_context: Additional clinical context
            
        Returns:
            Agent response with generated prompt
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Use 'async with' context manager.")
            
        # Get modality-specific template
        template = MODALITY_PROMPT_TEMPLATES.get(image_input.modality, "")
        
        message = ChatMessage(
            role="user",
            text=f"""
            Generate segmentation prompt for MedImageParse:
            - Modality: {image_input.modality}
            - Clinical Context: {clinical_context or 'General segmentation'}
            - Study ID: {image_input.study_id}
            
            Template Guidelines:
            {template}
            
            Create a precise, anatomically accurate prompt that will:
            1. Clearly specify target structures
            2. Account for modality-specific characteristics
            3. Handle potential anatomical variations
            4. Be optimized for MedImageParse model
            """
        )
        
        response = await self.agent.run(message)
        return response
