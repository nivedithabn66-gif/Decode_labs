import os
import sys
import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from ml.preprocessing import TextPreprocessor

class DuplicateDetectionService:
    """
    Duplicate Detection Engine. Uses TF-IDF representation and Cosine Similarity
    to match incoming issues against existing stored issue repositories.
    """

    def __init__(self):
        self.preprocessor = TextPreprocessor(lowercase=True, remove_stopwords=True)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)

    def check_duplicates(self, new_title: str, new_body: str, existing_issues: List[Dict[str, Any]], top_k: int = 5, min_threshold: float = 0.35) -> Dict[str, Any]:
        """
        Calculates cosine similarity between incoming issue text and all stored existing issues.
        """
        if not existing_issues:
            return {
                "has_duplicate": False,
                "max_similarity": 0.0,
                "potential_duplicates": []
            }

        new_text = self.preprocessor.preprocess_text(f"{new_title} {new_body}")
        if not new_text:
            return {
                "has_duplicate": False,
                "max_similarity": 0.0,
                "potential_duplicates": []
            }

        # Collect text from existing issues
        existing_texts = [
            self.preprocessor.preprocess_text(f"{issue.get('title', '')} {issue.get('description', issue.get('body', ''))}")
            for issue in existing_issues
        ]

        all_corpus = [new_text] + existing_texts
        tfidf_matrix = self.vectorizer.fit_transform(all_corpus)

        query_vector = tfidf_matrix[0]
        corpus_vectors = tfidf_matrix[1:]

        # Compute cosine similarity
        sim_scores = cosine_similarity(query_vector, corpus_vectors)[0]

        matches = []
        for idx, score in enumerate(sim_scores):
            if score >= min_threshold:
                issue_item = existing_issues[idx]
                matches.append({
                    "issue_id": issue_item.get("id", idx + 1),
                    "title": issue_item.get("title", "Untitled Issue"),
                    "category": issue_item.get("predicted_category", issue_item.get("category", "Bug")),
                    "similarity": round(float(score), 4),
                    "similarity_percentage": round(float(score) * 100, 1),
                    "created_at": issue_item.get("created_at", "2026-08-26"),
                    "status": issue_item.get("status", "open")
                })

        # Sort matches by similarity descending
        matches.sort(key=lambda x: x["similarity"], reverse=True)
        top_matches = matches[:top_k]

        max_sim = top_matches[0]["similarity"] if top_matches else 0.0
        has_dup = max_sim >= 0.70

        return {
            "has_duplicate": has_dup,
            "max_similarity": round(max_sim, 4),
            "max_similarity_percentage": round(max_sim * 100, 1),
            "potential_duplicates": top_matches,
            "total_matches_found": len(matches)
        }
