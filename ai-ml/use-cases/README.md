# AI/ML Use Cases

This directory contains the 27 AI/ML use cases planned for the SMART platform.

## Structure

Each use case should have its own folder:

```
use-cases/
├── use-case-01/
│   ├── model/          # Trained model files
│   ├── training/       # Training scripts
│   ├── inference/      # Inference API
│   └── README.md       # Use case documentation
├── use-case-02/
└── ...
```

## Use Case Documentation

Each use case should document:
- **Purpose**: What problem it solves
- **Input**: What data it requires
- **Output**: What predictions/insights it provides
- **Model**: Type of ML model used
- **Performance**: Accuracy metrics
- **Integration**: How it integrates with portals

## Integration

Use cases are integrated via the `aiml-service` which exposes REST APIs for:
- Model inference
- Batch predictions
- Model health checks

