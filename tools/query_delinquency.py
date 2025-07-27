#!/usr/bin/env python3
"""
ZRS Delinquency Query System
============================

Analyzes tenant payment data and generates delinquency reports for collections management.
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZRSDelinquencyAnalyzer:
    """ZRS Rent Delinquency Analysis System"""
    
    def __init__(self):
        """Initialize with sample delinquency data"""
        self.data_file = Path("db/demo_data/delinquency.csv")
        self.sample_data = self._generate_sample_data()
    
    def _generate_sample_data(self) -> list:
        """Generate sample delinquency data for demo"""
        return [
            {
                "tenant_name": "Tony Stark",
                "unit": "401", 
                "building": "Building A",
                "amount_owed": 2500.00,
                "days_late": 12,
                "last_payment_date": "2024-12-15",
                "phone": "555-0101",
                "email": "tony.stark@email.com",
                "lease_status": "active",
                "payment_history": "poor"
            },
            {
                "tenant_name": "Peter Parker",
                "unit": "205",
                "building": "Building A", 
                "amount_owed": 1200.00,
                "days_late": 7,
                "last_payment_date": "2025-01-20",
                "phone": "555-0102",
                "email": "peter.parker@email.com",
                "lease_status": "active",
                "payment_history": "good"
            },
            {
                "tenant_name": "Bruce Banner",
                "unit": "1201",
                "building": "Building B",
                "amount_owed": 2200.00,
                "days_late": 45,
                "last_payment_date": "2024-11-10",
                "phone": "555-0103",
                "email": "bruce.banner@email.com",
                "lease_status": "active",
                "payment_history": "poor"
            },
            {
                "tenant_name": "Diana Prince",
                "unit": "302",
                "building": "Building A",
                "amount_owed": 1800.00,
                "days_late": 23,
                "last_payment_date": "2024-12-01",
                "phone": "555-0104",
                "email": "diana.prince@email.com", 
                "lease_status": "active",
                "payment_history": "fair"
            },
            {
                "tenant_name": "Clark Kent",
                "unit": "505",
                "building": "Building B",
                "amount_owed": 1800.00,
                "days_late": 35,
                "last_payment_date": "2024-11-20",
                "phone": "555-0105",
                "email": "clark.kent@email.com",
                "lease_status": "active", 
                "payment_history": "poor"
            },
            {
                "tenant_name": "Natasha Romanoff",
                "unit": "401",
                "building": "Building B",
                "amount_owed": 2100.00,
                "days_late": 18,
                "last_payment_date": "2024-12-08",
                "phone": "555-0106",
                "email": "natasha.romanoff@email.com",
                "lease_status": "active",
                "payment_history": "fair"
            },
            {
                "tenant_name": "Steve Rogers",
                "unit": "101",
                "building": "Building A",
                "amount_owed": 900.00,
                "days_late": 5,
                "last_payment_date": "2025-01-22",
                "phone": "555-0107",
                "email": "steve.rogers@email.com",
                "lease_status": "active",
                "payment_history": "excellent"
            },
            {
                "tenant_name": "Wanda Maximoff",
                "unit": "607",
                "building": "Building B",
                "amount_owed": 3200.00,
                "days_late": 67,
                "last_payment_date": "2024-10-15",
                "phone": "555-0108",
                "email": "wanda.maximoff@email.com",
                "lease_status": "notice_served",
                "payment_history": "poor"
            }
        ]
    
    def load_delinquency_data(self) -> list:
        """Load delinquency data from CSV or use sample data"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as file:
                    reader = csv.DictReader(file)
                    data = []
                    for row in reader:
                        # Convert numeric fields
                        row['amount_owed'] = float(row.get('amount_owed', 0))
                        row['days_late'] = int(row.get('days_late', 0))
                        data.append(row)
                    return data
            except Exception as e:
                logger.warning(f"Could not load CSV data: {e}. Using sample data.")
        
        return self.sample_data
    
    def filter_delinquent_tenants(self, days_late: int = 1, building: str = None, 
                                amount_threshold: float = None, sort_by: str = "days_late") -> dict:
        """Filter and analyze delinquent tenants"""
        
        # Load data
        all_data = self.load_delinquency_data()
        
        # Apply filters
        filtered_tenants = []
        for tenant in all_data:
            # Days late filter
            if tenant["days_late"] < days_late:
                continue
            
            # Building filter
            if building and tenant.get("building", "").upper() != building.upper():
                continue
            
            # Amount threshold filter
            if amount_threshold and tenant["amount_owed"] < amount_threshold:
                continue
            
            # Calculate additional fields
            tenant["risk_level"] = self._calculate_risk_level(tenant)
            tenant["recommended_action"] = self._get_recommended_action(tenant)
            
            filtered_tenants.append(tenant)
        
        # Sort results
        sort_fields = {
            "days_late": lambda x: x["days_late"],
            "amount_owed": lambda x: x["amount_owed"],
            "tenant_name": lambda x: x["tenant_name"],
            "unit": lambda x: x["unit"]
        }
        
        if sort_by in sort_fields:
            filtered_tenants.sort(key=sort_fields[sort_by], reverse=(sort_by != "tenant_name"))
        
        # Calculate analytics
        analytics = self._calculate_analytics(filtered_tenants, all_data)
        
        return {
            "query_parameters": {
                "min_days_late": days_late,
                "building_filter": building,
                "amount_threshold": amount_threshold,
                "sort_by": sort_by
            },
            "results": {
                "total_delinquent": len(filtered_tenants),
                "total_amount_owed": sum(t["amount_owed"] for t in filtered_tenants),
                "delinquent_tenants": filtered_tenants
            },
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_risk_level(self, tenant: dict) -> str:
        """Calculate risk level for tenant"""
        days_late = tenant["days_late"]
        amount_owed = tenant["amount_owed"]
        payment_history = tenant.get("payment_history", "unknown")
        
        # Risk scoring
        risk_score = 0
        
        # Days late scoring
        if days_late >= 60:
            risk_score += 40
        elif days_late >= 30:
            risk_score += 25
        elif days_late >= 15:
            risk_score += 15
        elif days_late >= 7:
            risk_score += 10
        
        # Amount owed scoring
        if amount_owed >= 3000:
            risk_score += 30
        elif amount_owed >= 2000:
            risk_score += 20
        elif amount_owed >= 1000:
            risk_score += 10
        
        # Payment history scoring
        history_scores = {"poor": 20, "fair": 10, "good": 5, "excellent": 0}
        risk_score += history_scores.get(payment_history, 15)
        
        # Determine risk level
        if risk_score >= 70:
            return "critical"
        elif risk_score >= 50:
            return "high"
        elif risk_score >= 30:
            return "medium"
        else:
            return "low"
    
    def _get_recommended_action(self, tenant: dict) -> str:
        """Get recommended collection action"""
        days_late = tenant["days_late"]
        risk_level = tenant.get("risk_level", "medium")
        
        if days_late >= 60 or risk_level == "critical":
            return "legal_action"
        elif days_late >= 30 or risk_level == "high":
            return "final_notice"
        elif days_late >= 15:
            return "phone_call"
        elif days_late >= 7:
            return "late_notice"
        else:
            return "friendly_reminder"
    
    def _calculate_analytics(self, filtered_tenants: list, all_data: list) -> dict:
        """Calculate delinquency analytics"""
        if not filtered_tenants:
            return {
                "summary": "No tenants match the specified criteria",
                "total_portfolio_risk": 0
            }
        
        # Basic statistics
        amounts = [t["amount_owed"] for t in filtered_tenants]
        days_late_list = [t["days_late"] for t in filtered_tenants]
        
        # Risk distribution
        risk_distribution = {}
        action_distribution = {}
        
        for tenant in filtered_tenants:
            risk = tenant.get("risk_level", "unknown")
            action = tenant.get("recommended_action", "unknown")
            
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
            action_distribution[action] = action_distribution.get(action, 0) + 1
        
        # Building analysis
        building_analysis = {}
        for tenant in filtered_tenants:
            building = tenant.get("building", "Unknown")
            if building not in building_analysis:
                building_analysis[building] = {"count": 0, "total_owed": 0}
            building_analysis[building]["count"] += 1
            building_analysis[building]["total_owed"] += tenant["amount_owed"]
        
        return {
            "summary_statistics": {
                "avg_amount_owed": round(sum(amounts) / len(amounts), 2),
                "max_amount_owed": max(amounts),
                "avg_days_late": round(sum(days_late_list) / len(days_late_list), 1),
                "max_days_late": max(days_late_list)
            },
            "risk_distribution": risk_distribution,
            "recommended_actions": action_distribution,
            "building_breakdown": building_analysis,
            "portfolio_impact": {
                "total_portfolio_units": len(all_data),
                "delinquency_rate": round((len(filtered_tenants) / len(all_data)) * 100, 1),
                "total_at_risk": sum(amounts)
            }
        }

def main():
    """Command line interface for delinquency analysis"""
    parser = argparse.ArgumentParser(description="ZRS Delinquency Query System")
    parser.add_argument("--days", type=int, default=1, help="Minimum days late")
    parser.add_argument("--building", help="Filter by building")
    parser.add_argument("--amount", type=float, help="Minimum amount owed")
    parser.add_argument("--sort", choices=["days_late", "amount_owed", "tenant_name", "unit"],
                       default="days_late", help="Sort field")
    
    args = parser.parse_args()
    
    try:
        # Initialize analyzer
        analyzer = ZRSDelinquencyAnalyzer()
        
        # Query delinquent tenants
        result = analyzer.filter_delinquent_tenants(
            days_late=args.days,
            building=args.building,
            amount_threshold=args.amount,
            sort_by=args.sort
        )
        
        # Output result as JSON
        print(json.dumps(result, indent=2))
        
        # Log summary
        results = result["results"]
        logger.info(f"💰 DELINQUENCY ANALYSIS")
        logger.info(f"Found: {results['total_delinquent']} delinquent tenants")
        logger.info(f"Total Owed: ${results['total_amount_owed']:,.2f}")
        logger.info(f"Delinquency Rate: {result['analytics']['portfolio_impact']['delinquency_rate']}%")
        
        sys.exit(0)
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()