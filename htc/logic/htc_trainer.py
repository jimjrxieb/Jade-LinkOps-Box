#!/usr/bin/env python3
"""
HTC Autonomous Learning Trainer
===============================

Core module for training Jade to learn any new task, program, or data format.
Automatically generates tools, models, and RAG knowledge from uploaded content.

This is the brain of the HTC (Human-Trainable Computer) system.
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HTCTrainer:
    """
    Autonomous learning system that can ingest any task and generate:
    - Tools (scripts, configs, automation)
    - ML Models (classification, regression, clustering) 
    - RAG Memory Entries (embedded knowledge)
    - Executable Actions (MCP tools)
    """
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.intake_path = self.base_path / "intake" / "uploaded_docs"
        self.tools_path = self.base_path / "tools"
        self.models_path = self.base_path / "models"
        self.prompts_path = self.base_path / "prompts"
        self.test_history_path = self.base_path / "test_history"
        
        # Ensure directories exist
        for path in [self.intake_path, self.tools_path, self.models_path, self.test_history_path]:
            path.mkdir(parents=True, exist_ok=True)
            
        logger.info("🧠 HTC Trainer initialized")
        logger.info(f"   Intake: {self.intake_path}")
        logger.info(f"   Tools: {self.tools_path}")
        logger.info(f"   Models: {self.models_path}")

    async def train_on_task(
        self, 
        task_description: str,
        files: List[str],
        desired_outputs: List[str],
        tags: List[str],
        user_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main training pipeline - learns from task and generates outputs.
        
        Args:
            task_description: What the user wants Jade to learn
            files: List of uploaded file names
            desired_outputs: ["tool", "model", "rag", "action"]
            tags: Categorization tags
            user_context: Additional context from user
            
        Returns:
            Dict with results of training session
        """
        session_id = str(uuid.uuid4())[:8]
        logger.info(f"🔄 Starting HTC training session {session_id}")
        logger.info(f"   Task: {task_description}")
        logger.info(f"   Files: {files}")
        logger.info(f"   Outputs: {desired_outputs}")
        
        results = {
            "session_id": session_id,
            "task": task_description,
            "timestamp": datetime.now().isoformat(),
            "files_processed": files,
            "outputs_requested": desired_outputs,
            "tags": tags,
            "generated": {},
            "errors": []
        }
        
        try:
            # Step 1: Read and consolidate all uploaded content
            consolidated_content = await self._consolidate_content(files)
            results["content_size"] = len(consolidated_content)
            
            # Step 2: Generate RAG embeddings if requested
            if "rag" in desired_outputs:
                rag_result = await self._generate_rag_entries(
                    consolidated_content, task_description, tags, session_id
                )
                results["generated"]["rag"] = rag_result
                
            # Step 3: Generate ML model if requested and data is suitable
            if "model" in desired_outputs:
                model_result = await self._generate_ml_model(
                    files, task_description, tags, session_id
                )
                results["generated"]["model"] = model_result
                
            # Step 4: Generate tool/script if requested
            if "tool" in desired_outputs:
                tool_result = await self._generate_tool(
                    consolidated_content, task_description, tags, session_id
                )
                results["generated"]["tool"] = tool_result
                
            # Step 5: Generate executable action if requested
            if "action" in desired_outputs:
                action_result = await self._generate_mcp_action(
                    consolidated_content, task_description, tags, session_id
                )
                results["generated"]["action"] = action_result
                
            # Step 6: Save training session history
            await self._save_training_session(results)
            
            logger.info(f"✅ HTC training session {session_id} completed successfully")
            
        except Exception as e:
            error_msg = f"Training session {session_id} failed: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            
        return results

    async def _consolidate_content(self, files: List[str]) -> str:
        """Read and consolidate content from all uploaded files."""
        consolidated = []
        
        for filename in files:
            file_path = self.intake_path / filename
            if not file_path.exists():
                logger.warning(f"File not found: {filename}")
                continue
                
            try:
                # Handle different file types
                if filename.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    content = f"=== CSV File: {filename} ===\n"
                    content += f"Shape: {df.shape}\n"
                    content += f"Columns: {list(df.columns)}\n"
                    content += f"Sample data:\n{df.head().to_string()}\n\n"
                    consolidated.append(content)
                    
                elif filename.endswith('.json'):
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    content = f"=== JSON File: {filename} ===\n"
                    content += json.dumps(data, indent=2)[:1000] + "\n\n"
                    consolidated.append(content)
                    
                else:  # Text files (txt, md, py, etc.)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f"=== File: {filename} ===\n"
                        content += f.read()[:2000] + "\n\n"  # Limit to 2KB per file
                    consolidated.append(content)
                    
            except Exception as e:
                logger.error(f"Error reading {filename}: {e}")
                
        return "\n".join(consolidated)

    async def _generate_rag_entries(
        self, content: str, task: str, tags: List[str], session_id: str
    ) -> Dict[str, Any]:
        """Generate RAG knowledge entries from the content."""
        try:
            # Create a comprehensive knowledge entry
            knowledge_entry = {
                "id": f"htc_learned_{session_id}",
                "title": f"HTC Learning: {task[:50]}...",
                "content": content,
                "summary": task,
                "tags": tags + ["htc-learned", "auto-generated"],
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "source": "HTC Training"
            }
            
            # Save to RAG knowledge base (simulate for now)
            rag_file = self.base_path.parent / "rag" / "uploads" / f"htc_knowledge_{session_id}.json"
            rag_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(rag_file, 'w') as f:
                json.dump(knowledge_entry, f, indent=2)
                
            logger.info(f"📚 Generated RAG entry: {rag_file}")
            
            return {
                "status": "success",
                "entry_id": knowledge_entry["id"],
                "file_path": str(rag_file),
                "content_size": len(content)
            }
            
        except Exception as e:
            logger.error(f"RAG generation failed: {e}")
            return {"status": "error", "error": str(e)}

    async def _generate_ml_model(
        self, files: List[str], task: str, tags: List[str], session_id: str
    ) -> Dict[str, Any]:
        """Generate ML model from CSV data if applicable."""
        try:
            # Find CSV files for model training
            csv_files = [f for f in files if f.endswith('.csv')]
            if not csv_files:
                return {"status": "skipped", "reason": "No CSV files for model training"}
                
            # Load the primary CSV
            csv_path = self.intake_path / csv_files[0]
            df = pd.read_csv(csv_path)
            
            if len(df) < 10:
                return {"status": "skipped", "reason": "Insufficient data (< 10 rows)"}
                
            # Determine model type based on data
            model_info = self._analyze_data_for_modeling(df, task)
            
            if model_info["type"] == "classification":
                model, accuracy = self._train_classification_model(df, model_info)
            elif model_info["type"] == "regression": 
                model, score = self._train_regression_model(df, model_info)
            else:
                return {"status": "skipped", "reason": "Data not suitable for modeling"}
                
            # Save the trained model
            model_file = self.models_path / f"htc_model_{session_id}.joblib"
            joblib.dump({
                "model": model,
                "model_info": model_info,
                "session_id": session_id,
                "task": task,
                "tags": tags,
                "timestamp": datetime.now().isoformat()
            }, model_file)
            
            logger.info(f"🤖 Generated ML model: {model_file}")
            
            return {
                "status": "success",
                "model_type": model_info["type"],
                "target_column": model_info["target"],
                "features": model_info["features"],
                "accuracy": accuracy if model_info["type"] == "classification" else score,
                "file_path": str(model_file)
            }
            
        except Exception as e:
            logger.error(f"Model generation failed: {e}")
            return {"status": "error", "error": str(e)}

    def _analyze_data_for_modeling(self, df: pd.DataFrame, task: str) -> Dict[str, Any]:
        """Analyze DataFrame to determine best modeling approach."""
        # Smart target column detection based on task description and column names
        potential_targets = []
        
        # Look for common target column indicators
        target_keywords = [
            'risk', 'score', 'rating', 'status', 'class', 'category', 
            'result', 'outcome', 'target', 'label', 'priority'
        ]
        
        for col in df.columns:
            if any(keyword in col.lower() for keyword in target_keywords):
                potential_targets.append(col)
                
        # Also check if task mentions specific columns
        for col in df.columns:
            if col.lower() in task.lower():
                potential_targets.append(col)
                
        if not potential_targets:
            # Default to last column
            potential_targets = [df.columns[-1]]
            
        target_col = potential_targets[0]
        
        # Determine if classification or regression
        if df[target_col].dtype == 'object' or df[target_col].nunique() < 10:
            model_type = "classification"
        else:
            model_type = "regression"
            
        # Select feature columns (exclude target)
        feature_cols = [col for col in df.columns if col != target_col]
        
        return {
            "type": model_type,
            "target": target_col,
            "features": feature_cols[:10],  # Limit to 10 features
            "data_shape": df.shape
        }

    def _train_classification_model(self, df: pd.DataFrame, model_info: Dict) -> tuple:
        """Train a classification model."""
        target_col = model_info["target"]
        feature_cols = model_info["features"]
        
        # Prepare data
        X = df[feature_cols].select_dtypes(include=[np.number]).fillna(0)
        y = df[target_col]
        
        # Encode target if string
        if y.dtype == 'object':
            le = LabelEncoder()
            y = le.fit_transform(y)
            
        # Train model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        
        accuracy = model.score(X_test, y_test)
        
        return model, accuracy

    def _train_regression_model(self, df: pd.DataFrame, model_info: Dict) -> tuple:
        """Train a regression model."""
        target_col = model_info["target"]
        feature_cols = model_info["features"]
        
        # Prepare data
        X = df[feature_cols].select_dtypes(include=[np.number]).fillna(0)
        y = df[target_col].fillna(0)
        
        # Train model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        
        score = model.score(X_test, y_test)
        
        return model, score

    async def _generate_tool(
        self, content: str, task: str, tags: List[str], session_id: str
    ) -> Dict[str, Any]:
        """Generate a Python tool/script based on the learned content."""
        try:
            # Generate tool based on task type
            tool_template = self._select_tool_template(task, content)
            tool_code = self._generate_tool_code(tool_template, task, content, session_id)
            
            # Save the tool
            tool_file = self.tools_path / f"htc_tool_{session_id}.py"
            with open(tool_file, 'w') as f:
                f.write(tool_code)
                
            # Make it executable
            os.chmod(tool_file, 0o755)
            
            logger.info(f"🔧 Generated tool: {tool_file}")
            
            return {
                "status": "success",
                "tool_name": f"htc_tool_{session_id}",
                "file_path": str(tool_file),
                "description": f"Auto-generated tool for: {task}"
            }
            
        except Exception as e:
            logger.error(f"Tool generation failed: {e}")
            return {"status": "error", "error": str(e)}

    def _select_tool_template(self, task: str, content: str) -> str:
        """Select appropriate tool template based on task."""
        task_lower = task.lower()
        
        if "csv" in content and ("analyze" in task_lower or "report" in task_lower):
            return "csv_analyzer"
        elif "rank" in task_lower or "suggest" in task_lower:
            return "recommendation_tool"
        elif "monitor" in task_lower or "check" in task_lower:
            return "monitoring_tool"
        else:
            return "generic_processor"

    def _generate_tool_code(self, template: str, task: str, content: str, session_id: str) -> str:
        """Generate actual Python code for the tool."""
        
        if template == "csv_analyzer":
            return f'''#!/usr/bin/env python3
"""
Auto-generated CSV Analysis Tool
Generated by HTC Learning Session: {session_id}
Task: {task}
"""

import pandas as pd
import sys
from pathlib import Path

def analyze_csv(file_path):
    """Analyze CSV file and generate insights."""
    try:
        df = pd.read_csv(file_path)
        
        print(f"📊 CSV Analysis Results")
        print(f"========================")
        print(f"File: {{file_path}}")
        print(f"Shape: {{df.shape}}")
        print(f"Columns: {{list(df.columns)}}")
        print()
        
        # Basic statistics
        print("📈 Numerical Summary:")
        print(df.describe())
        print()
        
        # Missing values
        missing = df.isnull().sum()
        if missing.any():
            print("⚠️  Missing Values:")
            print(missing[missing > 0])
            print()
            
        # Top values for categorical columns
        for col in df.select_dtypes(include=['object']).columns:
            print(f"🏷️  Top values in {{col}}:")
            print(df[col].value_counts().head())
            print()
            
        return df
        
    except Exception as e:
        print(f"❌ Error analyzing CSV: {{e}}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python htc_tool_{session_id}.py <csv_file>")
        sys.exit(1)
        
    csv_file = sys.argv[1]
    analyze_csv(csv_file)
'''
        elif template == "recommendation_tool":
            return f'''#!/usr/bin/env python3
"""
Auto-generated Recommendation Tool
Generated by HTC Learning Session: {session_id}
Task: {task}
"""

import pandas as pd
import sys
import json
from pathlib import Path

def generate_recommendations(data_file, criteria=None):
    """Generate recommendations based on learned patterns."""
    try:
        df = pd.read_csv(data_file)
        
        print(f"🎯 Recommendation Engine")
        print(f"========================")
        print(f"Data source: {{data_file}}")
        print(f"Records: {{len(df)}}")
        print()
        
        # Simple scoring algorithm
        if criteria:
            print(f"Filtering by criteria: {{criteria}}")
        
        # Score each row (simplified)
        if len(df.select_dtypes(include=['number']).columns) > 0:
            numeric_cols = df.select_dtypes(include=['number']).columns
            df['htc_score'] = df[numeric_cols].mean(axis=1)
            
            # Top recommendations
            top_recs = df.nlargest(5, 'htc_score')
            
            print("🏆 Top Recommendations:")
            for idx, row in top_recs.iterrows():
                print(f"  {{idx + 1}}. Score: {{row['htc_score']:.2f}}")
                print(f"     Data: {{dict(row.drop('htc_score'))}}")
                print()
        else:
            print("ℹ️  No numerical data for scoring")
            
    except Exception as e:
        print(f"❌ Error generating recommendations: {{e}}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python htc_tool_{session_id}.py <data_file> [criteria]")
        sys.exit(1)
        
    data_file = sys.argv[1]
    criteria = sys.argv[2] if len(sys.argv) > 2 else None
    generate_recommendations(data_file, criteria)
'''
        else:  # generic_processor
            return f'''#!/usr/bin/env python3
"""
Auto-generated Data Processor
Generated by HTC Learning Session: {session_id}
Task: {task}
"""

import sys
import json
from pathlib import Path

def process_data(input_file):
    """Process data based on learned task."""
    try:
        print(f"🔄 Processing: {{input_file}}")
        print(f"Task: {task}")
        print()
        
        # Read file content
        with open(input_file, 'r') as f:
            content = f.read()
            
        print(f"✅ File processed successfully")
        print(f"Content length: {{len(content)}} characters")
        
        # Add task-specific processing here
        result = {{
            "task": "{task}",
            "file": input_file,
            "content_length": len(content),
            "status": "processed"
        }}
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing file: {{e}}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python htc_tool_{session_id}.py <input_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    result = process_data(input_file)
    
    if result:
        print(f"\\n📋 Result:")
        print(json.dumps(result, indent=2))
'''

    async def _generate_mcp_action(
        self, content: str, task: str, tags: List[str], session_id: str
    ) -> Dict[str, Any]:
        """Generate MCP (Model Context Protocol) action for AutoRunner."""
        try:
            # Create MCP tool definition
            mcp_tool = {
                "name": f"htc_learned_{session_id}",
                "description": f"Auto-learned action: {task}",
                "category": "htc-generated",
                "tags": tags,
                "metadata": {
                    "session_id": session_id,
                    "generated_by": "HTC Training",
                    "timestamp": datetime.now().isoformat()
                },
                "command": f"python htc/tools/htc_tool_{session_id}.py",
                "parameters": {
                    "input_file": {
                        "type": "string",
                        "description": "Input file to process",
                        "required": True
                    }
                },
                "output_format": "json",
                "timeout": 30
            }
            
            # Save to MCP tools directory
            mcp_file = self.base_path.parent / "db" / "mcp_tools" / f"htc_learned_{session_id}.json"
            mcp_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(mcp_file, 'w') as f:
                json.dump(mcp_tool, f, indent=2)
                
            logger.info(f"⚡ Generated MCP action: {mcp_file}")
            
            return {
                "status": "success",
                "action_name": mcp_tool["name"],
                "file_path": str(mcp_file),
                "description": mcp_tool["description"]
            }
            
        except Exception as e:
            logger.error(f"MCP action generation failed: {e}")
            return {"status": "error", "error": str(e)}

    async def _save_training_session(self, results: Dict[str, Any]):
        """Save complete training session results for history."""
        session_file = self.test_history_path / f"session_{results['session_id']}.json"
        
        with open(session_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"💾 Saved training session: {session_file}")

    def get_training_history(self) -> List[Dict[str, Any]]:
        """Get list of all training sessions."""
        history = []
        
        for session_file in self.test_history_path.glob("session_*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                history.append(session_data)
            except Exception as e:
                logger.warning(f"Could not load session {session_file}: {e}")
                
        return sorted(history, key=lambda x: x['timestamp'], reverse=True)

    def get_generated_assets(self) -> Dict[str, List[str]]:
        """Get list of all generated assets."""
        return {
            "tools": [f.name for f in self.tools_path.glob("htc_tool_*.py")],
            "models": [f.name for f in self.models_path.glob("htc_model_*.joblib")],
            "sessions": [f.name for f in self.test_history_path.glob("session_*.json")]
        }

# Global trainer instance
_trainer = None

def get_htc_trainer() -> HTCTrainer:
    """Get the global HTC trainer instance."""
    global _trainer
    if _trainer is None:
        _trainer = HTCTrainer()
    return _trainer

async def train_on_task(task: str, files: List[str], outputs: List[str], tags: List[str]) -> Dict[str, Any]:
    """Convenience function for training."""
    trainer = get_htc_trainer()
    return await trainer.train_on_task(task, files, outputs, tags)