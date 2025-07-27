#!/usr/bin/env python3
"""
ZRS Vendor Ranking System
=========================

Analyzes vendor performance data and recommends the best contractors for property maintenance work.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZRSVendorRanker:
    """ZRS Vendor Selection and Ranking System"""
    
    def __init__(self):
        """Initialize with vendor database"""
        self.vendor_db = self._load_vendor_database()
    
    def _load_vendor_database(self) -> dict:
        """Load vendor database with performance metrics"""
        return {
            "HVAC": [
                {
                    "name": "CoolAir Systems",
                    "contact": "555-COOL-AIR",
                    "email": "service@coolair.com",
                    "rating": 4.8,
                    "avg_cost": 650,
                    "response_time": "2 hours",
                    "availability": "24/7",
                    "specialties": ["emergency repair", "maintenance", "installation"],
                    "certifications": ["EPA certified", "Licensed"],
                    "last_job_date": "2025-01-15",
                    "job_count": 45,
                    "success_rate": 98
                },
                {
                    "name": "TempControl Pro",
                    "contact": "555-TEMP-PRO", 
                    "email": "dispatch@tempcontrol.com",
                    "rating": 4.6,
                    "avg_cost": 580,
                    "response_time": "4 hours",
                    "availability": "M-F 7AM-7PM",
                    "specialties": ["maintenance", "repair"],
                    "certifications": ["Licensed", "Bonded"],
                    "last_job_date": "2025-01-20",
                    "job_count": 32,
                    "success_rate": 95
                },
                {
                    "name": "QuickFix HVAC",
                    "contact": "555-QUICK-FX",
                    "email": "info@quickfixhvac.com", 
                    "rating": 4.2,
                    "avg_cost": 420,
                    "response_time": "6 hours",
                    "availability": "M-Sat 8AM-6PM",
                    "specialties": ["budget repair", "maintenance"],
                    "certifications": ["Licensed"],
                    "last_job_date": "2025-01-10",
                    "job_count": 28,
                    "success_rate": 92
                }
            ],
            
            "plumbing": [
                {
                    "name": "AquaTech Plumbing",
                    "contact": "555-AQUA-TECH",
                    "email": "emergency@aquatech.com",
                    "rating": 4.9,
                    "avg_cost": 380,
                    "response_time": "1 hour",
                    "availability": "24/7",
                    "specialties": ["emergency", "leak repair", "pipe replacement"],
                    "certifications": ["Master Plumber", "Licensed", "Insured"],
                    "last_job_date": "2025-01-22",
                    "job_count": 67,
                    "success_rate": 99
                },
                {
                    "name": "FlowMaster Services",
                    "contact": "555-FLOW-MASTER",
                    "email": "service@flowmaster.com",
                    "rating": 4.5,
                    "avg_cost": 320,
                    "response_time": "3 hours",
                    "availability": "M-F 6AM-8PM, Weekends 8AM-4PM", 
                    "specialties": ["drain cleaning", "fixture repair"],
                    "certifications": ["Licensed", "Bonded"],
                    "last_job_date": "2025-01-18",
                    "job_count": 41,
                    "success_rate": 94
                }
            ],
            
            "electrical": [
                {
                    "name": "PowerUp Electric",
                    "contact": "555-POWER-UP",
                    "email": "dispatch@powerupelectric.com",
                    "rating": 4.7,
                    "avg_cost": 290,
                    "response_time": "2 hours",
                    "availability": "24/7 emergency, M-F 7AM-6PM regular",
                    "specialties": ["emergency repair", "panel upgrades", "outlet installation"],
                    "certifications": ["Master Electrician", "Licensed", "Insured"],
                    "last_job_date": "2025-01-19",
                    "job_count": 38,
                    "success_rate": 97
                },
                {
                    "name": "Wired Right",
                    "contact": "555-WIRED-RT",
                    "email": "info@wiredright.com",
                    "rating": 4.3,
                    "avg_cost": 240,
                    "response_time": "4 hours",
                    "availability": "M-Sat 8AM-5PM",
                    "specialties": ["lighting", "wiring", "maintenance"],
                    "certifications": ["Licensed", "Insured"],
                    "last_job_date": "2025-01-16",
                    "job_count": 25,
                    "success_rate": 91
                }
            ],
            
            "painting": [
                {
                    "name": "ColorPro Painters",
                    "contact": "555-COLOR-PRO",
                    "email": "estimates@colorpro.com",
                    "rating": 4.6,
                    "avg_cost": 1200,
                    "response_time": "24 hours",
                    "availability": "M-F 8AM-5PM",
                    "specialties": ["interior", "exterior", "touch-ups"],
                    "certifications": ["Licensed", "Insured"],
                    "last_job_date": "2025-01-12",
                    "job_count": 22,
                    "success_rate": 96
                }
            ],
            
            "flooring": [
                {
                    "name": "FloorMasters",
                    "contact": "555-FLOOR-MASTER",
                    "email": "sales@floormasters.com",
                    "rating": 4.8,
                    "avg_cost": 2200,
                    "response_time": "48 hours",
                    "availability": "M-F 9AM-5PM",
                    "specialties": ["carpet", "hardwood", "tile", "repair"],
                    "certifications": ["Licensed", "Bonded", "Insured"],
                    "last_job_date": "2025-01-08",
                    "job_count": 15,
                    "success_rate": 98
                }
            ],
            
            "roofing": [
                {
                    "name": "RoofShield Contractors",
                    "contact": "555-ROOF-SHIELD",
                    "email": "emergency@roofshield.com",
                    "rating": 4.9,
                    "avg_cost": 3500,
                    "response_time": "4 hours emergency, 24 hours routine",
                    "availability": "24/7 emergency, M-Sat regular",
                    "specialties": ["emergency repair", "leak repair", "full replacement"],
                    "certifications": ["Licensed", "Bonded", "Insured", "Manufacturer Certified"],
                    "last_job_date": "2025-01-14",
                    "job_count": 18,
                    "success_rate": 100
                }
            ],
            
            "general": [
                {
                    "name": "AllFix Contractors", 
                    "contact": "555-ALL-FIX",
                    "email": "service@allfix.com",
                    "rating": 4.4,
                    "avg_cost": 450,
                    "response_time": "6 hours",
                    "availability": "M-F 8AM-6PM",
                    "specialties": ["general repair", "maintenance", "handyman services"],
                    "certifications": ["Licensed", "Insured"],
                    "last_job_date": "2025-01-21",
                    "job_count": 52,
                    "success_rate": 93
                }
            ]
        }
    
    def calculate_vendor_score(self, vendor: dict, urgency: str = "routine", budget_max: float = None) -> float:
        """Calculate weighted score for vendor selection"""
        # Base scoring weights
        weights = {
            "rating": 0.35,      # Quality is most important
            "cost": 0.25,        # Cost efficiency
            "response": 0.20,    # Response time
            "reliability": 0.20  # Success rate and job count
        }
        
        # Adjust weights based on urgency
        if urgency == "emergency":
            weights = {"rating": 0.25, "cost": 0.15, "response": 0.40, "reliability": 0.20}
        elif urgency == "urgent":
            weights = {"rating": 0.30, "cost": 0.20, "response": 0.30, "reliability": 0.20}
        
        # Calculate individual scores (0-1 scale)
        rating_score = vendor["rating"] / 5.0
        
        # Cost score (lower cost = higher score, but normalize against category average)
        cost_score = max(0, 1 - (vendor["avg_cost"] / 5000))  # Normalize to $5000 max
        
        # Response time score (convert hours to score)
        response_hours = self._parse_response_time(vendor["response_time"])
        response_score = max(0, 1 - (response_hours / 24))  # 24 hours = 0 score
        
        # Reliability score (based on success rate and experience)
        reliability_score = (vendor["success_rate"] / 100) * (min(vendor["job_count"], 50) / 50)
        
        # Budget constraint
        if budget_max and vendor["avg_cost"] > budget_max:
            cost_score *= 0.5  # Penalty for exceeding budget
        
        # Calculate weighted total
        total_score = (
            rating_score * weights["rating"] +
            cost_score * weights["cost"] +
            response_score * weights["response"] +
            reliability_score * weights["reliability"]
        )
        
        return round(total_score, 3)
    
    def _parse_response_time(self, response_time: str) -> float:
        """Parse response time string to hours"""
        if "hour" in response_time:
            try:
                return float(response_time.split()[0])
            except:
                return 24.0
        elif "day" in response_time:
            try:
                return float(response_time.split()[0]) * 24
            except:
                return 24.0
        return 24.0
    
    def recommend_vendors(self, work_type: str, urgency: str = "routine", budget_max: float = None) -> dict:
        """Get ranked vendor recommendations"""
        work_type = work_type.upper()
        
        if work_type not in self.vendor_db:
            available_types = list(self.vendor_db.keys())
            return {
                "error": f"Unknown work type: {work_type}",
                "available_types": available_types,
                "timestamp": datetime.now().isoformat()
            }
        
        vendors = self.vendor_db[work_type].copy()
        
        # Calculate scores and rank vendors
        for vendor in vendors:
            vendor["score"] = self.calculate_vendor_score(vendor, urgency, budget_max)
            vendor["recommended_for"] = urgency
        
        # Sort by score (highest first)
        vendors.sort(key=lambda x: x["score"], reverse=True)
        
        # Filter by budget if specified
        if budget_max:
            affordable_vendors = [v for v in vendors if v["avg_cost"] <= budget_max]
            if affordable_vendors:
                vendors = affordable_vendors
        
        return {
            "work_type": work_type,
            "urgency": urgency,
            "budget_max": budget_max,
            "recommended_vendors": vendors[:3],  # Top 3 recommendations
            "total_vendors_available": len(self.vendor_db[work_type]),
            "ranking_criteria": {
                "primary_factors": ["Quality Rating", "Cost Efficiency", "Response Time", "Reliability"],
                "urgency_adjustment": f"Optimized for {urgency} work",
                "budget_constraint": f"Under ${budget_max}" if budget_max else "No budget limit"
            },
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Command line interface for vendor ranking"""
    parser = argparse.ArgumentParser(description="ZRS Vendor Ranking System")
    parser.add_argument("--type", required=True, 
                       choices=["HVAC", "plumbing", "electrical", "painting", "flooring", "roofing", "general"],
                       help="Type of work needed")
    parser.add_argument("--urgency", choices=["routine", "urgent", "emergency"], 
                       default="routine", help="Urgency level")
    parser.add_argument("--budget", type=float, help="Maximum budget")
    
    args = parser.parse_args()
    
    try:
        # Initialize vendor ranker
        ranker = ZRSVendorRanker()
        
        # Get recommendations
        result = ranker.recommend_vendors(
            work_type=args.type,
            urgency=args.urgency,
            budget_max=args.budget
        )
        
        # Output result as JSON
        print(json.dumps(result, indent=2))
        
        # Log summary
        if "recommended_vendors" in result:
            logger.info(f"🔧 VENDOR RECOMMENDATIONS for {args.type.upper()}")
            for i, vendor in enumerate(result["recommended_vendors"], 1):
                logger.info(f"{i}. {vendor['name']} - Score: {vendor['score']:.2f} - Cost: ${vendor['avg_cost']}")
        
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