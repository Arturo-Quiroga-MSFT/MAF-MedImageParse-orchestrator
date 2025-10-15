"""
Batch processing example for Healthcare Agent Orchestrator

This example demonstrates how to process multiple medical images
in a batch workflow using Microsoft Agent Framework.
"""

import asyncio
from pathlib import Path
from healthcare_orchestrator import HealthcareOrchestrator, Settings
from healthcare_orchestrator.models.schemas import MedicalImageInput, ImageModality, ProcessingStatus


async def main():
    """Batch processing example"""
    
    settings = Settings()
    
    print("=== Healthcare Agent Orchestrator - Batch Processing ===\n")
    
    # Create multiple medical image inputs
    image_inputs = [
        MedicalImageInput(
            study_id="STUDY-001",
            patient_id="PATIENT-001",
            modality=ImageModality.CT,
            image_path="/path/to/ct_1.dcm",
            metadata={"series_description": "Chest CT"}
        ),
        MedicalImageInput(
            study_id="STUDY-002",
            patient_id="PATIENT-002",
            modality=ImageModality.MRI,
            image_path="/path/to/mri_1.dcm",
            metadata={"series_description": "Brain MRI"}
        ),
        MedicalImageInput(
            study_id="STUDY-003",
            patient_id="PATIENT-003",
            modality=ImageModality.XRAY,
            image_path="/path/to/xray_1.dcm",
            metadata={"series_description": "Chest X-Ray"}
        ),
    ]
    
    print(f"Processing {len(image_inputs)} medical images...\n")
    
    async with HealthcareOrchestrator(settings) as orchestrator:
        # Process batch
        results = await orchestrator.process_batch(
            image_inputs=image_inputs,
            clinical_context="Batch processing for research study"
        )
        
        # Summarize results
        print("\n=== Batch Processing Results ===\n")
        
        completed = sum(1 for r in results if r.status == ProcessingStatus.COMPLETED)
        failed = sum(1 for r in results if r.status == ProcessingStatus.FAILED)
        
        print(f"Total Images: {len(results)}")
        print(f"Completed: {completed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(completed/len(results)*100):.1f}%\n")
        
        # Detailed results
        for idx, result in enumerate(results, 1):
            print(f"Image {idx}: {result.study_id}")
            print(f"  Status: {result.status}")
            print(f"  Modality: {result.modality}")
            print(f"  Processing Time: {result.processing_time_seconds:.2f}s")
            
            if result.error_message:
                print(f"  Error: {result.error_message}")
            elif result.segmentation_masks:
                print(f"  Segmentation Masks: {len(result.segmentation_masks)}")
                
            print()
    
    print("=== Batch Processing Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
