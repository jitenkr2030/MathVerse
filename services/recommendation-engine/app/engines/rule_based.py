"""
Rule-Based Recommendation Engine

This module implements a rule-based recommendation system that applies predefined
pedagogical rules to generate content recommendations. The engine evaluates
student profiles against a set of configurable rules to determine appropriate
learning materials and exercises.

The rule-based approach ensures consistent, explainable recommendations that
follow established educational principles and curriculum sequencing requirements.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

from ..schemas import (
    StudentProfile,
    ContentItem,
    ConceptNode,
    LearningPath,
    RecommendationReason
)


logger = logging.getLogger(__name__)


class DifficultyLevel(Enum):
    """Enumeration of content difficulty levels."""
    FOUNDATIONAL = "foundational"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MASTERY = "mastery"


class RulePriority(Enum):
    """Enumeration of rule execution priorities."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class RuleCondition:
    """
    Represents a condition that must be met for a rule to apply.
    
    Conditions are combined using logical AND operations within a rule,
    while multiple rules are evaluated using logical OR operations.
    """
    attribute: str
    operator: str  # "eq", "ne", "gt", "gte", "lt", "lte", "in", "contains"
    value: Any
    
    def evaluate(self, profile: StudentProfile) -> bool:
        """
        Evaluate the condition against a student profile.
        
        Args:
            profile: The student profile to evaluate against
            
        Returns:
            True if the condition is satisfied, False otherwise
        """
        # Navigate nested attributes using dot notation
        attributes = self.attribute.split(".")
        value = profile
        
        for attr in attributes:
            if hasattr(value, attr):
                value = getattr(value, attr)
            elif isinstance(value, dict) and attr in value:
                value = value[attr]
            else:
                return False
        
        # Apply the appropriate operator
        if self.operator == "eq":
            return value == self.value
        elif self.operator == "ne":
            return value != self.value
        elif self.operator == "gt":
            return value > self.value
        elif self.operator == "gte":
            return value >= self.value
        elif self.operator == "lt":
            return value < self.value
        elif self.operator == "lte":
            return value <= self.value
        elif self.operator == "in":
            return value in self.value
        elif self.operator == "contains":
            return self.value in value if hasattr(value, "__contains__") else False
        
        return False


@dataclass
class Rule:
    """
    Represents a recommendation rule with conditions and actions.
    
    Rules define when specific content should be recommended based on
    student characteristics and learning context.
    """
    name: str
    description: str
    conditions: List[RuleCondition]
    recommended_content_types: List[str]
    priority: RulePriority
    difficulty_adjustment: int = 0  # -2 to +2 adjustment to difficulty
    max_recommendations: int = 5
    subject_filter: Optional[List[str]] = None
    topic_filter: Optional[List[str]] = None
    
    def evaluate(self, profile: StudentProfile) -> bool:
        """
        Evaluate all conditions of the rule against a profile.
        
        All conditions must be satisfied (logical AND) for the rule to apply.
        
        Args:
            profile: The student profile to evaluate against
            
        Returns:
            True if all conditions are satisfied, False otherwise
        """
        return all(condition.evaluate(profile) for condition in self.conditions)


@dataclass
class RuleExecutionResult:
    """Result of executing a recommendation rule."""
    rule_name: str
    recommended_items: List[ContentItem]
    confidence_score: float
    reasons: List[RecommendationReason]
    executed_at: datetime


class RuleBasedEngine:
    """
    Engine that generates recommendations based on predefined pedagogical rules.
    
    This engine provides explainable, consistent recommendations by applying
    educational best practices through a configurable rule system. It serves
    as a foundational recommendation approach that can be enhanced with
    more sophisticated machine learning models.
    """
    
    def __init__(self):
        """Initialize the rule-based recommendation engine."""
        self.rules: List[Rule] = []
        self.difficulty_weights = {
            DifficultyLevel.FOUNDATIONAL: 1.0,
            DifficultyLevel.INTERMEDIATE: 2.0,
            DifficultyLevel.ADVANCED: 3.0,
            DifficultyLevel.MASTERY: 4.0
        }
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize the default set of pedagogical rules."""
        
        # Rule 1: Foundational reinforcement for struggling students
        foundational_rule = Rule(
            name="foundational_reinforcement",
            description="Recommend foundational content when student struggles with concepts",
            conditions=[
                RuleCondition("mastery_states", "lt", 0.5),
                RuleCondition("average_score", "lt", 0.6)
            ],
            recommended_content_types=["practice", "tutorial", "video"],
            priority=RulePriority.CRITICAL,
            difficulty_adjustment=-1,
            max_recommendations=5,
            subject_filter=None
        )
        self.rules.append(foundational_rule)
        
        # Rule 2: Challenge advancement for high performers
        challenge_rule = Rule(
            name="challenge_advancement",
            description="Recommend advanced content for students demonstrating mastery",
            conditions=[
                RuleCondition("mastery_states", "gte", 0.8),
                RuleCondition("average_score", "gte", 0.85),
                RuleCondition("learning_streak", "gte", 5)
            ],
            recommended_content_types=["challenge", "competition", "advanced_practice"],
            priority=RulePriority.HIGH,
            difficulty_adjustment=1,
            max_recommendations=3,
            subject_filter=None
        )
        self.rules.append(challenge_rule)
        
        # Rule 3: Spaced repetition for review
        spaced_rule = Rule(
            name="spaced_repetition",
            description="Recommend review content based on forgetting curve",
            conditions=[
                RuleCondition("review_queue_count", "gt", 0)
            ],
            recommended_content_types=["review", "practice"],
            priority=RulePriority.MEDIUM,
            difficulty_adjustment=0,
            max_recommendations=7,
            subject_filter=None
        )
        self.rules.append(spaced_rule)
        
        # Rule 4: Concept progression for sequential learning
        progression_rule = Rule(
            name="concept_progression",
            description="Recommend next concepts in learning sequence",
            conditions=[
                RuleCondition("completed_concepts_count", "gt", 0),
                RuleCondition("incomplete_prerequisites_count", "eq", 0)
            ],
            recommended_content_types=["lesson", "tutorial"],
            priority=RulePriority.HIGH,
            difficulty_adjustment=0,
            max_recommendations=5,
            subject_filter=None
        )
        self.rules.append(progression_rule)
        
        # Rule 5: Weakness remediation
        weakness_rule = Rule(
            name="weakness_remediation",
            description="Target recommendations at identified weak areas",
            conditions=[
                RuleCondition("identified_weaknesses", "gt", 0)
            ],
            recommended_content_types=["remediation", "targeted_practice"],
            priority=RulePriority.CRITICAL,
            difficulty_adjustment=-1,
            max_recommendations=4,
            subject_filter=None
        )
        self.rules.append(weakness_rule)
        
        # Rule 6: New content introduction
        new_content_rule = Rule(
            name="new_content_exploration",
            description="Introduce new topics aligned with interests",
            conditions=[
                RuleCondition("topic_interests", "contains", "new"),
                RuleCondition("completed_concepts_count", "gte", 3)
            ],
            recommended_content_types=["introduction", "exploration"],
            priority=RulePriority.LOW,
            difficulty_adjustment=0,
            max_recommendations=3,
            subject_filter=None
        )
        self.rules.append(new_content_rule)
        
        # Sort rules by priority for consistent execution
        self.rules.sort(key=lambda r: r.priority.value)
        
        logger.info(f"Initialized {len(self.rules)} default pedagogical rules")
    
    def add_rule(self, rule: Rule):
        """
        Add a new rule to the engine.
        
        Args:
            rule: The rule to add
        """
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority.value)
        logger.info(f"Added rule: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove a rule from the engine by name.
        
        Args:
            rule_name: The name of the rule to remove
            
        Returns:
            True if the rule was found and removed, False otherwise
        """
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                logger.info(f"Removed rule: {rule_name}")
                return True
        return False
    
    def get_applicable_rules(self, profile: StudentProfile) -> List[Rule]:
        """
        Get all rules that apply to a given student profile.
        
        Args:
            profile: The student profile to evaluate
            
        Returns:
            List of applicable rules sorted by priority
        """
        return [rule for rule in self.rules if rule.evaluate(profile)]
    
    def calculate_difficulty_score(
        self,
        profile: StudentProfile,
        rule: Optional[Rule] = None
    ) -> float:
        """
        Calculate the appropriate difficulty score for recommendations.
        
        Args:
            profile: The student profile
            rule: Optional rule that may influence difficulty
            
        Returns:
            Difficulty score between 1.0 and 5.0
        """
        # Base difficulty on student's average performance
        base_difficulty = 1.0
        
        if profile.average_score >= 0.9:
            base_difficulty = 4.0
        elif profile.average_score >= 0.8:
            base_difficulty = 3.5
        elif profile.average_score >= 0.7:
            base_difficulty = 3.0
        elif profile.average_score >= 0.6:
            base_difficulty = 2.5
        elif profile.average_score >= 0.5:
            base_difficulty = 2.0
        else:
            base_difficulty = 1.5
        
        # Apply rule-based adjustments
        if rule:
            adjustment = rule.difficulty_adjustment
            base_difficulty = max(1.0, min(5.0, base_difficulty + adjustment * 0.5))
        
        return base_difficulty
    
    def generate_reason(
        self,
        rule: Rule,
        profile: StudentProfile
    ) -> RecommendationReason:
        """
        Generate a recommendation reason based on the applied rule.
        
        Args:
            rule: The rule that triggered the recommendation
            profile: The student profile
            
        Returns:
            Recommendation reason explaining why content is recommended
        """
        return RecommendationReason(
            rule_applied=rule.name,
            explanation=rule.description,
            confidence=0.8,  # Rule-based confidence is typically high
            factors=[
                f"Rule priority: {rule.priority.name}",
                f"Conditions met: {len(rule.conditions)}",
                f"Content types: {', '.join(rule.recommended_content_types)}"
            ]
        )
    
    def recommend(
        self,
        profile: StudentProfile,
        available_content: List[ContentItem],
        max_results: int = 10
    ) -> Tuple[List[ContentItem], List[RecommendationReason], Dict[str, Any]]:
        """
        Generate content recommendations based on applicable rules.
        
        This method evaluates the student profile against all rules and
        selects content that matches the applicable rules' criteria.
        
        Args:
            profile: The student profile to generate recommendations for
            available_content: List of available content items
            max_results: Maximum number of recommendations to return
            
        Returns:
            Tuple of (recommended_items, reasons, metadata)
        """
        applicable_rules = self.get_applicable_rules(profile)
        
        if not applicable_rules:
            logger.info(f"No applicable rules for student {profile.student_id}")
            # Return empty recommendations with default reason
            default_reason = RecommendationReason(
                rule_applied="default_fallback",
                explanation="No specific rules matched; using general recommendations",
                confidence=0.5,
                factors=["No rule conditions satisfied"]
            )
            return [], [default_reason], {"rules_applied": 0}
        
        # Calculate target difficulty
        primary_rule = applicable_rules[0]  # Highest priority rule
        target_difficulty = self.calculate_difficulty_score(profile, primary_rule)
        
        # Filter and score content based on applicable rules
        scored_content = []
        
        for rule in applicable_rules:
            for content in available_content:
                # Skip if content doesn't match rule filters
                if rule.subject_filter and content.subject not in rule.subject_filter:
                    continue
                if rule.topic_filter and content.topic not in rule.topic_filter:
                    continue
                
                # Skip if content type doesn't match
                if content.content_type not in rule.recommended_content_types:
                    continue
                
                # Calculate content score
                content_score = self._score_content_for_rule(
                    content, profile, rule, target_difficulty
                )
                
                if content_score > 0:
                    scored_content.append((content, content_score, rule))
        
        # Sort by score and deduplicate
        scored_content.sort(key=lambda x: x[1], reverse=True)
        
        # Remove duplicates while preserving order
        seen_ids = set()
        unique_recommendations = []
        
        for content, score, rule in scored_content:
            if content.content_id not in seen_ids:
                seen_ids.add(content.content_id)
                unique_recommendations.append((content, score, rule))
        
        # Extract final recommendations
        recommended_items = [
            item for item, _, _ in unique_recommendations[:max_results]
        ]
        
        # Generate reasons for each applicable rule
        reasons = [
            self.generate_reason(rule, profile)
            for rule in applicable_rules
        ]
        
        # Build metadata
        metadata = {
            "rules_applied": len(applicable_rules),
            "primary_rule": primary_rule.name,
            "target_difficulty": target_difficulty,
            "content_scored": len(scored_content),
            "recommendation_count": len(recommended_items)
        }
        
        logger.info(
            f"Generated {len(recommended_items)} recommendations for "
            f"student {profile.student_id} using {len(applicable_rules)} rules"
        )
        
        return recommended_items, reasons, metadata
    
    def _score_content_for_rule(
        self,
        content: ContentItem,
        profile: StudentProfile,
        rule: Rule,
        target_difficulty: float
    ) -> float:
        """
        Score a content item for a specific rule.
        
        Args:
            content: The content item to score
            profile: The student profile
            rule: The rule being evaluated
            target_difficulty: The target difficulty level
            
        Returns:
            Score between 0 and 1, where 0 means not recommended
        """
        score = 0.5  # Base score
        
        # Difficulty alignment scoring
        content_difficulty = self.difficulty_weights.get(
            DifficultyLevel(content.difficulty_level),
            2.5
        )
        
        difficulty_diff = abs(content_difficulty - target_difficulty)
        if difficulty_diff < 0.5:
            score += 0.3
        elif difficulty_diff < 1.0:
            score += 0.1
        else:
            score -= 0.2
        
        # Boost score for matching content types
        if content.content_type in rule.recommended_content_types:
            score += 0.2
        
        # Prioritize content not yet completed
        if content.content_id not in profile.completed_content_ids:
            score += 0.1
        
        # Boost for high-quality content
        if hasattr(content, "quality_score") and content.quality_score > 0.8:
            score += 0.1
        
        # Penalize content that was previously recommended but not completed
        if hasattr(content, "content_id") and content.content_id in profile.ignored_content_ids:
            score -= 0.3
        
        return max(0, min(1, score))
    
    def recommend_for_learning_path(
        self,
        profile: StudentProfile,
        target_concepts: List[ConceptNode],
        available_content: List[ContentItem]
    ) -> LearningPath:
        """
        Generate a learning path recommendation for target concepts.
        
        This method creates an ordered sequence of content items that
        systematically builds toward mastery of target concepts.
        
        Args:
            profile: The student profile
            target_concepts: List of concepts to learn
            available_content: Available content items
            
        Returns:
            LearningPath with ordered recommendations
        """
        # Get applicable rules for this context
        applicable_rules = self.get_applicable_rules(profile)
        
        # Filter content for each target concept
        concept_content_map = {}
        for concept in target_concepts:
            concept_content = [
                c for c in available_content
                if concept.concept_id in c.related_concepts
            ]
            concept_content_map[concept.concept_id] = concept_content
        
        # Build ordered sequence
        path_items = []
        reasons = []
        
        for concept in target_concepts:
            concept_content = concept_content_map.get(concept.concept_id, [])
            
            if concept_content:
                # Score and sort content for this concept
                for content in concept_content:
                    for rule in applicable_rules:
                        if content.content_type in rule.recommended_content_types:
                            score = self._score_content_for_rule(
                                content, profile, rule, 2.5
                            )
                            content._temp_score = score
                            break
                
                # Sort by score and add to path
                concept_content.sort(
                    key=lambda c: getattr(c, "_temp_score", 0.5),
                    reverse=True
                )
                
                if concept_content:
                    best_content = concept_content[0]
                    path_items.append(best_content)
                    
                    # Generate reason for this item
                    reason = RecommendationReason(
                        rule_applied="learning_path_construction",
                        explanation=f"Content selected for concept: {concept.name}",
                        confidence=0.75,
                        factors=[
                            f"Target concept: {concept.name}",
                            f"Content type: {best_content.content_type}",
                            f"Difficulty: {best_content.difficulty_level}"
                        ]
                    )
                    reasons.append(reason)
        
        # Create learning path
        learning_path = LearningPath(
            path_id=f"lp_{profile.student_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            student_id=profile.student_id,
            items=path_items,
            total_duration=sum(c.estimated_duration for c in path_items),
            reasons=reasons,
            created_at=datetime.now()
        )
        
        return learning_path
    
    def get_recommendation_explanation(
        self,
        profile: StudentProfile,
        content: ContentItem
    ) -> Dict[str, Any]:
        """
        Get a detailed explanation for why content is recommended.
        
        Args:
            profile: The student profile
            content: The content item
            
        Returns:
            Dictionary containing explanation details
        """
        applicable_rules = self.get_applicable_rules(profile)
        
        matching_rules = []
        blocking_rules = []
        
        for rule in self.rules:
            if rule in applicable_rules:
                if content.content_type in rule.recommended_content_types:
                    matching_rules.append({
                        "rule": rule.name,
                        "description": rule.description,
                        "priority": rule.priority.name
                    })
            else:
                # Check if rule would have matched except for content type
                for condition in rule.conditions:
                    if not condition.evaluate(profile):
                        blocking_rules.append({
                            "rule": rule.name,
                            "condition": condition.attribute,
                            "reason": f"Condition not met: {condition.attribute} {condition.operator} {condition.value}"
                        })
        
        return {
            "content_id": content.content_id,
            "content_title": content.title,
            "matching_rules": matching_rules,
            "blocking_rules": blocking_rules,
            "applicable_rules_count": len(applicable_rules),
            "recommendation_strength": "strong" if len(matching_rules) >= 2 else "moderate" if len(matching_rules) == 1 else "weak"
        }
