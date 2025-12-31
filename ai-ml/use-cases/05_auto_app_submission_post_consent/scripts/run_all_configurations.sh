#!/bin/bash
# Run All Configuration Scripts
# Execute this to set up all configuration in the correct order

set -e

echo "================================================================================"
echo "Running All Configuration Scripts for AI-PLATFORM-05"
echo "================================================================================"

# Activate virtual environment
cd /mnt/c/Projects/SMART/ai-ml/use-cases/05_auto_app_submission_post_consent
source /mnt/c/Projects/SMART/ai-ml/.venv/bin/activate

echo ""
echo "Step 1: Creating Field Mapping Rules..."
python scripts/create_field_mappings_template.py

echo ""
echo "Step 2: Enhancing Form Schemas..."
python scripts/enhance_form_schemas.py

echo ""
echo "Step 3: Verifying Configuration..."
python scripts/check_config.py

echo ""
echo "================================================================================"
echo "✅ All configuration scripts completed!"
echo "================================================================================"
echo ""
echo "Next steps:"
echo "1. Review field mappings in application.scheme_field_mappings"
echo "2. Review form schemas in application.scheme_form_schemas"
echo "3. Configure department connectors when API information is available"
echo "4. Customize submission modes per scheme requirements"
echo ""

