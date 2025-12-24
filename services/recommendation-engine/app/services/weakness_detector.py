"""
Weakness Detector Service

This module provides capabilities for detecting, analyzing, and tracking
student weaknesses across mathematical concepts and learning domains.
The service identifies patterns in errors and performance to pinpoint
specific areas requiring improvement.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import logging
import statistics

from ..schemas import (
    StudentProfile,
    ContentItem,
    LearningEvent,
    ConceptNode,
    RecommendationReason
)


logger = logging.getLogger(__name__)


class WeaknessType(Enum):
    """Enumeration of weakness types."""
    CONCEPTUAL = "conceptual"  # Fundamental understanding issues
    PROCEDURAL = "procedural"  # Step-by-step process issues
    APPLICATION = "application"  # Real-world application issues
    COMPUTATIONAL = "computational"  # Calculation errors
    ANALYTICAL = "analytical"  # Problem-solving approach issues
    MEMORY = "memory"  # Forgetting previously learned material


@dataclass
class Weakness:
    """Represents a detected student weakness."""
    weakness_id: str
    weakness_type: WeaknessType
    concept_id: Optional[str]
    concept_name: Optional[str]
    severity: float  # 0-1 scale
    frequency: int  # How often observed
    first_observed: datetime
    last_observed: datetime
    evidence: List[str]
    related_content_ids: List[str]
    remediation_priority: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert weakness to dictionary."""
        return {
            "weakness_id": self.weakness_id,
            "weakness_type": self.weakness_type.value,
            "concept_id": self.concept_id,
            "concept_name": self.concept_name,
            "severity": self.severity,
            "frequency": self.frequency,
            "first_observed": self.first_observed.isoformat(),
            "last_observed": self.last_observed.isoformat(),
            "evidence": self.evidence,
            "related_content_ids": self.related_content_ids,
            "remediation_priority": self.remediation_priority
        }


@dataclass
class WeaknessPattern:
    """Represents a pattern of related weaknesses."""
    pattern_id: str
    pattern_type: str
    weaknesses: List[Weakness]
    root_cause_hypothesis: str
    recommended_intervention: str
    confidence: float


class WeaknessDetector:
    """
    Service for detecting and analyzing student weaknesses.
    
    This service analyzes learning events, assessment results, and
    performance patterns to identify specific areas where students
    struggle and provides actionable insights for remediation.
    """
    
    def __init__(self):
        """Initialize the weakness detector service."""
        # Store for weakness history (in production, use database)
        self.student_weaknesses: Dict[str, List[Weakness]] = {}
        self.weakness_events: Dict[str, List[LearningEvent]] = {}
        self.concept_error_patterns: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Thresholds for weakness detection
        self.error_rate_threshold = 0.4
        self.consecutive_failure_threshold = 3
        self.time_decay_factor = 0.95
        
        logger.info("Initialized WeaknessDetector service")
    
    def analyze_student(
        self,
        profile: StudentProfile,
        recent_events: List[LearningEvent]
    ) -> List[Weakness]:
        """
        Analyze a student to detect weaknesses.
        
        Performs comprehensive analysis of recent learning events
        and performance data to identify areas of weakness.
        
        Args:
            profile: The student profile
            recent_events: Recent learning events
            
        Returns:
            List of detected weaknesses
        """
        detected_weaknesses = []
        
        # Analyze assessment failures
        assessment_weaknesses = self._analyze_assessment_failures(
            profile, recent_events
        )
        detected_weaknesses.extend(assessment_weaknesses)
        
        # Analyze error patterns
        pattern_weaknesses = self._analyze_error_patterns(
            profile, recent_events
        )
        detected_weaknesses.extend(pattern_weaknesses)
        
        # Analyze low mastery concepts
        mastery_weaknesses = self._analyze_low_mastery_concepts(profile)
        detected_weaknesses.extend(mastery_weaknesses)
        
        # Analyze forgetting patterns
        forgetting_weaknesses = self._analyze_forgetting_patterns(profile)
        detected_weaknesses.extend(forgetting_weaknesses)
        
        # Update stored weaknesses
        self._update_stored_weaknesses(profile.student_id, detected_weaknesses)
        
        logger.info(
            f"Detected {len(detected_weaknesses)} weaknesses for "
            f"student {profile.student_id}"
        )
        
        return detected_weaknesses
    
    def get_active_weaknesses(
        self,
        student_id: str,
        max_severity: float = 1.0,
        min_severity: float = 0.0
    ) -> List[Weakness]:
        """
        Get active weaknesses for a student.
        
        Retrieves current weaknesses, filtered by severity range.
        
        Args:
            student_id: The student ID
            max_severity: Maximum severity to include
            min_severity: Minimum severity to include
            
        Returns:
            List of active weaknesses
        """
        weaknesses = self.student_weaknesses.get(student_id, [])
        
        now = datetime.now()
        
        # Filter and update severity based on recency
        active_weaknesses = []
        for weakness in weaknesses:
            # Apply time decay
            days_since_last = (now - weakness.last_observed).days
            decay_factor = self.time_decay_factor ** days_since_last
            
            updated_severity = weakness.severity * decay_factor
            
            if min_severity <= updated_severity <= max_severity:
                # Create updated weakness with decayed severity
                updated_weakness = Weakness(
                    **weakness.__dict__,
                    severity=updated_severity
                )
                active_weaknesses.append(updated_weakness)
        
        # Sort by severity
        active_weaknesses.sort(key=lambda w: w.severity, reverse=True)
        
        return active_weaknesses
    
    def identify_weakness_patterns(
        self,
        student_id: str
    ) -> List[WeaknessPattern]:
        """
        Identify patterns among student weaknesses.
        
        Analyzes multiple weaknesses to find common themes and
        potential root causes.
        
        Args:
            student_id: The student ID
            
        Returns:
            List of identified weakness patterns
        """
        weaknesses = self.get_active_weaknesses(student_id)
        
        if len(weaknesses) < 2:
            return []
        
        patterns = []
        
        # Group by concept
        concept_groups = defaultdict(list)
        for weakness in weaknesses:
            if weakness.concept_id:
                concept_groups[weakness.concept_id].append(weakness)
        
        # Create patterns for concepts with multiple weaknesses
        for concept_id, concept_weaknesses in concept_groups.items():
            if len(concept_weaknesses) >= 2:
                pattern = self._create_concept_pattern(
                    concept_id, concept_weaknesses
                )
                patterns.append(pattern)
        
        # Group by weakness type
        type_groups = defaultdict(list)
        for weakness in weaknesses:
            type_groups[weakness.weakness_type].append(weakness)
        
        # Create patterns for common weakness types
        for weak_type, type_weaknesses in type_groups.items():
            if len(type_weaknesses) >= 3:
                pattern = self._create_type_pattern(
                    weak_type, type_weaknesses
                )
                patterns.append(pattern)
        
        return patterns
    
    def get_remediation_plan(
        self,
        student_id: str,
        max_weaknesses: int = 3
    ) -> Dict[str, Any]:
        """
        Generate a remediation plan for student weaknesses.
        
        Creates a prioritized plan addressing the most critical
        weaknesses with specific interventions.
        
        Args:
            student_id: The student ID
            max_weaknesses: Maximum weaknesses to address
            
        Returns:
            Remediation plan dictionary
        """
        weaknesses = self.get_active_weaknesses(student_id)
        
        if not weaknesses:
            return {
                "status": "no_weaknesses",
                "message": "No significant weaknesses detected",
                "plan": []
            }
        
        # Get top weaknesses
        top_weaknesses = weaknesses[:max_weaknesses]
        
        plan_items = []
        total_estimated_time = 0
        
        for i, weakness in enumerate(top_weaknesses):
            intervention = self._generate_intervention(weakness)
            
            plan_item = {
                "order": i + 1,
                "weakness": weakness.to_dict(),
                "intervention": intervention,
                "estimated_time_minutes": weakness.severity * 60 + 15,
                "success_criteria": self._generate_success_criteria(weakness)
            }
            
            plan_items.append(plan_item)
            total_estimated_time += plan_item["estimated_time_minutes"]
        
        return {
            "status": "remediation_required",
            "weakness_count": len(weaknesses),
            "total_estimated_time_minutes": total_estimated_time,
            "plan": plan_items,
            "created_at": datetime.now().isoformat()
        }
    
    def track_remediation_progress(
        self,
        student_id: str,
        weakness_id: str,
        assessment_score: float,
        content_id: str
    ) -> Dict[str, Any]:
        """
        Track progress on weakness remediation.
        
        Updates weakness severity based on remediation attempt results.
        
        Args:
            student_id: The student ID
            weakness_id: The weakness being addressed
            assessment_score: Score on remediation assessment (0-1)
            content_id: Content used for remediation
            
        Returns:
            Updated weakness status
        """
        weaknesses = self.student_weaknesses.get(student_id, [])
        
        weakness = next(
            (w for w in weaknesses if w.weakness_id == weakness_id),
            None
        )
        
        if not weakness:
            return {"error": "Weakness not found"}
        
        # Calculate improvement
        improvement = assessment_score - (1 - weakness.severity)
        
        if assessment_score >= 0.8:
            # Significant improvement
            new_severity = max(0.1, weakness.severity - 0.3)
            status = "improving"
        elif assessment_score >= 0.6:
            # Moderate improvement
            new_severity = max(0.2, weakness.severity - 0.15)
            status = "slight_improvement"
        else:
            # No improvement or decline
            new_severity = min(1.0, weakness.severity + 0.1)
            status = "no_improvement"
        
        # Update weakness
        weakness.severity = new_severity
        weakness.last_observed = datetime.now()
        weakness.frequency += 1
        weakness.related_content_ids.append(content_id)
        
        # Add evidence
        weakness.evidence.append(
            f"Remediation attempt: score={assessment_score:.2f}, "
            f"status={status}"
        )
        
        return {
            "weakness_id": weakness_id,
            "previous_severity": weakness.severity + 0.1 if status != "no_improvement" else weakness.severity,
            "new_severity": new_severity,
            "status": status,
            "improvement": improvement
        }
    
    def _analyze_assessment_failures(
        self,
        profile: StudentProfile,
        events: List[LearningEvent]
    ) -> List[Weakness]:
        """Analyze assessment failures to detect weaknesses."""
        weaknesses = []
        
        # Find low-scoring assessments
        low_score_events = [
            e for e in events
            if e.event_type == "assessment" and
            e.metadata.get("assessment_score", 1.0) < 0.6
        ]
        
        # Group by content/concept
        content_failures = defaultdict(list)
        for event in low_score_events:
            content_id = event.content_id
            content_failures[content_id].append(event)
        
        for content_id, failure_events in content_failures.items():
            if len(failure_events) >= 2:
                # Determine weakness type
                avg_score = sum(
                    e.metadata.get("assessment_score", 0)
                    for e in failure_events
                ) / len(failure_events)
                
                # Analyze error types if available
                error_types = []
                for event in failure_events:
                    error_types.extend(
                        event.metadata.get("error_types", [])
                    )
                
                weakness_type = self._classify_weakness_type(error_types, avg_score)
                
                weakness = Weakness(
                    weakness_id=f"wf_{content_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    weakness_type=weakness_type,
                    concept_id=content_id,
                    concept_name=self._get_concept_name(content_id),
                    severity=1.0 - avg_score,
                    frequency=len(failure_events),
                    first_observed=failure_events[0].timestamp,
                    last_observed=failure_events[-1].timestamp,
                    evidence=[
                        f"Failed {len(failure_events)} assessments",
                        f"Average score: {avg_score:.2f}"
                    ],
                    related_content_ids=[content_id],
                    remediation_priority=self._calculate_priority(1.0 - avg_score, len(failure_events))
                )
                
                weaknesses.append(weakness)
        
        return weaknesses
    
    def _analyze_error_patterns(
        self,
        profile: StudentProfile,
        events: List[LearningEvent]
    ) -> List[Weakness]:
        """Analyze error patterns to detect systematic weaknesses."""
        weaknesses = []
        
        # Collect error patterns
        error_patterns = defaultdict(list)
        
        for event in events:
            if "error_pattern" in event.metadata:
                pattern = event.metadata["error_pattern"]
                error_patterns[pattern].append(event)
        
        for pattern, pattern_events in error_patterns.items():
            if len(pattern_events) >= 3:
                weakness_type = self._classify_from_pattern(pattern)
                
                # Get associated concept
                concept_id = pattern_events[0].metadata.get("concept_id")
                
                weakness = Weakness(
                    weakness_id=f"wp_{pattern}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    weakness_type=weakness_type,
                    concept_id=concept_id,
                    concept_name=self._get_concept_name(concept_id) if concept_id else None,
                    severity=0.6,
                    frequency=len(pattern_events),
                    first_observed=pattern_events[0].timestamp,
                    last_observed=pattern_events[-1].timestamp,
                    evidence=[
                        f"Repeated error pattern: {pattern}",
                        f"Observed {len(pattern_events)} times"
                    ],
                    related_content_ids=list(set(e.content_id for e in pattern_events)),
                    remediation_priority=5
                )
                
                weaknesses.append(weakness)
        
        return weaknesses
    
    def _analyze_low_mastery_concepts(
        self,
        profile: StudentProfile
    ) -> List[Weakness]:
        """Analyze concepts with low mastery levels."""
        weaknesses = []
        
        for concept_id, mastery in profile.mastery_states.items():
            if mastery < 0.5:
                # Determine weakness type based on mastery pattern
                weakness_type = WeaknessType.CONCEPTUAL
                
                # Check if this is a recent decline
                decay_predictions = getattr(profile, "decay_predictions", {})
                predicted_decay = decay_predictions.get(concept_id, 0)
                
                if predicted_decay > 0.2:
                    weakness_type = WeaknessType.MEMORY
                
                weakness = Weakness(
                    weakness_id=f"wm_{concept_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    weakness_type=weakness_type,
                    concept_id=concept_id,
                    concept_name=self._get_concept_name(concept_id),
                    severity=1.0 - mastery,
                    frequency=1,
                    first_observed=datetime.now() - timedelta(days=7),
                    last_observed=datetime.now(),
                    evidence=[
                        f"Mastery level: {mastery:.2f}",
                        "Below threshold for proficiency"
                    ],
                    related_content_ids=[],
                    remediation_priority=self._calculate_priority(1.0 - mastery, 1)
                )
                
                weaknesses.append(weakness)
        
        return weaknesses
    
    def _analyze_forgetting_patterns(
        self,
        profile: StudentProfile
    ) -> List[Weakness]:
        """Analyze patterns indicating forgetting of material."""
        weaknesses = []
        
        decay_predictions = getattr(profile, "decay_predictions", {})
        
        for concept_id, predicted_mastery in decay_predictions.items():
            if predicted_mastery < 0.5:
                original_mastery = profile.mastery_states.get(concept_id, 1.0)
                
                if original_mastery - predicted_mastery > 0.3:
                    weakness = Weakness(
                        weakness_id=f"wf_{concept_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        weakness_type=WeaknessType.MEMORY,
                        concept_id=concept_id,
                        concept_name=self._get_concept_name(concept_id),
                        severity=original_mastery - predicted_mastery,
                        frequency=1,
                        first_observed=datetime.now() - timedelta(days=14),
                        last_observed=datetime.now(),
                        evidence=[
                            f"Original mastery: {original_mastery:.2f}",
                            f"Predicted current: {predicted_mastery:.2f}",
                            "Significant decay detected"
                        ],
                        related_content_ids=[],
                        remediation_priority=6
                    )
                    
                    weaknesses.append(weakness)
        
        return weaknesses
    
    def _create_concept_pattern(
        self,
        concept_id: str,
        weaknesses: List[Weakness]
    ) -> WeaknessPattern:
        """Create a pattern from multiple weaknesses in the same concept."""
        concept_name = self._get_concept_name(concept_id)
        
        # Determine root cause
        types = set(w.weakness_type for w in weaknesses)
        
        if WeaknessType.CONCEPTUAL in types:
            root_cause = "Fundamental understanding gaps in concept"
            intervention = "Review core concepts with interactive tutorials"
        elif WeaknessType.PROCEDURAL in types:
            root_cause = "Difficulty with step-by-step processes"
            intervention = "Practice with guided step-by-step exercises"
        else:
            root_cause = "Multiple issue types in concept area"
            intervention = "Comprehensive review with varied content types"
        
        avg_severity = sum(w.severity for w in weaknesses) / len(weaknesses)
        
        return WeaknessPattern(
            pattern_id=f"pattern_{concept_id}",
            pattern_type="concept_cluster",
            weaknesses=weaknesses,
            root_cause_hypothesis=root_cause,
            recommended_intervention=intervention,
            confidence=0.7 + avg_severity * 0.3
        )
    
    def _create_type_pattern(
        self,
        weakness_type: WeaknessType,
        weaknesses: List[Weakness]
    ) -> WeaknessPattern:
        """Create a pattern from multiple weaknesses of the same type."""
        # Determine root cause by type
        type_interventions = {
            WeaknessType.CONCEPTUAL: "Focus on conceptual understanding with visual aids and examples",
            WeaknessType.PROCEDURAL: "Provide structured practice with worked examples",
            WeaknessType.APPLICATION: "Include more real-world problem scenarios",
            WeaknessType.COMPUTATIONAL: "Practice basic calculations with immediate feedback",
            WeaknessType.ANALYTICAL: "Teach systematic problem-solving frameworks",
            WeaknessType.MEMORY: "Implement spaced repetition for retention"
        }
        
        concepts = set(w.concept_id for w in weaknesses if w.concept_id)
        
        return WeaknessPattern(
            pattern_id=f"pattern_type_{weakness_type.value}",
            pattern_type="weakness_type_cluster",
            weaknesses=weaknesses,
            root_cause_hypothesis=f"Systemic {weakness_type.value} issues across multiple concepts",
            recommended_intervention=type_interventions.get(
                weakness_type,
                "General review and practice"
            ),
            confidence=0.75
        )
    
    def _classify_weakness_type(
        self,
        error_types: List[str],
        avg_score: float
    ) -> WeaknessType:
        """Classify weakness type from error patterns and scores."""
        if not error_types:
            return WeaknessType.CONCEPTUAL
        
        type_mapping = {
            "calculation": WeaknessType.COMPUTATIONAL,
            "formula": WeaknessType.CONCEPTUAL,
            "understanding": WeaknessType.CONCEPTUAL,
            "steps": WeaknessType.PROCEDURAL,
            "application": WeaknessType.APPLICATION,
            "problem_solving": WeaknessType.ANALYTICAL,
            "forgot": WeaknessType.MEMORY
        }
        
        # Count error types
        type_counts = defaultdict(int)
        for error in error_types:
            for key, weak_type in type_mapping.items():
                if key in error.lower():
                    type_counts[weak_type] += 1
        
        if type_counts:
            return max(type_counts.items(), key=lambda x: x[1])[0]
        
        return WeaknessType.CONCEPTUAL
    
    def _classify_from_pattern(self, pattern: str) -> WeaknessType:
        """Classify weakness type from error pattern name."""
        pattern_lower = pattern.lower()
        
        type_mapping = {
            "calculation": WeaknessType.COMPUTATIONAL,
            "formula": WeaknessType.CONCEPTUAL,
            "procedure": WeaknessType.PROCEDURAL,
            "application": WeaknessType.APPLICATION,
            "analysis": WeaknessType.ANALYTICAL,
            "memory": WeaknessType.MEMORY
        }
        
        for key, weak_type in type_mapping.items():
            if key in pattern_lower:
                return weak_type
        
        return WeaknessType.CONCEPTUAL
    
    def _generate_intervention(self, weakness: Weakness) -> str:
        """Generate intervention strategy for a weakness."""
        interventions = {
            WeaknessType.CONCEPTUAL: (
                "Review fundamental concepts through interactive tutorials. "
                "Use visual aids and concrete examples to build understanding."
            ),
            WeaknessType.PROCEDURAL: (
                "Practice step-by-step with guided exercises. "
                "Use worked examples and progressive problem difficulty."
            ),
            WeaknessType.APPLICATION: (
                "Solve real-world scenarios with scaffolded support. "
                "Connect abstract concepts to practical situations."
            ),
            WeaknessType.COMPUTATIONAL: (
                "Practice basic calculations with immediate feedback. "
                "Use timed drills to build fluency."
            ),
            WeaknessType.ANALYTICAL: (
                "Learn systematic problem-solving approaches. "
                "Practice decomposition and strategic planning."
            ),
            WeaknessType.MEMORY: (
                "Implement spaced repetition review sessions. "
                "Use varied practice to strengthen retention."
            )
        }
        
        return interventions.get(
            weakness.weakness_type,
            "General review and practice with varied content types."
        )
    
    def _generate_success_criteria(self, weakness: Weakness) -> str:
        """Generate success criteria for weakness remediation."""
        target_score = 0.8
        
        return (
            f"Achievement of {target_score:.0%} or higher on "
            f"targeted assessments in the affected concept area."
        )
    
    def _calculate_priority(
        self,
        severity: float,
        frequency: int
    ) -> int:
        """Calculate remediation priority score."""
        return min(10, int(severity * 5 + frequency * 2))
    
    def _get_concept_name(self, concept_id: Optional[str]) -> Optional[str]:
        """Get concept name from cache or return ID."""
        # In a real implementation, this would look up the concept
        return concept_id
    
    def _update_stored_weaknesses(
        self,
        student_id: str,
        new_weaknesses: List[Weakness]
    ):
        """Update stored weaknesses with new detections."""
        if student_id not in self.student_weaknesses:
            self.student_weaknesses[student_id] = []
        
        existing = self.student_weaknesses[student_id]
        existing_ids = {w.weakness_id for w in existing}
        
        # Add new weaknesses
        for weakness in new_weaknesses:
            if weakness.weakness_id not in existing_ids:
                existing.append(weakness)
