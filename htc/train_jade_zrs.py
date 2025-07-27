#!/usr/bin/env python3
"""
ZRS Jade AI Training System
============================

Fine-tunes Jade AI assistant specifically for ZRS property management workflows.
Uses LoRA (Low-Rank Adaptation) for efficient training on local hardware.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ZRSJadeTrainer:
    """
    ZRS-specific Jade AI training system for property management.
    """

    def __init__(
        self,
        model_name: str = "microsoft/DialoGPT-small",  # Lightweight for local training
        dataset_path: str = "htc/datasets/zrs_property_finetune.jsonl",
        output_dir: str = "./models/jade-zrs-property",
    ):
        """Initialize ZRS Jade trainer."""
        self.model_name = model_name
        self.dataset_path = Path(dataset_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Training hyperparameters
        self.max_length = 256  # Shorter for property management commands
        self.batch_size = 4
        self.learning_rate = 3e-4
        self.num_epochs = 5
        self.warmup_steps = 100
        
        # Initialize components
        self.tokenizer = None
        self.model = None
        self.dataset = None

    def setup_model_and_tokenizer(self):
        """Setup model and tokenizer with quantization for local training."""
        logger.info(f"🔧 Loading model: {self.model_name}")
        
        # Quantization config for memory efficiency
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        
        # Set special tokens
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model with quantization
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16,
        )
        
        # Prepare for k-bit training
        self.model = prepare_model_for_kbit_training(self.model)
        
        logger.info("✅ Model and tokenizer loaded successfully")

    def setup_lora_config(self):
        """Setup LoRA configuration for efficient fine-tuning."""
        logger.info("🔧 Setting up LoRA configuration")
        
        # LoRA configuration optimized for property management
        lora_config = LoraConfig(
            r=16,  # Rank
            lora_alpha=32,  # LoRA scaling parameter
            target_modules=["c_attn", "c_proj"],  # DialoGPT attention modules
            lora_dropout=0.1,
            bias="none",
            task_type="CAUSAL_LM",
        )
        
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
        
        logger.info("✅ LoRA configuration applied")

    def load_and_preprocess_dataset(self):
        """Load and preprocess the ZRS property management dataset."""
        logger.info(f"📊 Loading dataset from: {self.dataset_path}")
        
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")
        
        # Load JSONL data
        data = []
        with open(self.dataset_path, "r") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data.append(json.loads(line.strip()))
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping invalid JSON on line {line_num}: {e}")
        
        if not data:
            raise ValueError("No valid training data found")
        
        logger.info(f"📈 Loaded {len(data)} training examples")
        
        # Convert to HuggingFace dataset
        self.dataset = Dataset.from_list(data)
        
        # Tokenize dataset
        self.dataset = self.dataset.map(
            self._tokenize_function,
            batched=True,
            remove_columns=self.dataset.column_names
        )
        
        logger.info("✅ Dataset preprocessing complete")

    def _format_zrs_prompt(self, instruction: str, output: str = "") -> str:
        """Format training prompt specifically for ZRS property management."""
        prompt = f"""### ZRS Property Management Assistant

You are Jade, an AI assistant specialized in ZRS property management. You help with:
- Rent collection and late notices
- Maintenance requests and vendor coordination
- Tenant communication and broadcasts
- Unit turnover and preparation
- Delinquency tracking and reporting

Respond with the appropriate tool command for ZRS operations.

### Property Manager Request:
{instruction}

### Jade Response:
{output}"""
        
        return prompt

    def _tokenize_function(self, examples):
        """Tokenize training examples for ZRS property management."""
        prompts = []
        
        for i in range(len(examples["instruction"])):
            # Format with ZRS-specific prompt template
            prompt = self._format_zrs_prompt(
                examples["instruction"][i],
                examples["output"][i]
            )
            prompts.append(prompt)
        
        # Tokenize
        tokenized = self.tokenizer(
            prompts,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        # Labels for causal language modeling
        tokenized["labels"] = tokenized["input_ids"].clone()
        
        return tokenized

    def setup_training_args(self):
        """Setup training arguments optimized for local ZRS training."""
        return TrainingArguments(
            output_dir=self.output_dir,
            per_device_train_batch_size=self.batch_size,
            gradient_accumulation_steps=2,
            warmup_steps=self.warmup_steps,
            num_train_epochs=self.num_epochs,
            learning_rate=self.learning_rate,
            fp16=True,
            logging_dir=f"{self.output_dir}/logs",
            logging_steps=10,
            save_strategy="epoch",
            save_total_limit=3,
            evaluation_strategy="no",
            remove_unused_columns=False,
            dataloader_drop_last=True,
            push_to_hub=False,
            report_to=None,
        )

    def train(self):
        """Execute the complete ZRS Jade training process."""
        logger.info("🚀 Starting ZRS Jade AI training...")
        
        try:
            # Setup components
            self.setup_model_and_tokenizer()
            self.setup_lora_config()
            self.load_and_preprocess_dataset()
            
            # Setup trainer
            training_args = self.setup_training_args()
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False,  # Causal LM, not masked LM
            )
            
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=self.dataset,
                tokenizer=self.tokenizer,
                data_collator=data_collator,
            )
            
            # Start training
            logger.info("🏋️ Beginning training process...")
            trainer.train()
            
            # Save the model
            trainer.save_model()
            self.tokenizer.save_pretrained(self.output_dir)
            
            # Save training metadata
            self._save_training_metadata()
            
            logger.info(f"✅ Training complete! Model saved to: {self.output_dir}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            raise

    def _save_training_metadata(self):
        """Save training metadata and configuration."""
        metadata = {
            "model_name": self.model_name,
            "dataset_path": str(self.dataset_path),
            "training_config": {
                "max_length": self.max_length,
                "batch_size": self.batch_size,
                "learning_rate": self.learning_rate,
                "num_epochs": self.num_epochs,
                "warmup_steps": self.warmup_steps
            },
            "training_date": datetime.now().isoformat(),
            "dataset_size": len(self.dataset) if self.dataset else 0,
            "zrs_specialization": "Property Management AI Assistant",
            "supported_tools": [
                "send_late_notice",
                "notify_maintenance", 
                "vendor_suggest",
                "schedule_turnover",
                "query_delinquency",
                "broadcast_notice"
            ]
        }
        
        metadata_path = self.output_dir / "training_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"💾 Training metadata saved to: {metadata_path}")

    def test_model(self, test_prompts: List[str] = None):
        """Test the trained model with property management prompts."""
        if not test_prompts:
            test_prompts = [
                "Send late notice to Tony Stark in unit 401 for $2500, 12 days late",
                "Water leak emergency in unit 303",
                "Schedule turnover for unit 205 after move-out tomorrow",
                "Which HVAC vendor should I use for urgent repair?",
                "Show me tenants more than 30 days late on rent"
            ]
        
        logger.info("🧪 Testing trained model...")
        
        for prompt in test_prompts:
            try:
                formatted_prompt = self._format_zrs_prompt(prompt)
                inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=50,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                response = response.split("### Jade Response:")[-1].strip()
                
                logger.info(f"🏠 Prompt: {prompt}")
                logger.info(f"🤖 Jade: {response}")
                logger.info("-" * 60)
                
            except Exception as e:
                logger.error(f"Error testing prompt '{prompt}': {e}")


def main():
    """Main training function."""
    logger.info("🏢 ZRS Property Management AI Training System")
    logger.info("=" * 60)
    
    # Check for dataset
    dataset_path = Path("htc/datasets/zrs_property_finetune.jsonl")
    if not dataset_path.exists():
        logger.error(f"❌ Dataset not found: {dataset_path}")
        logger.error("Please ensure the ZRS property management dataset exists.")
        sys.exit(1)
    
    try:
        # Initialize trainer
        trainer = ZRSJadeTrainer()
        
        # Run training
        success = trainer.train()
        
        if success:
            # Test the model
            trainer.test_model()
            
            logger.info("🎉 ZRS Jade AI training completed successfully!")
            logger.info("🏠 Jade is now trained for ZRS property management tasks")
            
            # Print usage instructions
            print("\n" + "=" * 60)
            print("🚀 JADE ZRS PROPERTY MANAGEMENT AI READY!")
            print("=" * 60)
            print("Jade can now help with:")
            print("• Late rent notices and collection")
            print("• Maintenance requests and vendor coordination") 
            print("• Unit turnover scheduling")
            print("• Tenant communication and broadcasts")
            print("• Delinquency tracking and reporting")
            print("=" * 60)
            
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()