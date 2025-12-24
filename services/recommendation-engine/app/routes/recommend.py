"""
Recommendation Routes

This module provides FastAPI routes for the recommendation engine API.
It exposes endpoints for generating recommendations, managing student profiles,
and retrieving recommendation insights.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
import logging

from ..schemas import (
    StudentProfile,
    ContentItem,
    LearningPath,
    RecommendationRequest,
    RecommendationResponse,
    LearningEvent,
    ConceptNode
)
from ..engines.rule_based import RuleBasedEngine
from ..engines.graph_based import GraphBasedEngine
from ..engines.adaptive_engine import AdaptiveEngine
from ..services.concept_recommender import ConceptRecommender
from ..services.progress_analyzer import ProgressAnalyzer
from ..services.weakness_detector import WeaknessDetector


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/recommend", tags=["Recommendations"])


# Storage for demo purposes (in production, use database)
student_profiles: Dict[str, StudentProfile] = {}
content_items: Dict[str, ContentItem] = {}
concept_nodes: Dict[str, ConceptNode] = {}


def get_engine() -> AdaptiveEngine:
    """Get or create the adaptive recommendation engine."""
    if not hasattr(router, "_engine"):
        rule_engine = RuleBasedEngine()
        graph_engine = GraphBasedEngine()
        router._engine = AdaptiveEngine(
            rule_engine=rule_engine,
            graph_engine=graph_engine
        )
    return router._engine


def get_concept_recommender() -> ConceptRecommender:
    """Get or create the concept recommender service."""
    if not hasattr(router, "_concept_recommender"):
        router._concept_recommender = ConceptRecommender()
    return router._concept_recommender


def get_progress_analyzer() -> ProgressAnalyzer:
    """Get or create the progress analyzer service."""
    if not hasattr(router, "_progress_analyzer"):
        router._progress_analyzer = ProgressAnalyzer()
    return router._progress_analyzer


def get_weakness_detector() -> WeaknessDetector:
    """Get or create the weakness detector service."""
    if not hasattr(router, "_weakness_detector"):
        router._weakness_detector = WeaknessDetector()
    return router._weakness_detector


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Generate content recommendations for a student.
    
    This endpoint accepts a student profile and available content,
    then returns personalized recommendations based on multiple
    recommendation strategies.
    """
    try:
        engine = get_engine()
        
        # Get available content
        available = [
            content_items[c_id] for c_id in request.available_content_ids
            if c_id in content_items
        ]
        
        if not available:
            # Return empty response with available content check
            return RecommendationResponse(
                student_id=request.student_id,
                recommendations=[],
                reasons=[],
                metadata={
                    "status": "no_content_available",
                    "message": "No matching content found for requested IDs"
                }
            )
        
        # Generate recommendations
        profile = request.profile or student_profiles.get(
            request.student_id,
            StudentProfile(student_id=request.student_id)
        )
        
        recommendations, reasons, metadata = engine.recommend(
            profile=profile,
            available_content=available,
            max_results=request.max_results or 10
        )
        
        return RecommendationResponse(
            student_id=request.student_id,
            recommendations=[r.content_id for r in recommendations],
            reasons=reasons,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning-path", response_model=LearningPath)
async def generate_learning_path(
    student_id: str,
    target_concepts: List[str],
    content_ids: Optional[List[str]] = Query(default=None)
):
    """
    Generate a learning path for target concepts.
    
    Creates an ordered sequence of content items that systematically
    builds toward mastery of the specified target concepts.
    """
    try:
        engine = get_engine()
        concept_recommender = get_concept_recommender()
        
        # Get profile
        profile = student_profiles.get(
            student_id,
            StudentProfile(student_id=student_id)
        )
        
        # Get available content
        if content_ids:
            available = [
                content_items[c_id] for c_id in content_ids
                if c_id in content_items
            ]
        else:
            available = list(content_items.values())
        
        # Generate learning path
        learning_path = engine.generate_adaptive_learning_path(
            profile=profile,
            target_outcomes=target_concepts,
            available_content=available
        )
        
        return learning_path
        
    except Exception as e:
        logger.error(f"Learning path generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/concepts/next")
async def get_next_concepts(
    student_id: str,
    max_concepts: int = Query(default=5, le=10)
):
    """
    Get recommended next concepts to learn.
    
    Analyzes current mastery states and learning progress to
    recommend the most appropriate next concepts.
    """
    try:
        concept_recommender = get_concept_recommender()
        
        # Get profile
        profile = student_profiles.get(
            student_id,
            StudentProfile(student_id=student_id)
        )
        
        recommendations = concept_recommender.recommend_next_concepts(
            profile=profile,
            max_concepts=max_concepts
        )
        
        return {
            "student_id": student_id,
            "recommendations": [
                {
                    "concept_id": r.concept_id,
                    "concept_name": r.concept_name,
                    "priority": r.priority,
                    "confidence": r.confidence,
                    "estimated_time_minutes": r.estimated_time_minutes,
                    "reasoning": r.reasoning
                }
                for r in recommendations
            ]
        }
        
    except Exception as e:
        logger.error(f"Next concepts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/concepts/gaps")
async def get_concept_gaps(
    student_id: str,
    target_mastery: float = Query(default=0.8, ge=0.5, le=1.0)
):
    """
    Identify gaps in concept mastery.
    
    Returns concepts where mastery is below the target level,
    ranked by gap size.
    """
    try:
        concept_recommender = get_concept_recommender()
        
        # Get profile
        profile = student_profiles.get(
            student_id,
            StudentProfile(student_id=student_id)
        )
        
        gaps = concept_recommender.identify_concept_gaps(
            profile=profile,
            target_mastery=target_mastery
        )
        
        return {
            "student_id": student_id,
            "target_mastery": target_mastery,
            "gaps": [
                {
                    "concept_id": g.concept_id,
                    "concept_name": g.concept_name,
                    "current_mastery": g.current_mastery,
                    "gap_size": g.gap_size,
                    "estimated_time_to_fill": g.estimated_time_to_fill,
                    "priority_concepts": g.priority_concepts
                }
                for g in gaps
            ]
        }
        
    except Exception as e:
        logger.error(f"Concept gaps error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/concepts/prerequisites/{concept_id}")
async def get_prerequisite_status(
    student_id: str,
    concept_id: str
):
    """
    Get prerequisite status for a concept.
    
    Returns which prerequisites are completed and which are missing.
    """
    try:
        concept_recommender = get_concept_recommender()
        
        # Get profile
        profile = student_profiles.get(
            student_id,
            StudentProfile(student_id=student_id)
        )
        
        status = concept_recommender.get_concept_prerequisites(
            concept_id=concept_id,
            profile=profile
        )
        
        return {
            "student_id": student_id,
            "concept_id": concept_id,
            "prerequisite_status": status
        }
        
    except Exception as e:
        logger.error(f"Prerequisite status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/concepts/review")
async def get_review_recommendations(
    student_id: str,
    review_threshold: float = Query(default=0.6, ge=0.3, le=0.9),
    max_concepts: int = Query(default=5, le=10)
):
    """
    Get concepts requiring review.
    
    Identifies concepts where mastery has decayed below the
    review threshold.
    """
    try:
        concept_recommender = get_concept_recommender()
        
        # Get profile
        profile = student_profiles.get(
            student_id,
            StudentProfile(student_id=student_id)
        )
        
        recommendations = concept_recommender.suggest_review_concepts(
            profile=profile,
            review_threshold=review_threshold,
            max_concepts=max_concepts
        )
        
        return {
            "student_id": student_id,
            "review_threshold": review_threshold,
            "recommendations": [
                {
                    "concept_id": r.concept_id,
                    "concept_name": r.concept_name,
                    "priority": r.priority,
                    "mastery_prerequisite": r.mastery_prerequisite,
                    "reasoning": r.reasoning
                }
                for r in recommendations
            ]
        }
        
    except Exception as e:
        logger.error(f"Review recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress/report")
async def get_progress_report(
    student_id: str,
    period_days: int = Query(default=30, ge=7, le=365)
):
    """
    Generate a comprehensive progress report.
    
    Returns detailed analysis of learning progress over the
    specified time period.
    """
    try:
        progress_analyzer = get_progress_analyzer()
        
        report = progress_analyzer.generate_progress_report(
            student_id=student_id,
            period_days=period_days
        )
        
        return {
            "student_id": student_id,
            "report_period": {
                "start": report.report_period[0].isoformat(),
                "end": report.report_period[1].isoformat()
            },
            "summary": report.summary,
            "trends": [
                {
                    "metric": t.metric.value,
                    "direction": t.direction,
                    "slope": t.slope,
                    "confidence": t.confidence
                }
                for t in report.trends
            ],
            "recommendations": report.recommendations,
            "generated_at": report.generated_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Progress report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress/velocity")
async def get_learning_velocity(
    student_id: str,
    window_days: int = Query(default=7, ge=1, le=30)
):
    """
    Calculate learning velocity metrics.
    
    Returns metrics showing how quickly the student is progressing
    through the curriculum.
    """
    try:
        progress_analyzer = get_progress_analyzer()
        
        velocity = progress_analyzer.calculate_learning_velocity(
            student_id=student_id,
            window_days=window_days
        )
        
        return {
            "student_id": student_id,
            "velocity_metrics": velocity
        }
        
    except Exception as e:
        logger.error(f"Learning velocity error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress/prediction")
async def predict_future_mastery(
    student_id: str,
    days_ahead: int = Query(default=30, ge=7, le=365)
):
    """
    Predict future mastery levels.
    
    Uses current trends to project future mastery assuming
    continued learning patterns.
    """
    try:
        progress_analyzer = get_progress_analyzer()
        
        prediction = progress_analyzer.predict_future_mastery(
            student_id=student_id,
            days_ahead=days_ahead
        )
        
        return {
            "student_id": student_id,
            "prediction": prediction
        }
        
    except Exception as e:
        logger.error(f"Mastery prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weaknesses")
async def get_student_weaknesses(
    student_id: str,
    min_severity: float = Query(default=0.3, ge=0.0, le=1.0),
    max_severity: float = Query(default=1.0, ge=0.0, le=1.0)
):
    """
    Get active weaknesses for a student.
    
    Returns detected weaknesses within the specified severity range.
    """
    try:
        weakness_detector = get_weakness_detector()
        
        weaknesses = weakness_detector.get_active_weaknesses(
            student_id=student_id,
            min_severity=min_severity,
            max_severity=max_severity
        )
        
        return {
            "student_id": student_id,
            "weakness_count": len(weaknesses),
            "weaknesses": [w.to_dict() for w in weaknesses]
        }
        
    except Exception as e:
        logger.error(f"Weaknesses error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weaknesses/patterns")
async def get_weakness_patterns(student_id: str):
    """
    Identify patterns among student weaknesses.
    
    Returns groups of related weaknesses that may share
    common root causes.
    """
    try:
        weakness_detector = get_weakness_detector()
        
        patterns = weakness_detector.identify_weakness_patterns(
            student_id=student_id
        )
        
        return {
            "student_id": student_id,
            "pattern_count": len(patterns),
            "patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "pattern_type": p.pattern_type,
                    "weakness_count": len(p.weaknesses),
                    "root_cause_hypothesis": p.root_cause_hypothesis,
                    "recommended_intervention": p.recommended_intervention,
                    "confidence": p.confidence
                }
                for p in patterns
            ]
        }
        
    except Exception as e:
        logger.error(f"Weakness patterns error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weaknesses/remediation-plan")
async def get_remediation_plan(
    student_id: str,
    max_weaknesses: int = Query(default=3, ge=1, le=5)
):
    """
    Generate a remediation plan for weaknesses.
    
    Creates a prioritized plan for addressing the most
    critical weaknesses.
    """
    try:
        weakness_detector = get_weakness_detector()
        
        plan = weakness_detector.get_remediation_plan(
            student_id=student_id,
            max_weaknesses=max_weaknesses
        )
        
        return plan
        
    except Exception as e:
        logger.error(f"Remediation plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def record_feedback(
    student_id: str,
    content_id: str,
    engagement_score: float = Query(..., ge=0.0, le=1.0),
    completion: bool = True,
    assessment_score: Optional[float] = Query(default=None, ge=0.0, le=1.0)
):
    """
    Record feedback for a recommendation.
    
    Updates the recommendation system based on student interaction
    with recommended content.
    """
    try:
        engine = get_engine()
        
        engine.process_feedback(
            student_id=student_id,
            content_id=content_id,
            engagement_score=engagement_score,
            completion=completion,
            assessment_score=assessment_score
        )
        
        return {
            "status": "recorded",
            "student_id": student_id,
            "content_id": content_id
        }
        
    except Exception as e:
        logger.error(f"Feedback recording error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/strategies")
async def get_strategy_insights():
    """
    Get insights about recommendation strategy performance.
    
    Returns metrics showing how well different recommendation
    strategies are performing.
    """
    try:
        engine = get_engine()
        
        insights = engine.get_strategy_insights()
        
        return insights
        
    except Exception as e:
        logger.error(f"Strategy insights error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Profile management endpoints

@router.post("/profiles")
async def create_profile(profile: StudentProfile):
    """
    Create or update a student profile.
    
    Stores the profile for use in future recommendations.
    """
    student_profiles[profile.student_id] = profile
    
    # Initialize progress analyzer snapshot
    progress_analyzer = get_progress_analyzer()
    progress_analyzer.create_snapshot(profile)
    
    return {
        "status": "created",
        "student_id": profile.student_id
    }


@router.get("/profiles/{student_id}")
async def get_profile(student_id: str):
    """
    Get a student profile.
    
    Returns the stored profile for the specified student.
    """
    if student_id not in student_profiles:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return student_profiles[student_id]


# Content management endpoints

@router.post("/content")
async def add_content(content: ContentItem):
    """
    Add content to the recommendation system.
    
    Stores content for use in recommendations.
    """
    content_items[content.content_id] = content
    
    return {
        "status": "added",
        "content_id": content.content_id
    }


@router.get("/content/{content_id}")
async def get_content(content_id: str):
    """
    Get content details.
    
    Returns the stored content item.
    """
    if content_id not in content_items:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return content_items[content_id]


@router.post("/concepts")
async def add_concepts(concepts: List[ConceptNode]):
    """
    Add concepts to the knowledge base.
    
    Stores concepts and builds the concept dependency graph.
    """
    concept_recommender = get_concept_recommender()
    concept_recommender.add_concepts(concepts)
    
    for concept in concepts:
        concept_nodes[concept.concept_id] = concept
    
    return {
        "status": "added",
        "concepts_added": len(concepts)
    }


@router.get("/concepts/{concept_id}")
async def get_concept(concept_id: str):
    """
    Get concept details.
    
    Returns the stored concept.
    """
    if concept_id not in concept_nodes:
        raise HTTPException(status_code=404, detail="Concept not found")
    
    return concept_nodes[concept_id]
