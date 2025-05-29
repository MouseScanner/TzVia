import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import numpy as np
from sqlalchemy import select
from database import async_session_maker, MovieReview
import asyncio

class ModelManager:
    def __init__(self):
        self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        self.model = None
        self.sentence_model = SentenceTransformer('distilbert-base-nli-mean-tokens')
        
    def train_model(self):
        dataset = load_dataset("imdb", split="train[:5000]")
        
        def tokenize_function(examples):
            return self.tokenizer(examples['text'], truncation=True, padding=True, max_length=512)
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        tokenized_dataset = tokenized_dataset.rename_column("label", "labels")
        
        model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
        
        training_args = TrainingArguments(
            output_dir='./results',
            num_train_epochs=2,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=64,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir='./logs',
            save_strategy="no"
        )
        
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            tokenizer=self.tokenizer,
        )
        
        trainer.train()
        model.save_pretrained('./fine_tuned_model')
        self.tokenizer.save_pretrained('./fine_tuned_model')
        self.model = model
        
    def get_embedding(self, text):
        return self.sentence_model.encode(text)
    
    async def populate_database(self):
        dataset = load_dataset("imdb", split="test[:1000]")
        
        async with async_session_maker() as session:
            for item in dataset:
                text = item['text']
                sentiment = item['label']
                embedding = self.get_embedding(text)
                
                review = MovieReview(
                    text=text,
                    sentiment=sentiment,
                    embedding=embedding.tolist()
                )
                session.add(review)
            
            await session.commit()

model_manager = ModelManager() 