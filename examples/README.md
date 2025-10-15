# Healthcare Agent Orchestrator - Examples

This directory contains example scripts demonstrating how to use the Healthcare Agent Orchestrator with Microsoft Agent Framework (MAF).

## Prerequisites

Before running the examples, ensure you have:

1. **Python 3.10+** installed
2. **Dependencies installed**: `pip install -e .`
3. **Environment variables configured**: Copy `.env.example` to `.env` and fill in your values
4. **Azure OpenAI** deployment configured
5. **MedImageParse** endpoint available

## Examples

### 1. Basic Usage (`basic_usage.py`)

Demonstrates the fundamental workflow:
- Initializing the orchestrator
- Processing a single medical image
- Streaming vs. standard processing modes
- Accessing results (segmentation masks, validation, reports)

**Run:**
```bash
python examples/basic_usage.py
```

**What it does:**
- Creates a sample medical image input
- Processes it through the complete 7-agent workflow
- Shows both streaming and standard processing
- Displays detailed results

### 2. Batch Processing (`batch_processing.py`)

Shows how to process multiple images efficiently:
- Batch image processing
- Error handling for individual images
- Result aggregation and statistics
- Success rate calculation

**Run:**
```bash
python examples/batch_processing.py
```

**What it does:**
- Processes multiple medical images in sequence
- Handles failures gracefully
- Provides batch statistics
- Shows per-image results

## Workflow Overview

The orchestrator coordinates 7 specialized agents using Microsoft Agent Framework:

```
Input Image
    ↓
1. Image Preprocessing Agent
    ↓
2. Prompt Generation Agent
    ↓
3. MedImageParse Inference Agent
    ↓
4. Validation & QA Agent
    ↓
5. Post-Processing Agent
    ↓
6. Report Generation Agent
    ↓
7. Integration Agent (PACS/Storage)
    ↓
Final Result
```

## Key Features

### Streaming Processing
Real-time updates as the workflow progresses through each agent:

```python
async for update in orchestrator.process_medical_image_streaming(image_input):
    print(update, end="", flush=True)
```

### Standard Processing
Wait for complete results:

```python
result = await orchestrator.process_medical_image(image_input)
```

### Batch Processing
Process multiple images with automatic error handling:

```python
results = await orchestrator.process_batch(image_inputs)
```

## Customization

### Clinical Context
Add specific clinical context to guide the workflow:

```python
result = await orchestrator.process_medical_image(
    image_input=image_input,
    clinical_context="Suspected pulmonary nodule, follow-up scan"
)
```

### Modality-Specific Processing
The orchestrator automatically adapts to different modalities:
- CT (Computed Tomography)
- MRI (Magnetic Resonance Imaging)
- X-Ray (Radiography)
- Ultrasound
- PET (Positron Emission Tomography)

## Error Handling

All examples include proper error handling:

```python
try:
    result = await orchestrator.process_medical_image(image_input)
except Exception as e:
    print(f"Processing failed: {e}")
```

## Next Steps

After running the examples, you can:
1. Adapt them for your specific use case
2. Integrate with your PACS/EHR systems
3. Add custom validation rules
4. Extend with additional agents
5. Deploy to production with Azure

## Support

For issues or questions:
- Check the main [README.md](../README.md)
- Review the [reference documentation](../MedImageParse-Orchestrator-Reference.md)
- Open an issue on GitHub
