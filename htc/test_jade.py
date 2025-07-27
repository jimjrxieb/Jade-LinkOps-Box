#!/usr/bin/env python3
"""
Jade Property Management Evaluation Framework
=============================================

Tests and benchmarks Jade's property management reasoning after fine-tuning.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class JadePropertyEvaluator:
    """
    Evaluation framework for Jade property management capabilities.
    """

    def __init__(self, model_path: str = "./models/jade-property-lora"):
        """Initialize evaluator."""
        self.model_path = Path(model_path)
        self.test_results = []
        self.evaluation_metrics = {}
        
        # Load test scenarios
        self.test_scenarios = self._load_test_scenarios()

    def _load_test_scenarios(self) -> List[Dict]:
        """Load property management test scenarios."""
        scenarios = [
            {
                "category": "rent_collection",
                "scenario": "Tenant Tony Stark in unit 401 is 7 days late on $2500 rent",
                "expected_actions": ["email_late_notice", "apply_late_fee", "log_delinquency"],
                "expected_command": "email_late_notice --tenant 'Tony Stark' --unit '401' --amount_due 2500 --days_late 7",
                "complexity": "medium",
                "urgency": "medium"
            },
            {
                "category": "emergency_maintenance", 
                "scenario": "Water leak reported in unit 303, tenant says it's flooding",
                "expected_actions": ["emergency_dispatch", "notify_maintenance", "document_incident"],
                "expected_command": "emergency_dispatch --unit 303 --type 'water_leak' --priority emergency --response_time '2 hours'",
                "complexity": "high",
                "urgency": "high"
            },
            {
                "category": "lease_renewal",
                "scenario": "Jane Smith's lease expires in 30 days, current rent $1800, market rate $1950",
                "expected_actions": ["market_analysis", "renewal_offer", "schedule_discussion"],
                "expected_command": "lease_renewal --tenant 'Jane Smith' --current_rent 1800 --new_rate 1950 --lease_term 12",
                "complexity": "medium",
                "urgency": "medium"
            },
            {
                "category": "vendor_selection",
                "scenario": "HVAC system failed in Building A, need emergency repair under $5000",
                "expected_actions": ["vendor_search", "emergency_approval", "schedule_repair"],
                "expected_command": "vendor_recommend --type HVAC --building 'Building A' --urgency emergency --budget_max 5000",
                "complexity": "high",
                "urgency": "high"
            },
            {
                "category": "compliance",
                "scenario": "Annual fire safety inspection due for all units by March 31st",
                "expected_actions": ["schedule_inspection", "notify_tenants", "prepare_documentation"],
                "expected_command": "schedule_inspection --type fire_safety --scope all_units --deadline '2025-03-31'",
                "complexity": "low",
                "urgency": "low"
            },
            {
                "category": "tenant_communication",
                "scenario": "New tenant John Doe needs move-in packet and orientation",
                "expected_actions": ["prepare_packet", "schedule_orientation", "setup_portal_access"],
                "expected_command": "new_tenant_setup --name 'John Doe' --move_in_date '2025-02-01' --unit 205",
                "complexity": "low",
                "urgency": "medium"
            },
            {
                "category": "financial_reporting",
                "scenario": "Generate monthly financial report with variance analysis for January",
                "expected_actions": ["compile_data", "calculate_variance", "generate_report"],
                "expected_command": "generate_financial_report --period 'January 2025' --include_variance true --format pdf",
                "complexity": "medium",
                "urgency": "low"
            }
        ]
        
        return scenarios

    def evaluate_response_accuracy(self, generated_response: str, expected_command: str) -> float:
        """Evaluate accuracy of generated command against expected."""
        # Simple similarity check - can be enhanced with more sophisticated NLP
        generated_clean = generated_response.lower().strip()
        expected_clean = expected_command.lower().strip()
        
        # Check if key components are present
        expected_parts = expected_clean.split()
        matches = sum(1 for part in expected_parts if part in generated_clean)
        
        accuracy = matches / len(expected_parts) if expected_parts else 0
        return min(accuracy, 1.0)

    def evaluate_action_relevance(self, generated_response: str, expected_actions: List[str]) -> float:
        """Evaluate if response includes relevant actions."""
        response_lower = generated_response.lower()
        action_matches = sum(1 for action in expected_actions if action.replace('_', ' ') in response_lower)
        
        relevance = action_matches / len(expected_actions) if expected_actions else 0
        return min(relevance, 1.0)

    def evaluate_urgency_handling(self, generated_response: str, urgency: str) -> float:
        """Evaluate if response appropriately handles urgency."""
        response_lower = generated_response.lower()
        
        urgency_keywords = {
            "high": ["emergency", "urgent", "immediate", "asap", "priority"],
            "medium": ["soon", "timely", "scheduled", "planned"],
            "low": ["routine", "regular", "standard", "when convenient"]
        }
        
        expected_keywords = urgency_keywords.get(urgency, [])
        keyword_matches = sum(1 for keyword in expected_keywords if keyword in response_lower)
        
        return min(keyword_matches / len(expected_keywords) if expected_keywords else 0.5, 1.0)

    def run_evaluation(self) -> Dict:
        """Run comprehensive evaluation on all test scenarios."""
        logger.info("Starting Jade property management evaluation...")
        
        total_scenarios = len(self.test_scenarios)
        results = {
            "accuracy_scores": [],
            "relevance_scores": [],
            "urgency_scores": [],
            "category_performance": {},
            "overall_metrics": {}
        }
        
        for i, scenario in enumerate(self.test_scenarios, 1):
            logger.info(f"Evaluating scenario {i}/{total_scenarios}: {scenario['category']}")
            
            # Simulate Jade response (replace with actual model inference)
            generated_response = self._simulate_jade_response(scenario)
            
            # Calculate metrics
            accuracy = self.evaluate_response_accuracy(
                generated_response, scenario["expected_command"]
            )
            relevance = self.evaluate_action_relevance(
                generated_response, scenario["expected_actions"]
            )
            urgency = self.evaluate_urgency_handling(
                generated_response, scenario["urgency"]
            )
            
            # Store results
            test_result = {
                "scenario": scenario["scenario"],
                "category": scenario["category"],
                "complexity": scenario["complexity"],
                "urgency": scenario["urgency"],
                "generated_response": generated_response,
                "expected_command": scenario["expected_command"],
                "accuracy_score": accuracy,
                "relevance_score": relevance,
                "urgency_score": urgency,
                "overall_score": (accuracy + relevance + urgency) / 3,
                "timestamp": datetime.now().isoformat()
            }
            
            self.test_results.append(test_result)
            results["accuracy_scores"].append(accuracy)
            results["relevance_scores"].append(relevance)
            results["urgency_scores"].append(urgency)
            
            # Track category performance
            category = scenario["category"]
            if category not in results["category_performance"]:
                results["category_performance"][category] = []
            results["category_performance"][category].append(test_result["overall_score"])
        
        # Calculate overall metrics
        results["overall_metrics"] = {
            "mean_accuracy": sum(results["accuracy_scores"]) / len(results["accuracy_scores"]),
            "mean_relevance": sum(results["relevance_scores"]) / len(results["relevance_scores"]),
            "mean_urgency": sum(results["urgency_scores"]) / len(results["urgency_scores"]),
            "overall_performance": sum(r["overall_score"] for r in self.test_results) / len(self.test_results),
            "total_scenarios": total_scenarios,
            "evaluation_date": datetime.now().isoformat()
        }
        
        # Category averages
        for category, scores in results["category_performance"].items():
            results["category_performance"][category] = {
                "scores": scores,
                "average": sum(scores) / len(scores),
                "count": len(scores)
            }
        
        self.evaluation_metrics = results
        logger.info("Evaluation complete!")
        
        return results

    def _simulate_jade_response(self, scenario: Dict) -> str:
        """
        Simulate Jade response for testing.
        Replace this with actual model inference when model is available.
        """
        # This is a placeholder - replace with actual model inference
        category = scenario["category"]
        
        if category == "rent_collection":
            return "email_late_notice --tenant 'Tony Stark' --unit '401' --amount_due 2500 --days_late 7 --template late_notice_7days"
        elif category == "emergency_maintenance":
            return "emergency_dispatch --unit 303 --type 'water_leak' --priority emergency --notify_manager true --response_time '2 hours'"
        elif category == "lease_renewal":
            return "lease_renewal --tenant 'Jane Smith' --current_rent 1800 --new_rate 1950 --lease_term 12 --send_notice true"
        elif category == "vendor_selection":
            return "vendor_recommend --type HVAC --building 'Building A' --urgency emergency --budget_max 5000 --approval_required true"
        elif category == "compliance":
            return "schedule_inspection --type fire_safety --scope all_units --deadline '2025-03-31' --notify_tenants true"
        elif category == "tenant_communication":
            return "new_tenant_setup --name 'John Doe' --move_in_date '2025-02-01' --unit 205 --packet_type standard"
        elif category == "financial_reporting":
            return "generate_financial_report --period 'January 2025' --include_variance true --format pdf --distribution owners"
        else:
            return "Unknown command for scenario"

    def generate_report(self, output_file: str = "jade_evaluation_report.json"):
        """Generate detailed evaluation report."""
        if not self.evaluation_metrics:
            logger.warning("No evaluation data available. Run evaluation first.")
            return
        
        report = {
            "evaluation_summary": self.evaluation_metrics["overall_metrics"],
            "category_performance": self.evaluation_metrics["category_performance"],
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Evaluation report saved to: {output_file}")
        
        # Print summary
        self._print_summary()

    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations based on evaluation."""
        recommendations = []
        metrics = self.evaluation_metrics["overall_metrics"]
        
        if metrics["mean_accuracy"] < 0.8:
            recommendations.append("Consider additional fine-tuning with more command examples")
        
        if metrics["mean_relevance"] < 0.7:
            recommendations.append("Expand training data with more diverse property management scenarios")
        
        if metrics["mean_urgency"] < 0.6:
            recommendations.append("Include more urgency-specific training examples and keywords")
        
        # Category-specific recommendations
        for category, data in self.evaluation_metrics["category_performance"].items():
            if data["average"] < 0.7:
                recommendations.append(f"Improve {category} handling with targeted training data")
        
        if not recommendations:
            recommendations.append("Performance is good! Consider testing with more complex scenarios")
        
        return recommendations

    def _print_summary(self):
        """Print evaluation summary to console."""
        metrics = self.evaluation_metrics["overall_metrics"]
        
        print("\n" + "="*60)
        print("JADE PROPERTY MANAGEMENT EVALUATION SUMMARY")
        print("="*60)
        print(f"Overall Performance: {metrics['overall_performance']:.2%}")
        print(f"Accuracy Score:      {metrics['mean_accuracy']:.2%}")
        print(f"Relevance Score:     {metrics['mean_relevance']:.2%}")
        print(f"Urgency Handling:    {metrics['mean_urgency']:.2%}")
        print(f"Total Scenarios:     {metrics['total_scenarios']}")
        
        print("\nCATEGORY PERFORMANCE:")
        print("-"*40)
        for category, data in self.evaluation_metrics["category_performance"].items():
            print(f"{category:<20}: {data['average']:.2%} ({data['count']} scenarios)")
        
        print("\n" + "="*60)


def main():
    """Main evaluation function."""
    evaluator = JadePropertyEvaluator()
    
    # Run evaluation
    results = evaluator.run_evaluation()
    
    # Generate report
    evaluator.generate_report()


if __name__ == "__main__":
    main()