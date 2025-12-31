"""
Test Imports
Quick test to verify all imports work correctly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

print("Testing imports...")

try:
    print("  - Testing campaign_manager...")
    from campaign_manager import CampaignManager
    print("    ✅ campaign_manager imported")
except Exception as e:
    print(f"    ❌ Error: {e}")

try:
    print("  - Testing message_personalizer...")
    from message_personalizer import MessagePersonalizer
    print("    ✅ message_personalizer imported")
except Exception as e:
    print(f"    ❌ Error: {e}")

try:
    print("  - Testing consent_manager...")
    from consent_manager import ConsentManager
    print("    ✅ consent_manager imported")
except Exception as e:
    print(f"    ❌ Error: {e}")

try:
    print("  - Testing smart_orchestrator...")
    from smart_orchestrator import SmartOrchestrator
    print("    ✅ smart_orchestrator imported")
except Exception as e:
    print(f"    ❌ Error: {e}")

try:
    print("  - Testing intimation_service...")
    from intimation_service import IntimationService
    print("    ✅ intimation_service imported")
except Exception as e:
    print(f"    ❌ Error: {e}")

print("\n✅ Import test complete!")

