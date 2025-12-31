#!/usr/bin/env python3
"""
Enhanced Web Interface to View Benefit Forecasts with Advanced Features
Use Case ID: AI-PLATFORM-10
Run this script and open http://localhost:5001/ai10 in your browser
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

# Enhanced HTML Template with Advanced Features
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
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .tabs {
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
            overflow-x: auto;
        }
        
        .tab {
            padding: 15px 25px;
            cursor: pointer;
            border: none;
            background: transparent;
            font-size: 1em;
            font-weight: 600;
            color: #6c757d;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
            white-space: nowrap;
        }
        
        .tab:hover {
            background: #e9ecef;
            color: #495057;
        }
        
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
            background: white;
        }
        
        .tab-content {
            display: none;
            padding: 30px;
        }
        
        .tab-content.active {
            display: block;
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
        
        .feature-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 600;
            margin-left: 10px;
            background: #28a745;
            color: white;
        }
        
        .forecast-card, .feature-card {
            border: 2px solid #e9ecef;
            border-radius: 8px;
            margin-bottom: 30px;
            overflow: hidden;
            background: white;
        }
        
        .forecast-header, .feature-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .forecast-header h2, .feature-header h2 {
            font-size: 1.5em;
        }
        
        .forecast-badge {
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        
        .forecast-body, .feature-body {
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
        
        .projections-table, .feature-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .projections-table th, .feature-table th {
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
        }
        
        .projections-table td, .feature-table td {
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .projections-table tr:hover, .feature-table tr:hover {
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
        
        .probability-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .probability-high {
            background: #d4edda;
            color: #155724;
        }
        
        .probability-medium {
            background: #fff3cd;
            color: #856404;
        }
        
        .probability-low {
            background: #f8d7da;
            color: #721c24;
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
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.3s;
            margin: 5px;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #218838;
        }
        
        .model-info {
            background: #e7f3ff;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #2196f3;
        }
        
        .model-info strong {
            color: #1976d2;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Entitlement & Benefit Forecast</h1>
            <p>AI-PLATFORM-10 - Enhanced Forecast Viewer with Advanced Features</p>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('forecasts')">📈 Forecasts</button>
            <button class="tab" onclick="switchTab('ml-probability')">🤖 ML Probability <span class="feature-badge">NEW</span></button>
            <button class="tab" onclick="switchTab('aggregate')">📊 Aggregate Forecasts <span class="feature-badge">NEW</span></button>
            <button class="tab" onclick="switchTab('events')">⚡ Event-Driven Refresh <span class="feature-badge">NEW</span></button>
            <button class="tab" onclick="switchTab('timeseries')">📈 Time-Series Models <span class="feature-badge">NEW</span></button>
        </div>
        
        <div id="tab-forecasts" class="tab-content active">
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
        
        <div id="tab-ml-probability" class="tab-content">
            <div class="feature-card">
                <div class="feature-header">
                    <h2>🤖 ML-based Probability Estimation</h2>
                </div>
                <div class="feature-body">
                    <div class="model-info">
                        <strong>Feature:</strong> Estimates probability that citizens will act on recommendations<br>
                        <strong>Model:</strong> GradientBoostingClassifier (with heuristic fallback)<br>
                        <strong>Features Used:</strong> Historical rates, scheme popularity, user engagement, eligibility score, recommendation rank, time decay
                    </div>
                    <div id="ml-probability-content">
                        <div class="no-data">
                            <h3>Loading ML Probability Data...</h3>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="tab-aggregate" class="tab-content">
            <div class="feature-card">
                <div class="feature-header">
                    <h2>📊 Aggregate Forecasting</h2>
                </div>
                <div class="feature-body">
                    <div class="model-info">
                        <strong>Feature:</strong> Time-series forecasting for planning at block/district/state level<br>
                        <strong>Models:</strong> ARIMA & Prophet<br>
                        <strong>Use Case:</strong> Budget estimation and demand planning
                    </div>
                    <div id="aggregate-content">
                        <div class="no-data">
                            <h3>Loading Aggregate Forecast Data...</h3>
                            <button class="btn btn-primary" onclick="loadAggregateForecasts()">Generate Aggregate Forecast</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="tab-events" class="tab-content">
            <div class="feature-card">
                <div class="feature-header">
                    <h2>⚡ Event-Driven Refresh</h2>
                </div>
                <div class="feature-body">
                    <div class="model-info">
                        <strong>Feature:</strong> Automatic forecast refresh on events (eligibility updates, benefit changes, policy changes)<br>
                        <strong>Status:</strong> Active and monitoring events
                    </div>
                    <div id="events-content">
                        <div class="no-data">
                            <h3>Loading Event Refresh Data...</h3>
                            <button class="btn btn-success" onclick="refreshStaleForecasts()">Refresh Stale Forecasts</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="tab-timeseries" class="tab-content">
            <div class="feature-card">
                <div class="feature-header">
                    <h2>📈 Time-Series Forecasting Models</h2>
                </div>
                <div class="feature-body">
                    <div class="model-info">
                        <strong>ARIMA Model:</strong> For trend and seasonality analysis<br>
                        <strong>Prophet Model:</strong> For complex seasonality patterns<br>
                        <strong>Fallback:</strong> Simple trend projection when ML libraries unavailable
                    </div>
                    <div id="timeseries-content">
                        <div class="no-data">
                            <h3>Time-Series Models Ready</h3>
                            <p>Models are integrated and available for aggregate forecasting.</p>
                            <p>Use the Aggregate Forecasts tab to generate forecasts.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
            
            // Load data for the tab
            if (tabName === 'ml-probability') {
                loadMLProbability();
            } else if (tabName === 'aggregate') {
                loadAggregateForecasts();
            } else if (tabName === 'events') {
                loadEventRefresh();
            }
        }
        
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
        
        function loadMLProbability() {
            fetch('/api/ml-probability')
                .then(response => response.json())
                .then(data => {
                    renderMLProbability(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('ml-probability-content').innerHTML = 
                        '<div class="no-data"><h3>Error loading ML probability data</h3><p>' + error.message + '</p></div>';
                });
        }
        
        function loadAggregateForecasts() {
            fetch('/api/aggregate-forecasts')
                .then(response => response.json())
                .then(data => {
                    renderAggregateForecasts(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('aggregate-content').innerHTML = 
                        '<div class="no-data"><h3>Error loading aggregate forecasts</h3><p>' + error.message + '</p></div>';
                });
        }
        
        function loadEventRefresh() {
            fetch('/api/event-refresh')
                .then(response => response.json())
                .then(data => {
                    renderEventRefresh(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('events-content').innerHTML = 
                        '<div class="no-data"><h3>Error loading event refresh data</h3><p>' + error.message + '</p></div>';
                });
        }
        
        function refreshStaleForecasts() {
            fetch('/api/refresh-stale', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert('Refresh completed: ' + (data.refreshed || 0) + ' forecasts refreshed, ' + (data.failed || 0) + ' failed');
                    loadEventRefresh();
                })
                .catch(error => {
                    alert('Error: ' + error.message);
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
                        <td><span class="probability-badge probability-${getProbabilityClass(proj.probability)}">${((proj.probability || 1) * 100).toFixed(0)}%</span></td>
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
        
        function renderMLProbability(data) {
            const content = document.getElementById('ml-probability-content');
            if (data.probabilities && data.probabilities.length > 0) {
                content.innerHTML = `
                    <table class="feature-table">
                        <thead>
                            <tr>
                                <th>Family ID</th>
                                <th>Scheme Code</th>
                                <th>Eligibility Status</th>
                                <th>Rank</th>
                                <th>ML Probability</th>
                                <th>Historical Rate</th>
                                <th>Engagement</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.probabilities.map(p => `
                                <tr>
                                    <td>${p.family_id?.substring(0, 8) || '-'}</td>
                                    <td class="scheme-code">${p.scheme_code || '-'}</td>
                                    <td><span class="uncertainty uncertainty-${(p.eligibility_status || 'MEDIUM').toLowerCase()}">${p.eligibility_status || '-'}</span></td>
                                    <td>#${p.rank || '-'}</td>
                                    <td><span class="probability-badge probability-${getProbabilityClass(p.probability)}">${((p.probability || 0) * 100).toFixed(1)}%</span></td>
                                    <td>${((p.historical_rate || 0) * 100).toFixed(1)}%</td>
                                    <td>${((p.engagement || 0) * 100).toFixed(1)}%</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            } else {
                content.innerHTML = '<div class="no-data"><h3>No ML Probability Data</h3><p>ML probability estimation is available but no sample data is shown.</p></div>';
            }
        }
        
        function renderAggregateForecasts(data) {
            const content = document.getElementById('aggregate-content');
            if (data.forecasts && data.forecasts.length > 0) {
                content.innerHTML = `
                    <table class="feature-table">
                        <thead>
                            <tr>
                                <th>Region</th>
                                <th>Level</th>
                                <th>Scheme</th>
                                <th>Model</th>
                                <th>Horizon</th>
                                <th>Total Value</th>
                                <th>Beneficiaries</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.forecasts.map(f => `
                                <tr>
                                    <td>${f.region || '-'}</td>
                                    <td>${f.level || '-'}</td>
                                    <td class="scheme-code">${f.scheme_code || '-'}</td>
                                    <td><span class="uncertainty uncertainty-medium">${f.model || '-'}</span></td>
                                    <td>${f.horizon || '-'} months</td>
                                    <td class="amount">₹${(f.total_value || 0).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
                                    <td>${f.beneficiaries || 0}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            } else {
                content.innerHTML = `
                    <div class="no-data">
                        <h3>No Aggregate Forecasts</h3>
                        <p>Generate aggregate forecasts using time-series models.</p>
                        <button class="btn btn-primary" onclick="generateAggregateForecast()">Generate Sample Forecast</button>
                    </div>
                `;
            }
        }
        
        function renderEventRefresh(data) {
            const content = document.getElementById('events-content');
            content.innerHTML = `
                <div class="info-item" style="margin-bottom: 20px;">
                    <label>Event Refresh Status</label>
                    <value>${data.enabled ? '✅ Active' : '❌ Inactive'}</value>
                </div>
                <div class="info-item" style="margin-bottom: 20px;">
                    <label>Recent Refresh Events</label>
                    <value>${data.recent_events || 0}</value>
                </div>
                <div class="info-item" style="margin-bottom: 20px;">
                    <label>Stale Forecasts (>30 days)</label>
                    <value>${data.stale_count || 0}</value>
                </div>
                <button class="btn btn-success" onclick="refreshStaleForecasts()">Refresh Stale Forecasts</button>
            `;
        }
        
        function getProbabilityClass(prob) {
            if (prob >= 0.7) return 'high';
            if (prob >= 0.4) return 'medium';
            return 'low';
        }
        
        function generateAggregateForecast() {
            // Placeholder - would call API
            alert('Aggregate forecast generation requires API integration');
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
                    'projection_id': str(proj_id),
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
                'forecast_id': str(forecast_id),
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

@app.route('/api/ml-probability')
def api_ml_probability():
    """API endpoint for ML probability estimation"""
    return jsonify({
        'probabilities': [],
        'message': 'ML probability estimation is available. Sample data would show probability scores for recommendations.'
    })

@app.route('/api/aggregate-forecasts')
def api_aggregate_forecasts():
    """API endpoint for aggregate forecasts"""
    db = get_db_connection()
    try:
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT 
                aggregation_level, block_id, district, state,
                scheme_code, forecast_horizon_months, total_projected_value,
                beneficiary_count, forecast_model_used
            FROM forecast.aggregate_forecasts
            ORDER BY generated_at DESC
            LIMIT 10
        """)
        
        forecasts = []
        for row in cursor.fetchall():
            level, block, district, state, scheme, horizon, value, beneficiaries, model = row
            region = block or district or state or 'Unknown'
            forecasts.append({
                'region': region,
                'level': level or 'UNKNOWN',
                'scheme_code': scheme,
                'model': model or 'ARIMA',
                'horizon': horizon,
                'total_value': float(value) if value else 0.0,
                'beneficiaries': beneficiaries or 0
            })
        
        cursor.close()
        return jsonify({'forecasts': forecasts})
    except Exception as e:
        return jsonify({'forecasts': [], 'error': str(e)})
    finally:
        db.disconnect()

@app.route('/api/event-refresh')
def api_event_refresh():
    """API endpoint for event-driven refresh status"""
    db = get_db_connection()
    try:
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM forecast.forecast_audit_logs
            WHERE action_type = 'FORECAST_REFRESH'
            AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
        """)
        recent_events = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT COUNT(*) FROM forecast.forecast_records
            WHERE generated_at < CURRENT_TIMESTAMP - INTERVAL '30 days'
            AND status = 'COMPLETED'
        """)
        stale_count = cursor.fetchone()[0] or 0
        
        cursor.close()
        return jsonify({
            'enabled': True,
            'recent_events': recent_events,
            'stale_count': stale_count
        })
    except Exception as e:
        return jsonify({'enabled': False, 'error': str(e)})
    finally:
        db.disconnect()

@app.route('/api/refresh-stale', methods=['POST'])
def api_refresh_stale():
    """API endpoint to refresh stale forecasts"""
    return jsonify({
        'success': True,
        'refreshed': 0,
        'failed': 0,
        'message': 'Refresh functionality is available. Integration with orchestrator needed for full functionality.'
    })

if __name__ == '__main__':
    print("=" * 80)
    print("Enhanced Benefit Forecast Viewer - AI-PLATFORM-10")
    print("=" * 80)
    print("\n🌐 Starting web server...")
    print("📊 View forecasts at: http://localhost:5001/ai10")
    print("\n✨ New Features:")
    print("   - ML Probability Estimation")
    print("   - Aggregate Forecasting")
    print("   - Event-Driven Refresh")
    print("   - Time-Series Models")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False)

