"""
Score Normalizer Utility

This module provides utility functions for normalizing, comparing, and
transforming recommendation scores from different engines and strategies.
It ensures consistent scoring across the recommendation system.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math
import logging


logger = logging.getLogger(__name__)


class NormalizationMethod(Enum):
    """Enumeration of score normalization methods."""
    MIN_MAX = "min_max"
    Z_SCORE = "z_score"
    PERCENTILE = "percentile"
    SIGMOID = "sigmoid"
    LOG = "log"
    RANK = "rank"


class ScoreScale(Enum):
    """Enumeration of score scales."""
    ZERO_TO_ONE = (0.0, 1.0)
    ZERO_TO_HUNDRED = (0.0, 100.0)
    STANDARD = (-1.0, 1.0)  # Z-score like


@dataclass
class ScoreRange:
    """Represents a range of scores."""
    min_value: float
    max_value: float
    mean: float
    std_dev: float
    
    @property
    def range(self) -> float:
        """Calculate the range of the score."""
        return self.max_value - self.min_value


class ScoreNormalizer:
    """
    Utility class for normalizing recommendation scores.
    
    This class provides various normalization methods to ensure
    consistent scoring across different recommendation engines
    and strategies.
    """
    
    def __init__(self, default_scale: ScoreScale = ScoreScale.ZERO_TO_ONE):
        """
        Initialize the score normalizer.
        
        Args:
            default_scale: Default output scale for normalization
        """
        self.default_scale = default_scale
        self.score_ranges: Dict[str, ScoreRange] = {}
        
        logger.info("Initialized ScoreNormalizer")
    
    def normalize(
        self,
        scores: List[float],
        method: NormalizationMethod = NormalizationMethod.MIN_MAX,
        target_scale: Optional[ScoreScale] = None
    ) -> List[float]:
        """
        Normalize a list of scores.
        
        Args:
            scores: List of raw scores
            method: Normalization method to use
            target_scale: Target output scale
            
        Returns:
            List of normalized scores
        """
        if not scores:
            return []
        
        target = target_scale or self.default_scale
        
        if method == NormalizationMethod.MIN_MAX:
            return self._min_max_normalize(scores, target)
        elif method == NormalizationMethod.Z_SCORE:
            return self._z_score_normalize(scores, target)
        elif method == NormalizationMethod.PERCENTILE:
            return self._percentile_normalize(scores, target)
        elif method == NormalizationMethod.SIGMOID:
            return self._sigmoid_normalize(scores, target)
        elif method == NormalizationMethod.LOG:
            return self._log_normalize(scores, target)
        elif method == NormalizationMethod.RANK:
            return self._rank_normalize(scores, target)
        
        return scores
    
    def _min_max_normalize(
        self,
        scores: List[float],
        target: ScoreScale
    ) -> List[float]:
        """Normalize using min-max scaling."""
        min_val = min(scores)
        max_val = max(scores)
        
        if max_val == min_val:
            # All scores are the same
            return [self._scale_value(0.5, target)] * len(scores)
        
        target_min, target_max = target.value
        
        normalized = []
        for score in scores:
            scaled = (score - min_val) / (max_val - min_val)
            normalized.append(self._scale_value(scaled, target))
        
        return normalized
    
    def _z_score_normalize(
        self,
        scores: List[float],
        target: ScoreScale
    ) -> List[float]:
        """Normalize using z-score."""
        mean = sum(scores) / len(scores)
        
        # Calculate standard deviation
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return [self._scale_value(0.5, target)] * len(scores)
        
        target_min, target_max = target.value
        
        normalized = []
        for score in scores:
            z_score = (score - mean) / std_dev
            # Scale z-score to target range
            scaled = (z_score + 3) / 6  # Maps -3 to 3 to 0 to 1
            normalized.append(self._scale_value(max(0, min(1, scaled)), target))
        
        return normalized
    
    def _percentile_normalize(
        self,
        scores: List[float],
        target: ScoreScale
    ) -> List[float]:
        """Normalize using percentile ranks."""
        sorted_scores = sorted(scores)
        n = len(sorted_scores)
        
        target_min, target_max = target.value
        
        normalized = []
        for score in scores:
            # Find percentile rank
            rank = sum(1 for s in sorted_scores if s < score) / n
            normalized.append(self._scale_value(rank, target))
        
        return normalized
    
    def _sigmoid_normalize(
        self,
        scores: List[float],
        target: ScoreScale
    ) -> List[float]:
        """Normalize using sigmoid function."""
        target_min, target_max = target.value
        
        normalized = []
        for score in scores:
            # Apply sigmoid transformation
            # Shift and scale to prevent saturation
            scaled = 1 / (1 + math.exp(-(score - 0.5) * 10))
            normalized.append(self._scale_value(scaled, target))
        
        return normalized
    
    def _log_normalize(
        self,
        scores: List[float],
        target: ScoreScale
    ) -> List[float]:
        """Normalize using log transformation."""
        target_min, target_max = target.value
        
        # Handle negative values
        min_score = min(scores)
        if min_score <= 0:
            scores = [s - min_score + 1 for s in scores]
        
        log_scores = [math.log(s + 1e-10) for s in scores]
        min_log = min(log_scores)
        max_log = max(log_scores)
        
        if max_log == min_log:
            return [self._scale_value(0.5, target)] * len(scores)
        
        normalized = []
        for score in scores:
            log_val = math.log(score + 1e-10)
            scaled = (log_val - min_log) / (max_log - min_log)
            normalized.append(self._scale_value(scaled, target))
        
        return normalized
    
    def _rank_normalize(
        self,
        scores: List[float],
        target: ScoreScale
    ) -> List[float]:
        """Normalize using rank-based scaling."""
        # Sort and assign ranks
        indexed = list(enumerate(scores))
        sorted_indexed = sorted(indexed, key=lambda x: x[1])
        
        n = len(sorted_indexed)
        target_min, target_max = target.value
        
        ranks = [0] * n
        for rank, (original_idx, _) in enumerate(sorted_indexed):
            ranks[original_idx] = rank
        
        # Normalize ranks to [0, 1]
        normalized = [r / (n - 1) if n > 1 else 0.5 for r in ranks]
        
        return [self._scale_value(n, target) for n in normalized]
    
    def _scale_value(
        self,
        value: float,
        target: ScoreScale
    ) -> float:
        """
        Scale a value to the target scale.
        
        Args:
            value: Value in [0, 1] range
            target: Target scale
            
        Returns:
            Scaled value
        """
        target_min, target_max = target.value
        return target_min + value * (target_max - target_min)
    
    def combine_scores(
        self,
        score_dicts: List[Dict[str, float]],
        weights: Optional[List[float]] = None,
        method: str = "weighted_average"
    ) -> Dict[str, float]:
        """
        Combine scores from multiple sources.
        
        Args:
            score_dicts: List of score dictionaries
            weights: Optional weights for each source
            method: Combination method
            
        Returns:
            Dictionary with combined scores
        """
        if not score_dicts:
            return {}
        
        # Get union of all item IDs
        all_ids = set()
        for scores in score_dicts:
            all_ids.update(scores.keys())
        
        if weights is None:
            weights = [1.0 / len(score_dicts)] * len(score_dicts)
        
        combined = {}
        
        if method == "weighted_average":
            for item_id in all_ids:
                weighted_sum = 0.0
                total_weight = 0.0
                
                for scores, weight in zip(score_dicts, weights):
                    if item_id in scores:
                        weighted_sum += scores[item_id] * weight
                        total_weight += weight
                
                if total_weight > 0:
                    combined[item_id] = weighted_sum / total_weight
                    
        elif method == "harmonic_mean":
            for item_id in all_ids:
                scores = [
                    scores[item_id]
                    for scores in score_dicts
                    if item_id in scores
                ]
                
                if scores and len(scores) > 0:
                    n = len(scores)
                    harmonic = n / sum(1 / max(s, 0.0001) for s in scores)
                    combined[item_id] = harmonic / max(scores)
                    
        elif method == "geometric_mean":
            for item_id in all_ids:
                scores = [
                    scores[item_id]
                    for scores in score_dicts
                    if item_id in scores and scores[item_id] > 0
                ]
                
                if scores:
                    product = math.prod(scores)
                    combined[item_id] = product ** (1 / len(scores))
        
        return combined
    
    def adjust_for_difficulty(
        self,
        scores: Dict[str, float],
        difficulties: Dict[str, str],
        student_level: float
    ) -> Dict[str, float]:
        """
        Adjust scores based on content difficulty and student level.
        
        Args:
            scores: Original scores
            difficulties: Content difficulties
            student_level: Student's current level (0-1)
            
        Returns:
            Difficulty-adjusted scores
        """
        difficulty_multipliers = {
            "foundational": 0.8,
            "intermediate": 1.0,
            "advanced": 1.2,
            "mastery": 1.4
        }
        
        adjusted = {}
        
        for item_id, score in scores.items():
            difficulty = difficulties.get(item_id, "intermediate")
            multiplier = difficulty_multipliers.get(difficulty, 1.0)
            
            # Adjust based on student level
            level_diff = multiplier - (student_level * 0.5 + 0.5)
            adjusted_score = score * (1 + level_diff * 0.2)
            
            adjusted[item_id] = max(0, min(1, adjusted_score))
        
        return adjusted
    
    def apply_confidence_decay(
        self,
        scores: Dict[str, float],
        confidences: Dict[str, float],
        decay_factor: float = 0.9
    ) -> Dict[str, float]:
        """
        Apply confidence-based decay to scores.
        
        Lower confidence scores are decayed more than higher ones.
        
        Args:
            scores: Original scores
            confidences: Confidence values for each item
            decay_factor: Base decay factor
            
        Returns:
            Confidence-adjusted scores
        """
        adjusted = {}
        
        for item_id, score in scores.items():
            confidence = confidences.get(item_id, 0.5)
            
            # Apply decay based on confidence
            decay = decay_factor ** (1 - confidence)
            adjusted[item_id] = score * decay
        
        return adjusted
    
    def calculate_diversity_bonus(
        self,
        scores: Dict[str, float],
        categories: Dict[str, str],
        target_category: Optional[str] = None,
        bonus: float = 0.1
    ) -> Dict[str, float]:
        """
        Calculate diversity bonuses for category coverage.
        
        Args:
            scores: Original scores
            categories: Item categories
            target_category: Target category to boost
            bonus: Bonus amount
            
        Returns:
            Scores with diversity bonuses
        """
        adjusted = dict(scores)
        
        # Count categories in current top items
        top_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
        category_counts = {}
        
        for item_id, _ in top_items:
            category = categories.get(item_id, "unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Boost underrepresented categories
        if target_category:
            target_count = category_counts.get(target_category, 0)
            
            if target_count < 2:  # Underrepresented
                for item_id, category in categories.items():
                    if category == target_category:
                        adjusted[item_id] = min(
                            1.0,
                            adjusted.get(item_id, 0) + bonus
                        )
        
        return adjusted
    
    def compute_normalized_discounted_cumulative_gain(
        self,
        scores: Dict[str, float],
        relevance_scores: Dict[str, float],
        k: int = 10
    ) -> float:
        """
        Compute NDCG (Normalized Discounted Cumulative Gain).
        
        Measures ranking quality based on relevance scores.
        
        Args:
            scores: Predicted scores
            relevance_scores: Actual relevance scores
            k: Cut-off position
            
        Returns:
            NDCG score
        """
        # Sort items by predicted score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
        
        # Calculate DCG
        dcg = 0.0
        for i, (item_id, _) in enumerate(ranked):
            relevance = relevance_scores.get(item_id, 0)
            dcg += relevance / math.log2(i + 2)  # i+2 because log2(1) = 0
        
        # Calculate ideal DCG (sorted by actual relevance)
        ideal_ranked = sorted(
            relevance_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:k]
        
        idcg = 0.0
        for i, (_, relevance) in enumerate(ideal_ranked):
            idcg += relevance / math.log2(i + 2)
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def compute_reciprocal_rank(
        self,
        scores: Dict[str, float],
        target_id: str
    ) -> float:
        """
        Compute Reciprocal Rank.
        
        Measures the rank of the first correct item.
        
        Args:
            scores: Predicted scores
            target_id: ID of the target item
            
        Returns:
            Reciprocal rank score
        """
        if target_id not in scores:
            return 0.0
        
        # Find rank (1-indexed)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        for i, (item_id, _) in enumerate(ranked):
            if item_id == target_id:
                return 1.0 / (i + 1)
        
        return 0.0
    
    def compute_precision_at_k(
        self,
        scores: Dict[str, float],
        relevant_ids: set,
        k: int = 10
    ) -> float:
        """
        Compute Precision at K.
        
        Measures the proportion of relevant items in top K.
        
        Args:
            scores: Predicted scores
            relevant_ids: Set of relevant item IDs
            k: Cut-off position
            
        Returns:
            Precision at K
        """
        ranked = list(scores.items())[:k]
        
        if not ranked:
            return 0.0
        
        relevant_count = sum(1 for item_id, _ in ranked if item_id in relevant_ids)
        
        return relevant_count / k
    
    def compute_recall_at_k(
        self,
        scores: Dict[str, float],
        relevant_ids: set,
        k: int = 10
    ) -> float:
        """
        Compute Recall at K.
        
        Measures the proportion of relevant items retrieved in top K.
        
        Args:
            scores: Predicted scores
            relevant_ids: Set of relevant item IDs
            k: Cut-off position
            
        Returns:
            Recall at K
        """
        ranked = list(scores.items())[:k]
        
        if not relevant_ids:
            return 1.0
        
        relevant_count = sum(1 for item_id, _ in ranked if item_id in relevant_ids)
        
        return relevant_count / len(relevant_ids)
    
    def compute_f1_at_k(
        self,
        scores: Dict[str, float],
        relevant_ids: set,
        k: int = 10
    ) -> float:
        """
        Compute F1 Score at K.
        
        Harmonic mean of precision and recall.
        
        Args:
            scores: Predicted scores
            relevant_ids: Set of relevant item IDs
            k: Cut-off position
            
        Returns:
            F1 score at K
        """
        precision = self.compute_precision_at_k(scores, relevant_ids, k)
        recall = self.compute_recall_at_k(scores, relevant_ids, k)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
    def evaluate_recommendation_quality(
        self,
        scores: Dict[str, float],
        relevance_scores: Dict[str, float],
        relevant_ids: set,
        k: int = 10
    ) -> Dict[str, float]:
        """
        Comprehensive evaluation of recommendation quality.
        
        Args:
            scores: Predicted scores
            relevance_scores: Actual relevance scores
            relevant_ids: Set of relevant item IDs
            k: Cut-off position
            
        Returns:
            Dictionary with multiple evaluation metrics
        """
        return {
            "ndcg": self.compute_normalized_discounted_cumulative_gain(
                scores, relevance_scores, k
            ),
            "precision_at_k": self.compute_precision_at_k(scores, relevant_ids, k),
            "recall_at_k": self.compute_recall_at_k(scores, relevant_ids, k),
            "f1_at_k": self.compute_f1_at_k(scores, relevant_ids, k)
        }
    
    def denormalize(
        self,
        normalized_score: float,
        original_min: float,
        original_max: float
    ) -> float:
        """
        Denormalize a score back to original range.
        
        Args:
            normalized_score: Score in normalized [0, 1] range
            original_min: Original minimum value
            original_max: Original maximum value
            
        Returns:
            Denormalized score
        """
        return original_min + normalized_score * (original_max - original_min)
    
    def store_range(self, source: str, scores: List[float]):
        """
        Store the score range for a source.
        
        Useful for consistent normalization across calls.
        
        Args:
            source: Source identifier
            scores: Scores to compute range from
        """
        if not scores:
            return
        
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = math.sqrt(variance)
        
        self.score_ranges[source] = ScoreRange(
            min_value=min(scores),
            max_value=max(scores),
            mean=mean,
            std_dev=std_dev
        )
    
    def normalize_with_stored_range(
        self,
        scores: List[float],
        source: str,
        method: NormalizationMethod = NormalizationMethod.MIN_MAX
    ) -> List[float]:
        """
        Normalize using stored range for the source.
        
        Args:
            scores: Scores to normalize
            source: Source identifier
            method: Normalization method
            
        Returns:
            Normalized scores
        """
        if source not in self.score_ranges:
            self.store_range(source, scores)
        
        range_info = self.score_ranges[source]
        
        if method == NormalizationMethod.MIN_MAX:
            if range_info.range == 0:
                return [0.5] * len(scores)
            return [
                (s - range_info.min_value) / range_info.range
                for s in scores
            ]
        
        # For other methods, use standard normalization
        return self.normalize(scores, method)
