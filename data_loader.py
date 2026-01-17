"""
Data loader for security alerts from JSON or CSV files.
Handles normalization and validation of alert data.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any


def load_json(file_path: str) -> List[Dict[str, Any]]:
    """Load alerts from a JSON file."""
    with open(file_path, 'r') as f:
        alerts = json.load(f)
    return alerts if isinstance(alerts, list) else [alerts]


def load_csv(file_path: str) -> List[Dict[str, Any]]:
    """Load alerts from a CSV file."""
    alerts = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert frequency to int
            row['frequency'] = int(row['frequency'])
            alerts.append(row)
    return alerts


def load_alerts(file_path: str) -> List[Dict[str, Any]]:
    """
    Load alerts from JSON or CSV file based on extension.
    
    Args:
        file_path: Path to alert file (.json or .csv)
        
    Returns:
        List of normalized alert dictionaries
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Alert file not found: {file_path}")
    
    if path.suffix.lower() == '.json':
        alerts = load_json(file_path)
    elif path.suffix.lower() == '.csv':
        alerts = load_csv(file_path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")
    
    return normalize_alerts(alerts)


def normalize_alerts(alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize alert data for consistency.
    Ensures required fields exist and are in expected format.
    
    Args:
        alerts: Raw alert data
        
    Returns:
        List of normalized alerts
    """
    required_fields = {'alert_id', 'source', 'severity', 'asset_type', 'frequency', 'timestamp'}
    normalized = []
    
    for alert in alerts:
        # Check required fields
        missing = required_fields - set(alert.keys())
        if missing:
            print(f"Warning: Alert {alert.get('alert_id', '?')} missing fields: {missing}")
            continue
        
        # Normalize severity to lowercase
        alert['severity'] = alert['severity'].lower()
        
        # Ensure frequency is an integer
        try:
            alert['frequency'] = int(alert['frequency'])
        except (ValueError, TypeError):
            print(f"Warning: Alert {alert['alert_id']} has invalid frequency: {alert['frequency']}")
            continue
        
        normalized.append(alert)
    
    return normalized
