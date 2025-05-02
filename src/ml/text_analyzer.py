"""
Healthcare text analysis utilities.

Author: Robert Torres
"""

from typing import List, Dict, Any, Tuple
import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score


class HealthcareTextAnalyzer:
    """Analyzer for healthcare-related text data."""

    def __init__(self):
        """Initialize the analyzer."""
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2)
        )
        self.classifier = MultinomialNB()
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        self.pipeline = None

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for analysis.

        Args:
            text: Raw text to process

        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Convert to list of words
        words = text.split()
        
        # Remove stopwords
        stop_words = set(['a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for',
                         'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on',
                         'that', 'the', 'to', 'was', 'were', 'will', 'with'])
        words = [w for w in words if w.lower() not in stop_words]
        
        # Join words back together
        text = ' '.join(words)
        
        return text

    def train(self, texts: List[str], labels: List[str]) -> None:
        """
        Train the text analyzer.

        Args:
            texts: List of training texts
            labels: List of corresponding labels
        """
        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Transform texts to TF-IDF features
        X = self.vectorizer.fit_transform(processed_texts)
        
        # Encode labels
        y = self.label_encoder.fit_transform(labels)
        
        # Store training data and labels
        self.texts = [self.preprocess_text(text) for text in texts]
        self.labels = labels  # Keep original labels for metrics
        self.unique_labels = list(set(labels))
        self.pipeline = self.classifier.fit(X, y)
        self.is_trained = True

    def predict(self, texts: List[str]) -> List[str]:
        """
        Predict labels for texts.

        Args:
            texts: List of texts to classify

        Returns:
            Predicted labels
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
            
        processed_texts = [self.preprocess_text(text) for text in texts]
        X = self.vectorizer.transform(processed_texts)
        y_pred = self.classifier.predict(X)
        return self.label_encoder.inverse_transform(y_pred)

    def predict_proba(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Get prediction probabilities for texts.

        Args:
            texts: List of texts to classify

        Returns:
            List of dictionaries mapping labels to probabilities
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
            
        processed_texts = [self.preprocess_text(text) for text in texts]
        X = self.vectorizer.transform(processed_texts)
        probas = self.classifier.predict_proba(X)
        
        results = []
        labels = self.label_encoder.classes_
        for proba in probas:
            results.append(dict(zip(labels, proba)))
        return results

    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Extract important keywords from text.

        Args:
            text: Text to analyze
            top_k: Number of top keywords to return

        Returns:
            List of (keyword, importance_score) tuples
        """
        processed_text = self.preprocess_text(text)
        X = self.vectorizer.transform([processed_text])
        
        feature_names = self.vectorizer.get_feature_names_out()
        importance_scores = X.toarray()[0]
        
        # Get top n keywords by TF-IDF score
        top_indices = np.argsort(importance_scores)[-top_n:][::-1]
        return [(feature_names[i], importance_scores[i]) for i in top_indices]

    def get_metrics(self) -> Dict[str, float]:
        """
        Get model performance metrics.

        Returns:
            Dictionary containing model metrics
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before getting metrics")
            
        # Get predictions on training data
        X = self.vectorizer.transform(self.texts)
        y_true = self.label_encoder.transform(self.labels)
        y_pred = self.classifier.predict(X)
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        report = classification_report(y_true, y_pred,
                                    target_names=self.label_encoder.classes_,
                                    output_dict=True)
        
        return {
            'num_features': len(self.vectorizer.get_feature_names_out()),
            'num_classes': len(self.labels),
            'vocab_size': len(self.vectorizer.vocabulary_),
            'accuracy': float(accuracy),
            'classification_report': report
        }
        
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze healthcare-related text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary containing analysis results
        """
        # Basic text cleaning
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        
        # Get word frequencies
        words = text.split()
        word_freq = pd.Series(words).value_counts()
        
        # Get TF-IDF features
        tfidf = self.vectorizer.fit_transform([text])
        feature_names = self.vectorizer.get_feature_names_out()
        
        return {
            'word_count': len(words),
            'unique_words': len(word_freq),
            'top_words': word_freq.head(10).to_dict(),
            'key_terms': dict(zip(feature_names, tfidf.toarray()[0]))
        }
    
    def extract_medical_terms(self, text: str) -> List[str]:
        """
        Extract medical terminology from text.

        Args:
            text: Text to analyze

        Returns:
            List of identified medical terms
        """
        # Basic medical term patterns
        patterns = [
            r'\b[A-Z][a-z]+itis\b',  # Inflammation conditions
            r'\b[A-Z][a-z]+oma\b',   # Tumors
            r'\b[A-Z][a-z]+osis\b',  # Medical conditions
            r'\b[A-Z][a-z]+emia\b',  # Blood conditions
        ]
        
        medical_terms = []
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            medical_terms.extend([m.group() for m in matches])
        
        return list(set(medical_terms))
    
    def analyze_clinical_notes(self, notes: List[str]) -> Dict[str, Any]:
        """
        Analyze a collection of clinical notes.

        Args:
            notes: List of clinical notes

        Returns:
            Dictionary containing analysis results
        """
        all_words = []
        all_medical_terms = []
        
        for note in notes:
            words = note.lower().split()
            all_words.extend(words)
            all_medical_terms.extend(self.extract_medical_terms(note))
        
        word_freq = pd.Series(all_words).value_counts()
        term_freq = pd.Series(all_medical_terms).value_counts()
        
        return {
            'total_notes': len(notes),
            'avg_length': np.mean([len(note.split()) for note in notes]),
            'common_words': word_freq.head(20).to_dict(),
            'medical_terms': term_freq.to_dict()
        }