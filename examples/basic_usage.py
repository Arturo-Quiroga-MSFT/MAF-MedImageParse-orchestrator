"""
Basic usage example of Healthcare Agent Orchestrator with Microsoft Agent Framework

This example demonstrates how to:
1. Initialize the orchestrator
2. Process a single medical image
3. Handle results

Prerequisites:
- Azure OpenAI deployment configured
- MedImageParse endpoint available
- Environment variables configured (see .env.example)
"""

import asyncio
from pathlib import Path
from healthcare_orchestrator import HealthcareOrchestrator, Settings
from healthcare_orchestrator.models.schemas import MedicalImageInput, ImageModality


async def main():
    """Main example function"""
    
    # Load settings from environment
    settings = Settings()
    
    print("=== Healthcare Agent Orchestrator - Basic Example ===\n")
    print(f"Using Azure OpenAI: {settings.azure_openai_deployment}")
    print(f"MedImageParse Endpoint: {settings.medimageparse_endpoint}\n")
    
    # Create sample medical image input
    image_input = MedicalImageInput(
        study_id="STUDY-001",
        patient_id="PATIENT-12345",
        modality=ImageModality.CT,
        image_path="/path/to/ct_scan.dcm",  # Replace with actual path
        metadata={
            "series_description": "Chest CT with contrast",
            "acquisition_date": "2024-01-15",
            "institution": "Demo Hospital"
        }
    )
    
    print(f"Processing image: {image_input.study_id}")
    print(f"  - Modality: {image_input.modality}")
    print(f"  - Patient ID: {image_input.patient_id}\n")
    
    # Initialize orchestrator with context manager
    async with HealthcareOrchestrator(settings) as orchestrator:
        print("Orchestrator initialized successfully\n")
        
        # Option 1: Process with streaming updates
        print("--- Streaming Processing ---")
        async for update in orchestrator.process_medical_image_streaming(
            image_input=image_input,
            clinical_context="Routine chest CT for pulmonary assessment"
        ):
            print(update, end="", flush=True)
        print("\n\n--- Processing Complete ---\n")
        
        # Option 2: Process without streaming (get final result)
        print("--- Standard Processing ---")
        result = await orchestrator.process_medical_image(
            image_input=image_input,
            clinical_context="Routine chest CT for pulmonary assessment"
        )
        
        # Display results
        print(f"\nProcessing Result:")
        print(f"  Status: {result.status}")
        print(f"  Processing Time: {result.processing_time_seconds:.2f}s")
        print(f"  Number of Segmentation Masks: {len(result.segmentation_masks)}")
        
        if result.segmentation_masks:
            for idx, mask in enumerate(result.segmentation_masks):
                print(f"\n  Mask {idx + 1}:")
                print(f"    - Shape: {mask.shape}")
                print(f"    - Confidence: {mask.confidence_score:.3f}")
                
        if result.validation_results:
            print(f"\n  Validation Results:")
            for validation in result.validation_results:
                print(f"    - Passed: {validation.passed}")
                if not validation.passed:
                    print(f"    - Issues: {', '.join(validation.issues)}")
                    
        if result.clinical_report:
            print(f"\n  Clinical Report:")
            print(f"    - Generated: {result.clinical_report.generated_date}")
            print(f"    - Report Preview: {result.clinical_report.report_text[:200]}...")
            
        if result.error_message:
            print(f"\n  Error: {result.error_message}")
    
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
