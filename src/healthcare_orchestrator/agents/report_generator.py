"""
Report Generator Agent
"""

from typing import AsyncIterator
from agent_framework import ChatAgent, ChatMessage, AgentRunResponse, AgentRunResponseUpdate
from azure.identity.aio import AzureCliCredential, DefaultAzureCredential

from healthcare_orchestrator.config.settings import Settings
from healthcare_orchestrator.models.schemas import ProcessingResult, SegmentationMask
from healthcare_orchestrator.models.prompts import REPORT_GENERATOR_INSTRUCTIONS


class ReportGeneratorAgent:
    """
    Agent responsible for generating clinical reports.
    Creates structured reports with findings and metrics.
    """
    
    def __init__(self, settings: Settings):
        """Initialize the report generator agent."""
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
            name="ReportGeneratorAgent",
            instructions=REPORT_GENERATOR_INSTRUCTIONS,
            ai_model_id=self.settings.azure_openai_deployment
        )
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.credential:
            await self.credential.close()
            
    async def generate_report(
        self, 
        processing_result: ProcessingResult,
        include_metrics: bool = True
    ) -> AgentRunResponse:
        """
        Generate clinical report from processing results.
        
        Args:
            processing_result: Complete processing results
            include_metrics: Whether to include quantitative metrics
            
        Returns:
            Agent response with clinical report
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Use 'async with' context manager.")
            
        # Build context from results
        metrics_text = ""
        if include_metrics and processing_result.segmentation_masks:
            mask = processing_result.segmentation_masks[0]
            metrics_text = f"""
            Quantitative Metrics:
            - Segmentation shape: {mask.shape}
            - Confidence score: {mask.confidence_score:.3f}
            """
        
        message = ChatMessage(
            role="user",
            text=f"""
            Generate clinical report:
            - Study ID: {processing_result.study_id}
            - Status: {processing_result.status}
            - Processing time: {processing_result.processing_time_seconds:.2f}s
            {metrics_text}
            
            Report Requirements:
            1. Executive Summary
            2. Segmentation Overview (structures identified)
            3. {f'Quantitative Metrics (volumes, areas)' if include_metrics else 'Qualitative Assessment'}
            4. Quality Assessment
            5. Clinical Recommendations (if applicable)
            6. Technical Details
            
            Format as structured clinical report suitable for medical review.
            """
        )
        
        response = await self.agent.run(message)
        return response
