#!/usr/bin/env python3
"""
Enhanced Web Interface to View Benefit Forecasts with Advanced Features
Use Case ID: AI-PLATFORM-10
Run this script and open http://localhost:5001/ai10 in your browser
Note: This file is now enhanced - use view_forecast_web_enhanced.py for latest features
"""

import sys
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request
from datetime import datetime
import pandas as pd
import yaml
import json

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
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
    <title>Benefit Forecast Viewer - AI-PLATFORM-10</title>
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
        
        .forecast-header h2 {
            font-size: 1.5em;
        }
        
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
            fetch('/api/forecasts')
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
        
        // Load forecasts on page load
        loadForecasts();
        
        // Refresh every 30 seconds
        setInterval(loadForecasts, 30000);
    </script>
</body>
</html>
"""

@app.route('/ai10')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/forecasts')
def api_forecasts():
    """API endpoint for forecasts"""
    db = get_db_connection()
    try:
        cursor = db.connection.cursor()
        
        # Get forecast summaries
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
            
            # Get projections
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
        
        # Calculate average uncertainty
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

if __name__ == '__main__':
    print("=" * 80)
    print("Benefit Forecast Viewer - AI-PLATFORM-10")
    print("=" * 80)
    print("\n🌐 Starting web server...")
    print("📊 View forecasts at: http://localhost:5001/ai10")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Check if port 5001 is already in use (might be used by other viewers)
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 5001))
    sock.close()
    
    if result == 0:
        print("⚠️  Port 5001 is already in use.")
        print("   The viewer might already be running or another service is using this port.")
        print("   You can still access the forecast viewer if it's already running.\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False)

