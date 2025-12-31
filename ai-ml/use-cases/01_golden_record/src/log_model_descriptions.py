"""
Helper module to log model descriptions to MLflow for browser viewing
These descriptions appear in MLflow UI tags, notes, and artifacts
"""

MODEL_DESCRIPTIONS = {
    'deduplication': {
        'fellegi_sunter': {
            'name': 'Fellegi-Sunter Probabilistic Record Linkage',
            'description': 'Classical probabilistic matching algorithm for deduplication. Uses m-probabilities (probability of agreement given that records match) and u-probabilities (probability of agreement given that records don\'t match) to compute match scores. Well-suited for structured data with known matching attributes. Fast, interpretable, and requires minimal training data.',
            'algorithm': 'Probabilistic Record Linkage',
            'use_case': 'Deduplication of citizen records across multiple government data sources (Jan Aadhaar, Raj D.Ex, Schemes, Services)',
            'features': 'Fuzzy string matching (Jaro-Winkler 30%), Phonetic encoding (Soundex 20%), Date of Birth exact match (25%), Geospatial distance - Haversine ≤5km (15%), Numeric similarity - Income ±10% (10%)',
            'output': 'Match probability score (0-1) with decision: auto_merge (≥95% confidence), manual_review (80-95% confidence), or reject (<80% confidence)',
            'strengths': 'Interpretable, fast, works well with structured data, requires minimal labeled data',
            'limitations': 'Assumes feature independence, may struggle with complex non-linear relationships',
            'best_for': 'Structured citizen data with consistent formats, when interpretability is important'
        },
        'siamese_nn': {
            'name': 'Siamese Neural Network for Record Similarity',
            'description': 'Deep learning approach for record similarity learning. Uses twin neural networks with shared weights to learn similarity representations from record pairs. Better at handling complex patterns, non-linear relationships, and can automatically learn feature interactions. Requires more training data but can achieve higher accuracy.',
            'algorithm': 'Deep Learning / Neural Networks',
            'use_case': 'Advanced deduplication with complex feature relationships, when large training dataset is available',
            'features': 'Learns similarity representations from data, automatically handles feature interactions, can capture non-linear patterns',
            'output': 'Similarity score (0-1) indicating record match probability, with same decision thresholds as Fellegi-Sunter',
            'strengths': 'Learns complex patterns, handles non-linear relationships, can improve with more data',
            'limitations': 'Requires more training data, less interpretable, slower inference, requires GPU for large datasets',
            'best_for': 'Large datasets with complex patterns, when interpretability is less critical, future improvements'
        }
    },
    'conflict_reconciliation': {
        'xgboost_ensemble': {
            'name': 'XGBoost Ensemble for Conflict Resolution',
            'description': 'Gradient boosting ensemble classifier that ranks conflicting attribute values from different data sources. Uses recency (40% weight), source authority (dynamic weights: Aadhaar=10, Passport=8, etc.), and completeness (20% weight) to determine which version of an attribute is most reliable. Outputs confidence scores for each reconciled attribute.',
            'algorithm': 'Gradient Boosting / Ensemble Learning',
            'use_case': 'Resolving conflicts when same citizen attribute (e.g., DOB, address, income) has different values across sources',
            'features': 'Recency score (data age), Source authority score (trust level of source), Completeness score (how complete the record is)',
            'output': 'Ranked attribute versions with confidence scores (0-1), selecting best version per attribute',
            'strengths': 'Handles multiple ranking factors, provides confidence scores, interpretable feature importance',
            'limitations': 'Requires labeled conflict resolution data for training, may need retraining as source quality changes',
            'best_for': 'Multi-source data conflicts, when source quality varies, when confidence scores are needed'
        }
    },
    'best_truth_selection': {
        'survival_analysis': {
            'name': 'Survival Analysis for Best Truth Selection',
            'description': 'Predicts record staleness (when a record becomes outdated) using survival analysis (Cox Proportional Hazards model). Combines ML predictions with rule-based source priority hierarchy (Aadhaar > Passport > Birth Certificate > Employment Ledger > Educational Certificate). Retrained weekly on admin corrections to improve staleness predictions.',
            'algorithm': 'Survival Analysis (Cox Proportional Hazards) + Rule-Based',
            'use_case': 'Selecting the final "best truth" for each citizen attribute, predicting when records need updating',
            'features': 'Record age, Source authority, Completeness, Admin correction patterns, Historical staleness',
            'output': 'Best truth attribute value with staleness prediction (days until outdated), source attribution',
            'strengths': 'Handles time-dependent data quality, learns from corrections, combines ML with domain rules',
            'limitations': 'Requires historical correction data, may be sensitive to data distribution shifts',
            'best_for': 'Long-term Golden Record maintenance, when record freshness matters, continuous improvement scenarios'
        }
    }
}

def get_model_description(model_category, model_type):
    """
    Get model description for a given category and type
    
    Args:
        model_category: 'deduplication', 'conflict_reconciliation', or 'best_truth_selection'
        model_type: e.g., 'fellegi_sunter', 'xgboost_ensemble', 'survival_analysis'
    
    Returns:
        Dictionary with model description and metadata
    """
    return MODEL_DESCRIPTIONS.get(model_category, {}).get(model_type, {
        'name': model_type,
        'description': 'ML model description not available',
        'algorithm': 'N/A',
        'use_case': 'N/A',
        'features': 'N/A',
        'output': 'N/A'
    })

def log_model_description_to_mlflow(mlflow_client, model_category, model_type, run_id=None):
    """
    Log model description to MLflow run (for browser viewing)
    
    Args:
        mlflow_client: MLflow client instance
        model_category: Category of model
        model_type: Type of model
        run_id: MLflow run ID (if None, uses active run)
    """
    import mlflow
    
    description = get_model_description(model_category, model_type)
    
    # Set tags (visible in MLflow UI run overview)
    tags = {
        f'model_{model_category}_name': description['name'],
        f'model_{model_category}_algorithm': description['algorithm'],
        f'model_{model_category}_description': description['description'][:500],  # Truncate for tag limits
    }
    
    if run_id:
        mlflow_client.set_tags(run_id, tags)
    else:
        for key, value in tags.items():
            mlflow.set_tag(key, value)
    
    # Log full description as text artifact
    full_description = f"""
{'='*80}
{description['name'].upper()}
{'='*80}

CATEGORY: {model_category.upper()}
TYPE: {model_type}

DESCRIPTION
-----------
{description['description']}

ALGORITHM
---------
{description['algorithm']}

USE CASE
--------
{description['use_case']}

FEATURES
--------
{description['features']}

OUTPUT
------
{description['output']}

STRENGTHS
---------
{description.get('strengths', 'N/A')}

LIMITATIONS
-----------
{description.get('limitations', 'N/A')}

BEST FOR
--------
{description.get('best_for', 'N/A')}
"""
    
    artifact_path = f"model_descriptions/{model_category}_{model_type}_description.txt"
    if run_id:
        mlflow_client.log_text(run_id, full_description, artifact_path)
    else:
        mlflow.log_text(full_description, artifact_path)

