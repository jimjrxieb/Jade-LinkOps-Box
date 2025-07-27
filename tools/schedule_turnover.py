#!/usr/bin/env python3
"""
ZRS Unit Turnover Scheduler
===========================

Manages scheduling of cleaning, inspection, and preparation workflow for vacant units.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZRSTurnoverScheduler:
    """ZRS Unit Turnover Management System"""
    
    def __init__(self):
        """Initialize scheduler with service providers and costs"""
        self.service_providers = {
            "cleaning": {
                "standard": {"provider": "CleanTeam Pro", "cost": 200, "duration": 4},
                "deep": {"provider": "DeepClean Specialists", "cost": 350, "duration": 6}
            },
            "inspection": {
                "provider": "ZRS Property Inspectors", 
                "cost": 75,
                "duration": 2
            },
            "photography": {
                "provider": "PropertyPics Studio",
                "cost": 125, 
                "duration": 1
            },
            "minor_repairs": {
                "provider": "QuickFix Maintenance",
                "cost": 150,
                "duration": 4
            }
        }
    
    def calculate_timeline(self, move_out_date: str, new_lease_date: str = None, deep_clean: bool = False) -> dict:
        """Calculate optimal turnover timeline"""
        move_out = datetime.strptime(move_out_date, "%Y-%m-%d")
        
        # Standard timeline
        timeline = []
        current_date = move_out
        
        # Day 1: Initial inspection
        timeline.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "task": "Move-out inspection and damage assessment",
            "duration": 2,
            "cost": 75,
            "assigned_to": "Property Manager",
            "priority": "high"
        })
        
        # Day 2: Cleaning
        current_date += timedelta(days=1)
        clean_type = "deep" if deep_clean else "standard"
        clean_info = self.service_providers["cleaning"][clean_type]
        
        timeline.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "task": f"{clean_type.title()} cleaning of entire unit",
            "duration": clean_info["duration"],
            "cost": clean_info["cost"],
            "assigned_to": clean_info["provider"],
            "priority": "high"
        })
        
        # Day 3: Minor repairs (if needed)
        current_date += timedelta(days=1)
        timeline.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "task": "Minor repairs and touch-ups",
            "duration": 4,
            "cost": 150,
            "assigned_to": "QuickFix Maintenance",
            "priority": "medium"
        })
        
        # Day 4: Final inspection and photography
        current_date += timedelta(days=1)
        timeline.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "task": "Final inspection and professional photography",
            "duration": 3,
            "cost": 200,
            "assigned_to": "Property Manager + PropertyPics",
            "priority": "high"
        })
        
        # Day 5: Unit ready
        ready_date = current_date + timedelta(days=1)
        
        # Check if timeline meets new lease date
        if new_lease_date:
            new_lease = datetime.strptime(new_lease_date, "%Y-%m-%d")
            if ready_date > new_lease:
                # Expedite timeline
                timeline = self._expedite_timeline(move_out, new_lease, deep_clean)
                ready_date = new_lease - timedelta(days=1)
        
        return {
            "move_out_date": move_out_date,
            "new_lease_date": new_lease_date,
            "ready_date": ready_date.strftime("%Y-%m-%d"),
            "timeline": timeline,
            "total_cost": sum(task["cost"] for task in timeline),
            "total_duration": len(timeline)
        }
    
    def _expedite_timeline(self, move_out: datetime, new_lease: datetime, deep_clean: bool) -> list:
        """Create expedited timeline for quick turnaround"""
        days_available = (new_lease - move_out).days - 1  # Leave 1 day buffer
        
        if days_available < 2:
            # Emergency 1-2 day turnaround
            timeline = [
                {
                    "date": move_out.strftime("%Y-%m-%d"),
                    "task": "Same-day inspection and cleaning",
                    "duration": 8,
                    "cost": 450 if deep_clean else 300,
                    "assigned_to": "Emergency Turnover Team",
                    "priority": "emergency"
                }
            ]
            
            if days_available == 2:
                timeline.append({
                    "date": (move_out + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "task": "Final touches and photography",
                    "duration": 4,
                    "cost": 200,
                    "assigned_to": "Property Manager",
                    "priority": "high"
                })
        
        else:
            # Standard expedited timeline (3-4 days)
            timeline = [
                {
                    "date": move_out.strftime("%Y-%m-%d"),
                    "task": "Inspection and cleaning (same day)",
                    "duration": 6,
                    "cost": 350 if deep_clean else 250,
                    "assigned_to": "Expedited Cleaning Team",
                    "priority": "high"
                },
                {
                    "date": (move_out + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "task": "Repairs and final inspection",
                    "duration": 6,
                    "cost": 250,
                    "assigned_to": "Maintenance + Manager",
                    "priority": "high"
                }
            ]
        
        return timeline
    
    def schedule_turnover(self, unit: str, move_out_date: str, new_lease_date: str = None, deep_clean: bool = False) -> dict:
        """Schedule complete turnover process for a unit"""
        try:
            # Calculate timeline
            schedule = self.calculate_timeline(move_out_date, new_lease_date, deep_clean)
            
            # Generate work orders
            work_orders = []
            for i, task in enumerate(schedule["timeline"], 1):
                work_orders.append({
                    "work_order_id": f"TO-{unit}-{datetime.now().strftime('%Y%m%d')}-{i:02d}",
                    "unit": unit,
                    "task": task["task"],
                    "scheduled_date": task["date"],
                    "estimated_duration": f"{task['duration']} hours",
                    "assigned_to": task["assigned_to"],
                    "estimated_cost": task["cost"],
                    "priority": task["priority"],
                    "status": "scheduled"
                })
            
            # Calculate revenue impact
            days_vacant = (datetime.strptime(schedule["ready_date"], "%Y-%m-%d") - 
                          datetime.strptime(move_out_date, "%Y-%m-%d")).days
            
            # Estimate daily rent (demo data)
            estimated_daily_rent = 60  # $1800/month ÷ 30 days
            revenue_loss = days_vacant * estimated_daily_rent
            
            return {
                "unit_number": unit,
                "turnover_scheduled": True,
                "schedule": schedule,
                "work_orders": work_orders,
                "financial_impact": {
                    "total_cost": schedule["total_cost"],
                    "days_vacant": days_vacant,
                    "estimated_revenue_loss": revenue_loss,
                    "cost_per_day": round(schedule["total_cost"] / max(days_vacant, 1), 2)
                },
                "notifications": {
                    "property_manager": "Turnover scheduled and work orders created",
                    "maintenance_team": f"{len(work_orders)} work orders assigned",
                    "leasing_office": f"Unit {unit} available {schedule['ready_date']}"
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scheduling turnover: {e}")
            return {
                "unit_number": unit,
                "turnover_scheduled": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

def main():
    """Command line interface for turnover scheduling"""
    parser = argparse.ArgumentParser(description="ZRS Unit Turnover Scheduler")
    parser.add_argument("--unit", required=True, help="Unit number")
    parser.add_argument("--moveout", required=True, help="Move-out date (YYYY-MM-DD)")
    parser.add_argument("--movein", help="New lease start date (YYYY-MM-DD)")
    parser.add_argument("--deep_clean", action="store_true", help="Schedule deep cleaning")
    
    args = parser.parse_args()
    
    try:
        # Initialize scheduler
        scheduler = ZRSTurnoverScheduler()
        
        # Schedule turnover
        result = scheduler.schedule_turnover(
            unit=args.unit,
            move_out_date=args.moveout,
            new_lease_date=args.movein,
            deep_clean=args.deep_clean
        )
        
        # Output result as JSON
        print(json.dumps(result, indent=2))
        
        # Log summary
        if result.get("turnover_scheduled"):
            logger.info(f"🏠 TURNOVER SCHEDULED for Unit {args.unit}")
            logger.info(f"Ready Date: {result['schedule']['ready_date']}")
            logger.info(f"Total Cost: ${result['financial_impact']['total_cost']}")
            logger.info(f"Work Orders: {len(result['work_orders'])}")
        
        sys.exit(0 if result.get("turnover_scheduled") else 1)
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()