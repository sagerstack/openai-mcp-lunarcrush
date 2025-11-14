"""
Test data management utilities for integration tests.

This module provides utilities for creating, managing, and cleaning up test data
used in integration tests, including fixtures for various scenarios.
"""

import os
import json
import time
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.lunarcrush_client import (
    CurrentSocialMetrics,
    MomentumMetrics,
    SocialMetrics
)


@dataclass
class TestDataScenario:
    """Data class representing a test data scenario."""
    name: str
    symbols: List[str]
    description: str
    expected_count: int
    data_variety: str  # "realistic", "edge_case", "stress_test"


class TestDataGenerator:
    """Generates test data for various integration test scenarios."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the test data generator.
        
        Args:
            seed: Random seed for reproducible test data
        """
        if seed is not None:
            random.seed(seed)
        
        self.base_symbols = ["BTC", "ETH", "ADA", "DOT", "LINK", "UNI", "AAVE", "COMP", "MKR", "SNX"]
        self.extended_symbols = [
            "BTC", "ETH", "ADA", "DOT", "LINK", "UNI", "AAVE", "COMP", "MKR", "SNX",
            "YFI", "SUSHI", "CRV", "BAL", "ZRX", "BAT", "MANA", "ENJ", "SAND", "AXS"
        ]
    
    def generate_current_metrics(self, symbol: str, variance: float = 0.2) -> CurrentSocialMetrics:
        """Generate realistic current metrics for a symbol.
        
        Args:
            symbol: Cryptocurrency symbol
            variance: Variance factor for data generation
            
        Returns:
            CurrentSocialMetrics object with realistic data
        """
        # Base values with some randomness
        base_interactions = 100000 + hash(symbol) % 200000
        base_volume = 2000 + hash(symbol) % 3000
        base_dominance = 10.0 + (hash(symbol) % 40)
        base_galaxy = 50.0 + (hash(symbol) % 40)
        base_sentiment = 40.0 + (hash(symbol) % 40)
        base_rank = 1 + (hash(symbol) % 100)
        
        # Add variance
        interactions = int(base_interactions * (1 + random.uniform(-variance, variance)))
        volume = int(base_volume * (1 + random.uniform(-variance, variance)))
        dominance = max(0, min(100, base_dominance * (1 + random.uniform(-variance, variance))))
        galaxy = max(0, min(100, base_galaxy * (1 + random.uniform(-variance, variance))))
        sentiment = max(0, min(100, base_sentiment * (1 + random.uniform(-variance, variance))))
        rank = max(1, base_rank + int(random.uniform(-10, 10)))
        
        # Previous values (slightly different from current)
        galaxy_previous = max(0, min(100, galaxy + random.uniform(-5, 5)))
        rank_previous = max(1, rank + int(random.uniform(-3, 3)))
        
        return CurrentSocialMetrics(
            symbol=symbol,
            interactions_24h=interactions,
            social_volume_24h=volume,
            social_dominance=dominance,
            galaxy_score=galaxy,
            galaxy_score_previous=galaxy_previous if random.random() > 0.1 else None,
            sentiment=sentiment,
            alt_rank=rank,
            alt_rank_previous=rank_previous if random.random() > 0.1 else None
        )
    
    def generate_momentum_metrics(self, symbol: str, current_metrics: CurrentSocialMetrics) -> MomentumMetrics:
        """Generate momentum metrics based on current metrics.
        
        Args:
            symbol: Cryptocurrency symbol
            current_metrics: Current metrics to base momentum on
            
        Returns:
            MomentumMetrics object with realistic trend data
        """
        # Generate realistic percentage changes
        interactions_trend = random.uniform(-50, 100)  # -50% to +100%
        volume_trend = random.uniform(-30, 80)  # -30% to +80%
        dominance_trend = random.uniform(-20, 40)  # -20% to +40%
        sentiment_trend = random.uniform(-15, 25)  # -15% to +25%
        
        # Galaxy score and alt rank use absolute changes
        galaxy_score_change = (
            current_metrics.galaxy_score - current_metrics.galaxy_score_previous
            if current_metrics.galaxy_score_previous is not None
            else random.uniform(-2, 5)
        )
        
        alt_rank_change = (
            current_metrics.alt_rank_previous - current_metrics.alt_rank
            if current_metrics.alt_rank_previous is not None
            else random.uniform(-5, 5)
        )
        
        return MomentumMetrics(
            symbol=symbol,
            galaxy_score_trend=galaxy_score_change,
            alt_rank_trend=alt_rank_change,
            sentiment_trend=sentiment_trend,
            interactions_trend=interactions_trend,
            social_dominance_trend=dominance_trend,
            volume_trend=volume_trend
        )
    
    def generate_social_metrics(self, symbol: str, timestamp: Optional[datetime] = None) -> SocialMetrics:
        """Generate complete social metrics for a symbol.
        
        Args:
            symbol: Cryptocurrency symbol
            timestamp: Timestamp for the metrics (defaults to now)
            
        Returns:
            SocialMetrics object with current and momentum data
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        current = self.generate_current_metrics(symbol)
        momentum = self.generate_momentum_metrics(symbol, current)
        
        return SocialMetrics(
            symbol=symbol,
            current_metrics=current,
            momentum_metrics=momentum,
            timestamp=timestamp
        )
    
    def generate_test_scenario(self, scenario: TestDataScenario) -> List[SocialMetrics]:
        """Generate test data for a specific scenario.
        
        Args:
            scenario: Test data scenario configuration
            
        Returns:
            List of SocialMetrics objects for the scenario
        """
        metrics = []
        
        for symbol in scenario.symbols:
            if scenario.data_variety == "realistic":
                metric = self.generate_social_metrics(symbol)
            elif scenario.data_variety == "edge_case":
                metric = self._generate_edge_case_metrics(symbol)
            elif scenario.data_variety == "stress_test":
                metric = self._generate_stress_test_metrics(symbol)
            else:
                metric = self.generate_social_metrics(symbol)
            
            metrics.append(metric)
        
        return metrics
    
    def _generate_edge_case_metrics(self, symbol: str) -> SocialMetrics:
        """Generate edge case metrics for testing."""
        if symbol.endswith("_MIN"):
            # Minimum values
            current = CurrentSocialMetrics(
                symbol=symbol.replace("_MIN", ""),
                interactions_24h=0,
                social_volume_24h=0,
                social_dominance=0.0,
                galaxy_score=0.0,
                sentiment=0.0,
                alt_rank=1
            )
        elif symbol.endswith("_MAX"):
            # Maximum values
            current = CurrentSocialMetrics(
                symbol=symbol.replace("_MAX", ""),
                interactions_24h=999999999,
                social_volume_24h=999999,
                social_dominance=100.0,
                galaxy_score=100.0,
                sentiment=100.0,
                alt_rank=1
            )
        elif symbol.endswith("_NULL"):
            # Null previous values
            current = CurrentSocialMetrics(
                symbol=symbol.replace("_NULL", ""),
                interactions_24h=100000,
                social_volume_24h=2000,
                social_dominance=25.0,
                galaxy_score=75.0,
                sentiment=65.0,
                alt_rank=1,
                galaxy_score_previous=None,
                alt_rank_previous=None
            )
        else:
            # Default realistic values
            current = self.generate_current_metrics(symbol)
        
        momentum = self.generate_momentum_metrics(current.symbol, current)
        
        return SocialMetrics(
            symbol=current.symbol,
            current_metrics=current,
            momentum_metrics=momentum,
            timestamp=datetime.now(timezone.utc)
        )
    
    def _generate_stress_test_metrics(self, symbol: str) -> SocialMetrics:
        """Generate stress test metrics with extreme values."""
        # Use extreme but valid values
        current = CurrentSocialMetrics(
            symbol=symbol,
            interactions_24h=random.randint(1, 10000000),  # Very high range
            social_volume_24h=random.randint(1, 100000),
            social_dominance=random.uniform(0.1, 99.9),
            galaxy_score=random.uniform(0.1, 99.9),
            sentiment=random.uniform(0.1, 99.9),
            alt_rank=random.randint(1, 1000)
        )
        
        momentum = MomentumMetrics(
            symbol=symbol,
            galaxy_score_trend=random.uniform(-50, 50),
            alt_rank_trend=random.uniform(-100, 100),
            sentiment_trend=random.uniform(-100, 100),
            interactions_trend=random.uniform(-200, 200),
            social_dominance_trend=random.uniform(-100, 100),
            volume_trend=random.uniform(-200, 200)
        )
        
        return SocialMetrics(
            symbol=symbol,
            current_metrics=current,
            momentum_metrics=momentum,
            timestamp=datetime.now(timezone.utc)
        )


class TestDataManager:
    """Manages test data for integration tests."""
    
    def __init__(self, data_dir: str = "tests/integration/data"):
        """Initialize the test data manager.
        
        Args:
            data_dir: Directory to store test data files
        """
        self.data_dir = data_dir
        self.generator = TestDataGenerator()
        self.scenarios = self._create_test_scenarios()
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
    
    def _create_test_scenarios(self) -> Dict[str, TestDataScenario]:
        """Create predefined test scenarios."""
        return {
            "basic": TestDataScenario(
                name="Basic Test",
                symbols=["BTC", "ETH", "ADA"],
                description="Basic functionality test with common symbols",
                expected_count=3,
                data_variety="realistic"
            ),
            "extended": TestDataScenario(
                name="Extended Test",
                symbols=self.generator.extended_symbols[:10],
                description="Extended test with more symbols",
                expected_count=10,
                data_variety="realistic"
            ),
            "edge_cases": TestDataScenario(
                name="Edge Cases",
                symbols=["BTC_MIN", "ETH_MAX", "ADA_NULL"],
                description="Edge case testing with boundary values",
                expected_count=3,
                data_variety="edge_case"
            ),
            "stress_test": TestDataScenario(
                name="Stress Test",
                symbols=[f"STRESS{i}" for i in range(20)],
                description="Stress test with many symbols and extreme values",
                expected_count=20,
                data_variety="stress_test"
            ),
            "single_symbol": TestDataScenario(
                name="Single Symbol",
                symbols=["BTC"],
                description="Single symbol test",
                expected_count=1,
                data_variety="realistic"
            ),
            "invalid_symbols": TestDataScenario(
                name="Invalid Symbols",
                symbols=["INVALID123", "FAKECOIN", "NONEXISTENT"],
                description="Test with invalid/non-existent symbols",
                expected_count=0,
                data_variety="realistic"
            )
        }
    
    def get_scenario(self, scenario_name: str) -> TestDataScenario:
        """Get a test scenario by name.
        
        Args:
            scenario_name: Name of the scenario
            
        Returns:
            TestDataScenario object
        """
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        return self.scenarios[scenario_name]
    
    def generate_scenario_data(self, scenario_name: str) -> List[SocialMetrics]:
        """Generate test data for a scenario.
        
        Args:
            scenario_name: Name of the scenario
            
        Returns:
            List of SocialMetrics objects
        """
        scenario = self.get_scenario(scenario_name)
        return self.generator.generate_test_scenario(scenario)
    
    def save_scenario_data(self, scenario_name: str, filename: Optional[str] = None) -> str:
        """Save scenario data to JSON file.
        
        Args:
            scenario_name: Name of the scenario
            filename: Optional custom filename
            
        Returns:
            Path to the saved file
        """
        metrics = self.generate_scenario_data(scenario_name)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{scenario_name}_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        # Convert to JSON-serializable format
        data = {
            "scenario": scenario_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": [metric.to_dict() for metric in metrics]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return filepath
    
    def load_scenario_data(self, filepath: str) -> Dict[str, Any]:
        """Load scenario data from JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Dictionary containing the scenario data
        """
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def create_lambda_event(self, scenario_name: str, **kwargs) -> Dict[str, Any]:
        """Create a Lambda event for testing.
        
        Args:
            scenario_name: Name of the scenario
            **kwargs: Additional event parameters
            
        Returns:
            Lambda event dictionary
        """
        scenario = self.get_scenario(scenario_name)
        
        event = {
            "body": json.dumps({
                "symbols": scenario.symbols,
                "parameters": {
                    "scenario": scenario_name,
                    "description": scenario.description,
                    **kwargs
                }
            }),
            "httpMethod": "POST",
            "headers": {
                "Content-Type": "application/json"
            }
        }
        
        return event
    
    def cleanup_test_data(self, older_than_hours: int = 24) -> int:
        """Clean up old test data files.
        
        Args:
            older_than_hours: Remove files older than this many hours
            
        Returns:
            Number of files removed
        """
        if not os.path.exists(self.data_dir):
            return 0
        
        cutoff_time = time.time() - (older_than_hours * 3600)
        removed_count = 0
        
        for filename in os.listdir(self.data_dir):
            filepath = os.path.join(self.data_dir, filename)
            
            if os.path.isfile(filepath):
                file_time = os.path.getmtime(filepath)
                
                if file_time < cutoff_time:
                    try:
                        os.remove(filepath)
                        removed_count += 1
                    except OSError:
                        pass  # Ignore removal errors
        
        return removed_count
    
    def validate_test_data(self, metrics: List[SocialMetrics]) -> Dict[str, Any]:
        """Validate test data for correctness.
        
        Args:
            metrics: List of SocialMetrics to validate
            
        Returns:
            Validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "statistics": {
                "total_symbols": len(metrics),
                "unique_symbols": len(set(m.symbol for m in metrics)),
                "avg_interactions": 0,
                "avg_volume": 0,
                "avg_dominance": 0
            }
        }
        
        if not metrics:
            results["errors"].append("No metrics provided")
            results["valid"] = False
            return results
        
        total_interactions = 0
        total_volume = 0
        total_dominance = 0
        
        for metric in metrics:
            try:
                # Validate current metrics
                metric.current_metrics._validate_data()
                
                # Validate momentum metrics
                metric.momentum_metrics._validate_data()
                
                # Validate social metrics
                metric._validate_data()
                
                # Accumulate statistics
                total_interactions += metric.current_metrics.interactions_24h
                total_volume += metric.current_metrics.social_volume_24h
                total_dominance += metric.current_metrics.social_dominance
                
            except Exception as e:
                results["errors"].append(f"Validation error for {metric.symbol}: {e}")
                results["valid"] = False
        
        # Calculate averages
        if metrics:
            results["statistics"]["avg_interactions"] = total_interactions / len(metrics)
            results["statistics"]["avg_volume"] = total_volume / len(metrics)
            results["statistics"]["avg_dominance"] = total_dominance / len(metrics)
        
        # Check for warnings
        if results["statistics"]["unique_symbols"] != results["statistics"]["total_symbols"]:
            results["warnings"].append("Duplicate symbols found")
        
        return results


# Global instance for easy access
test_data_manager = TestDataManager()


def get_test_scenario(scenario_name: str) -> TestDataScenario:
    """Get a test scenario by name.
    
    Args:
        scenario_name: Name of the scenario
        
    Returns:
        TestDataScenario object
    """
    return test_data_manager.get_scenario(scenario_name)


def generate_test_metrics(scenario_name: str) -> List[SocialMetrics]:
    """Generate test metrics for a scenario.
    
    Args:
        scenario_name: Name of the scenario
        
    Returns:
        List of SocialMetrics objects
    """
    return test_data_manager.generate_scenario_data(scenario_name)


def create_test_event(scenario_name: str, **kwargs) -> Dict[str, Any]:
    """Create a test Lambda event.
    
    Args:
        scenario_name: Name of the scenario
        **kwargs: Additional event parameters
        
    Returns:
        Lambda event dictionary
    """
    return test_data_manager.create_lambda_event(scenario_name, **kwargs)


def save_test_data(scenario_name: str, filename: Optional[str] = None) -> str:
    """Save test data to file.
    
    Args:
        scenario_name: Name of the scenario
        filename: Optional custom filename
        
    Returns:
        Path to the saved file
    """
    return test_data_manager.save_scenario_data(scenario_name, filename)


def cleanup_old_test_data(older_than_hours: int = 24) -> int:
    """Clean up old test data files.
    
    Args:
        older_than_hours: Remove files older than this many hours
        
    Returns:
        Number of files removed
    """
    return test_data_manager.cleanup_test_data(older_than_hours)