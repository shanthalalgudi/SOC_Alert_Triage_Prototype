"""
Risk scoring engine for SOC alerts.
Computes a risk score based on severity, asset type, and frequency.
"""

from typing import Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class ScoredAlert:
    """Alert with computed risk score and priority."""
    alert: Dict[str, Any]
    risk_score: float
    priority: str
    explanation: str


class ScoringEngine:
    """Computes risk scores for security alerts."""
    
    def __init__(self, severity_weights: Dict[str, float] = None,
                 asset_weights: Dict[str, float] = None,
                 frequency_factor: float = 0.1,
                 risk_threshold: float = 60.0):
        """
        Initialize scoring engine with configurable weights.
        
        Args:
            severity_weights: Weight for each severity level (0-100 scale)
            asset_weights: Weight for each asset type (0-100 scale)
            frequency_factor: Multiplier for alert frequency
            risk_threshold: Score threshold for "Critical" classification
        """
        self.severity_weights = severity_weights or {
            'low': 20,
            'medium': 50,
            'high': 90
        }
        
        self.asset_weights = asset_weights or {
            'standard': 10,
            'important': 50,
            'critical': 100
        }
        
        self.frequency_factor = frequency_factor
        self.risk_threshold = risk_threshold
    
    def score_alert(self, alert: Dict[str, Any]) -> ScoredAlert:
        """
        Compute risk score for a single alert.
        
        Score formula: (severity_weight + asset_weight) / 2 + (frequency * frequency_factor)
        
        Args:
            alert: Alert dictionary with required fields
            
        Returns:
            ScoredAlert with score, priority, and explanation
        """
        severity = alert['severity'].lower()
        asset_type = alert['asset_type'].lower()
        frequency = alert['frequency']
        
        # Get weights (default to 0 if unknown)
        severity_weight = self.severity_weights.get(severity, 0)
        asset_weight = self.asset_weights.get(asset_type, 0)
        
        # Calculate risk score
        base_score = (severity_weight + asset_weight) / 2
        frequency_boost = frequency * self.frequency_factor
        risk_score = min(100, base_score + frequency_boost)  # Cap at 100
        
        # Determine priority
        if risk_score >= self.risk_threshold:
            priority = "Critical"
        elif risk_score >= 40:
            priority = "High"
        elif risk_score >= 20:
            priority = "Medium"
        else:
            priority = "Low"
        
        # Generate explanation
        explanation = self._generate_explanation(alert, severity_weight, asset_weight, frequency_boost)
        
        return ScoredAlert(
            alert=alert,
            risk_score=risk_score,
            priority=priority,
            explanation=explanation
        )
    
    def _generate_explanation(self, alert: Dict[str, Any], 
                            severity_weight: float, 
                            asset_weight: float,
                            frequency_boost: float) -> str:
        """Generate a human-readable explanation for the score."""
        factors = []
        
        if severity_weight >= 80:
            factors.append("high severity")
        elif severity_weight >= 40:
            factors.append("medium severity")
        
        if asset_weight >= 80:
            factors.append("critical asset")
        elif asset_weight >= 40:
            factors.append("important asset")
        
        if alert['frequency'] >= 3:
            factors.append(f"high frequency ({alert['frequency']} occurrences)")
        
        if not factors:
            return "Low-risk alert"
        
        return f"Alert triggered due to {', '.join(factors)}"
    
    def score_alerts(self, alerts: list) -> list:
        """
        Score multiple alerts and return sorted by risk.
        
        Args:
            alerts: List of alert dictionaries
            
        Returns:
            List of ScoredAlert objects sorted by risk_score (descending)
        """
        scored = [self.score_alert(alert) for alert in alerts]
        return sorted(scored, key=lambda x: x.risk_score, reverse=True)
