#!/usr/bin/env python3
"""
HTC CLI Tool - Command Line Interface for Human-Trainable Computer
=================================================================

Test and interact with the HTC autonomous learning system from the command line.
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import List

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from logic.htc_trainer import get_htc_trainer, train_on_task
    HTC_AVAILABLE = True
except ImportError as e:
    print(f"Error: Could not import HTC trainer: {e}")
    print("Make sure you're running from the HTC directory")
    HTC_AVAILABLE = False
    sys.exit(1)

def print_banner():
    """Print HTC CLI banner."""
    print("=" * 60)
    print("🧠 HTC CLI - Human-Trainable Computer")
    print("   Autonomous Learning System for Jade Assistant")
    print("=" * 60)
    print()

async def train_command(args):
    """Execute HTC training command."""
    print(f"🚀 Starting HTC training session...")
    print(f"Task: {args.task}")
    print(f"Files: {args.files}")
    print(f"Outputs: {args.outputs}")
    print()
    
    try:
        # Copy files to intake directory if they exist
        trainer = get_htc_trainer()
        copied_files = []
        
        for file_path in args.files:
            file_path = Path(file_path)
            if file_path.exists():
                dest_path = trainer.intake_path / file_path.name
                import shutil
                shutil.copy2(file_path, dest_path)
                copied_files.append(file_path.name)
                print(f"📁 Copied {file_path.name} to intake directory")
            else:
                print(f"⚠️  File not found: {file_path}")
        
        if not copied_files:
            print("❌ No valid files to process")
            return
        
        # Start training
        print(f"\n🔄 Training Jade on task...")
        results = await train_on_task(
            task=args.task,
            files=copied_files,
            outputs=args.outputs,
            tags=args.tags
        )
        
        # Display results
        print(f"\n✅ Training completed!")
        print(f"Session ID: {results['session_id']}")
        print(f"Execution time: {results.get('execution_time', 0):.2f}s")
        print()
        
        # Show generated assets
        if results['generated']:
            print("🎯 Generated Assets:")
            for output_type, result in results['generated'].items():
                status = result.get('status', 'unknown')
                if status == 'success':
                    print(f"  ✅ {output_type.upper()}: {result.get('file_path', result.get('entry_id', 'Generated successfully'))}")
                else:
                    print(f"  ❌ {output_type.upper()}: {result.get('error', result.get('reason', 'Failed'))}")
        
        if results['errors']:
            print("\n⚠️  Errors:")
            for error in results['errors']:
                print(f"  - {error}")
        
        print(f"\n💾 Session saved to: htc/test_history/session_{results['session_id']}.json")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")

async def history_command(args):
    """Display training history."""
    print("📜 HTC Training History")
    print("-" * 40)
    
    try:
        trainer = get_htc_trainer()
        history = trainer.get_training_history()
        
        if not history:
            print("No training sessions found.")
            return
        
        for session in history[:args.limit]:
            print(f"\n🔹 Session: {session['session_id']}")
            print(f"   Date: {session['timestamp']}")
            print(f"   Task: {session['task'][:80]}...")
            print(f"   Files: {len(session['files_processed'])}")
            print(f"   Outputs: {', '.join(session['outputs_requested'])}")
            
            # Show generated assets
            generated = session.get('generated', {})
            successful = [k for k, v in generated.items() if v.get('status') == 'success']
            if successful:
                print(f"   Generated: {', '.join(successful)}")
    
    except Exception as e:
        print(f"❌ Failed to get history: {e}")

async def assets_command(args):
    """Display generated assets."""
    print("📦 Generated HTC Assets")
    print("-" * 40)
    
    try:
        trainer = get_htc_trainer()
        assets = trainer.get_generated_assets()
        
        for asset_type, files in assets.items():
            print(f"\n🔹 {asset_type.upper()}:")
            if files:
                for file in files:
                    print(f"   - {file}")
            else:
                print("   (none)")
    
    except Exception as e:
        print(f"❌ Failed to get assets: {e}")

def status_command(args):
    """Display HTC system status."""
    print("🔍 HTC System Status")
    print("-" * 40)
    
    if not HTC_AVAILABLE:
        print("❌ HTC system is not available")
        return
    
    print("✅ HTC system is available")
    
    try:
        trainer = get_htc_trainer()
        
        # Check directories
        print(f"\n📁 Directories:")
        print(f"   Intake: {trainer.intake_path} {'✅' if trainer.intake_path.exists() else '❌'}")
        print(f"   Tools: {trainer.tools_path} {'✅' if trainer.tools_path.exists() else '❌'}")
        print(f"   Models: {trainer.models_path} {'✅' if trainer.models_path.exists() else '❌'}")
        print(f"   History: {trainer.test_history_path} {'✅' if trainer.test_history_path.exists() else '❌'}")
        
        # Check assets
        assets = trainer.get_generated_assets()
        print(f"\n📊 Asset Counts:")
        for asset_type, files in assets.items():
            print(f"   {asset_type}: {len(files)}")
        
        # Check history
        history = trainer.get_training_history()
        print(f"\n📜 Training Sessions: {len(history)}")
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="HTC CLI - Human-Trainable Computer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train on CSV data to generate analysis tools
  python cli.py train "Analyze customer data and generate risk scores" data.csv --outputs tool model rag

  # Train on documentation to create knowledge base
  python cli.py train "Learn API documentation" api_docs.md --outputs rag action --tags api documentation

  # View training history
  python cli.py history

  # Check system status
  python cli.py status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Start HTC training session')
    train_parser.add_argument('task', help='Description of what Jade should learn')
    train_parser.add_argument('files', nargs='+', help='Files to learn from')
    train_parser.add_argument('--outputs', nargs='+', 
                            choices=['tool', 'model', 'rag', 'action'],
                            default=['tool', 'rag'],
                            help='What to generate (default: tool rag)')
    train_parser.add_argument('--tags', nargs='+', default=[],
                            help='Tags for categorization')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show training history')
    history_parser.add_argument('--limit', type=int, default=10,
                               help='Number of sessions to show (default: 10)')
    
    # Assets command
    assets_parser = subparsers.add_parser('assets', help='List generated assets')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    print_banner()
    
    # Execute command
    if args.command == 'train':
        asyncio.run(train_command(args))
    elif args.command == 'history':
        asyncio.run(history_command(args))
    elif args.command == 'assets':
        asyncio.run(assets_command(args))
    elif args.command == 'status':
        status_command(args)

if __name__ == "__main__":
    main()