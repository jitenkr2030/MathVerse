"""
Concept Recommender Service

This module provides concept-level recommendation capabilities, including
concept mastery assessment, prerequisite identification, and learning
path construction for mathematical concepts.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

from ..schemas import (
    StudentProfile,
    ContentItem,
    ConceptNode,
    LearningPath,
    MasteryState,
    RecommendationReason
)
from ..engines.rule_based import RuleBasedEngine
from ..engines.graph_based import GraphBasedEngine, ConceptDependencyGraph


logger = logging.getLogger(__name__)


@dataclass
class ConceptRecommendation:
    """Represents a concept recommendation with supporting evidence."""
    concept_id: str
    concept_name: str
    priority: int
    confidence: float
    recommended_content_ids: List[str]
    prerequisites_fulfilled: bool
    mastery_prerequisite: float
    reasoning: str
    estimated_time_minutes: int


@dataclass
class ConceptGap:
    """Represents a gap in concept mastery."""
    concept_id: str
    concept_name: str
    current_mastery: float
    target_mastery: float
    gap_size: float
    priority_concepts: List[str]
    estimated_time_to_fill: int


class ConceptRecommender:
    """
    Service for generating concept-based recommendations.
    
    This service analyzes student mastery states and concept relationships
    to recommend the next concepts to learn and identify gaps in knowledge.
    """
    
    def __init__(
        self,
        rule_engine: Optional[RuleBasedEngine] = None,
        graph_engine: Optional[GraphBasedEngine] = None
    ):
        """
        Initialize the concept recommender service.
        
        Args:
            rule_engine: Optional rule-based engine
            graph_engine: Optional graph-based engine
        """
        self.rule_engine = rule_engine or RuleBasedEngine()
        self.graph_engine = graph_engine or GraphBasedEngine()
        self.concept_cache: Dict[str, ConceptNode] = {}
        
        logger.info("Initialized ConceptRecommender service")
    
    def add_concepts(self, concepts: List[ConceptNode]):
        """
        Add concepts to the recommender's knowledge base.
        
        Args:
            concepts: List of concepts to add
        """
        for concept in concepts:
            self.concept_cache[concept.concept_id] = concept
        
        # Rebuild graph
        graph = ConceptDependencyGraph()
        graph.build_from_concepts(concepts)
        self.graph_engine.set_graph(graph)
        
        logger.info(f"Added {len(concepts)} concepts to knowledge base")
    
    def recommend_next_concepts(
        self,
        profile: StudentProfile,
        max_concepts: int = 5
    ) -> List[ConceptRecommendation]:
        """
        Recommend the next concepts for a student to learn.
        
        Analyzes current mastery states, prerequisites, and learning
        goals to identify the most appropriate next concepts.
        
        Args:
            profile: The student profile
            max_concepts: Maximum concepts to recommend
            
        Returns:
            List of concept recommendations sorted by priority
        """
        recommendations = []
        
        # Get concepts that need attention
        for concept_id, mastery in profile.mastery_states.items():
            if mastery < 0.8:  # Not yet mastered
                concept = self.concept_cache.get(concept_id)
                
                if concept:
                    # Check if prerequisites are met
                    prereqs_met = self._check_prerequisites(
                        concept_id, profile.completed_concepts_ids
                    )
                    
                    if prereqs_met:
                        priority = self._calculate_concept_priority(
                            concept_id, mastery, profile
                        )
                        
                        rec = ConceptRecommendation(
                            concept_id=concept_id,
                            concept_name=concept.name,
                            priority=priority,
                            confidence=self._calculate_confidence(concept_id, profile),
                            recommended_content_ids=self._get_content_for_concept(concept_id),
                            prerequisites_fulfilled=True,
                            mastery_prerequisite=1.0 - mastery,
                            reasoning=self._generate_concept_reasoning(concept_id, mastery, profile),
                            estimated_time_minutes=concept.estimated_minutes or 30
                        )
                        recommendations.append(rec)
        
        # Find new concepts not yet started
        for concept_id, concept in self.concept_cache.items():
            if concept_id not in profile.mastery_states:
                # Check if prerequisites are met
                prereqs_met = self._check_prerequisites(
                    concept_id, profile.completed_concepts_ids
                )
                
                if prereqs_met:
                    # This is a reachable new concept
                    rec = ConceptRecommendation(
                        concept_id=concept_id,
                        concept_name=concept.name,
                        priority=self._calculate_new_concept_priority(concept_id, profile),
                        confidence=0.7,
                        recommended_content_ids=self._get_content_for_concept(concept_id),
                        prerequisites_fulfilled=True,
                        mastery_prerequisite=1.0,
                        reasoning=f"New concept '{concept.name}' is ready to learn based on completed prerequisites.",
                        estimated_time_minutes=concept.estimated_minutes or 30
                    )
                    recommendations.append(rec)
        
        # Sort by priority and return top results
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        
        return recommendations[:max_concepts]
    
    def identify_concept_gaps(
        self,
        profile: StudentProfile,
        target_mastery: float = 0.8
    ) -> List[ConceptGap]:
        """
        Identify gaps in concept mastery.
        
        Analyzes the student's current mastery states and identifies
        concepts that need additional attention to reach target mastery.
        
        Args:
            profile: The student profile
            target_mastery: Target mastery level (default 0.8)
            
        Returns:
            List of concept gaps sorted by priority
        """
        gaps = []
        
        for concept_id, current_mastery in profile.mastery_states.items():
            if current_mastery < target_mastery:
                concept = self.concept_cache.get(concept_id)
                
                if concept:
                    gap_size = target_mastery - current_mastery
                    
                    # Find priority concepts that depend on this
                    dependents = self.graph_engine.graph.get_dependents(concept_id)
                    priority_concepts = [
                        self.concept_cache.get(d, ConceptNode(d, "")).name
                        for d in dependents[:5]
                        if d in self.concept_cache
                    ]
                    
                    gap = ConceptGap(
                        concept_id=concept_id,
                        concept_name=concept.name,
                        current_mastery=current_mastery,
                        target_mastery=target_mastery,
                        gap_size=gap_size,
                        priority_concepts=priority_concepts,
                        estimated_time_to_fill=int(gap_size * (concept.estimated_minutes or 30))
                    )
                    gaps.append(gap)
        
        # Sort by gap size (largest gaps first)
        gaps.sort(key=lambda x: x.gap_size, reverse=True)
        
        return gaps
    
    def build_learning_path(
        self,
        profile: StudentProfile,
        target_concepts: List[str],
        content_items: List[ContentItem]
    ) -> LearningPath:
        """
        Build a learning path for target concepts.
        
        Creates an ordered sequence of content items that systematically
        builds toward mastery of the target concepts.
        
        Args:
            profile: The student profile
            target_concepts: List of concept IDs to learn
            content_items: Available content items
            
        Returns:
            LearningPath with ordered content recommendations
        """
        return self.graph_engine.generate_learning_path(
            profile,
            target_concepts,
            content_items
        )
    
    def get_concept_prerequisites(
        self,
        concept_id: str,
        profile: StudentProfile
    ) -> Dict[str, Any]:
        """
        Get prerequisite status for a concept.
        
        Returns detailed information about which prerequisites are
        fulfilled and which still need to be completed.
        
        Args:
            concept_id: The target concept ID
            profile: The student profile
            
        Returns:
            Dictionary with prerequisite status
        """
        concept = self.concept_cache.get(concept_id)
        
        if not concept:
            return {"error": "Concept not found"}
        
        prereqs = self.graph_engine.graph.get_prerequisites(concept_id)
        
        fulfilled = []
        missing = []
        
        for prereq_id in prereqs:
            if prereq_id in profile.completed_concepts_ids:
                mastery = profile.mastery_states.get(prereq_id, 1.0)
                fulfilled.append({
                    "concept_id": prereq_id,
                    "concept_name": self.concept_cache.get(prereq_id, ConceptNode(prereq_id, "")).name,
                    "mastery": mastery
                })
            else:
                mastery = profile.mastery_states.get(prereq_id, 0.0)
                missing.append({
                    "concept_id": prereq_id,
                    "concept_name": self.concept_cache.get(prereq_id, ConceptNode(prereq_id, "")).name,
                    "current_mastery": mastery,
                    "required_for": concept.name
                })
        
        return {
            "concept_id": concept_id,
            "concept_name": concept.name,
            "total_prerequisites": len(prereqs),
            "fulfilled_prerequisites": fulfilled,
            "missing_prerequisites": missing,
            "all_fulfilled": len(missing) == 0,
            "readiness_score": len(fulfilled) / len(prereqs) if prereqs else 1.0
        }
    
    def suggest_review_concepts(
        self,
        profile: StudentProfile,
        review_threshold: float = 0.6,
        max_concepts: int = 5
    ) -> List[ConceptRecommendation]:
        """
        Suggest concepts that need review.
        
        Identifies concepts where mastery has decayed below the
        review threshold and recommends review content.
        
        Args:
            profile: The student profile
            review_threshold: Mastery threshold for review (default 0.6)
            max_concepts: Maximum concepts to recommend
            
        Returns:
            List of concepts needing review
        """
        review_recommendations = []
        
        # Use decay predictions from profile if available
        decay_predictions = getattr(profile, "decay_predictions", {})
        
        for concept_id, current_mastery in profile.mastery_states.items():
            # Use current mastery or predicted decayed mastery
            decayed_mastery = decay_predictions.get(concept_id, current_mastery)
            
            if decayed_mastery < review_threshold:
                concept = self.concept_cache.get(concept_id)
                
                if concept:
                    rec = ConceptRecommendation(
                        concept_id=concept_id,
                        concept_name=concept.name,
                        priority=self._calculate_review_priority(decayed_mastery, profile),
                        confidence=0.85,
                        recommended_content_ids=self._get_review_content_for_concept(concept_id),
                        prerequisites_fulfilled=True,
                        mastery_prerequisite=review_threshold - decayed_mastery,
                        reasoning=f"Concept mastery has decayed to {decayed_mastery:.2f}, below review threshold of {review_threshold}.",
                        estimated_time_minutes=int((review_threshold - decayed_mastery) * 20)
                    )
                    review_recommendations.append(rec)
        
        review_recommendations.sort(key=lambda x: x.priority, reverse=True)
        
        return review_recommendations[:max_concepts]
    
    def _check_prerequisites(
        self,
        concept_id: str,
        completed_concepts: List[str]
    ) -> bool:
        """
        Check if all prerequisites for a concept are completed.
        
        Args:
            concept_id: The concept to check
            completed_concepts: List of completed concept IDs
            
        Returns:
            True if all prerequisites are completed
        """
        prereqs = self.graph_engine.graph.get_prerequisites(concept_id)
        
        if not prereqs:
            return True
        
        completed_set = set(completed_concepts)
        
        return all(prereq in completed_set for prereq in prereqs)
    
    def _calculate_concept_priority(
        self,
        concept_id: str,
        current_mastery: float,
        profile: StudentProfile
    ) -> int:
        """Calculate priority score for a concept."""
        priority = 5  # Base priority
        
        # Lower mastery = higher priority
        if current_mastery < 0.3:
            priority = 10
        elif current_mastery < 0.5:
            priority = 8
        elif current_mastery < 0.7:
            priority = 6
        
        # Boost for concepts needed in learning goals
        if hasattr(profile, "learning_goals"):
            for goal in profile.learning_goals:
                if concept_id in goal.get("target_concepts", []):
                    priority += 3
                    break
        
        # Boost for foundational concepts
        dependents = self.graph_engine.graph.get_dependents(concept_id)
        if len(dependents) > 3:
            priority += 2
        
        return min(10, priority)
    
    def _calculate_new_concept_priority(
        self,
        concept_id: str,
        profile: StudentProfile
    ) -> int:
        """Calculate priority for a new concept."""
        priority = 4  # Base priority for new concepts
        
        # Boost for foundational concepts
        prereqs = self.graph_engine.graph.get_prerequisites(concept_id)
        if not prereqs:
            priority += 2  # Foundational concept
        
        # Boost based on dependencies
        dependents = self.graph_engine.graph.get_dependents(concept_id)
        if len(dependents) > 5:
            priority += 2  # High-degree concept
        
        return min(10, priority)
    
    def _calculate_review_priority(
        self,
        decayed_mastery: float,
        profile: StudentProfile
    ) -> int:
        """Calculate priority for review recommendations."""
        priority = 7  # Base priority for review
        
        # Lower mastery = higher priority
        if decayed_mastery < 0.3:
            priority = 10
        elif decayed_mastery < 0.5:
            priority = 8
        
        return priority
    
    def _calculate_confidence(
        self,
        concept_id: str,
        profile: StudentProfile
    ) -> float:
        """Calculate confidence score for recommendation."""
        # Base confidence
        confidence = 0.6
        
        # Increase confidence if we have good mastery data
        mastery_data_points = len(profile.mastery_states)
        if mastery_data_points > 10:
            confidence += 0.2
        elif mastery_data_points > 5:
            confidence += 0.1
        
        # Increase confidence if prerequisites are clearly met
        prereqs = self.graph_engine.graph.get_prerequisites(concept_id)
        if prereqs:
            completed_prereqs = len(set(prereqs) & set(profile.completed_concepts_ids))
            confidence += (completed_prereqs / len(prereqs)) * 0.2
        
        return min(0.95, confidence)
    
    def _generate_concept_reasoning(
        self,
        concept_id: str,
        current_mastery: float,
        profile: StudentProfile
    ) -> str:
        """Generate human-readable reasoning for recommendation."""
        concept = self.concept_cache.get(concept_id)
        
        if not concept:
            return "Concept recommendation based on learning progression."
        
        reasoning_parts = []
        
        # Mastery status
        if current_mastery < 0.5:
            reasoning_parts.append(f"Current mastery ({current_mastery:.2f}) is below proficient level.")
        elif current_mastery < 0.8:
            reasoning_parts.append(f"Concept is progressing well ({current_mastery:.2f}) but not yet mastered.")
        
        # Prerequisite status
        prereqs = self.graph_engine.graph.get_prerequisites(concept_id)
        if prereqs:
            completed = set(prereqs) & set(profile.completed_concepts_ids)
            reasoning_parts.append(
                f"All {len(prereqs)} prerequisites have been completed."
            )
        
        # Future dependencies
        dependents = self.graph_engine.graph.get_dependents(concept_id)
        if dependents:
            reasoning_parts.append(
                f"This concept is a prerequisite for {len(dependents)} other concepts."
            )
        
        return " ".join(reasoning_parts) if reasoning_parts else "Recommended for continued learning."
    
    def _get_content_for_concept(self, concept_id: str) -> List[str]:
        """Get content IDs associated with a concept."""
        # In a real implementation, this would query a content-concept mapping
        return [f"content_{concept_id}_lesson_1"]
    
    def _get_review_content_for_concept(self, concept_id: str) -> List[str]:
        """Get review content IDs for a concept."""
        return [f"content_{concept_id}_review"]
