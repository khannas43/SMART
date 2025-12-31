#!/usr/bin/env python3
"""
Web Interface for Viewing Intimation Campaign Results
Flask application to display campaigns, candidates, messages, and consents in a browser
"""

import sys
from pathlib import Path
import yaml
import pandas as pd
from datetime import datetime
from flask import Flask, render_template_string, jsonify

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

app = Flask(__name__)

# Load database configuration
CONFIG_PATH = Path(__file__).parent.parent / "config" / "db_config.yaml"
with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)

db_config = config['database']
db = DBConnector(
    host=db_config['host'],
    port=db_config['port'],
    database=db_config['name'],
    user=db_config['user'],
    password=db_config['password']
)

# HTML Template
HTML_TEMPLATE = """
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
def index():
    """Main page displaying all campaign results"""
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
            if pd.notna(campaign['created_at']):
                campaign['created_at'] = campaign['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        for message in messages:
            if pd.notna(message['created_at']):
                message['created_at'] = message['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        for consent in consents:
            if pd.notna(consent['created_at']):
                consent['created_at'] = consent['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return render_template_string(
            HTML_TEMPLATE,
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
            HTML_TEMPLATE,
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
def api_stats():
    """API endpoint for statistics"""
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


if __name__ == '__main__':
    print("=" * 60)
    print("Intimation Campaign Results Web Viewer")
    print("=" * 60)
    print("\nStarting Flask server...")
    print("Access the web interface at: http://127.0.0.1:5001/ai04")
    print("Main Eligibility Rules Viewer: http://127.0.0.1:5001")
    print("Press Ctrl+C to stop the server\n")
    
    app.run(host='127.0.0.1', port=5001, debug=True)

