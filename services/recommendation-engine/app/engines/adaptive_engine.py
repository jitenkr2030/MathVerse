"""
Adaptive Recommendation Engine

This module implements an adaptive recommendation system that combines
multiple recommendation strategies and dynamically adjusts its approach
based on student feedback, performance patterns, and learning outcomes.

The adaptive engine uses techniques from collaborative filtering,
reinforcement learning, and multi-armed bandit algorithms to optimize
recommendations over time while respecting pedagogical constraints.
"""

from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import random
import math

from .rule_based import RuleBasedEngine, Rule
from .graph_based import GraphBasedEngine, ConceptDependencyGraph, TraversalStrategy
from ..schemas import (
    StudentProfile,
    ContentItem,
    LearningEvent,
    LearningPath,
    RecommendationReason,
    AdaptationSignal
)


logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Enumeration of recommendation strategy types."""
    RULE_BASED = "rule_based"
    GRAPH_BASED = "graph_based"
    COLLABORATIVE = "collaborative"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"


@dataclass
class StrategyWeight:
    """Represents the weight and performance metrics for a strategy."""
    strategy_type: StrategyType
    weight: float
    success_rate: float = 0.5
    total_uses: int = 0
    successful_uses: int = 0
    average_engagement: float = 0.5
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_feedback(
        self,
        engagement_score: float,
        success: bool,
        learning_gain: float
    ):
        """
        Update strategy metrics based on feedback.
        
        Args:
            engagement_score: How engaged the student was (0-1)
            success: Whether the recommendation was successful
            learning_gain: Measured learning improvement (0-1)
        """
        self.total_uses += 1
        self.average_engagement = (
            (self.average_engagement * (self.total_uses - 1) + engagement_score)
            / self.total_uses
        )
        
        if success:
            self.successful_uses += 1
        
        # Update success rate
        self.success_rate = self.successful_uses / self.total_uses if self.total_uses > 0 else 0.5
        
        self.last_updated = datetime.now()


@dataclass
class BanditState:
    """State for multi-armed bandit exploration-exploitation."""
    strategy_weights: Dict[StrategyType, StrategyWeight] = field(default_factory=dict)
    exploration_rate: float = 0.2  # Initial exploration rate
    min_exploration: float = 0.05  # Minimum exploration rate
    exploration_decay: float = 0.995  # Decay factor per update
    learning_rate: float = 0.1  # Learning rate for weight updates
    
    def __post_init__(self):
        """Initialize default strategy weights."""
        if not self.strategy_weights:
            for strategy in StrategyType:
                self.strategy_weights[strategy] = StrategyWeight(
                    strategy_type=strategy,
                    weight=1.0 / len(StrategyType)  # Equal initial weights
                )
    
    def select_strategy(self) -> StrategyType:
        """
        Select a strategy using epsilon-greedy with annealing.
        
        Returns:
            Selected strategy type
        """
        # Anneal exploration rate
        self.exploration_rate = max(
            self.min_exploration,
            self.exploration_rate * self.exploration_decay
        )
        
        # Epsilon-greedy selection
        if random.random() < self.exploration_rate:
            # Explore: select random strategy
            return random.choice(list(StrategyType))
        else:
            # Exploit: select best strategy
            best_strategy = max(
                self.strategy_weights.items(),
                key=lambda x: x[1].weight
            )
            return best_strategy[0]
    
    def update_strategy(
        self,
        strategy: StrategyType,
        reward: float
    ):
        """
        Update strategy weights based on received reward.
        
        Uses softmax-like update for weight adjustment.
        
        Args:
            strategy: The strategy that was used
            reward: The reward received (0-1)
        """
        current_weight = self.strategy_weights[strategy].weight
        
        # Update based on reward
        if reward > 0.5:
            # Positive reward: increase weight
            adjustment = self.learning_rate * (reward - 0.5) * 2
            new_weight = min(1.0, current_weight + adjustment)
        else:
            # Negative reward: decrease weight
            adjustment = self.learning_rate * (0.5 - reward) * 2
            new_weight = max(0.1, current_weight - adjustment)
        
        self.strategy_weights[strategy].weight = new_weight
        
        # Normalize weights
        total = sum(w.weight for w in self.strategy_weights.values())
        if total > 0:
            for sw in self.strategy_weights.values():
                sw.weight /= total


@dataclass
class StudentContext:
    """Current context for adaptive decision making."""
    student_id: str
    current_mood: str = "neutral"  # engaged, frustrated, bored, confused
    session_duration: int = 0  # minutes
    recent_performance: List[float] = field(default_factory=list)
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    time_of_day: str = "day"  # morning, afternoon, evening, night
    day_of_week: str = "weekday"  # weekday, weekend
    
    def get_engagement_level(self) -> str:
        """Determine current engagement level."""
        if not self.recent_performance:
            return "neutral"
        
        avg_performance = sum(self.recent_performance) / len(self.recent_performance)
        
        if avg_performance >= 0.8 and self.consecutive_successes >= 3:
            return "engaged"
        elif avg_performance < 0.5 and self.consecutive_failures >= 2:
            return "frustrated"
        elif self.consecutive_failures >= 4:
            return "confused"
        elif avg_performance < 0.6 and self.session_duration > 30:
            return "bored"
        
        return "neutral"
    
    def update_performance(self, score: float):
        """Update performance tracking."""
        self.recent_performance.append(score)
        
        # Keep only last 10 scores
        if len(self.recent_performance) > 10:
            self.recent_performance = self.recent_performance[-10:]
        
        # Update consecutive counters
        if score >= 0.7:
            self.consecutive_successes += 1
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1
            self.consecutive_successes = 0


class AdaptiveEngine:
    """
    Engine that adaptively combines multiple recommendation strategies.
    
    This engine uses multi-armed bandit algorithms to balance exploration
    and exploitation across different recommendation strategies. It adapts
    to student feedback and performance patterns to optimize recommendations
    over time.
    """
    
    def __init__(
        self,
        rule_engine: Optional[RuleBasedEngine] = None,
        graph_engine: Optional[GraphBasedEngine] = None
    ):
        """
        Initialize the adaptive recommendation engine.
        
        Args:
            rule_engine: Optional pre-initialized rule-based engine
            graph_engine: Optional pre-initialized graph-based engine
        """
        self.rule_engine = rule_engine or RuleBasedEngine()
        self.graph_engine = graph_engine or GraphBasedEngine()
        
        # Bandit state for strategy selection
        self.bandit_state = BanditState()
        
        # Student contexts (in production, use cache/database)
        self.student_contexts: Dict[str, StudentContext] = {}
        
        # Performance history for each student
        self.performance_history: Dict[str, List[LearningEvent]] = defaultdict(list)
        
        # Adaptation rules for context-sensitive adjustments
        self.adaptation_rules: List[Callable] = []
        
        self._initialize_adaptation_rules()
        
        logger.info("Initialized adaptive recommendation engine")
    
    def _initialize_adaptation_rules(self):
        """Initialize context adaptation rules."""
        
        def adjust_for_frustration(context: StudentContext) -> Dict[str, Any]:
            """Adjust recommendations when student is frustrated."""
            if context.get_engagement_level() == "frustrated":
                return {
                    "difficulty_adjustment": -0.5,
                    "content_type_preference": ["tutorial", "practice"],
                    "break_recommended": True
                }
            return {}
        
        def adjust_for_boredom(context: StudentContext) -> Dict[str, Any]:
            """Adjust recommendations when student is bored."""
            if context.get_engagement_level() == "bored":
                return {
                    "difficulty_adjustment": 0.3,
                    "content_type_preference": ["challenge", "game", "interactive"],
                    "variety_boost": True
                }
            return {}
        
        def adjust_for_engagement(context: StudentContext) -> Dict[str, Any]:
            """Boost recommendations when student is highly engaged."""
            if context.get_engagement_level() == "engaged":
                return {
                    "difficulty_adjustment": 0.4,
                    "content_type_preference": ["challenge", "advanced_practice"],
                    "extended_session": True
                }
            return {}
        
        def adjust_for_time(context: StudentContext) -> Dict[str, Any]:
            """Adjust based on time of day."""
            time_adjustments = {
                "morning": {"difficulty_preference": 0.2},
                "afternoon": {"difficulty_preference": 0.0},
                "evening": {"difficulty_preference": -0.1},
                "night": {"difficulty_preference": -0.2}
            }
            return time_adjustments.get(context.time_of_day, {})
        
        self.adaptation_rules = [
            adjust_for_frustration,
            adjust_for_boredom,
            adjust_for_engagement,
            adjust_for_time
        ]
    
    def set_concept_graph(self, graph: ConceptDependencyGraph):
        """
        Set the concept dependency graph for the graph-based engine.
        
        Args:
            graph: The concept dependency graph
        """
        self.graph_engine.set_graph(graph)
    
    def get_student_context(self, student_id: str) -> StudentContext:
        """
        Get or create student context.
        
        Args:
            student_id: The student ID
            
        Returns:
            StudentContext for the student
        """
        if student_id not in self.student_contexts:
            self.student_contexts[student_id] = StudentContext(student_id=student_id)
        
        return self.student_contexts[student_id]
    
    def recommend(
        self,
        profile: StudentProfile,
        available_content: List[ContentItem],
        max_results: int = 10,
        context: Optional[StudentContext] = None
    ) -> Tuple[List[ContentItem], List[RecommendationReason], Dict[str, Any]]:
        """
        Generate adaptive content recommendations.
        
        This method combines multiple strategies and adapts based on
        student context and feedback history.
        
        Args:
            profile: The student profile
            available_content: Available content items
            max_results: Maximum recommendations to return
            context: Optional student context for adaptation
            
        Returns:
            Tuple of (recommended_items, reasons, metadata)
        """
        # Get or create context
        if context is None:
            context = self.get_student_context(profile.student_id)
        
        # Apply adaptation rules
        adaptations = self._apply_adaptation_rules(context)
        
        # Get recommendations from each strategy
        strategy_results = self._get_all_strategy_recommendations(
            profile, available_content, adaptations
        )
        
        # Combine recommendations using bandit-selected strategy
        combined = self._combine_recommendations(
            strategy_results, profile, adaptations, max_results
        )
        
        # Generate metadata
        metadata = {
            "adaptations": adaptations,
            "strategy_used": self.bandit_state.select_strategy().__dict__,
            "exploration_rate": self.bandit_state.exploration_rate,
            "strategy_performance": {
                s.value: {
                    "weight": w.weight,
                    "success_rate": w.success_rate
                }
                for s, w in self.bandit_state.strategy_weights.items()
            }
        }
        
        return combined, [], metadata
    
    def _apply_adaptation_rules(self, context: StudentContext) -> Dict[str, Any]:
        """
        Apply all adaptation rules to generate adaptation parameters.
        
        Args:
            context: The student context
            
        Returns:
            Dictionary of adaptation parameters
        """
        combined_adaptations = {}
        
        for rule in self.adaptation_rules:
            adaptation = rule(context)
            combined_adaptations.update(adaptation)
        
        return combined_adaptations
    
    def _get_all_strategy_recommendations(
        self,
        profile: StudentProfile,
        available_content: List[ContentItem],
        adaptations: Dict[str, Any]
    ) -> Dict[StrategyType, Tuple[List[ContentItem], Dict[str, Any]]]:
        """
        Get recommendations from all available strategies.
        
        Args:
            profile: The student profile
            available_content: Available content items
            adaptations: Applied adaptations
            
        Returns:
            Dictionary mapping strategy types to their results
        """
        results = {}
        
        # Rule-based recommendations
        try:
            rule_results, rule_reasons, rule_meta = self.rule_engine.recommend(
                profile, available_content, max_results=20
            )
            results[StrategyType.RULE_BASED] = (rule_results, rule_meta)
        except Exception as e:
            logger.error(f"Rule-based strategy failed: {e}")
            results[StrategyType.RULE_BASED] = ([], {"error": str(e)})
        
        # Graph-based recommendations
        try:
            graph_results, graph_reasons, graph_meta = self.graph_engine.recommend_based_on_concepts(
                profile, available_content, max_results=20
            )
            results[StrategyType.GRAPH_BASED] = (graph_results, graph_meta)
        except Exception as e:
            logger.error(f"Graph-based strategy failed: {e}")
            results[StrategyType.GRAPH_BASED] = ([], {"error": str(e)})
        
        # Content-based (simplified - uses rule engine with different rules)
        try:
            content_results, content_reasons, content_meta = self._content_based_recommend(
                profile, available_content, adaptations
            )
            results[StrategyType.CONTENT_BASED] = (content_results, content_meta)
        except Exception as e:
            logger.error(f"Content-based strategy failed: {e}")
            results[StrategyType.CONTENT_BASED] = ([], {"error": str(e)})
        
        # Collaborative (simplified - uses rule engine with peer patterns)
        try:
            collab_results, collab_reasons, collab_meta = self._collaborative_recommend(
                profile, available_content
            )
            results[StrategyType.COLLABORATIVE] = (collab_results, collab_meta)
        except Exception as e:
            logger.error(f"Collaborative strategy failed: {e}")
            results[StrategyType.COLLABORATIVE] = ([], {"error": str(e)})
        
        return results
    
    def _content_based_recommend(
        self,
        profile: StudentProfile,
        available_content: List[ContentItem],
        adaptations: Dict[str, Any]
    ) -> Tuple[List[ContentItem], List[RecommendationReason], Dict[str, Any]]:
        """
        Generate content-based recommendations.
        
        Uses content similarity and student preferences.
        """
        # Score content based on topic preferences
        topic_scores = profile.topic_interests if hasattr(profile, "topic_interests") else {}
        
        scored_content = []
        for content in available_content:
            score = 0.0
            
            # Boost for matching topics
            if hasattr(content, "topics") and content.topics:
                for topic in content.topics:
                    if topic in topic_scores:
                        score += topic_scores[topic] * 0.3
            
            # Boost for content type preferences
            if hasattr(content, "content_type"):
                type_prefs = profile.content_type_preferences if hasattr(profile, "content_type_preferences") else {}
                if content.content_type in type_prefs:
                    score += type_prefs[content.content_type] * 0.2
            
            # Adjust for difficulty preference
            difficulty = getattr(content, "difficulty_level", "intermediate")
            difficulty_map = {"foundational": 0.8, "intermediate": 1.0, "advanced": 1.2}
            diff_factor = difficulty_map.get(difficulty, 1.0)
            adaptation = adaptations.get("difficulty_adjustment", 0)
            score += (diff_factor + adaptation) * 0.1
            
            # Prefer unseen content
            if content.content_id not in profile.completed_content_ids:
                score += 0.3
            
            scored_content.append((content, score))
        
        # Sort and return top results
        scored_content.sort(key=lambda x: x[1], reverse=True)
        
        return (
            [c for c, _ in scored_content[:15]],
            [],
            {"strategy": "content_based", "content_scored": len(scored_content)}
        )
    
    def _collaborative_recommend(
        self,
        profile: StudentProfile,
        available_content: List[ContentItem]
    ) -> Tuple[List[ContentItem], List[RecommendationReason], Dict[str, Any]]:
        """
        Generate collaborative recommendations.
        
        Uses patterns from similar students (simplified implementation).
        """
        # In a real system, this would query a collaborative filtering model
        # Here we simulate based on popularity and peer success
        
        content_scores = []
        
        for content in available_content:
            score = 0.0
            
            # Base popularity score (would come from peer data)
            popularity = getattr(content, "popularity_score", 0.5)
            score += popularity * 0.4
            
            # Success rate among similar students
            success_rate = getattr(content, "success_rate", 0.5)
            score += success_rate * 0.4
            
            # Completion rate
            completion_rate = getattr(content, "completion_rate", 0.5)
            score += completion_rate * 0.2
            
            content_scores.append((content, score))
        
        content_scores.sort(key=lambda x: x[1], reverse=True)
        
        return (
            [c for c, _ in content_scores[:15]],
            [],
            {"strategy": "collaborative", "content_scored": len(content_scores)}
        )
    
    def _combine_recommendations(
        self,
        strategy_results: Dict[StrategyType, Tuple[List[ContentItem], Dict[str, Any]]],
        profile: StudentProfile,
        adaptations: Dict[str, Any],
        max_results: int
    ) -> List[ContentItem]:
        """
        Combine recommendations from multiple strategies.
        
        Uses weighted combination based on strategy weights.
        """
        # Select primary strategy using bandit
        primary_strategy = self.bandit_state.select_strategy()
        
        # Get recommendations from primary strategy
        if primary_strategy in strategy_results:
            primary_results, _ = strategy_results[primary_strategy]
        else:
            # Fallback to first available strategy
            primary_results = strategy_results[StrategyType.RULE_BASED][0]
        
        # Build hybrid recommendations
        all_recommendations = []
        seen_ids = set()
        
        # Add primary strategy results
        for content in primary_results:
            if content.content_id not in seen_ids:
                all_recommendations.append((content, primary_strategy, 1.0))
                seen_ids.add(content.content_id)
        
        # Add complementary results from other strategies
        for strategy, (results, _) in strategy_results.items():
            if strategy != primary_strategy:
                weight = self.bandit_state.strategy_weights[strategy].weight
                
                for content in results[:10]:  # Limit from secondary strategies
                    if content.content_id not in seen_ids:
                        all_recommendations.append((content, strategy, weight))
                        seen_ids.add(content.content_id)
        
        # Apply variety boost if requested
        if adaptations.get("variety_boost"):
            random.shuffle(all_recommendations)
        
        # Sort by strategy weight and score
        all_recommendations.sort(key=lambda x: x[2], reverse=True)
        
        # Return top results
        return [item for item, _, _ in all_recommendations[:max_results]]
    
    def process_feedback(
        self,
        student_id: str,
        content_id: str,
        engagement_score: float,
        completion: bool,
        assessment_score: Optional[float] = None
    ):
        """
        Process feedback from a recommendation.
        
        This method updates the bandit state and strategy weights based
        on the student's interaction with the recommended content.
        
        Args:
            student_id: The student ID
            content_id: The recommended content ID
            engagement_score: How engaged the student was (0-1)
            completion: Whether the student completed the content
            assessment_score: Optional post-assessment score (0-1)
        """
        # Calculate overall reward
        reward = engagement_score * 0.3
        
        if completion:
            reward += 0.3
        
        if assessment_score is not None:
            reward += assessment_score * 0.4
        
        # Clamp reward to [0, 1]
        reward = max(0.0, min(1.0, reward))
        
        # Update context
        context = self.get_student_context(student_id)
        if assessment_score is not None:
            context.update_performance(assessment_score)
        
        # Record event
        event = LearningEvent(
            student_id=student_id,
            content_id=content_id,
            event_type="recommendation_feedback",
            timestamp=datetime.now(),
            metadata={
                "engagement_score": engagement_score,
                "completion": completion,
                "assessment_score": assessment_score,
                "reward": reward
            }
        )
        self.performance_history[student_id].append(event)
        
        # Update bandit state
        # Note: In a real implementation, we'd track which strategy was used
        # For now, we update all strategies proportionally
        for strategy in StrategyType:
            self.bandit_state.update_strategy(strategy, reward)
        
        logger.info(
            f"Processed feedback for student {student_id}, content {content_id}: "
            f"reward={reward:.2f}"
        )
    
    def generate_adaptive_learning_path(
        self,
        profile: StudentProfile,
        target_outcomes: List[str],
        available_content: List[ContentItem]
    ) -> LearningPath:
        """
        Generate an adaptive learning path to target outcomes.
        
        This method creates a personalized learning path that adapts
        based on student progress and feedback.
        
        Args:
            profile: The student profile
            target_outcomes: Target learning outcomes
            available_content: Available content items
            
        Returns:
            Adaptive learning path
        """
        # Get graph-based path as baseline
        path = self.graph_engine.generate_learning_path(
            profile,
            target_outcomes,
            available_content
        )
        
        # Apply adaptive adjustments
        context = self.get_student_context(profile.student_id)
        adaptations = self._apply_adaptation_rules(context)
        
        # Adjust path based on adaptations
        if adaptations.get("break_recommended"):
            # Insert break markers or shorter segments
            logger.info(f"Break recommended for student {profile.student_id}")
        
        if adaptations.get("difficulty_adjustment", 0) != 0:
            # Reorder or filter path items by difficulty
            adjusted_items = []
            for item in path.items:
                difficulty_map = {"foundational": 1, "intermediate": 2, "advanced": 3}
                current_diff = difficulty_map.get(item.difficulty_level, 2)
                target_diff = current_diff + adaptations.get("difficulty_adjustment", 0)
                
                if 0.5 <= target_diff <= 3.5:
                    adjusted_items.append(item)
            
            path.items = adjusted_items
            path.total_duration = sum(c.estimated_duration for c in adjusted_items)
        
        return path
    
    def detect_learning_patterns(
        self,
        student_id: str
    ) -> Dict[str, Any]:
        """
        Detect patterns in student learning behavior.
        
        Analyzes historical data to identify recurring patterns and
        trends in student engagement and performance.
        
        Args:
            student_id: The student ID
            
        Returns:
            Dictionary of detected patterns
        """
        events = self.performance_history[student_id]
        
        if len(events) < 5:
            return {"status": "insufficient_data"}
        
        patterns = {
            "total_events": len(events),
            "average_engagement": 0.0,
            "completion_rate": 0.0,
            "performance_trend": "stable",
            "peak_performance_time": None,
            "common_difficulties": []
        }
        
        # Calculate engagement metrics
        engagements = [
            e.metadata.get("engagement_score", 0.5)
            for e in events
            if "engagement_score" in e.metadata
        ]
        
        if engagements:
            patterns["average_engagement"] = sum(engagements) / len(engagements)
        
        # Calculate completion rate
        completions = sum(
            1 for e in events
            if e.metadata.get("completion", False)
        )
        patterns["completion_rate"] = completions / len(events) if events else 0
        
        # Detect performance trend
        assessments = [
            e.metadata.get("assessment_score", 0.5)
            for e in events
            if "assessment_score" in e.metadata
        ]
        
        if len(assessments) >= 3:
            first_half = sum(assessments[:len(assessments)//2]) / (len(assessments)//2)
            second_half = sum(assessments[len(assessments)//2:]) / (len(assessments) - len(assessments)//2)
            
            if second_half - first_half > 0.1:
                patterns["performance_trend"] = "improving"
            elif first_half - second_half > 0.1:
                patterns["performance_trend"] = "declining"
        
        # Get context for pattern analysis
        context = self.get_student_context(student_id)
        patterns["current_engagement"] = context.get_engagement_level()
        patterns["recent_performance"] = context.recent_performance[-5:]
        
        return patterns
    
    def get_strategy_insights(self) -> Dict[str, Any]:
        """
        Get insights about strategy performance.
        
        Returns:
            Dictionary of strategy performance metrics
        """
        insights = {
            "exploration_rate": self.bandit_state.exploration_rate,
            "strategies": {}
        }
        
        for strategy, weight in self.bandit_state.strategy_weights.items():
            insights["strategies"][strategy.value] = {
                "weight": weight.weight,
                "success_rate": weight.success_rate,
                "total_uses": weight.total_uses,
                "successful_uses": weight.successful_uses,
                "average_engagement": weight.average_engagement
            }
        
        # Identify best performing strategy
        best_strategy = max(
            self.bandit_state.strategy_weights.items(),
            key=lambda x: x[1].success_rate
        )
        
        insights["best_strategy"] = {
            "type": best_strategy[0].value,
            "success_rate": best_strategy[1].success_rate
        }
        
        return insights
    
    def should_suggest_break(self, student_id: str) -> bool:
        """
        Determine if the student should take a break.
        
        Analyzes recent performance and engagement to detect fatigue
        or frustration that warrants a break.
        
        Args:
            student_id: The student ID
            
        Returns:
            True if break is recommended
        """
        context = self.get_student_context(student_id)
        
        # Check for frustration indicators
        if context.get_engagement_level() == "frustrated":
            return True
        
        # Check for long session without improvement
        if context.session_duration > 45:
            if context.consecutive_failures >= 3:
                return True
        
        # Check for declining performance
        if len(context.recent_performance) >= 5:
            recent = context.recent_performance[-5:]
            if all(s < 0.6 for s in recent[-3:]):  # Last 3 scores are low
                return True
        
        return False
