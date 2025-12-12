#!/usr/bin/env python3
"""
Train TrOCR model on handwritten prescription dataset
Fine-tunes microsoft/trocr-base-handwritten on medication names
"""
import sys
import os
import base64
from io import BytesIO

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from transformers import (
    TrOCRProcessor,
    VisionEncoderDecoderModel,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    default_data_collator
)
from datasets import load_metric
import numpy as np

from app.main import create_app
from app.database import get_db
from app.models.training_image import TrainingImage


class HandwrittenMedicationDataset(Dataset):
    """Dataset for handwritten medication name images"""
    
    def __init__(self, split='Training', processor=None):
        """
        Args:
            split: 'Training', 'Testing', or 'Validation'
            processor: TrOCRProcessor instance
        """
        self.processor = processor
        self.split = split
        
        # Load from database
        app = create_app()
        with app.app_context():
            db = get_db()
            
            # Map splits to database tags
            split_filter = f"%{split.lower()}%"
            
            # Get all handwritten training images from this split
            query = db.query(TrainingImage).filter(
                TrainingImage.image_type == 'handwritten',
                TrainingImage.is_training_data == True
            )
            
            # Filter by examining corrected_text for split indicator
            # Since we stored them sequentially, we can use ID ranges
            # Or we could add a split column - for now use all and split manually
            all_images = query.all()
            
            # Manual split based on our load order:
            # Training: 0-3003, Testing: 3004-3760, Validation: 3761-4498
            if split == 'Training':
                self.images = all_images[:3004]
            elif split == 'Testing':
                self.images = all_images[3004:3761]
            else:  # Validation
                self.images = all_images[3761:]
        
        print(f"Loaded {len(self.images)} images for {split}")
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_record = self.images[idx]
        
        # Decode base64 image
        image_bytes = base64.b64decode(img_record.image_data)
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        
        # Get text label (use corrected_text which has full label)
        # Format: "BrandName (GenericName)" - we want just the brand name
        text = img_record.extracted_text or img_record.corrected_text
        if '(' in text:
            text = text.split('(')[0].strip()
        
        # Process with TrOCR processor
        pixel_values = self.processor(image, return_tensors="pt").pixel_values
        labels = self.processor.tokenizer(
            text,
            padding="max_length",
            max_length=64,
            truncation=True
        ).input_ids
        
        # Convert labels to tensor
        labels = torch.tensor(labels)
        # Replace padding token id's with -100 (ignored by loss)
        labels[labels == self.processor.tokenizer.pad_token_id] = -100
        
        encoding = {
            "pixel_values": pixel_values.squeeze(),
            "labels": labels
        }
        
        return encoding


def compute_cer(pred_str, label_str):
    """Compute Character Error Rate"""
    from jiwer import cer
    return cer(label_str, pred_str)


def compute_metrics(pred):
    """Compute CER metric for evaluation"""
    labels_ids = pred.label_ids
    pred_ids = pred.predictions
    
    # Decode predictions and labels
    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
    
    pred_str = processor.batch_decode(pred_ids, skip_special_tokens=True)
    labels_ids[labels_ids == -100] = processor.tokenizer.pad_token_id
    label_str = processor.batch_decode(labels_ids, skip_special_tokens=True)
    
    # Compute CER
    cer_score = compute_cer(pred_str, label_str)
    
    return {"cer": cer_score}


def train_trocr_model(
    output_dir="./models/trocr_finetuned",
    num_epochs=10,
    batch_size=8,
    learning_rate=5e-5
):
    """
    Train TrOCR model on handwritten medication dataset
    
    Args:
        output_dir: Where to save the trained model
        num_epochs: Number of training epochs
        batch_size: Training batch size
        learning_rate: Learning rate for optimizer
    """
    print("\n" + "="*70)
    print("TrOCR Training - Handwritten Medication Recognition")
    print("="*70 + "\n")
    
    # Check for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    print()
    
    # Load processor and model
    print("Loading pretrained TrOCR model...")
    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
    model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")
    model.to(device)
    
    # Set model configuration
    model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
    model.config.pad_token_id = processor.tokenizer.pad_token_id
    model.config.vocab_size = model.config.decoder.vocab_size
    model.config.eos_token_id = processor.tokenizer.sep_token_id
    model.config.max_length = 64
    model.config.early_stopping = True
    model.config.no_repeat_ngram_size = 3
    model.config.length_penalty = 2.0
    model.config.num_beams = 4
    
    # Load datasets
    print("\nLoading datasets...")
    train_dataset = HandwrittenMedicationDataset('Training', processor)
    val_dataset = HandwrittenMedicationDataset('Validation', processor)
    test_dataset = HandwrittenMedicationDataset('Testing', processor)
    
    # Training arguments
    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        predict_with_generate=True,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_steps=100,
        num_train_epochs=num_epochs,
        learning_rate=learning_rate,
        warmup_steps=500,
        weight_decay=0.01,
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model="cer",
        greater_is_better=False,
        fp16=torch.cuda.is_available(),  # Use mixed precision if GPU available
    )
    
    # Initialize trainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=processor.feature_extractor,
        data_collator=default_data_collator,
        compute_metrics=compute_metrics,
    )
    
    # Train!
    print("\n" + "="*70)
    print("STARTING TRAINING")
    print("="*70)
    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    print(f"Test samples: {len(test_dataset)}")
    print(f"Epochs: {num_epochs}")
    print(f"Batch size: {batch_size}")
    print(f"Learning rate: {learning_rate}")
    print("="*70 + "\n")
    
    trainer.train()
    
    # Evaluate on test set
    print("\n" + "="*70)
    print("EVALUATING ON TEST SET")
    print("="*70 + "\n")
    
    test_results = trainer.evaluate(test_dataset)
    print(f"\nTest CER: {test_results['eval_cer']:.4f}")
    print(f"Test Loss: {test_results['eval_loss']:.4f}")
    
    # Save final model
    print("\n" + "="*70)
    print("SAVING MODEL")
    print("="*70 + "\n")
    
    trainer.save_model(output_dir)
    processor.save_pretrained(output_dir)
    
    print(f"✅ Model saved to: {output_dir}")
    print(f"✅ Training complete!")
    print(f"\nFinal test CER: {test_results['eval_cer']:.4f}")
    print("="*70 + "\n")
    
    return test_results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train TrOCR on handwritten prescriptions")
    parser.add_argument('--epochs', type=int, default=10, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=8, help='Batch size')
    parser.add_argument('--lr', type=float, default=5e-5, help='Learning rate')
    parser.add_argument('--output', type=str, default='./models/trocr_finetuned', 
                       help='Output directory')
    
    args = parser.parse_args()
    
    train_trocr_model(
        output_dir=args.output,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr
    )
