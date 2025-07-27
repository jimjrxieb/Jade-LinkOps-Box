#!/usr/bin/env python3
"""
Jade Property Management Fine-Tuning Script
==========================================

Fine-tunes Jade AI assistant for property management workflows using LoRA.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import torch
from datasets import Dataset, load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class JadePropertyTrainer:
    """
    LoRA fine-tuning trainer for Jade property management assistant.
    """

    def __init__(
        self,
        model_name: str = "microsoft/DialoGPT-medium",
        dataset_path: str = "htc/datasets/tool_usage_finetune.jsonl",
        output_dir: str = "./models/jade-property-lora",
    ):
        """Initialize the trainer."""
        self.model_name = model_name
        self.dataset_path = dataset_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Training configuration
        self.max_length = 512
        self.batch_size = 2
        self.learning_rate = 2e-4
        self.num_epochs = 3
        
        # Initialize components
        self.tokenizer = None
        self.model = None
        self.dataset = None

    def setup_model_and_tokenizer(self):
        """Setup model and tokenizer with quantization."""
        logger.info(f"Loading model: {self.model_name}")
        
        # Quantization config for efficient training
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
        
        # Prepare model for k-bit training
        self.model = prepare_model_for_kbit_training(self.model)
        
        logger.info("Model and tokenizer loaded successfully")

    def setup_lora_config(self):
        """Setup LoRA configuration."""
        lora_config = LoraConfig(
            r=16,  # Rank
            lora_alpha=32,  # LoRA scaling parameter
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
            lora_dropout=0.1,
            bias="none",
            task_type="CAUSAL_LM",
        )
        
        self.model = get_peft_model(self.model, lora_config)
        logger.info("LoRA configuration applied")

    def load_dataset(self):
        """Load and preprocess the property management dataset."""
        logger.info(f"Loading dataset from: {self.dataset_path}")
        
        # Load JSONL data
        data = []
        with open(self.dataset_path, "r") as f:
            for line in f:
                data.append(json.loads(line.strip()))
        
        # Convert to HuggingFace dataset
        self.dataset = Dataset.from_list(data)
        logger.info(f"Loaded {len(data)} training examples")

    def format_prompt(self, instruction: str, input_text: str = "", output: str = "") -> str:
        """Format training prompt for property management context."""
        prompt = f"""### Property Management Assistant

You are Jade, an AI assistant specialized in property management. You help with:
- Rent collection and delinquency management
- Maintenance requests and vendor coordination  
- Lease administration and renewals
- Tenant communication and inspections
- Financial reporting and compliance

### Instruction:
{instruction}

### Input:
{input_text}

### Response:
{output}"""
        
        return prompt

    def tokenize_function(self, examples):
        """Tokenize training examples."""
        prompts = []
        for i in range(len(examples["instruction"])):
            prompt = self.format_prompt(
                examples["instruction"][i],
                examples["input"][i],
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
        
        # Set labels for causal language modeling
        tokenized["labels"] = tokenized["input_ids"].clone()
        
        return tokenized

    def preprocess_dataset(self):
        """Preprocess the dataset for training."""
        logger.info("Preprocessing dataset...")
        
        # Tokenize dataset
        self.dataset = self.dataset.map(
            self.tokenize_function,
            batched=True,
            remove_columns=self.dataset.column_names
        )
        
        logger.info("Dataset preprocessing complete")

    def setup_training_args(self):
        """Setup training arguments."""
        return TrainingArguments(
            output_dir=self.output_dir,
            per_device_train_batch_size=self.batch_size,
            gradient_accumulation_steps=4,
            warmup_steps=100,
            num_train_epochs=self.num_epochs,
            learning_rate=self.learning_rate,
            fp16=True,
            logging_dir=f"{self.output_dir}/logs",
            logging_steps=10,
            save_strategy="epoch",
            save_total_limit=3,
            evaluation_strategy="no",
            remove_unused_columns=False,
            push_to_hub=False,
            report_to=None,
        )

    def train(self):
        """Execute the training process."""
        logger.info("Starting Jade property management training...")
        
        # Setup components
        self.setup_model_and_tokenizer()
        self.setup_lora_config()
        self.load_dataset()
        self.preprocess_dataset()
        
        # Setup trainer
        training_args = self.setup_training_args()
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.dataset,
            tokenizer=self.tokenizer,
        )
        
        # Train the model
        logger.info("Beginning training...")
        trainer.train()
        
        # Save the model
        trainer.save_model()
        self.tokenizer.save_pretrained(self.output_dir)
        
        logger.info(f"Training complete! Model saved to: {self.output_dir}")

    def generate_property_response(self, instruction: str, max_length: int = 200) -> str:
        """Generate a response for property management instruction."""
        if not self.model or not self.tokenizer:
            raise ValueError("Model not loaded. Run train() first.")
        
        prompt = self.format_prompt(instruction)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.split("### Response:")[-1].strip()


def main():
    """Main training function."""
    trainer = JadePropertyTrainer()
    
    try:
        trainer.train()
        
        # Test the trained model
        logger.info("Testing trained model...")
        test_instructions = [
            "Send late rent notice to tenant in unit 205",
            "Schedule maintenance for HVAC repair",
            "Find tenants more than 30 days late on rent"
        ]
        
        for instruction in test_instructions:
            response = trainer.generate_property_response(instruction)
            logger.info(f"Instruction: {instruction}")
            logger.info(f"Response: {response}")
            logger.info("-" * 50)
            
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise


if __name__ == "__main__":
    main()