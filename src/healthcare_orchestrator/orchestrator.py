"""
Healthcare Orchestrator using Microsoft Agent Framework
Coordinates multiple specialized agents for medical image processing workflow
"""

from typing import AsyncIterator, Optional
from dataclasses import dataclass
from agent_framework import (
    WorkflowBuilder,
    SequentialBuilder,
    Executor,
    WorkflowContext,
    ChatMessage,
    AgentExecutorRequest,
    AgentExecutorResponse,
    handler
)
from azure.identity.aio import AzureCliCredential, DefaultAzureCredential

from ..config.settings import Settings
from ..models.schemas import (
    MedicalImageInput,
    ProcessingResult,
    ProcessingStatus,
    SegmentationMask,
    ValidationResult,
    ClinicalReport
)
from ..agents import (
    PreprocessingAgent,
    PromptGeneratorAgent,
    MedImageParseAgent,
    ValidationAgent,
    PostProcessingAgent,
    ReportGeneratorAgent,
    IntegrationAgent
)


@dataclass
class OrchestrationState:
    """State passed between workflow executors"""
    image_input: MedicalImageInput
    preprocessed_image_path: Optional[str] = None
    segmentation_prompt: Optional[str] = None
    segmentation_mask: Optional[SegmentationMask] = None
    validation_result: Optional[ValidationResult] = None
    clinical_report: Optional[ClinicalReport] = None
    processing_result: Optional[ProcessingResult] = None
    error_message: Optional[str] = None


class HealthcareOrchestrator:
    """
    Main orchestrator for healthcare agent workflow using Microsoft Agent Framework.
    
    Workflow:
    1. Image Preprocessing → 2. Prompt Generation → 3. MedImageParse Inference →
    4. Validation & QA → 5. Post-Processing → 6. Report Generation → 7. Integration
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the healthcare orchestrator.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.workflow = None
        self.credential = None
        
        # Initialize agents
        self.preprocessing_agent = PreprocessingAgent(settings)
        self.prompt_agent = PromptGeneratorAgent(settings)
        self.inference_agent = MedImageParseAgent(settings)
        self.validation_agent = ValidationAgent(settings)
        self.postprocessing_agent = PostProcessingAgent(settings)
        self.report_agent = ReportGeneratorAgent(settings)
        self.integration_agent = IntegrationAgent(settings)
        
    async def __aenter__(self):
        """Async context manager entry"""
        # Initialize all agents
        await self.preprocessing_agent.__aenter__()
        await self.prompt_agent.__aenter__()
        await self.inference_agent.__aenter__()
        await self.validation_agent.__aenter__()
        await self.postprocessing_agent.__aenter__()
        await self.report_agent.__aenter__()
        await self.integration_agent.__aenter__()
        
        # Build the workflow
        self._build_workflow()
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Cleanup all agents
        await self.preprocessing_agent.__aexit__(exc_type, exc_val, exc_tb)
        await self.prompt_agent.__aexit__(exc_type, exc_val, exc_tb)
        await self.inference_agent.__aexit__(exc_type, exc_val, exc_tb)
        await self.validation_agent.__aexit__(exc_type, exc_val, exc_tb)
        await self.postprocessing_agent.__aexit__(exc_type, exc_val, exc_tb)
        await self.report_agent.__aexit__(exc_type, exc_val, exc_tb)
        await self.integration_agent.__aexit__(exc_type, exc_val, exc_tb)
        
    def _build_workflow(self):
        """
        Build the sequential workflow using Microsoft Agent Framework.
        Uses SequentialBuilder for linear agent pipeline.
        """
        # Create sequential workflow with all agents
        self.workflow = SequentialBuilder().participants([
            self.preprocessing_agent.agent,
            self.prompt_agent.agent,
            self.inference_agent.agent,
            self.validation_agent.agent,
            self.postprocessing_agent.agent,
            self.report_agent.agent,
            self.integration_agent.agent
        ]).build()
        
    async def process_medical_image(
        self,
        image_input: MedicalImageInput,
        clinical_context: str = ""
    ) -> ProcessingResult:
        """
        Process a medical image through the complete workflow.
        
        Args:
            image_input: Medical image input data
            clinical_context: Optional clinical context for processing
            
        Returns:
            Complete processing results
        """
        if not self.workflow:
            raise RuntimeError("Workflow not initialized. Use 'async with' context manager.")
            
        # Create initial message for workflow
        initial_message = f"""
        Process medical image:
        - Study ID: {image_input.study_id}
        - Patient ID: {image_input.patient_id}
        - Modality: {image_input.modality}
        - Image Path: {image_input.image_path}
        - Clinical Context: {clinical_context or 'General segmentation workflow'}
        
        Execute complete workflow:
        1. Preprocess DICOM image
        2. Generate segmentation prompt
        3. Run MedImageParse inference
        4. Validate results
        5. Post-process segmentation mask
        6. Generate clinical report
        7. Integrate with PACS/Storage
        """
        
        # Execute workflow
        result = await self.workflow.run(initial_message)
        
        # Build processing result from workflow output
        processing_result = ProcessingResult(
            study_id=image_input.study_id,
            patient_id=image_input.patient_id,
            modality=image_input.modality,
            status=ProcessingStatus.COMPLETED,
            processing_time_seconds=0.0,  # TODO: Track actual time
            segmentation_masks=[],  # TODO: Extract from workflow
            validation_results=[],  # TODO: Extract from workflow
            clinical_report=None,  # TODO: Extract from workflow
            error_message=None
        )
        
        return processing_result
        
    async def process_medical_image_streaming(
        self,
        image_input: MedicalImageInput,
        clinical_context: str = ""
    ) -> AsyncIterator[str]:
        """
        Process a medical image with streaming updates.
        
        Args:
            image_input: Medical image input data
            clinical_context: Optional clinical context
            
        Yields:
            Status updates as the workflow progresses
        """
        if not self.workflow:
            raise RuntimeError("Workflow not initialized. Use 'async with' context manager.")
            
        initial_message = f"""
        Process medical image: {image_input.study_id}
        Modality: {image_input.modality}
        Clinical Context: {clinical_context or 'General workflow'}
        """
        
        # Stream workflow execution
        last_executor_id = None
        async for event in self.workflow.run_streaming(initial_message):
            # Import event type
            from agent_framework import AgentRunUpdateEvent
            
            if isinstance(event, AgentRunUpdateEvent):
                # Track which agent is currently executing
                if event.executor_id != last_executor_id:
                    if last_executor_id is not None:
                        yield "\n"
                    yield f"[{event.executor_id}] "
                    last_executor_id = event.executor_id
                    
                # Stream the agent's output
                yield event.data
                
    async def process_batch(
        self,
        image_inputs: list[MedicalImageInput],
        clinical_context: str = ""
    ) -> list[ProcessingResult]:
        """
        Process multiple medical images in batch.
        
        Args:
            image_inputs: List of medical image inputs
            clinical_context: Shared clinical context
            
        Returns:
            List of processing results
        """
        results = []
        
        for image_input in image_inputs:
            try:
                result = await self.process_medical_image(
                    image_input=image_input,
                    clinical_context=clinical_context
                )
                results.append(result)
            except Exception as e:
                # Create error result
                error_result = ProcessingResult(
                    study_id=image_input.study_id,
                    patient_id=image_input.patient_id,
                    modality=image_input.modality,
                    status=ProcessingStatus.FAILED,
                    processing_time_seconds=0.0,
                    segmentation_masks=[],
                    validation_results=[],
                    clinical_report=None,
                    error_message=str(e)
                )
                results.append(error_result)
                
        return results
