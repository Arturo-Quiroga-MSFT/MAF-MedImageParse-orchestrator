# Healthcare Agent Orchestrator

> Production-ready healthcare agent orchestrator for MedImageParse using **Microsoft Agent Framework (MAF)**

## Overview

This repository contains a complete implementation of a healthcare agent orchestrator that transforms Azure's MedImageParse from a standalone medical image segmentation API into a production-ready clinical decision support system using **Microsoft Agent Framework**.

### Why Microsoft Agent Framework?

Microsoft Agent Framework (MAF) is the next-generation framework combining the best of Semantic Kernel and AutoGen, providing:
- 🔄 **Workflow Orchestration**: Sequential, concurrent, and conditional agent coordination
- 🎯 **Type Safety**: Strong typing for reliable multi-agent communication
- 🔍 **Built-in Observability**: OpenTelemetry integration for tracing
- 🏗️ **Enterprise-Grade**: Thread-based state management and extensive model support

## What's Inside

📄 **[MedImageParse-Orchestrator-Reference.md](./MedImageParse-Orchestrator-Reference.md)** - Complete technical reference covering:

- **MedImageParse Overview**: Capabilities, specifications, and API details for prompt-based medical image segmentation
- **Agent Orchestrator Architecture**: 7 core components for building production healthcare AI workflows
- **Implementation Guide**: End-to-end clinical workflow diagrams and integration patterns
- **Technical Specifications**: Request/response schemas, authentication, deployment strategies
- **Code Examples**: Python implementation snippets for Azure AI integration
- **Clinical Benefits**: Improved accuracy, efficiency, and patient outcomes
- **Security & Compliance**: HIPAA, FDA validation, audit trails, and PHI handling

## Key Features

✅ **Multi-Step Workflow Automation**: Image preprocessing → inference → validation → reporting  
✅ **Intelligent Prompt Engineering**: Context-aware, anatomically-specific segmentation prompts  
✅ **Clinical Systems Integration**: PACS, EMR/EHR, DICOM, HL7 FHIR compatibility  
✅ **Multi-Model Orchestration**: Coordinate MedImageParse, CXRReportGen, MedImageInsight  
✅ **Scalability**: Hospital-scale volumes (1000+ studies/day) with Azure auto-scaling  
✅ **Human-in-the-Loop**: Radiologist review workflows and feedback integration  
✅ **Regulatory Compliance**: HIPAA audit logging, FDA validation readiness  

## Use Cases

- 🏥 **Radiology Departments**: Automated segmentation for X-rays, CT, MRI studies
- 🔬 **Pathology Labs**: Digital slide analysis with AI-assisted annotations
- 🧬 **Research Institutions**: Large-scale biomedical image analysis pipelines
- 🏢 **Healthcare IT Vendors**: Integrate AI segmentation into clinical software

## Architecture Highlights

```
PACS/EMR → Ingestion → Preprocessing → Prompt Generation → MedImageParse API
                                                              ↓
  EMR Integration ← Report Generation ← Multi-Model ← Validation & QA
```

### Core Agent Components (MAF):

1. **Image Preprocessing Agent** - DICOM parsing, format conversion, windowing
2. **Prompt Generation Agent** - Modality-specific, anatomically accurate prompts
3. **MedImageParse Inference Agent** - API orchestration with error handling
4. **Validation & QA Agent** - Quality metrics and confidence scoring
5. **Post-Processing Agent** - Mask refinement and clinical measurements
6. **Report Generation Agent** - Structured clinical reports
7. **Integration Agent** - PACS/EHR connectivity and DICOM storage

## Installation

```bash
# Clone the repository
git clone https://github.com/Arturo-Quiroga-MSFT/MAF-MedImageParse-orchestrator.git
cd MAF-MedImageParse-orchestrator

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your Azure OpenAI and MedImageParse endpoints
```

## Quick Start

```python
import asyncio
from healthcare_orchestrator import HealthcareOrchestrator, Settings
from healthcare_orchestrator.models.schemas import MedicalImageInput, ImageModality

async def main():
    settings = Settings()  # Loads from .env
    
    image_input = MedicalImageInput(
        study_id="STUDY-001",
        patient_id="PATIENT-001",
        modality=ImageModality.CT,
        image_path="/path/to/ct_scan.dcm"
    )
    
    async with HealthcareOrchestrator(settings) as orchestrator:
        # Option 1: Streaming processing
        async for update in orchestrator.process_medical_image_streaming(image_input):
            print(update, end="", flush=True)
        
        # Option 2: Standard processing
        result = await orchestrator.process_medical_image(image_input)
        print(f"Status: {result.status}")
        print(f"Masks: {len(result.segmentation_masks)}")

asyncio.run(main())
```

See [examples/](./examples/) for more detailed usage patterns.

## Prerequisites

- **Python 3.10+**
- **Azure OpenAI** deployment (gpt-4o or gpt-4)
- **MedImageParse** endpoint deployed on Azure
- **Azure CLI** (for authentication during development)

## Project Structure

```
MAF-MedImageParse-orchestrator/
├── src/healthcare_orchestrator/
│   ├── agents/              # 7 specialized MAF agents
│   ├── config/              # Pydantic settings
│   ├── models/              # Data schemas and prompts
│   └── orchestrator.py      # Main MAF workflow orchestrator
├── examples/                # Usage examples
│   ├── basic_usage.py
│   └── batch_processing.py
├── MedImageParse-Orchestrator-Reference.md  # Technical reference
└── pyproject.toml
```

## Related Azure Healthcare AI Models

- **CXRReportGen**: Radiology report generation from chest X-rays
- **MedImageInsight**: Multimodal medical image understanding
- **Custom Classification Models**: Disease-specific predictive models

## Important Disclaimer

⚠️ **Clinical Use Notice**: Healthcare AI models including MedImageParse are intended for **research and model development exploration**. They are not designed or intended to be deployed in clinical settings as-is nor for use in the diagnosis or treatment of any health or medical condition. Individual model performances for clinical purposes have not been established.

You bear sole responsibility and liability for any use of healthcare AI models, including verification of outputs, regulatory compliance, and obtaining necessary clearances (e.g., FDA approval).

## Contributing

This is a reference architecture and documentation repository. Contributions, suggestions, and real-world implementation feedback are welcome!

## License

MIT License - See LICENSE file for details

## Resources

- [Microsoft Agent Framework Overview](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)
- [Deploy MedImageParse on Azure](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/healthcare-ai/deploy-medimageparse)
- [Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Healthcare AI on Azure](https://azure.microsoft.com/en-us/solutions/industries/healthcare/)

---

**Built with Microsoft Agent Framework** | **Updated**: October 15, 2025

## Relationship to the official Azure-Samples project

