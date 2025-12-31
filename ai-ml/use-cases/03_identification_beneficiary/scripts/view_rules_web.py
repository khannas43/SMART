#!/usr/bin/env python3
"""
Simple Web Interface to View Eligibility Rules
Run this script and open http://localhost:5001 in your browser
"""

import sys
from pathlib import Path
from flask import Flask, render_template_string, jsonify
from datetime import datetime
import pandas as pd
import yaml

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

app = Flask(__name__)

# Load database config
def get_db_connection():
    """Get database connection"""
    db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    return db

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eligibility Rules Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-item .number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-item .label {
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .filters {
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }
        
        .filters select {
            padding: 10px 15px;
            font-size: 1em;
            border: 2px solid #dee2e6;
            border-radius: 5px;
            margin-right: 10px;
            background: white;
            cursor: pointer;
        }
        
        .filters select:hover {
            border-color: #667eea;
        }
        
        .content {
            padding: 30px;
        }
        
        .scheme-section {
            margin-bottom: 40px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .scheme-header {
            background: #667eea;
            color: white;
            padding: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.3s;
        }
        
        .scheme-header:hover {
            background: #5568d3;
        }
        
        .scheme-header h2 {
            font-size: 1.5em;
        }
        
        .scheme-badge {
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        
        .scheme-content {
            padding: 0;
            display: none;
        }
        
        .scheme-content.active {
            display: block;
        }
        
        .rules-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .rules-table th {
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
        }
        
        .rules-table td {
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .rules-table tr:hover {
            background: #f8f9fa;
        }
        
        .rule-id {
            font-weight: bold;
            color: #667eea;
        }
        
        .rule-type {
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .rule-type.MANDATORY {
            background: #fff3cd;
            color: #856404;
        }
        
        .rule-type.OPTIONAL {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        .rule-mandatory {
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .rule-mandatory.true {
            background: #d4edda;
            color: #155724;
        }
        
        .rule-mandatory.false {
            background: #f8d7da;
            color: #721c24;
        }
        
        .rule-expression {
            font-family: 'Courier New', monospace;
            background: #f8f9fa;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.9em;
        }
        
        .no-rules {
            padding: 40px;
            text-align: center;
            color: #6c757d;
            font-size: 1.1em;
        }
        
        .refresh-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 50px;
            font-size: 1em;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            transition: all 0.3s;
        }
        
        .refresh-btn:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 7px 20px rgba(0,0,0,0.4);
        }
        
        @media (max-width: 768px) {
            .stats {
                flex-direction: column;
                gap: 15px;
            }
            
            .filters {
                flex-direction: column;
            }
            
            .filters select {
                width: 100%;
                margin-bottom: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Eligibility Rules Viewer</h1>
            <p>Auto Identification of Beneficiaries - AI-PLATFORM-03</p>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="number">{{ total_schemes }}</div>
                <div class="label">Schemes</div>
            </div>
            <div class="stat-item">
                <div class="number">{{ total_rules }}</div>
                <div class="label">Total Rules</div>
            </div>
            <div class="stat-item">
                <div class="number">{{ active_rules }}</div>
                <div class="label">Active Rules</div>
            </div>
        </div>
        
        <div class="content">
            {% for scheme in schemes %}
            <div class="scheme-section">
                <div class="scheme-header" onclick="toggleScheme('{{ scheme.scheme_code }}')">
                    <h2>{{ scheme.scheme_name }} ({{ scheme.scheme_code }})</h2>
                    <div class="scheme-badge">{{ scheme.rule_count }} Rules</div>
                </div>
                <div class="scheme-content" id="scheme-{{ scheme.scheme_code }}">
                    {% if scheme.rules %}
                    <table class="rules-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Rule Name</th>
                                <th>Type</th>
                                <th>Expression</th>
                                <th>Mandatory</th>
                                <th>Priority</th>
                                <th>Effective From</th>
                                <th>Effective To</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for rule in scheme.rules %}
                            <tr>
                                <td class="rule-id">#{{ rule.rule_id }}</td>
                                <td><strong>{{ rule.rule_name }}</strong></td>
                                <td><span class="rule-type {{ rule.rule_type }}">{{ rule.rule_type }}</span></td>
                                <td><code class="rule-expression">{{ rule.rule_expression }}</code></td>
                                <td><span class="rule-mandatory {% if rule.is_mandatory %}true{% else %}false{% endif %}">{% if rule.is_mandatory %}Yes{% else %}No{% endif %}</span></td>
                                <td>{{ rule.priority }}</td>
                                <td>{{ rule.effective_from or 'N/A' }}</td>
                                <td>{{ rule.effective_to or 'N/A' }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    {% else %}
                    <div class="no-rules">No rules defined for this scheme</div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
    
    <script>
        function toggleScheme(schemeCode) {
            const content = document.getElementById('scheme-' + schemeCode);
            content.classList.toggle('active');
        }
        
        // Expand first scheme by default
        document.addEventListener('DOMContentLoaded', function() {
            const firstScheme = document.querySelector('.scheme-section');
            if (firstScheme) {
                const firstContent = firstScheme.querySelector('.scheme-content');
                if (firstContent) {
                    firstContent.classList.add('active');
                }
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Display all eligibility rules"""
    db = get_db_connection()
    
    try:
        # Get all schemes with auto-identification enabled
        schemes_query = """
            SELECT 
                scheme_code, 
                scheme_name, 
                scheme_type,
                is_auto_id_enabled
            FROM public.scheme_master
            WHERE is_auto_id_enabled = true
            ORDER BY scheme_code
        """
        schemes_df = pd.read_sql(schemes_query, db.connection)
        
        # Get all rules grouped by scheme
        rules_query = """
            SELECT 
                rule_id,
                scheme_code,
                rule_name,
                rule_type,
                rule_expression,
                rule_operator,
                rule_value,
                is_mandatory,
                priority,
                version,
                effective_from,
                effective_to,
                created_at
            FROM eligibility.scheme_eligibility_rules
            WHERE (effective_to IS NULL OR effective_to >= CURRENT_DATE)
                AND (effective_from <= CURRENT_DATE)
            ORDER BY scheme_code, priority DESC, rule_id
        """
        rules_df = pd.read_sql(rules_query, db.connection)
        
        # Process data for template
        schemes_data = []
        total_rules = len(rules_df)
        active_rules = len(rules_df)
        
        for _, scheme in schemes_df.iterrows():
            scheme_code = scheme['scheme_code']
            scheme_rules = rules_df[rules_df['scheme_code'] == scheme_code]
            
            rules_list = []
            for _, rule in scheme_rules.iterrows():
                rules_list.append({
                    'rule_id': int(rule['rule_id']),
                    'rule_name': rule['rule_name'],
                    'rule_type': rule['rule_type'],
                    'rule_expression': rule['rule_expression'],
                    'is_mandatory': bool(rule['is_mandatory']),
                    'priority': int(rule['priority']) if pd.notna(rule['priority']) else 0,
                    'effective_from': rule['effective_from'].strftime('%Y-%m-%d') if pd.notna(rule['effective_from']) else None,
                    'effective_to': rule['effective_to'].strftime('%Y-%m-%d') if pd.notna(rule['effective_to']) else None
                })
            
            schemes_data.append({
                'scheme_code': scheme_code,
                'scheme_name': scheme['scheme_name'],
                'scheme_type': scheme['scheme_type'],
                'rule_count': len(rules_list),
                'rules': rules_list
            })
        
        return render_template_string(
            HTML_TEMPLATE,
            schemes=schemes_data,
            total_schemes=len(schemes_data),
            total_rules=total_rules,
            active_rules=active_rules
        )
    
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>", 500
    finally:
        db.disconnect()


# Intimation Campaign Results Routes
def get_intimation_db_connection():
    """Get database connection for intimation use case"""
    config_path = Path(__file__).parent.parent.parent / "04_intimation_smart_consent_triggering" / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    db_config = config['database']
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    return db


INTIMATION_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intimation Campaign Results - SMART Platform</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-card h3 {
            font-size: 2.5em;
            margin-bottom: 5px;
        }
        
        .stat-card p {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
        }
        
        tr:hover {
            background: #f5f5f5;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .badge-success {
            background: #4caf50;
            color: white;
        }
        
        .badge-warning {
            background: #ff9800;
            color: white;
        }
        
        .badge-info {
            background: #2196f3;
            color: white;
        }
        
        .badge-draft {
            background: #9e9e9e;
            color: white;
        }
        
        .message-preview {
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            margin-bottom: 20px;
            transition: background 0.3s;
        }
        
        .refresh-btn:hover {
            background: #5568d3;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Intimation Campaign Results</h1>
        <p class="subtitle">Auto Intimation & Smart Consent Triggering - AI-PLATFORM-04</p>
        
        <div style="margin-bottom: 20px;">
            <a href="/" style="color: #667eea; text-decoration: none; margin-right: 20px;">← Back to Eligibility Rules</a>
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Data</button>
        </div>
        
        {% if error %}
        <div class="error">
            <strong>Error:</strong> {{ error }}
        </div>
        {% else %}
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>{{ stats.total_campaigns }}</h3>
                <p>Total Campaigns</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.total_candidates }}</h3>
                <p>Total Candidates</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.total_messages }}</h3>
                <p>Messages Created</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.total_consents }}</h3>
                <p>Consents Recorded</p>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Recent Campaigns</h2>
            {% if campaigns %}
            <table>
                <thead>
                    <tr>
                        <th>Campaign ID</th>
                        <th>Name</th>
                        <th>Scheme</th>
                        <th>Candidates</th>
                        <th>Status</th>
                        <th>Created At</th>
                    </tr>
                </thead>
                <tbody>
                    {% for campaign in campaigns %}
                    <tr>
                        <td>{{ campaign.campaign_id }}</td>
                        <td><strong>{{ campaign.campaign_name }}</strong></td>
                        <td><span class="badge badge-info">{{ campaign.scheme_code }}</span></td>
                        <td>{{ campaign.candidate_count }}</td>
                        <td>
                            <span class="badge badge-{{ campaign.status.lower() }}">
                                {{ campaign.status.upper() }}
                            </span>
                        </td>
                        <td>{{ campaign.created_at }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="loading">No campaigns found</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>👥 Recent Candidates</h2>
            {% if candidates %}
            <table>
                <thead>
                    <tr>
                        <th>Candidate ID</th>
                        <th>Family ID</th>
                        <th>Scheme</th>
                        <th>Eligibility Score</th>
                        <th>Priority Score</th>
                        <th>Campaign ID</th>
                    </tr>
                </thead>
                <tbody>
                    {% for candidate in candidates %}
                    <tr>
                        <td>{{ candidate.candidate_id }}</td>
                        <td>{{ candidate.family_id[:8] }}...</td>
                        <td><span class="badge badge-info">{{ candidate.scheme_code }}</span></td>
                        <td>{{ "%.2f"|format(candidate.eligibility_score) }}</td>
                        <td>{{ "%.2f"|format(candidate.priority_score) if candidate.priority_score else "N/A" }}</td>
                        <td>{{ candidate.campaign_id }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="loading">No candidates found</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>💬 Messages Created</h2>
            {% if messages %}
            <table>
                <thead>
                    <tr>
                        <th>Message ID</th>
                        <th>Family ID</th>
                        <th>Scheme</th>
                        <th>Channel</th>
                        <th>Language</th>
                        <th>Status</th>
                        <th>Message Preview</th>
                        <th>Created At</th>
                    </tr>
                </thead>
                <tbody>
                    {% for message in messages %}
                    <tr>
                        <td>{{ message.message_id }}</td>
                        <td>{{ message.family_id[:8] if message.family_id else 'N/A' }}...</td>
                        <td><span class="badge badge-info">{{ message.scheme_code or 'N/A' }}</span></td>
                        <td><span class="badge badge-success">{{ message.channel.upper() if message.channel else 'N/A' }}</span></td>
                        <td>{{ message.language.upper() if message.language else 'N/A' }}</td>
                        <td>
                            <span class="badge badge-{{ message.status.lower() if message.status else 'info' }}">
                                {{ message.status.upper() if message.status else 'PENDING' }}
                            </span>
                        </td>
                        <td class="message-preview" title="{{ message.message_body[:100] if message.message_body else 'N/A' }}...">
                            {{ message.message_body[:50] if message.message_body else 'N/A' }}...
                        </td>
                        <td>{{ message.created_at }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="loading">No messages found</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>✅ Consent Records</h2>
            {% if consents %}
            <table>
                <thead>
                    <tr>
                        <th>Consent ID</th>
                        <th>Family ID</th>
                        <th>Scheme</th>
                        <th>Consent Type</th>
                        <th>Status</th>
                        <th>Method</th>
                        <th>Channel</th>
                        <th>Created At</th>
                    </tr>
                </thead>
                <tbody>
                    {% for consent in consents %}
                    <tr>
                        <td>{{ consent.consent_id }}</td>
                        <td>{{ consent.family_id[:8] }}...</td>
                        <td><span class="badge badge-info">{{ consent.scheme_code }}</span></td>
                        <td>
                            <span class="badge badge-{{ 'success' if consent.consent_type == 'soft' else 'warning' }}">
                                {{ consent.consent_type.upper() }}
                            </span>
                        </td>
                        <td>
                            <span class="badge badge-{{ 'success' if consent.status == 'valid' else 'warning' }}">
                                {{ consent.status.upper() }}
                            </span>
                        </td>
                        <td>{{ consent.consent_method }}</td>
                        <td>{{ consent.consent_channel.upper() if consent.consent_channel else 'N/A' }}</td>
                        <td>{{ consent.created_at }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="loading">No consent records found</p>
            {% endif %}
        </div>
        
        {% endif %}
        
        <div style="text-align: center; margin-top: 40px; color: #666; padding-top: 20px; border-top: 1px solid #eee;">
            <p>SMART Platform - AI-PLATFORM-04 | Last updated: {{ timestamp }}</p>
        </div>
    </div>
</body>
</html>
"""


@app.route('/ai04')
@app.route('/ai04/')
def intimation_index():
    """Main page displaying all campaign results"""
    db = get_intimation_db_connection()
    
    try:
        db.connect()
        
        # Get statistics
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM intimation.campaigns) as total_campaigns,
                (SELECT COUNT(*) FROM intimation.campaign_candidates) as total_candidates,
                (SELECT COUNT(*) FROM intimation.message_logs) as total_messages,
                (SELECT COUNT(*) FROM intimation.consent_records) as total_consents
        """
        stats_df = pd.read_sql(stats_query, db.connection)
        stats = stats_df.iloc[0].to_dict()
        
        # Get recent campaigns
        campaigns_query = """
            SELECT 
                campaign_id,
                campaign_name,
                scheme_code,
                status,
                created_at,
                (SELECT COUNT(*) FROM intimation.campaign_candidates 
                 WHERE campaign_id = c.campaign_id) as candidate_count
            FROM intimation.campaigns c
            ORDER BY created_at DESC
            LIMIT 10
        """
        campaigns_df = pd.read_sql(campaigns_query, db.connection)
        campaigns = campaigns_df.to_dict('records')
        
        # Get recent candidates
        candidates_query = """
            SELECT 
                candidate_id,
                campaign_id,
                family_id,
                scheme_code,
                eligibility_score,
                priority_score
            FROM intimation.campaign_candidates
            ORDER BY candidate_id DESC
            LIMIT 20
        """
        candidates_df = pd.read_sql(candidates_query, db.connection)
        candidates = candidates_df.to_dict('records')
        
        # Get recent messages
        messages_query = """
            SELECT 
                ml.message_id,
                ml.recipient_id as family_id,
                cc.scheme_code,
                ml.channel,
                ml.message_language as language,
                ml.message_body,
                ml.status,
                ml.created_at
            FROM intimation.message_logs ml
            LEFT JOIN intimation.campaign_candidates cc ON ml.candidate_id = cc.candidate_id
            ORDER BY ml.created_at DESC
            LIMIT 20
        """
        messages_df = pd.read_sql(messages_query, db.connection)
        messages = messages_df.to_dict('records')
        
        # Get recent consents
        consents_query = """
            SELECT 
                consent_id,
                family_id,
                scheme_code,
                consent_type,
                status,
                consent_method,
                consent_channel,
                created_at
            FROM intimation.consent_records
            ORDER BY created_at DESC
            LIMIT 20
        """
        consents_df = pd.read_sql(consents_query, db.connection)
        consents = consents_df.to_dict('records')
        
        # Format timestamps
        for campaign in campaigns:
            if pd.notna(campaign.get('created_at')):
                campaign['created_at'] = campaign['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        for message in messages:
            if pd.notna(message.get('created_at')):
                message['created_at'] = message['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        for consent in consents:
            if pd.notna(consent.get('created_at')):
                consent['created_at'] = consent['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return render_template_string(
            INTIMATION_HTML_TEMPLATE,
            stats=stats,
            campaigns=campaigns,
            candidates=candidates,
            messages=messages,
            consents=consents,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=None
        )
        
    except Exception as e:
        return render_template_string(
            INTIMATION_HTML_TEMPLATE,
            stats={'total_campaigns': 0, 'total_candidates': 0, 'total_messages': 0, 'total_consents': 0},
            campaigns=[],
            candidates=[],
            messages=[],
            consents=[],
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=str(e)
        )
    finally:
        db.disconnect()


@app.route('/ai04/api/stats')
def intimation_api_stats():
    """API endpoint for statistics"""
    db = get_intimation_db_connection()
    
    try:
        db.connect()
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM intimation.campaigns) as total_campaigns,
                (SELECT COUNT(*) FROM intimation.campaign_candidates) as total_candidates,
                (SELECT COUNT(*) FROM intimation.message_logs) as total_messages,
                (SELECT COUNT(*) FROM intimation.consent_records) as total_consents
        """
        stats_df = pd.read_sql(stats_query, db.connection)
        return jsonify(stats_df.iloc[0].to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.disconnect()


# Application Submission Routes (AI-PLATFORM-05)
def get_application_db_connection():
    """Get database connection for application submission use case"""
    config_path = Path(__file__).parent.parent.parent / "05_auto_app_submission_post_consent" / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    db_config = config['database']
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    return db


APPLICATION_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Application Submission Viewer - SMART Platform</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-card h3 {
            font-size: 2.5em;
            margin-bottom: 5px;
        }
        
        .stat-card p {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
        }
        
        tr:hover {
            background: #f5f5f5;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .badge-creating {
            background: #2196f3;
            color: white;
        }
        
        .badge-mapped {
            background: #ff9800;
            color: white;
        }
        
        .badge-validated {
            background: #4caf50;
            color: white;
        }
        
        .badge-submitted {
            background: #9c27b0;
            color: white;
        }
        
        .badge-rejected {
            background: #f44336;
            color: white;
        }
        
        .badge-error {
            background: #f44336;
            color: white;
        }
        
        .badge-auto {
            background: #4caf50;
            color: white;
        }
        
        .badge-review {
            background: #ff9800;
            color: white;
        }
        
        .badge-info {
            background: #2196f3;
            color: white;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            margin-bottom: 20px;
            transition: background 0.3s;
        }
        
        .refresh-btn:hover {
            background: #5568d3;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
        }
        
        .score {
            font-weight: bold;
        }
        
        .score-high {
            color: #4caf50;
        }
        
        .score-medium {
            color: #ff9800;
        }
        
        .score-low {
            color: #f44336;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 Application Submission Viewer</h1>
        <p class="subtitle">Auto Application Submission Post-Consent - AI-PLATFORM-05</p>
        
        <div style="margin-bottom: 20px;">
            <a href="/" style="color: #667eea; text-decoration: none; margin-right: 20px;">← Back to Eligibility Rules</a>
            <a href="/ai04" style="color: #667eea; text-decoration: none; margin-right: 20px;">📊 Campaign Results</a>
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Data</button>
        </div>
        
        {% if error %}
        <div class="error">
            <strong>Error:</strong> {{ error }}
        </div>
        {% else %}
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>{{ stats.total_applications }}</h3>
                <p>Total Applications</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.submitted_applications }}</h3>
                <p>Submitted</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.pending_applications }}</h3>
                <p>Pending</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.error_applications }}</h3>
                <p>Errors</p>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Recent Applications</h2>
            {% if applications %}
            <table>
                <thead>
                    <tr>
                        <th>Application ID</th>
                        <th>Family ID</th>
                        <th>Scheme</th>
                        <th>Status</th>
                        <th>Submission Mode</th>
                        <th>Eligibility Score</th>
                        <th>Fields Mapped</th>
                        <th>Created At</th>
                    </tr>
                </thead>
                <tbody>
                    {% for app in applications %}
                    <tr>
                        <td>{{ app.application_id }}</td>
                        <td>{{ app.family_id[:8] }}...</td>
                        <td><span class="badge badge-info">{{ app.scheme_code }}</span></td>
                        <td>
                            <span class="badge badge-{{ app.status.lower() }}">
                                {{ app.status.upper() }}
                            </span>
                        </td>
                        <td>
                            <span class="badge badge-{{ app.submission_mode.lower() if app.submission_mode else 'info' }}">
                                {{ app.submission_mode.upper() if app.submission_mode else 'N/A' }}
                            </span>
                        </td>
                        <td>
                            <span class="score {% if app.eligibility_score >= 0.8 %}score-high{% elif app.eligibility_score >= 0.5 %}score-medium{% else %}score-low{% endif %}">
                                {{ "%.4f"|format(app.eligibility_score) if app.eligibility_score else 'N/A' }}
                            </span>
                        </td>
                        <td>{{ app.fields_count }}</td>
                        <td>{{ app.created_at }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="loading">No applications found</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>✅ Submission Status</h2>
            {% if submissions %}
            <table>
                <thead>
                    <tr>
                        <th>Submission ID</th>
                        <th>Application ID</th>
                        <th>Scheme</th>
                        <th>Status</th>
                        <th>Department Response</th>
                        <th>Submitted At</th>
                    </tr>
                </thead>
                <tbody>
                    {% for sub in submissions %}
                    <tr>
                        <td>{{ sub.submission_id }}</td>
                        <td>{{ sub.application_id }}</td>
                        <td><span class="badge badge-info">{{ sub.scheme_code }}</span></td>
                        <td>
                            <span class="badge badge-{{ sub.status.lower() if sub.status else 'info' }}">
                                {{ sub.status.upper() if sub.status else 'PENDING' }}
                            </span>
                        </td>
                        <td>{{ sub.dept_response_code or 'N/A' }}</td>
                        <td>{{ sub.submitted_at or 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="loading">No submissions found</p>
            {% endif %}
        </div>
        
        {% endif %}
        
        <div style="text-align: center; margin-top: 40px; color: #666; padding-top: 20px; border-top: 1px solid #eee;">
            <p>SMART Platform - AI-PLATFORM-05 | Last updated: {{ timestamp }}</p>
        </div>
    </div>
</body>
</html>
"""


@app.route('/ai05')
@app.route('/ai05/')
def application_index():
    """Main page displaying application submission results"""
    db = get_application_db_connection()
    
    try:
        db.connect()
        
        # Get statistics
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM application.applications) as total_applications,
                (SELECT COUNT(*) FROM application.applications WHERE status = 'submitted') as submitted_applications,
                (SELECT COUNT(*) FROM application.applications WHERE status IN ('creating', 'mapped', 'validated', 'pending_review')) as pending_applications,
                (SELECT COUNT(*) FROM application.applications WHERE status = 'error') as error_applications
        """
        stats_df = pd.read_sql(stats_query, db.connection)
        stats = stats_df.iloc[0].to_dict()
        
        # Get recent applications
        applications_query = """
            SELECT 
                a.application_id,
                a.family_id,
                a.scheme_code,
                a.status,
                a.submission_mode,
                a.eligibility_score,
                a.created_at,
                (SELECT COUNT(*) FROM application.application_fields WHERE application_id = a.application_id) as fields_count
            FROM application.applications a
            ORDER BY a.created_at DESC
            LIMIT 20
        """
        applications_df = pd.read_sql(applications_query, db.connection)
        applications = applications_df.to_dict('records')
        
        # Get recent submissions
        submissions_query = """
            SELECT 
                s.submission_id,
                s.application_id,
                a.scheme_code,
                s.response_status as status,
                s.department_application_number as dept_response_code,
                s.submitted_at
            FROM application.application_submissions s
            JOIN application.applications a ON s.application_id = a.application_id
            ORDER BY s.submitted_at DESC NULLS LAST
            LIMIT 20
        """
        submissions_df = pd.read_sql(submissions_query, db.connection)
        submissions = submissions_df.to_dict('records')
        
        # Format timestamps
        for app in applications:
            if pd.notna(app.get('created_at')):
                app['created_at'] = app['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        for sub in submissions:
            if pd.notna(sub.get('submitted_at')):
                sub['submitted_at'] = sub['submitted_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return render_template_string(
            APPLICATION_HTML_TEMPLATE,
            stats=stats,
            applications=applications,
            submissions=submissions,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=None
        )
        
    except Exception as e:
        return render_template_string(
            APPLICATION_HTML_TEMPLATE,
            stats={'total_applications': 0, 'submitted_applications': 0, 'pending_applications': 0, 'error_applications': 0},
            applications=[],
            submissions=[],
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=str(e)
        )
    finally:
        db.disconnect()


@app.route('/ai05/api/stats')
def application_api_stats():
    """API endpoint for application statistics"""
    db = get_application_db_connection()
    
    try:
        db.connect()
        
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM application.applications) as total_applications,
                (SELECT COUNT(*) FROM application.applications WHERE status = 'submitted') as submitted_applications,
                (SELECT COUNT(*) FROM application.applications WHERE status IN ('creating', 'mapped', 'validated', 'pending_review')) as pending_applications,
                (SELECT COUNT(*) FROM application.applications WHERE status = 'error') as error_applications
        """
        stats_df = pd.read_sql(stats_query, db.connection)
        stats = stats_df.iloc[0].to_dict()
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.disconnect()


# Decision Evaluation Routes (AI-PLATFORM-06)
def get_decision_db_connection():
    """Get database connection for decision evaluation use case"""
    config_path = Path(__file__).parent.parent.parent / "06_auto_approval_straight_processing" / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    db_config = config['database']
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    return db


DECISION_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Decision Evaluation Viewer - SMART Platform</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-card h3 {
            font-size: 2.5em;
            margin-bottom: 5px;
        }
        
        .stat-card p {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f5576c;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        th {
            background: #f5576c;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
        }
        
        tr:hover {
            background: #f5f5f5;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .badge-auto_approve {
            background: #4caf50;
            color: white;
        }
        
        .badge-route_to_officer {
            background: #ff9800;
            color: white;
        }
        
        .badge-route_to_fraud {
            background: #f44336;
            color: white;
        }
        
        .badge-auto_reject {
            background: #9e9e9e;
            color: white;
        }
        
        .badge-approved {
            background: #4caf50;
            color: white;
        }
        
        .badge-rejected {
            background: #f44336;
            color: white;
        }
        
        .badge-under_review {
            background: #ff9800;
            color: white;
        }
        
        .badge-pending {
            background: #2196f3;
            color: white;
        }
        
        .badge-low {
            background: #4caf50;
            color: white;
        }
        
        .badge-medium {
            background: #ff9800;
            color: white;
        }
        
        .badge-high {
            background: #f44336;
            color: white;
        }
        
        .badge-info {
            background: #2196f3;
            color: white;
        }
        
        .risk-score {
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
        }
        
        .risk-score.low {
            background: #e8f5e9;
            color: #2e7d32;
        }
        
        .risk-score.medium {
            background: #fff3e0;
            color: #e65100;
        }
        
        .risk-score.high {
            background: #ffebee;
            color: #c62828;
        }
        
        .refresh-btn {
            background: #f5576c;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            margin-bottom: 20px;
            transition: background 0.3s;
        }
        
        .refresh-btn:hover {
            background: #e0485a;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚖️ Decision Evaluation Viewer</h1>
        <p class="subtitle">Auto Approval & Straight-through Processing - AI-PLATFORM-06</p>
        
        <div style="margin-bottom: 20px;">
            <a href="/" style="color: #f5576c; text-decoration: none; margin-right: 20px;">← Back to Eligibility Rules</a>
            <a href="/ai04" style="color: #f5576c; text-decoration: none; margin-right: 20px;">📊 Campaign Results</a>
            <a href="/ai05" style="color: #f5576c; text-decoration: none; margin-right: 20px;">📝 Application Submission</a>
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Data</button>
        </div>
        
        {% if error %}
        <div class="error">
            <strong>Error:</strong> {{ error }}
        </div>
        {% else %}
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>{{ stats.total_decisions }}</h3>
                <p>Total Decisions</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.auto_approved }}</h3>
                <p>Auto Approved</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.officer_reviewed }}</h3>
                <p>Officer Reviewed</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.rejected }}</h3>
                <p>Rejected</p>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Recent Decisions</h2>
            {% if decisions %}
            <table>
                <thead>
                    <tr>
                        <th>Decision ID</th>
                        <th>Application ID</th>
                        <th>Scheme</th>
                        <th>Decision Type</th>
                        <th>Status</th>
                        <th>Risk Score</th>
                        <th>Risk Band</th>
                        <th>Decision Time</th>
                    </tr>
                </thead>
                <tbody>
                    {% for decision in decisions %}
                    <tr>
                        <td>{{ decision.decision_id }}</td>
                        <td>{{ decision.application_id }}</td>
                        <td><span class="badge badge-info">{{ decision.scheme_code }}</span></td>
                        <td>
                            <span class="badge badge-{{ decision.decision_type.lower() }}">
                                {{ decision.decision_type.replace('_', ' ').title() }}
                            </span>
                        </td>
                        <td>
                            <span class="badge badge-{{ decision.decision_status.lower() if decision.decision_status else 'pending' }}">
                                {{ decision.decision_status.replace('_', ' ').title() if decision.decision_status else 'PENDING' }}
                            </span>
                        </td>
                        <td>
                            {% if decision.risk_score is not none %}
                            <span class="risk-score {% if decision.risk_score <= 0.3 %}low{% elif decision.risk_score <= 0.7 %}medium{% else %}high{% endif %}">
                                {{ "%.4f"|format(decision.risk_score) }}
                            </span>
                            {% else %}
                            N/A
                            {% endif %}
                        </td>
                        <td>
                            {% if decision.risk_band %}
                            <span class="badge badge-{{ decision.risk_band.lower() }}">
                                {{ decision.risk_band }}
                            </span>
                            {% else %}
                            N/A
                            {% endif %}
                        </td>
                        <td>{{ decision.decision_timestamp or 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="loading">No decisions found</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>💳 Payment Triggers</h2>
            {% if payment_triggers %}
            <table>
                <thead>
                    <tr>
                        <th>Trigger ID</th>
                        <th>Decision ID</th>
                        <th>Payment Status</th>
                        <th>Payment System</th>
                        <th>Triggered At</th>
                    </tr>
                </thead>
                <tbody>
                    {% for trigger in payment_triggers %}
                    <tr>
                        <td>{{ trigger.trigger_id }}</td>
                        <td>{{ trigger.decision_id }}</td>
                        <td>
                            <span class="badge badge-{{ trigger.payment_status.lower() if trigger.payment_status else 'pending' }}">
                                {{ trigger.payment_status.replace('_', ' ').title() if trigger.payment_status else 'PENDING' }}
                            </span>
                        </td>
                        <td>{{ trigger.payment_system or 'N/A' }}</td>
                        <td>{{ trigger.triggered_at or 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="loading">No payment triggers found</p>
            {% endif %}
        </div>
        
        {% endif %}
        
        <div style="text-align: center; margin-top: 40px; color: #666; padding-top: 20px; border-top: 1px solid #eee;">
            <p>SMART Platform - AI-PLATFORM-06 | Last updated: {{ timestamp }}</p>
        </div>
    </div>
</body>
</html>
"""


@app.route('/ai06')
@app.route('/ai06/')
def decision_index():
    """Main page displaying decision evaluation results"""
    db = get_decision_db_connection()
    
    try:
        db.connect()
        
        # Get statistics
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM decision.decisions) as total_decisions,
                (SELECT COUNT(*) FROM decision.decisions WHERE decision_type = 'AUTO_APPROVE') as auto_approved,
                (SELECT COUNT(*) FROM decision.decisions WHERE decision_type IN ('ROUTE_TO_OFFICER', 'ROUTE_TO_FRAUD')) as officer_reviewed,
                (SELECT COUNT(*) FROM decision.decisions WHERE decision_type = 'AUTO_REJECT') as rejected
        """
        stats_df = pd.read_sql(stats_query, db.connection)
        stats = stats_df.iloc[0].to_dict()
        
        # Get recent decisions
        decisions_query = """
            SELECT 
                d.decision_id,
                d.application_id,
                d.scheme_code,
                d.decision_type,
                d.decision_status,
                d.risk_score,
                d.risk_band,
                d.decision_timestamp
            FROM decision.decisions d
            ORDER BY d.decision_timestamp DESC NULLS LAST, d.created_at DESC
            LIMIT 20
        """
        decisions_df = pd.read_sql(decisions_query, db.connection)
        decisions = decisions_df.to_dict('records')
        
        # Get payment triggers
        payment_query = """
            SELECT 
                pt.trigger_id,
                pt.decision_id,
                pt.payment_status,
                pt.payment_system,
                pt.triggered_at
            FROM decision.payment_triggers pt
            ORDER BY pt.triggered_at DESC NULLS LAST
            LIMIT 20
        """
        payment_df = pd.read_sql(payment_query, db.connection)
        payment_triggers = payment_df.to_dict('records')
        
        # Format timestamps
        for decision in decisions:
            if pd.notna(decision.get('decision_timestamp')):
                decision['decision_timestamp'] = decision['decision_timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            elif pd.notna(decision.get('created_at')):
                decision['decision_timestamp'] = decision.get('created_at', 'N/A')
            else:
                decision['decision_timestamp'] = 'N/A'
        
        for trigger in payment_triggers:
            if pd.notna(trigger.get('triggered_at')):
                trigger['triggered_at'] = trigger['triggered_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return render_template_string(
            DECISION_HTML_TEMPLATE,
            stats=stats,
            decisions=decisions,
            payment_triggers=payment_triggers,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=None
        )
        
    except Exception as e:
        return render_template_string(
            DECISION_HTML_TEMPLATE,
            stats={'total_decisions': 0, 'auto_approved': 0, 'officer_reviewed': 0, 'rejected': 0},
            decisions=[],
            payment_triggers=[],
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=str(e)
        )
    finally:
        db.disconnect()


@app.route('/ai06/api/stats')
def decision_api_stats():
    """API endpoint for decision statistics"""
    db = get_decision_db_connection()
    
    try:
        db.connect()
        
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM decision.decisions) as total_decisions,
                (SELECT COUNT(*) FROM decision.decisions WHERE decision_type = 'AUTO_APPROVE') as auto_approved,
                (SELECT COUNT(*) FROM decision.decisions WHERE decision_type IN ('ROUTE_TO_OFFICER', 'ROUTE_TO_FRAUD')) as officer_reviewed,
                (SELECT COUNT(*) FROM decision.decisions WHERE decision_type = 'AUTO_REJECT') as rejected
        """
        stats_df = pd.read_sql(stats_query, db.connection)
        stats = stats_df.iloc[0].to_dict()
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.disconnect()


# Beneficiary Detection Routes (AI-PLATFORM-07)
def get_detection_db_connection():
    """Get database connection for beneficiary detection use case"""
    config_path = Path(__file__).parent.parent.parent / "07_ineligible_mistargeted_beneficiary_detection" / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    db_config = config['database']
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    return db


DETECTION_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Beneficiary Detection Viewer - SMART Platform</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-card h3 {
            font-size: 2.5em;
            margin-bottom: 5px;
        }
        
        .stat-card p {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #fa709a;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        th {
            background: #fa709a;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
        }
        
        tr:hover {
            background: #f5f5f5;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .badge-hard_ineligible {
            background: #f44336;
            color: white;
        }
        
        .badge-likely_mis_targeted {
            background: #ff9800;
            color: white;
        }
        
        .badge-low_confidence_flag {
            background: #ffc107;
            color: #333;
        }
        
        .badge-flagged {
            background: #ff9800;
            color: white;
        }
        
        .badge-under_verification {
            background: #2196f3;
            color: white;
        }
        
        .badge-verified_ineligible {
            background: #f44336;
            color: white;
        }
        
        .badge-verified_eligible {
            background: #4caf50;
            color: white;
        }
        
        .badge-high {
            background: #f44336;
            color: white;
        }
        
        .badge-medium {
            background: #ff9800;
            color: white;
        }
        
        .badge-low {
            background: #4caf50;
            color: white;
        }
        
        .badge-info {
            background: #2196f3;
            color: white;
        }
        
        .priority-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .priority-1, .priority-2, .priority-3 {
            background: #f44336;
            color: white;
        }
        
        .priority-4, .priority-5, .priority-6 {
            background: #ff9800;
            color: white;
        }
        
        .priority-7, .priority-8, .priority-9, .priority-10 {
            background: #4caf50;
            color: white;
        }
        
        .refresh-btn {
            background: #fa709a;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            margin-bottom: 20px;
            transition: background 0.3s;
        }
        
        .refresh-btn:hover {
            background: #f85d87;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Beneficiary Detection Viewer</h1>
        <p class="subtitle">Ineligible / Mistargeted Beneficiary Detection - AI-PLATFORM-07</p>
        
        <div style="margin-bottom: 20px;">
            <a href="/" style="color: #fa709a; text-decoration: none; margin-right: 20px;">← Back to Eligibility Rules</a>
            <a href="/ai04" style="color: #fa709a; text-decoration: none; margin-right: 20px;">📊 Campaign Results</a>
            <a href="/ai05" style="color: #fa709a; text-decoration: none; margin-right: 20px;">📝 Application Submission</a>
            <a href="/ai06" style="color: #fa709a; text-decoration: none; margin-right: 20px;">⚖️ Decision Evaluation</a>
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Data</button>
        </div>
        
        {% if error %}
        <div class="error">
            <strong>Error:</strong> {{ error }}
        </div>
        {% else %}
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>{{ stats.total_runs }}</h3>
                <p>Detection Runs</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.total_cases }}</h3>
                <p>Cases Flagged</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.hard_ineligible }}</h3>
                <p>Hard Ineligible</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.mis_targeted }}</h3>
                <p>Mis-targeted</p>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Recent Detection Runs</h2>
            {% if detection_runs %}
            <table>
                <thead>
                    <tr>
                        <th>Run ID</th>
                        <th>Run Type</th>
                        <th>Status</th>
                        <th>Beneficiaries Scanned</th>
                        <th>Cases Flagged</th>
                        <th>Started By</th>
                        <th>Run Date</th>
                    </tr>
                </thead>
                <tbody>
                    {% for run in detection_runs %}
                    <tr>
                        <td>{{ run.run_id }}</td>
                        <td><span class="badge badge-info">{{ run.run_type }}</span></td>
                        <td>
                            <span class="badge badge-{{ run.run_status.lower() if run.run_status else 'info' }}">
                                {{ run.run_status.upper() if run.run_status else 'N/A' }}
                            </span>
                        </td>
                        <td>{{ run.total_beneficiaries_scanned or 0 }}</td>
                        <td>{{ run.total_cases_flagged or 0 }}</td>
                        <td>{{ run.started_by or 'system' }}</td>
                        <td>{{ run.run_date or 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="loading">No detection runs found</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>🚨 Detected Cases</h2>
            {% if detected_cases %}
            <table>
                <thead>
                    <tr>
                        <th>Case ID</th>
                        <th>Beneficiary ID</th>
                        <th>Scheme</th>
                        <th>Case Type</th>
                        <th>Confidence</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th>Financial Exposure</th>
                        <th>Risk Score</th>
                        <th>Detected At</th>
                    </tr>
                </thead>
                <tbody>
                    {% for case in detected_cases %}
                    <tr>
                        <td>{{ case.case_id }}</td>
                        <td>{{ case.beneficiary_id[:12] if case.beneficiary_id else 'N/A' }}...</td>
                        <td><span class="badge badge-info">{{ case.scheme_code }}</span></td>
                        <td>
                            <span class="badge badge-{{ case.case_type.lower().replace('_', '_') }}">
                                {{ case.case_type.replace('_', ' ').title() }}
                            </span>
                        </td>
                        <td>
                            <span class="badge badge-{{ case.confidence_level.lower() if case.confidence_level else 'low' }}">
                                {{ case.confidence_level.upper() if case.confidence_level else 'LOW' }}
                            </span>
                        </td>
                        <td>
                            <span class="badge badge-{{ case.case_status.lower().replace('_', '_') if case.case_status else 'flagged' }}">
                                {{ case.case_status.replace('_', ' ').title() if case.case_status else 'FLAGGED' }}
                            </span>
                        </td>
                        <td>
                            {% if case.priority %}
                            <span class="priority-badge priority-{{ case.priority }}">
                                P{{ case.priority }}
                            </span>
                            {% else %}
                            N/A
                            {% endif %}
                        </td>
                        <td>
                            {% if case.financial_exposure %}
                            ₹{{ "%.2f"|format(case.financial_exposure) }}
                            {% else %}
                            N/A
                            {% endif %}
                        </td>
                        <td>
                            {% if case.risk_score is not none %}
                            <span class="badge badge-{{ 'high' if case.risk_score >= 0.7 else 'medium' if case.risk_score >= 0.4 else 'low' }}">
                                {{ "%.3f"|format(case.risk_score) }}
                            </span>
                            {% else %}
                            N/A
                            {% endif %}
                        </td>
                        <td>{{ case.detection_timestamp or 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="loading">No detected cases found</p>
            {% endif %}
        </div>
        
        {% endif %}
        
        <div style="text-align: center; margin-top: 40px; color: #666; padding-top: 20px; border-top: 1px solid #eee;">
            <p>SMART Platform - AI-PLATFORM-07 | Last updated: {{ timestamp }}</p>
        </div>
    </div>
</body>
</html>
"""


@app.route('/ai07')
@app.route('/ai07/')
def detection_index():
    """Main page displaying beneficiary detection results"""
    db = get_detection_db_connection()
    
    try:
        db.connect()
        
        # Get statistics
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM detection.detection_runs) as total_runs,
                (SELECT COUNT(*) FROM detection.detected_cases) as total_cases,
                (SELECT COUNT(*) FROM detection.detected_cases WHERE case_type = 'HARD_INELIGIBLE') as hard_ineligible,
                (SELECT COUNT(*) FROM detection.detected_cases WHERE case_type = 'LIKELY_MIS_TARGETED') as mis_targeted
        """
        stats_df = pd.read_sql(stats_query, db.connection)
        stats = stats_df.iloc[0].to_dict()
        
        # Get recent detection runs
        runs_query = """
            SELECT 
                run_id,
                run_type,
                run_status,
                total_beneficiaries_scanned,
                total_cases_flagged,
                started_by,
                run_date
            FROM detection.detection_runs
            ORDER BY run_date DESC
            LIMIT 10
        """
        runs_df = pd.read_sql(runs_query, db.connection)
        detection_runs = runs_df.to_dict('records')
        
        # Get recent detected cases
        cases_query = """
            SELECT 
                case_id,
                beneficiary_id,
                scheme_code,
                case_type,
                confidence_level,
                case_status,
                priority,
                financial_exposure,
                risk_score,
                detection_timestamp
            FROM detection.detected_cases
            ORDER BY priority ASC, detection_timestamp DESC
            LIMIT 20
        """
        cases_df = pd.read_sql(cases_query, db.connection)
        detected_cases = cases_df.to_dict('records')
        
        # Format timestamps
        for run in detection_runs:
            if pd.notna(run.get('run_date')):
                run['run_date'] = run['run_date'].strftime('%Y-%m-%d %H:%M:%S')
        
        for case in detected_cases:
            if pd.notna(case.get('detection_timestamp')):
                case['detection_timestamp'] = case['detection_timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        return render_template_string(
            DETECTION_HTML_TEMPLATE,
            stats=stats,
            detection_runs=detection_runs,
            detected_cases=detected_cases,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=None
        )
        
    except Exception as e:
        return render_template_string(
            DETECTION_HTML_TEMPLATE,
            stats={'total_runs': 0, 'total_cases': 0, 'hard_ineligible': 0, 'mis_targeted': 0},
            detection_runs=[],
            detected_cases=[],
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=str(e)
        )
    finally:
        db.disconnect()


# Eligibility Checker Viewer Routes (AI-PLATFORM-08)
def get_eligibility_checker_db_connection():
    """Get database connection for eligibility checker use case"""
    config_path = Path(__file__).parent.parent.parent / "08_eligibility_checker_recommendation" / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    db_config = config['database']
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    return db

ELIGIBILITY_CHECKER_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eligibility Checker & Recommendations - SMART Platform</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-card h3 {
            font-size: 2.5em;
            margin-bottom: 5px;
        }
        
        .stat-card p {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
        }
        
        tr:hover {
            background: #f5f5f5;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .badge-eligible {
            background: #4caf50;
            color: white;
        }
        
        .badge-possible_eligible {
            background: #ff9800;
            color: white;
        }
        
        .badge-not_eligible {
            background: #f44336;
            color: white;
        }
        
        .badge-logged_in {
            background: #2196f3;
            color: white;
        }
        
        .badge-guest {
            background: #9c27b0;
            color: white;
        }
        
        .badge-anonymous {
            background: #607d8b;
            color: white;
        }
        
        .badge-high {
            background: #4caf50;
            color: white;
        }
        
        .badge-medium {
            background: #ff9800;
            color: white;
        }
        
        .badge-low {
            background: #f44336;
            color: white;
        }
        
        .badge-info {
            background: #2196f3;
            color: white;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            margin-bottom: 20px;
            transition: background 0.3s;
        }
        
        .refresh-btn:hover {
            background: #5568d3;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
        }
        
        .score {
            font-weight: 600;
            color: #667eea;
        }
        
        .explanation {
            font-size: 0.9em;
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Eligibility Checker & Recommendations</h1>
        <p class="subtitle">Interactive Eligibility Checking - AI-PLATFORM-08</p>
        
        <div style="margin-bottom: 20px;">
            <a href="/" style="color: #667eea; text-decoration: none; margin-right: 20px;">← Eligibility Rules</a>
            <a href="/ai04" style="color: #667eea; text-decoration: none; margin-right: 20px;">📊 Campaign Results</a>
            <a href="/ai05" style="color: #667eea; text-decoration: none; margin-right: 20px;">📝 Application Submission</a>
            <a href="/ai06" style="color: #667eea; text-decoration: none; margin-right: 20px;">⚖️ Decision Evaluation</a>
            <a href="/ai07" style="color: #667eea; text-decoration: none; margin-right: 20px;">🚨 Beneficiary Detection</a>
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Data</button>
        </div>
        
        {% if error %}
        <div class="error">
            <strong>Error:</strong> {{ error }}
        </div>
        {% else %}
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>{{ stats.total_checks }}</h3>
                <p>Total Checks</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.logged_in_checks }}</h3>
                <p>Logged-in Checks</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.guest_checks }}</h3>
                <p>Guest Checks</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.total_recommendations }}</h3>
                <p>Recommendations</p>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Recent Eligibility Checks</h2>
            {% if checks %}
            <table>
                <thead>
                    <tr>
                        <th>Check ID</th>
                        <th>User Type</th>
                        <th>Check Type</th>
                        <th>Mode</th>
                        <th>Schemes Checked</th>
                        <th>Eligible</th>
                        <th>Possible</th>
                        <th>Not Eligible</th>
                        <th>Check Time</th>
                    </tr>
                </thead>
                <tbody>
                    {% for check in checks %}
                    <tr>
                        <td>{{ check.check_id }}</td>
                        <td>
                            <span class="badge badge-{{ check.user_type.lower().replace('_', '_') }}">
                                {{ check.user_type.replace('_', ' ').title() }}
                            </span>
                        </td>
                        <td><span class="badge badge-info">{{ check.check_type }}</span></td>
                        <td>{{ check.check_mode }}</td>
                        <td>{{ check.total_schemes_checked }}</td>
                        <td><span class="badge badge-eligible">{{ check.eligible_count }}</span></td>
                        <td><span class="badge badge-possible_eligible">{{ check.possible_eligible_count }}</span></td>
                        <td><span class="badge badge-not_eligible">{{ check.not_eligible_count }}</span></td>
                        <td>{{ check.check_timestamp }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="loading">No eligibility checks found</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>⭐ Top Recommendations</h2>
            {% if recommendations %}
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Scheme</th>
                        <th>Status</th>
                        <th>Eligibility Score</th>
                        <th>Priority Score</th>
                        <th>Confidence</th>
                        <th>Explanation</th>
                    </tr>
                </thead>
                <tbody>
                    {% for rec in recommendations %}
                    <tr>
                        <td><strong>#{{ rec.recommendation_rank }}</strong></td>
                        <td>
                            <strong>{{ rec.scheme_code }}</strong><br>
                            <small>{{ rec.scheme_name }}</small>
                        </td>
                        <td>
                            <span class="badge badge-{{ rec.eligibility_status.lower().replace('_', '_') }}">
                                {{ rec.eligibility_status.replace('_', ' ').title() }}
                            </span>
                        </td>
                        <td>
                            <span class="score">{{ "%.2f"|format(rec.eligibility_score) }}</span>
                        </td>
                        <td>
                            <span class="score">{{ "%.2f"|format(rec.priority_score) }}</span>
                        </td>
                        <td>
                            <span class="badge badge-{{ rec.confidence_level.lower() }}">
                                {{ rec.confidence_level }}
                            </span>
                        </td>
                        <td>
                            <div class="explanation">{{ rec.explanation_text[:80] }}...</div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="loading">No recommendations found</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>📋 Scheme Eligibility Results</h2>
            {% if scheme_results %}
            <table>
                <thead>
                    <tr>
                        <th>Check ID</th>
                        <th>Scheme</th>
                        <th>Status</th>
                        <th>Score</th>
                        <th>Confidence</th>
                        <th>Rank</th>
                        <th>Explanation</th>
                    </tr>
                </thead>
                <tbody>
                    {% for result in scheme_results %}
                    <tr>
                        <td>{{ result.check_id }}</td>
                        <td>
                            <strong>{{ result.scheme_code }}</strong><br>
                            <small>{{ result.scheme_name }}</small>
                        </td>
                        <td>
                            <span class="badge badge-{{ result.eligibility_status.lower().replace('_', '_') }}">
                                {{ result.eligibility_status.replace('_', ' ').title() }}
                            </span>
                        </td>
                        <td>
                            <span class="score">{{ "%.2f"|format(result.eligibility_score) }}</span>
                        </td>
                        <td>
                            <span class="badge badge-{{ result.confidence_level.lower() }}">
                                {{ result.confidence_level }}
                            </span>
                        </td>
                        <td>
                            {% if result.recommendation_rank %}
                            <span class="badge badge-info">#{{ result.recommendation_rank }}</span>
                            {% else %}
                            -
                            {% endif %}
                        </td>
                        <td>
                            <div class="explanation">{{ result.explanation_text[:60] if result.explanation_text else 'N/A' }}...</div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="loading">No scheme results found</p>
            {% endif %}
        </div>
        
        {% endif %}
        
        <div style="text-align: center; margin-top: 40px; color: #666; padding-top: 20px; border-top: 1px solid #eee;">
            <p>SMART Platform - AI-PLATFORM-08 | Last updated: {{ timestamp }}</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/ai08')
@app.route('/ai08/')
def eligibility_checker_index():
    """Main page displaying eligibility checker results"""
    db = get_eligibility_checker_db_connection()
    
    try:
        db.connect()
        
        # Get statistics
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM eligibility_checker.eligibility_checks) as total_checks,
                (SELECT COUNT(*) FROM eligibility_checker.eligibility_checks WHERE user_type = 'LOGGED_IN') as logged_in_checks,
                (SELECT COUNT(*) FROM eligibility_checker.eligibility_checks WHERE user_type = 'GUEST') as guest_checks,
                (SELECT COUNT(*) FROM eligibility_checker.recommendation_sets WHERE is_active = TRUE) as total_recommendations
        """
        stats_df = pd.read_sql(stats_query, db.connection)
        stats = stats_df.iloc[0].to_dict()
        
        # Get recent eligibility checks
        checks_query = """
            SELECT 
                check_id, user_type, check_type, check_mode,
                total_schemes_checked, eligible_count, possible_eligible_count, not_eligible_count,
                check_timestamp
            FROM eligibility_checker.eligibility_checks
            ORDER BY check_timestamp DESC
            LIMIT 15
        """
        checks_df = pd.read_sql(checks_query, db.connection)
        checks = checks_df.to_dict('records')
        
        # Get top recommendations (from recent checks)
        recommendations_query = """
            SELECT DISTINCT ON (ser.scheme_code)
                ser.scheme_code, ser.scheme_name, ser.eligibility_status, ser.eligibility_score,
                ser.confidence_level, ser.recommendation_rank, ser.priority_score,
                ser.explanation_text
            FROM eligibility_checker.scheme_eligibility_results ser
            INNER JOIN eligibility_checker.eligibility_checks ec ON ser.check_id = ec.check_id
            WHERE ser.eligibility_status IN ('ELIGIBLE', 'POSSIBLE_ELIGIBLE')
              AND ser.recommendation_rank IS NOT NULL
              AND ser.recommendation_rank <= 5
            ORDER BY ser.scheme_code, ser.recommendation_rank, ec.check_timestamp DESC
            LIMIT 20
        """
        recommendations_df = pd.read_sql(recommendations_query, db.connection)
        recommendations = recommendations_df.to_dict('records')
        
        # Get recent scheme results
        scheme_results_query = """
            SELECT 
                ser.check_id, ser.scheme_code, ser.scheme_name, ser.eligibility_status,
                ser.eligibility_score, ser.confidence_level, ser.recommendation_rank,
                ser.explanation_text
            FROM eligibility_checker.scheme_eligibility_results ser
            INNER JOIN eligibility_checker.eligibility_checks ec ON ser.check_id = ec.check_id
            ORDER BY ec.check_timestamp DESC, ser.recommendation_rank ASC NULLS LAST
            LIMIT 30
        """
        scheme_results_df = pd.read_sql(scheme_results_query, db.connection)
        scheme_results = scheme_results_df.to_dict('records')
        
        # Format timestamps
        for check in checks:
            if pd.notna(check.get('check_timestamp')):
                check['check_timestamp'] = check['check_timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        # Fill missing values
        for rec in recommendations:
            if rec.get('eligibility_score') is None:
                rec['eligibility_score'] = 0.0
            if rec.get('priority_score') is None:
                rec['priority_score'] = 0.0
            if rec.get('explanation_text') is None:
                rec['explanation_text'] = ''
        
        for result in scheme_results:
            if result.get('eligibility_score') is None:
                result['eligibility_score'] = 0.0
            if result.get('explanation_text') is None:
                result['explanation_text'] = ''
        
        return render_template_string(
            ELIGIBILITY_CHECKER_HTML_TEMPLATE,
            stats=stats,
            checks=checks,
            recommendations=recommendations,
            scheme_results=scheme_results,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=None
        )
        
    except Exception as e:
        return render_template_string(
            ELIGIBILITY_CHECKER_HTML_TEMPLATE,
            stats={'total_checks': 0, 'logged_in_checks': 0, 'guest_checks': 0, 'total_recommendations': 0},
            checks=[],
            recommendations=[],
            scheme_results=[],
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=str(e)
        )
    finally:
        db.disconnect()

@app.route('/ai07/api/stats')
def detection_api_stats():
    """API endpoint for detection statistics"""
    db = get_detection_db_connection()
    
    try:
        db.connect()
        
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM detection.detection_runs) as total_runs,
                (SELECT COUNT(*) FROM detection.detected_cases) as total_cases,
                (SELECT COUNT(*) FROM detection.detected_cases WHERE case_type = 'HARD_INELIGIBLE') as hard_ineligible,
                (SELECT COUNT(*) FROM detection.detected_cases WHERE case_type = 'LIKELY_MIS_TARGETED') as mis_targeted
        """
        stats_df = pd.read_sql(stats_query, db.connection)
        stats = stats_df.iloc[0].to_dict()
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.disconnect()


def get_inclusion_db_connection():
    """Get database connection for inclusion schema"""
    db_config_path = Path(__file__).parent.parent.parent / "09_proactive_inclusion_exception_handling" / "config" / "db_config.yaml"
    if not db_config_path.exists():
        # Fallback to default config
        db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    return db


INCLUSION_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proactive Inclusion & Exception Handling</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-card h3 {
            font-size: 2.5em;
            color: #667eea;
            margin-bottom: 10px;
        }
        .stat-card p {
            color: #6c757d;
            font-size: 1.1em;
        }
        .section {
            padding: 30px;
            border-bottom: 2px solid #e9ecef;
        }
        .section h2 {
            color: #495057;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }
        th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }
        tr:hover { background: #f8f9fa; }
        .badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        .badge-high { background: #dc3545; color: white; }
        .badge-medium { background: #ffc107; color: #000; }
        .badge-low { background: #28a745; color: white; }
        .badge-pending { background: #6c757d; color: white; }
        .badge-scheduled { background: #17a2b8; color: white; }
        .badge-delivered { background: #28a745; color: white; }
        .segment-tag {
            display: inline-block;
            padding: 3px 8px;
            margin: 2px;
            background: #e9ecef;
            border-radius: 12px;
            font-size: 0.8em;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .refresh-btn:hover { background: #5568d3; }
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Proactive Inclusion & Exception Handling</h1>
            <p>AI-PLATFORM-09 - Priority Households & Nudges</p>
        </div>
        
        <div style="padding: 20px; background: #f8f9fa;">
            <a href="/" style="color: #667eea; text-decoration: none; margin-right: 20px;">← Back to Eligibility Rules</a>
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Data</button>
        </div>
        
        {% if error %}
        <div class="error"><strong>Error:</strong> {{ error }}</div>
        {% else %}
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>{{ stats.total_priority_households }}</h3>
                <p>Priority Households</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.high_priority }}</h3>
                <p>High Priority</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.total_exceptions }}</h3>
                <p>Exception Flags</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.total_nudges }}</h3>
                <p>Nudges Sent</p>
            </div>
        </div>
        
        <div class="section">
            <h2>🏠 Priority Households</h2>
            {% if priority_households %}
            <table>
                <thead>
                    <tr>
                        <th>Priority ID</th>
                        <th>Family ID</th>
                        <th>District</th>
                        <th>Gap Score</th>
                        <th>Vulnerability</th>
                        <th>Priority Level</th>
                        <th>Segments</th>
                        <th>Eligibility Gap</th>
                        <th>Detected At</th>
                    </tr>
                </thead>
                <tbody>
                    {% for hh in priority_households %}
                    <tr>
                        <td>{{ hh.priority_id }}</td>
                        <td>{{ hh.family_id[:8] if hh.family_id else 'N/A' }}...</td>
                        <td>{{ hh.district or 'N/A' }}</td>
                        <td>{{ "%.3f"|format(hh.inclusion_gap_score) if hh.inclusion_gap_score else '0.000' }}</td>
                        <td>{{ "%.3f"|format(hh.vulnerability_score) if hh.vulnerability_score else '0.000' }}</td>
                        <td>
                            <span class="badge badge-{{ hh.priority_level.lower() if hh.priority_level else 'low' }}">
                                {{ hh.priority_level or 'LOW' }}
                            </span>
                        </td>
                        <td>
                            {% for seg in (hh.priority_segments or [])[:3] %}
                            <span class="segment-tag">{{ seg }}</span>
                            {% endfor %}
                        </td>
                        <td>{{ hh.eligibility_gap_count or 0 }}</td>
                        <td>{{ hh.detected_at[:19] if hh.detected_at else 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="padding: 20px; color: #6c757d;">No priority households found</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>⚠️ Exception Flags</h2>
            {% if exceptions %}
            <table>
                <thead>
                    <tr>
                        <th>Exception ID</th>
                        <th>Family ID</th>
                        <th>Category</th>
                        <th>Description</th>
                        <th>Anomaly Score</th>
                        <th>Review Status</th>
                        <th>Detected At</th>
                    </tr>
                </thead>
                <tbody>
                    {% for exc in exceptions %}
                    <tr>
                        <td>{{ exc.exception_id }}</td>
                        <td>{{ exc.family_id[:8] if exc.family_id else 'N/A' }}...</td>
                        <td><span class="badge badge-pending">{{ exc.exception_category or 'N/A' }}</span></td>
                        <td>{{ (exc.exception_description or 'N/A')[:60] }}...</td>
                        <td>{{ "%.3f"|format(exc.anomaly_score) if exc.anomaly_score else '0.000' }}</td>
                        <td>
                            <span class="badge badge-{{ exc.review_status.lower().replace('_', '-') if exc.review_status else 'pending' }}">
                                {{ exc.review_status or 'PENDING_REVIEW' }}
                            </span>
                        </td>
                        <td>{{ exc.detected_at[:19] if exc.detected_at else 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="padding: 20px; color: #6c757d;">No exception flags found</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>📬 Nudge Records</h2>
            {% if nudges %}
            <table>
                <thead>
                    <tr>
                        <th>Nudge ID</th>
                        <th>Family ID</th>
                        <th>Type</th>
                        <th>Message</th>
                        <th>Channel</th>
                        <th>Priority</th>
                        <th>Status</th>
                        <th>Scheduled At</th>
                    </tr>
                </thead>
                <tbody>
                    {% for nudge in nudges %}
                    <tr>
                        <td>{{ nudge.nudge_id }}</td>
                        <td>{{ nudge.family_id[:8] if nudge.family_id else 'N/A' }}...</td>
                        <td>{{ nudge.nudge_type or 'N/A' }}</td>
                        <td>{{ (nudge.nudge_message or 'N/A')[:50] }}...</td>
                        <td><span class="badge badge-info">{{ nudge.channel or 'N/A' }}</span></td>
                        <td>
                            <span class="badge badge-{{ nudge.priority_level.lower() if nudge.priority_level else 'low' }}">
                                {{ nudge.priority_level or 'LOW' }}
                            </span>
                        </td>
                        <td>
                            <span class="badge badge-{{ nudge.delivery_status.lower() if nudge.delivery_status else 'scheduled' }}">
                                {{ nudge.delivery_status or 'SCHEDULED' }}
                            </span>
                        </td>
                        <td>{{ nudge.scheduled_at[:19] if nudge.scheduled_at else 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="padding: 20px; color: #6c757d;">No nudges found</p>
            {% endif %}
        </div>
        
        {% endif %}
        
        <div style="padding: 20px; text-align: center; color: #6c757d;">
            <p>Last updated: {{ timestamp }}</p>
        </div>
    </div>
</body>
</html>
"""


@app.route('/ai09')
@app.route('/ai09/')
def inclusion_index():
    """Main page displaying inclusion and exception handling results"""
    db = get_inclusion_db_connection()
    
    try:
        db.connect()
        
        # Get statistics
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM inclusion.priority_households WHERE is_active = TRUE) as total_priority_households,
                (SELECT COUNT(*) FROM inclusion.priority_households WHERE is_active = TRUE AND priority_level = 'HIGH') as high_priority,
                (SELECT COUNT(*) FROM inclusion.exception_flags WHERE review_status = 'PENDING_REVIEW') as total_exceptions,
                (SELECT COUNT(*) FROM inclusion.nudge_records) as total_nudges
        """
        stats_df = pd.read_sql(stats_query, db.connection)
        stats = stats_df.iloc[0].to_dict()
        
        # Get priority households
        households_query = """
            SELECT 
                priority_id, family_id, district, inclusion_gap_score,
                vulnerability_score, priority_level, priority_segments,
                eligibility_gap_count, detected_at
            FROM inclusion.priority_households
            WHERE is_active = TRUE
            ORDER BY inclusion_gap_score DESC, vulnerability_score DESC
            LIMIT 20
        """
        households_df = pd.read_sql(households_query, db.connection)
        priority_households = households_df.to_dict('records')
        
        # Get exception flags
        exceptions_query = """
            SELECT 
                exception_id, family_id, exception_category, exception_description,
                anomaly_score, review_status, detected_at
            FROM inclusion.exception_flags
            WHERE review_status = 'PENDING_REVIEW'
            ORDER BY anomaly_score DESC, detected_at DESC
            LIMIT 20
        """
        exceptions_df = pd.read_sql(exceptions_query, db.connection)
        exceptions = exceptions_df.to_dict('records')
        
        # Get recent nudges
        nudges_query = """
            SELECT 
                nudge_id, family_id, nudge_type, nudge_message,
                channel, priority_level, delivery_status, scheduled_at
            FROM inclusion.nudge_records
            ORDER BY scheduled_at DESC
            LIMIT 20
        """
        nudges_df = pd.read_sql(nudges_query, db.connection)
        nudges = nudges_df.to_dict('records')
        
        # Format timestamps
        for hh in priority_households:
            if pd.notna(hh.get('detected_at')):
                hh['detected_at'] = str(hh['detected_at'])
            if isinstance(hh.get('priority_segments'), str):
                try:
                    import json
                    hh['priority_segments'] = json.loads(hh['priority_segments'])
                except:
                    hh['priority_segments'] = []
        
        for exc in exceptions:
            if pd.notna(exc.get('detected_at')):
                exc['detected_at'] = str(exc['detected_at'])
        
        for nudge in nudges:
            if pd.notna(nudge.get('scheduled_at')):
                nudge['scheduled_at'] = str(nudge['scheduled_at'])
        
        return render_template_string(
            INCLUSION_HTML_TEMPLATE,
            stats=stats,
            priority_households=priority_households,
            exceptions=exceptions,
            nudges=nudges,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=None
        )
        
    except Exception as e:
        return render_template_string(
            INCLUSION_HTML_TEMPLATE,
            stats={'total_priority_households': 0, 'high_priority': 0, 'total_exceptions': 0, 'total_nudges': 0},
            priority_households=[],
            exceptions=[],
            nudges=[],
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            error=str(e)
        )
    finally:
        db.disconnect()


@app.route('/ai09/api/stats')
def inclusion_api_stats():
    """API endpoint for inclusion statistics"""
    db = get_inclusion_db_connection()
    
    try:
        db.connect()
        
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM inclusion.priority_households WHERE is_active = TRUE) as total_priority_households,
                (SELECT COUNT(*) FROM inclusion.priority_households WHERE is_active = TRUE AND priority_level = 'HIGH') as high_priority,
                (SELECT COUNT(*) FROM inclusion.exception_flags WHERE review_status = 'PENDING_REVIEW') as total_exceptions,
                (SELECT COUNT(*) FROM inclusion.nudge_records) as total_nudges
        """
        stats_df = pd.read_sql(stats_query, db.connection)
        stats = stats_df.iloc[0].to_dict()
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.disconnect()


# Forecast database connection helper
def get_forecast_db_connection():
    """Get forecast database connection"""
    db_config_path = Path(__file__).parent.parent.parent / "10_entitlement_benefit_forecast" / "config" / "db_config.yaml"
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    return db


FORECAST_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Benefit Forecast Viewer - AI-PLATFORM-10</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }
        .stat-item {
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stat-item .number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-item .label {
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .content {
            padding: 30px;
        }
        .forecast-card {
            border: 2px solid #e9ecef;
            border-radius: 8px;
            margin-bottom: 30px;
            overflow: hidden;
            background: white;
        }
        .forecast-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .forecast-header h2 { font-size: 1.5em; }
        .forecast-badge {
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .forecast-body {
            padding: 20px;
        }
        .forecast-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .info-item {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .info-item label {
            display: block;
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        .info-item value {
            display: block;
            font-size: 1.2em;
            font-weight: bold;
            color: #495057;
        }
        .projections-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .projections-table th {
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
        }
        .projections-table td {
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
        }
        .projections-table tr:hover {
            background: #f8f9fa;
        }
        .scheme-code {
            font-weight: bold;
            color: #667eea;
        }
        .projection-type {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
        }
        .type-current {
            background: #d4edda;
            color: #155724;
        }
        .type-future {
            background: #fff3cd;
            color: #856404;
        }
        .type-policy {
            background: #d1ecf1;
            color: #0c5460;
        }
        .amount {
            font-weight: bold;
            color: #28a745;
        }
        .uncertainty {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
        }
        .uncertainty-low {
            background: #d4edda;
            color: #155724;
        }
        .uncertainty-medium {
            background: #fff3cd;
            color: #856404;
        }
        .uncertainty-high {
            background: #f8d7da;
            color: #721c24;
        }
        .no-data {
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }
        .no-data h3 {
            font-size: 1.5em;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Entitlement & Benefit Forecast</h1>
            <p>AI-PLATFORM-10 - Forecast Viewer</p>
        </div>
        
        <div class="stats" id="stats">
            <div class="stat-item">
                <div class="number" id="total-forecasts">0</div>
                <div class="label">Total Forecasts</div>
            </div>
            <div class="stat-item">
                <div class="number" id="total-schemes">0</div>
                <div class="label">Total Schemes</div>
            </div>
            <div class="stat-item">
                <div class="number" id="total-annual">₹0</div>
                <div class="label">Total Annual Value</div>
            </div>
            <div class="stat-item">
                <div class="number" id="avg-uncertainty">-</div>
                <div class="label">Avg Uncertainty</div>
            </div>
        </div>
        
        <div class="content" id="content">
            <div class="no-data">
                <h3>Loading forecasts...</h3>
                <p>Please wait while we fetch forecast data.</p>
            </div>
        </div>
    </div>
    
    <script>
        function loadForecasts() {
            fetch('/ai10/api/forecasts')
                .then(response => response.json())
                .then(data => {
                    updateStats(data);
                    renderForecasts(data.forecasts || []);
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('content').innerHTML = 
                        '<div class="no-data"><h3>Error loading forecasts</h3><p>' + error.message + '</p></div>';
                });
        }
        
        function updateStats(data) {
            document.getElementById('total-forecasts').textContent = data.total_forecasts || 0;
            document.getElementById('total-schemes').textContent = data.total_schemes || 0;
            document.getElementById('total-annual').textContent = '₹' + (data.total_annual_value || 0).toLocaleString('en-IN', {minimumFractionDigits: 2});
            document.getElementById('avg-uncertainty').textContent = data.avg_uncertainty || '-';
        }
        
        function renderForecasts(forecasts) {
            const content = document.getElementById('content');
            
            if (forecasts.length === 0) {
                content.innerHTML = '<div class="no-data"><h3>No forecasts found</h3><p>Generate forecasts to view them here.</p></div>';
                return;
            }
            
            content.innerHTML = forecasts.map(forecast => {
                const projections = forecast.projections || [];
                const projectionRows = projections.map(proj => `
                    <tr>
                        <td class="scheme-code">${proj.scheme_code || '-'}</td>
                        <td>${proj.scheme_name || '-'}</td>
                        <td><span class="projection-type type-${proj.projection_type?.toLowerCase().replace('_', '-') || 'current'}">${proj.projection_type || 'CURRENT'}</span></td>
                        <td>${proj.period_start || '-'}</td>
                        <td>${proj.period_end || '-'}</td>
                        <td>${proj.period_type || '-'}</td>
                        <td class="amount">₹${(proj.benefit_amount || 0).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
                        <td>${(proj.probability || 1) * 100}%</td>
                        <td><span class="uncertainty uncertainty-${(proj.confidence_level || 'MEDIUM').toLowerCase()}">${proj.confidence_level || 'MEDIUM'}</span></td>
                    </tr>
                `).join('');
                
                return `
                    <div class="forecast-card">
                        <div class="forecast-header">
                            <h2>Forecast #${forecast.forecast_id || 'N/A'}</h2>
                            <span class="forecast-badge">${forecast.forecast_type || 'BASELINE'}</span>
                        </div>
                        <div class="forecast-body">
                            <div class="forecast-info">
                                <div class="info-item">
                                    <label>Family ID</label>
                                    <value>${forecast.family_id || '-'}</value>
                                </div>
                                <div class="info-item">
                                    <label>Horizon</label>
                                    <value>${forecast.horizon_months || 0} months</value>
                                </div>
                                <div class="info-item">
                                    <label>Scenario</label>
                                    <value>${forecast.scenario_name || 'BASELINE'}</value>
                                </div>
                                <div class="info-item">
                                    <label>Total Annual Value</label>
                                    <value>₹${(forecast.total_annual_value || 0).toLocaleString('en-IN', {minimumFractionDigits: 2})}</value>
                                </div>
                                <div class="info-item">
                                    <label>Total Forecast Value</label>
                                    <value>₹${(forecast.total_forecast_value || 0).toLocaleString('en-IN', {minimumFractionDigits: 2})}</value>
                                </div>
                                <div class="info-item">
                                    <label>Uncertainty</label>
                                    <value><span class="uncertainty uncertainty-${(forecast.uncertainty_level || 'MEDIUM').toLowerCase()}">${forecast.uncertainty_level || 'MEDIUM'}</span></value>
                                </div>
                            </div>
                            
                            <h3 style="margin-top: 20px; margin-bottom: 10px;">Projections (${projections.length})</h3>
                            ${projections.length > 0 ? `
                                <table class="projections-table">
                                    <thead>
                                        <tr>
                                            <th>Scheme Code</th>
                                            <th>Scheme Name</th>
                                            <th>Type</th>
                                            <th>Period Start</th>
                                            <th>Period End</th>
                                            <th>Period Type</th>
                                            <th>Benefit Amount</th>
                                            <th>Probability</th>
                                            <th>Confidence</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${projectionRows}
                                    </tbody>
                                </table>
                            ` : '<p>No projections available.</p>'}
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        loadForecasts();
        setInterval(loadForecasts, 30000);
    </script>
</body>
</html>
"""

@app.route('/ai10')
@app.route('/ai10/')
def forecast_index():
    """Main page for benefit forecast viewer"""
    return render_template_string(FORECAST_HTML_TEMPLATE)

@app.route('/ai10/api/forecasts')
def forecast_api_forecasts():
    """API endpoint for forecasts"""
    db = get_forecast_db_connection()
    try:
        cursor = db.connection.cursor()
        
        cursor.execute("""
            SELECT 
                forecast_id, family_id, horizon_months, forecast_date,
                forecast_type, scenario_name, status,
                total_annual_value, total_forecast_value, scheme_count,
                uncertainty_level, generated_at
            FROM forecast.forecast_records
            WHERE status = 'COMPLETED'
            ORDER BY generated_at DESC
            LIMIT 20
        """)
        
        forecasts_data = cursor.fetchall()
        
        forecasts = []
        total_annual_value = 0
        total_schemes = set()
        uncertainty_levels = []
        
        for row in forecasts_data:
            forecast_id, family_id, horizon_months, forecast_date, forecast_type, scenario_name, status, total_annual, total_forecast, scheme_count, uncertainty, generated_at = row
            
            cursor.execute("""
                SELECT 
                    projection_id, scheme_code, scheme_name, projection_type,
                    period_start, period_end, period_type,
                    benefit_amount, benefit_frequency, probability, confidence_level,
                    assumptions, life_stage_event, event_date
                FROM forecast.forecast_projections
                WHERE forecast_id = %s
                ORDER BY period_start, scheme_code
            """, (forecast_id,))
            
            projections_data = cursor.fetchall()
            projections = []
            
            for proj_row in projections_data:
                proj_id, scheme_code, scheme_name, proj_type, period_start, period_end, period_type, benefit_amount, benefit_freq, probability, confidence, assumptions, life_stage, event_date = proj_row
                
                if scheme_code:
                    total_schemes.add(scheme_code)
                
                projections.append({
                    'projection_id': proj_id,
                    'scheme_code': scheme_code,
                    'scheme_name': scheme_name,
                    'projection_type': proj_type,
                    'period_start': period_start.isoformat() if period_start else None,
                    'period_end': period_end.isoformat() if period_end else None,
                    'period_type': period_type,
                    'benefit_amount': float(benefit_amount) if benefit_amount else 0.0,
                    'benefit_frequency': benefit_freq,
                    'probability': float(probability) if probability else 1.0,
                    'confidence_level': confidence
                })
            
            forecasts.append({
                'forecast_id': forecast_id,
                'family_id': str(family_id) if family_id else None,
                'horizon_months': horizon_months,
                'forecast_date': forecast_date.isoformat() if forecast_date else None,
                'forecast_type': forecast_type,
                'scenario_name': scenario_name,
                'status': status,
                'total_annual_value': float(total_annual) if total_annual else 0.0,
                'total_forecast_value': float(total_forecast) if total_forecast else 0.0,
                'scheme_count': scheme_count or 0,
                'uncertainty_level': uncertainty,
                'generated_at': generated_at.isoformat() if generated_at else None,
                'projections': projections
            })
            
            if total_annual:
                total_annual_value += float(total_annual)
            
            if uncertainty:
                uncertainty_levels.append(uncertainty)
        
        cursor.close()
        
        avg_uncertainty = None
        if uncertainty_levels:
            uncertainty_map = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
            avg_score = sum(uncertainty_map.get(u, 2) for u in uncertainty_levels) / len(uncertainty_levels)
            if avg_score <= 1.5:
                avg_uncertainty = 'LOW'
            elif avg_score <= 2.5:
                avg_uncertainty = 'MEDIUM'
            else:
                avg_uncertainty = 'HIGH'
        
        return jsonify({
            'forecasts': forecasts,
            'total_forecasts': len(forecasts),
            'total_schemes': len(total_schemes),
            'total_annual_value': total_annual_value,
            'avg_uncertainty': avg_uncertainty
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.disconnect()


# AI-PLATFORM-11: Personalized Communication & Nudging
NUDGE_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nudge Management Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .nav-links { margin-top: 15px; }
        .nav-links a {
            color: white;
            text-decoration: none;
            margin: 0 10px;
            padding: 5px 15px;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 5px;
            transition: background 0.3s;
        }
        .nav-links a:hover { background: rgba(255,255,255,0.2); }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }
        .stat-item {
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stat-item .number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-item .label {
            font-size: 0.9em;
            color: #6c757d;
            margin-top: 5px;
        }
        .tabs {
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
            padding: 0 20px;
        }
        .tab {
            padding: 15px 25px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
            font-weight: 500;
        }
        .tab:hover { background: #e9ecef; }
        .tab.active {
            border-bottom-color: #667eea;
            color: #667eea;
            background: white;
        }
        .tab-content {
            display: none;
            padding: 20px;
        }
        .tab-content.active { display: block; }
        .nudge-card {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .nudge-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e9ecef;
        }
        .nudge-header h3 { margin: 0; color: #333; }
        .badge {
            padding: 5px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 5px;
        }
        .status-scheduled { background: #fff3cd; color: #856404; }
        .status-sent { background: #d1ecf1; color: #0c5460; }
        .status-delivered { background: #d4edda; color: #155724; }
        .status-opened { background: #cce5ff; color: #004085; }
        .status-clicked { background: #b3d9ff; color: #003366; }
        .status-responded { background: #a3e4d7; color: #004d40; }
        .status-completed { background: #28a745; color: white; }
        .status-failed { background: #f8d7da; color: #721c24; }
        .urgency-high { background: #f8d7da; color: #721c24; }
        .urgency-critical { background: #dc3545; color: white; }
        .urgency-medium { background: #fff3cd; color: #856404; }
        .urgency-low { background: #d4edda; color: #155724; }
        .channel-sms { background: #e3f2fd; color: #1565c0; }
        .channel-app_push { background: #f3e5f5; color: #6a1b9a; }
        .channel-web_inbox { background: #e8f5e9; color: #2e7d32; }
        .channel-whatsapp { background: #e0f2f1; color: #00695c; }
        .channel-ivr { background: #fff3e0; color: #e65100; }
        .channel-assisted_visit { background: #fce4ec; color: #880e4f; }
        .nudge-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        .info-item { display: flex; flex-direction: column; }
        .info-item label {
            font-size: 0.85em;
            color: #6c757d;
            margin-bottom: 5px;
        }
        .info-item value {
            font-size: 1em;
            font-weight: 500;
            color: #333;
        }
        .nudge-content {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
            font-style: italic;
            color: #495057;
        }
        .no-data {
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }
        .no-data h3 { font-size: 1.5em; margin-bottom: 10px; }
        .refresh-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            font-size: 1em;
            transition: transform 0.2s;
        }
        .refresh-btn:hover { transform: scale(1.05); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📬 Personalized Communication & Nudging</h1>
            <p>AI-PLATFORM-11 - Nudge Management Dashboard</p>
            <div class="nav-links">
                <a href="/">Eligibility Rules</a>
                <a href="/ai04">Campaign Results</a>
                <a href="/ai05">Applications</a>
                <a href="/ai06">Decisions</a>
                <a href="/ai07">Detection</a>
                <a href="/ai08">Eligibility Checker</a>
                <a href="/ai09">Inclusion</a>
                <a href="/ai10">Forecast</a>
            </div>
        </div>
        
        <div class="stats" id="stats">
            <div class="stat-item">
                <div class="number" id="total-nudges">0</div>
                <div class="label">Total Nudges</div>
            </div>
            <div class="stat-item">
                <div class="number" id="scheduled-nudges">0</div>
                <div class="label">Scheduled</div>
            </div>
            <div class="stat-item">
                <div class="number" id="delivered-nudges">0</div>
                <div class="label">Delivered</div>
            </div>
            <div class="stat-item">
                <div class="number" id="responded-nudges">0</div>
                <div class="label">Responded</div>
            </div>
            <div class="stat-item">
                <div class="number" id="channels-used">0</div>
                <div class="label">Channels Used</div>
            </div>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('all')">All Nudges</div>
            <div class="tab" onclick="switchTab('scheduled')">Scheduled</div>
            <div class="tab" onclick="switchTab('active')">Active</div>
            <div class="tab" onclick="switchTab('completed')">Completed</div>
        </div>
        
        <div class="tab-content active" id="tab-all">
            <div id="nudges-container">
                <div class="no-data">
                    <h3>Loading nudges...</h3>
                    <p>Please wait while we fetch nudge data.</p>
                </div>
            </div>
        </div>
        
        <div class="tab-content" id="tab-scheduled">
            <div id="scheduled-container"><div class="no-data">Loading...</div></div>
        </div>
        
        <div class="tab-content" id="tab-active">
            <div id="active-container"><div class="no-data">Loading...</div></div>
        </div>
        
        <div class="tab-content" id="tab-completed">
            <div id="completed-container"><div class="no-data">Loading...</div></div>
        </div>
    </div>
    
    <button class="refresh-btn" onclick="loadNudges()">🔄 Refresh</button>
    
    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('tab-' + tabName).classList.add('active');
            loadNudges();
        }
        
        function loadNudges() {
            fetch('/ai11/api/nudges')
                .then(response => response.json())
                .then(data => {
                    updateStats(data);
                    renderNudges(data.nudges || [], 'all');
                    renderNudges(data.nudges?.filter(n => n.status === 'SCHEDULED') || [], 'scheduled');
                    renderNudges(data.nudges?.filter(n => ['SENT', 'DELIVERED', 'OPENED', 'CLICKED'].includes(n.status)) || [], 'active');
                    renderNudges(data.nudges?.filter(n => ['COMPLETED', 'RESPONDED'].includes(n.status)) || [], 'completed');
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('nudges-container').innerHTML = 
                        '<div class="no-data"><h3>Error loading nudges</h3><p>' + error.message + '</p></div>';
                });
        }
        
        function updateStats(data) {
            const nudges = data.nudges || [];
            document.getElementById('total-nudges').textContent = data.total_nudges || 0;
            document.getElementById('scheduled-nudges').textContent = nudges.filter(n => n.status === 'SCHEDULED').length;
            document.getElementById('delivered-nudges').textContent = nudges.filter(n => n.status === 'DELIVERED').length;
            document.getElementById('responded-nudges').textContent = nudges.filter(n => ['RESPONDED', 'COMPLETED'].includes(n.status)).length;
            const channels = new Set(nudges.map(n => n.channel).filter(c => c));
            document.getElementById('channels-used').textContent = channels.size;
        }
        
        function renderNudges(nudges, containerId) {
            let container;
            if (containerId === 'all') container = document.getElementById('nudges-container');
            else if (containerId === 'scheduled') container = document.getElementById('scheduled-container');
            else if (containerId === 'active') container = document.getElementById('active-container');
            else if (containerId === 'completed') container = document.getElementById('completed-container');
            else container = document.getElementById('nudges-container');
            
            if (nudges.length === 0) {
                container.innerHTML = '<div class="no-data"><h3>No nudges found</h3><p>Schedule nudges to view them here.</p></div>';
                return;
            }
            
            container.innerHTML = nudges.map(nudge => {
                const urgencyClass = 'urgency-' + (nudge.urgency?.toLowerCase() || 'medium');
                const channelClass = 'channel-' + (nudge.channel?.toLowerCase().replace('_', '_') || 'sms');
                const statusClass = 'status-' + (nudge.status?.toLowerCase() || 'scheduled');
                
                return `
                    <div class="nudge-card">
                        <div class="nudge-header">
                            <h3>${nudge.action_type?.replace('_', ' ').toUpperCase() || 'NUDGE'}</h3>
                            <div>
                                <span class="badge ${urgencyClass}">${nudge.urgency || 'MEDIUM'}</span>
                                <span class="badge ${channelClass}">${nudge.channel || 'N/A'}</span>
                                <span class="badge ${statusClass}">${nudge.status || 'SCHEDULED'}</span>
                            </div>
                        </div>
                        <div class="nudge-info">
                            <div class="info-item">
                                <label>Nudge ID</label>
                                <value>${(nudge.nudge_id || '').substring(0, 8)}...</value>
                            </div>
                            <div class="info-item">
                                <label>Family ID</label>
                                <value>${nudge.family_id || '-'}</value>
                            </div>
                            <div class="info-item">
                                <label>Scheduled Time</label>
                                <value>${nudge.scheduled_time ? new Date(nudge.scheduled_time).toLocaleString() : '-'}</value>
                            </div>
                            <div class="info-item">
                                <label>Sent At</label>
                                <value>${nudge.sent_at ? new Date(nudge.sent_at).toLocaleString() : 'Not sent yet'}</value>
                            </div>
                            <div class="info-item">
                                <label>Delivered At</label>
                                <value>${nudge.delivered_at ? new Date(nudge.delivered_at).toLocaleString() : '-'}</value>
                            </div>
                            <div class="info-item">
                                <label>Opened At</label>
                                <value>${nudge.opened_at ? new Date(nudge.opened_at).toLocaleString() : '-'}</value>
                            </div>
                            <div class="info-item">
                                <label>Responded At</label>
                                <value>${nudge.responded_at ? new Date(nudge.responded_at).toLocaleString() : '-'}</value>
                            </div>
                            <div class="info-item">
                                <label>Template</label>
                                <value>${nudge.template_name || '-'}</value>
                            </div>
                        </div>
                        ${nudge.personalized_content ? `
                            <div class="nudge-content">
                                "${nudge.personalized_content}"
                            </div>
                        ` : ''}
                    </div>
                `;
            }).join('');
        }
        
        loadNudges();
        setInterval(loadNudges, 30000);
    </script>
</body>
</html>
"""

def get_nudge_db_connection():
    """Get database connection for nudging schema"""
    try:
        db_config_path = Path(__file__).parent.parent.parent / "11_personalized_communication_nudging" / "config" / "db_config.yaml"
        if db_config_path.exists():
            with open(db_config_path, 'r') as f:
                db_config = yaml.safe_load(f)['database']
        else:
            raise FileNotFoundError
    except:
        db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
        with open(db_config_path, 'r') as f:
            db_config = yaml.safe_load(f)['database']
    
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    return db

@app.route('/ai11')
@app.route('/ai11/')
def nudge_index():
    """Main page for nudge management viewer"""
    return render_template_string(NUDGE_HTML_TEMPLATE)

@app.route('/ai11/api/nudges')
def nudge_api_nudges():
    """API endpoint for nudges"""
    db = get_nudge_db_connection()
    try:
        cursor = db.connection.cursor()
        
        cursor.execute("""
            SELECT 
                n.nudge_id, n.family_id, n.action_type, n.urgency, n.scheduled_channel,
                n.scheduled_time, n.status, n.delivery_status,
                n.sent_at, n.delivered_at, n.opened_at, n.clicked_at,
                n.responded_at, n.completed_at, n.personalized_content,
                t.template_name, t.tone
            FROM nudging.nudges n
            LEFT JOIN nudging.nudge_templates t ON n.template_id = t.template_id
            ORDER BY n.scheduled_time DESC
            LIMIT 50
        """)
        
        nudges_data = cursor.fetchall()
        
        nudges = []
        status_counts = {}
        channels_used = set()
        
        for row in nudges_data:
            nudge_id, family_id, action_type, urgency, scheduled_channel, scheduled_time, status, delivery_status, sent_at, delivered_at, opened_at, clicked_at, responded_at, completed_at, personalized_content, template_name, tone = row
            
            if scheduled_channel:
                channels_used.add(scheduled_channel)
            
            if status:
                status_counts[status] = status_counts.get(status, 0) + 1
            
            nudges.append({
                'nudge_id': str(nudge_id) if nudge_id else None,
                'family_id': family_id,
                'action_type': action_type,
                'urgency': urgency,
                'channel': scheduled_channel,
                'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
                'status': status,
                'delivery_status': delivery_status,
                'sent_at': sent_at.isoformat() if sent_at else None,
                'delivered_at': delivered_at.isoformat() if delivered_at else None,
                'opened_at': opened_at.isoformat() if opened_at else None,
                'clicked_at': clicked_at.isoformat() if clicked_at else None,
                'responded_at': responded_at.isoformat() if responded_at else None,
                'completed_at': completed_at.isoformat() if completed_at else None,
                'personalized_content': personalized_content,
                'template_name': template_name,
                'tone': tone
            })
        
        cursor.close()
        
        return jsonify({
            'nudges': nudges,
            'total_nudges': len(nudges),
            'channels_used': len(channels_used),
            'status_counts': status_counts
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
    finally:
        db.disconnect()


if __name__ == '__main__':
    print("=" * 70)
    print("SMART Platform Web Viewers")
    print("=" * 70)
    print("\n🌐 Starting web server...")
    print("📋 Available endpoints:")
    print("   Eligibility Rules:     http://localhost:5001")
    print("   Campaign Results:      http://localhost:5001/ai04")
    print("   Application Submission: http://localhost:5001/ai05")
    print("   Decision Evaluation:   http://localhost:5001/ai06")
    print("   Beneficiary Detection: http://localhost:5001/ai07")
    print("   Eligibility Checker:   http://localhost:5001/ai08")
    print("   Proactive Inclusion:   http://localhost:5001/ai09")
    print("   Benefit Forecast:      http://localhost:5001/ai10")
    print("   Nudge Management:      http://localhost:5001/ai11")
    print("\n⚠️  Press Ctrl+C to stop the server\n")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5001, debug=False)

