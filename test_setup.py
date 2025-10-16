"""
Quick setup test for Healthcare Agent Orchestrator
Tests configuration loading and basic connectivity
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from healthcare_orchestrator.config.settings import Settings
from healthcare_orchestrator.models.schemas import MedicalImageInput, ImageModality


def test_config_loading():
    """Test 1: Configuration Loading"""
    print("=" * 60)
    print("TEST 1: Configuration Loading")
    print("=" * 60)
    
    try:
        settings = Settings()
        print("✅ Configuration loaded successfully!")
        print(f"\n📋 Configuration Details:")
        print(f"   - Azure OpenAI Deployment: {settings.azure_openai_deployment}")
        print(f"   - Azure OpenAI Endpoint: {settings.azure_openai_endpoint or 'Using environment variable'}")
        print(f"   - Use Azure CLI Auth: {settings.use_azure_cli_auth}")
        print(f"   - MedImageParse Endpoint: {settings.medimageparse_endpoint}")
        
        # Check required fields
        if not settings.medimageparse_endpoint:
            print("⚠️  Warning: MEDIMAGEPARSE_ENDPOINT not set")
        
        return True, settings
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False, None


def test_model_creation():
    """Test 2: Data Model Creation"""
    print("\n" + "=" * 60)
    print("TEST 2: Data Model Creation")
    print("=" * 60)
    
    try:
        image_input = MedicalImageInput(
            study_id="TEST-001",
            patient_id="PATIENT-TEST",
            modality=ImageModality.CT,
            image_path="/tmp/test.dcm",
            metadata={"test": "data"}
        )
        print("✅ Data model created successfully!")
        print(f"\n📋 Model Details:")
        print(f"   - Study ID: {image_input.study_id}")
        print(f"   - Patient ID: {image_input.patient_id}")
        print(f"   - Modality: {image_input.modality}")
        print(f"   - Image Path: {image_input.image_path}")
        return True
    except Exception as e:
        print(f"❌ Data model creation failed: {e}")
        return False


async def test_agent_initialization(settings):
    """Test 3: Agent Initialization"""
    print("\n" + "=" * 60)
    print("TEST 3: Agent Initialization (Quick Test)")
    print("=" * 60)
    
    try:
        # Import here to avoid import errors if dependencies not installed
        from healthcare_orchestrator.agents.preprocessing import PreprocessingAgent
        
        print("📦 Initializing PreprocessingAgent...")
        async with PreprocessingAgent(settings) as agent:
            print("✅ Agent initialized successfully!")
            print(f"   - Agent type: PreprocessingAgent")
            print(f"   - Using credential: {'Azure CLI' if settings.use_azure_cli_auth else 'Default'}")
            
        return True
    except ImportError as e:
        print(f"⚠️  Dependencies not installed: {e}")
        print(f"   Run: pip install -e .")
        return False
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        print(f"\n💡 Common issues:")
        print(f"   - Check AZURE_OPENAI_ENDPOINT is set correctly")
        print(f"   - Verify Azure CLI is logged in: az login")
        print(f"   - Ensure you have access to the Azure OpenAI deployment")
        return False


async def test_orchestrator_initialization(settings):
    """Test 4: Orchestrator Initialization"""
    print("\n" + "=" * 60)
    print("TEST 4: Orchestrator Initialization")
    print("=" * 60)
    
    try:
        from healthcare_orchestrator import HealthcareOrchestrator
        
        print("📦 Initializing HealthcareOrchestrator...")
        async with HealthcareOrchestrator(settings) as orchestrator:
            print("✅ Orchestrator initialized successfully!")
            print(f"   - All 7 agents created")
            print(f"   - Workflow built with sequential orchestration")
            
        return True
    except ImportError as e:
        print(f"⚠️  Dependencies not installed: {e}")
        print(f"   Run: pip install -e .")
        return False
    except Exception as e:
        print(f"❌ Orchestrator initialization failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n🏥 Healthcare Agent Orchestrator - Setup Test")
    print("=" * 60)
    
    results = []
    
    # Test 1: Configuration
    success, settings = test_config_loading()
    results.append(("Configuration Loading", success))
    
    if not success:
        print("\n❌ Cannot proceed without valid configuration")
        return
    
    # Test 2: Data Models
    success = test_model_creation()
    results.append(("Data Model Creation", success))
    
    # Test 3: Agent Initialization (optional - requires dependencies)
    print("\n⏳ Testing agent initialization (requires dependencies)...")
    success = await test_agent_initialization(settings)
    results.append(("Agent Initialization", success))
    
    # Test 4: Orchestrator Initialization (optional - requires dependencies)
    if success:  # Only if agent test passed
        success = await test_orchestrator_initialization(settings)
        results.append(("Orchestrator Initialization", success))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\n📚 Next steps:")
        print("   - Run: python examples/basic_usage.py")
        print("   - Or: python examples/batch_processing.py")
    elif passed >= 2:
        print("\n⚠️  Core tests passed, but dependencies need to be installed.")
        print("\n📦 Install dependencies:")
        print("   pip install -e .")
    else:
        print("\n❌ Setup incomplete. Please check your .env configuration.")


if __name__ == "__main__":
    asyncio.run(main())
