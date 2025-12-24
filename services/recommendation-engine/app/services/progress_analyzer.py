"""
Progress Analyzer Service

This module provides comprehensive progress tracking and analysis capabilities
for monitoring student learning trajectories, identifying trends, and measuring
educational outcomes over time.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import statistics

from ..schemas import (
    StudentProfile,
    ContentItem,
    LearningEvent,
    MasteryState
)


logger = logging.getLogger(__name__)


class ProgressMetric(Enum):
    """Enumeration of progress metrics."""
    MASTERY_CHANGE = "mastery_change"
    CONTENT_COMPLETION = "content_completion"
    TIME_ON_TASK = "time_on_task"
    ENGAGEMENT_LEVEL = "engagement_level"
    LEARNING_VELOCITY = "learning_velocity"
    ACCURACY_TREND = "accuracy_trend"


@dataclass
class ProgressSnapshot:
    """A snapshot of student progress at a point in time."""
    timestamp: datetime
    overall_mastery: float
    concept_masteries: Dict[str, float]
    content_completed: int
    total_time_spent: int  # minutes
    average_accuracy: float
    current_streak: int  # days
    engagement_level: str


@dataclass
class ProgressTrend:
    """Represents a detected trend in student progress."""
    metric: ProgressMetric
    direction: str  # "improving", "stable", "declining"
    slope: float
    confidence: float
    start_value: float
    end_value: float
    start_date: datetime
    end_date: datetime


@dataclass
class ProgressReport:
    """Comprehensive progress report for a student."""
    student_id: str
    report_period: Tuple[datetime, datetime]
    snapshots: List[ProgressSnapshot]
    trends: List[ProgressTrend]
    summary: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime


class ProgressAnalyzer:
    """
    Service for analyzing student learning progress.
    
    This service tracks progress over time, identifies trends,
    measures learning velocity, and generates comprehensive
    progress reports for students and educators.
    """
    
    def __init__(self):
        """Initialize the progress analyzer service."""
        # Store for historical data (in production, use database)
        self.student_history: Dict[str, List[LearningEvent]] = {}
        self.student_snapshots: Dict[str, List[ProgressSnapshot]] = {}
        self.learning_velocity_window = 7  # days for velocity calculation
        
        logger.info("Initialized ProgressAnalyzer service")
    
    def record_event(self, event: LearningEvent):
        """
        Record a learning event for tracking.
        
        Args:
            event: The learning event to record
        """
        if event.student_id not in self.student_history:
            self.student_history[event.student_id] = []
        
        self.student_history[event.student_id].append(event)
        
        logger.debug(
            f"Recorded event for student {event.student_id}: "
            f"{event.event_type}"
        )
    
    def create_snapshot(
        self,
        profile: StudentProfile,
        current_time: Optional[datetime] = None
    ) -> ProgressSnapshot:
        """
        Create a progress snapshot for a student.
        
        Args:
            profile: The current student profile
            current_time: Optional timestamp (defaults to now)
            
        Returns:
            ProgressSnapshot with current state
        """
        if current_time is None:
            current_time = datetime.now()
        
        # Calculate overall mastery
        if profile.mastery_states:
            overall_mastery = sum(profile.mastery_states.values()) / len(profile.mastery_states)
        else:
            overall_mastery = 0.0
        
        # Calculate average accuracy from recent events
        recent_events = self._get_recent_events(
            profile.student_id,
            days=7
        )
        
        accuracy_scores = [
            e.metadata.get("assessment_score", 0.5)
            for e in recent_events
            if "assessment_score" in e.metadata
        ]
        
        average_accuracy = (
            sum(accuracy_scores) / len(accuracy_scores)
            if accuracy_scores
            else profile.average_score or 0.5
        )
        
        snapshot = ProgressSnapshot(
            timestamp=current_time,
            overall_mastery=overall_mastery,
            concept_masteries=dict(profile.mastery_states),
            content_completed=len(profile.completed_content_ids),
            total_time_spent=self._calculate_total_time(profile.student_id),
            average_accuracy=average_accuracy,
            current_streak=profile.learning_streak or 0,
            engagement_level=self._calculate_engagement_level(profile, recent_events)
        )
        
        # Store snapshot
        if profile.student_id not in self.student_snapshots:
            self.student_snapshots[profile.student_id] = []
        
        self.student_snapshots[profile.student_id].append(snapshot)
        
        return snapshot
    
    def analyze_trends(
        self,
        student_id: str,
        metric: ProgressMetric,
        days: int = 30
    ) -> Optional[ProgressTrend]:
        """
        Analyze trends for a specific metric.
        
        Uses linear regression to detect trends in the specified metric
        over the analysis period.
        
        Args:
            student_id: The student ID
            metric: The metric to analyze
            days: Number of days to analyze
            
        Returns:
            ProgressTrend with analysis results
        """
        snapshots = self._get_snapshots_in_range(student_id, days)
        
        if len(snapshots) < 3:
            logger.info(f"Insufficient data for trend analysis: {len(snapshots)} snapshots")
            return None
        
        # Extract values based on metric
        values = []
        timestamps = []
        
        for snapshot in snapshots:
            if metric == ProgressMetric.MASTERY_CHANGE:
                values.append(snapshot.overall_mastery)
            elif metric == ProgressMetric.CONTENT_COMPLETION:
                values.append(snapshot.content_completed)
            elif metric == ProgressMetric.TIME_ON_TASK:
                values.append(snapshot.total_time_spent)
            elif metric == ProgressMetric.ENGAGEMENT_LEVEL:
                engagement_map = {
                    "high": 1.0, "medium": 0.6, "low": 0.3
                }
                values.append(engagement_map.get(snapshot.engagement_level, 0.5))
            
            timestamps.append(snapshot.timestamp)
        
        if len(values) < 3:
            return None
        
        # Calculate trend using linear regression
        slope, intercept = self._linear_regression(range(len(values)), values)
        
        # Determine direction and confidence
        if abs(slope) < 0.01:
            direction = "stable"
            confidence = 0.5
        elif slope > 0:
            direction = "improving"
            confidence = min(0.95, 0.5 + slope * 10)
        else:
            direction = "declining"
            confidence = min(0.95, 0.5 + abs(slope) * 10)
        
        return ProgressTrend(
            metric=metric,
            direction=direction,
            slope=slope,
            confidence=confidence,
            start_value=values[0],
            end_value=values[-1],
            start_date=timestamps[0],
            end_date=timestamps[-1]
        )
    
    def calculate_learning_velocity(
        self,
        student_id: str,
        window_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate learning velocity metrics.
        
        Measures how quickly a student is progressing through
        the curriculum over a specified time window.
        
        Args:
            student_id: The student ID
            window_days: Optional custom window (defaults to config value)
            
        Returns:
            Dictionary with velocity metrics
        """
        if window_days is None:
            window_days = self.learning_velocity_window
        
        snapshots = self._get_snapshots_in_range(student_id, window_days)
        
        if len(snapshots) < 2:
            return {
                "mastery_velocity": 0.0,
                "content_velocity": 0.0,
                "time_velocity": 0.0,
                "window_days": window_days,
                "data_points": len(snapshots)
            }
        
        first = snapshots[0]
        last = snapshots[-1]
        
        days_diff = (last.timestamp - first.timestamp).days or 1
        
        # Calculate velocity metrics
        mastery_velocity = (
            (last.overall_mastery - first.overall_mastery) / days_diff
        )
        
        content_velocity = (
            (last.content_completed - first.content_completed) / days_diff
        )
        
        time_velocity = (
            (last.total_time_spent - first.total_time_spent) / days_diff
        )
        
        return {
            "mastery_velocity": mastery_velocity,
            "content_velocity": content_velocity,
            "time_velocity": time_velocity,
            "window_days": window_days,
            "data_points": len(snapshots),
            "period": {
                "start": first.timestamp.isoformat(),
                "end": last.timestamp.isoformat()
            }
        }
    
    def detect_plateau(
        self,
        student_id: str,
        threshold: float = 0.05,
        window_days: int = 14
    ) -> Optional[Dict[str, Any]]:
        """
        Detect if a student has hit a learning plateau.
        
        Identifies periods where progress has stalled or significantly
        slowed down, indicating potential need for intervention.
        
        Args:
            student_id: The student ID
            threshold: Maximum allowed mastery change for plateau detection
            window_days: Number of days to analyze
            
        Returns:
            Plateau detection results or None if not detected
        """
        snapshots = self._get_snapshots_in_range(student_id, window_days)
        
        if len(snapshots) < 5:
            return None
        
        # Calculate mastery change over window
        first = snapshots[0]
        last = snapshots[-1]
        
        mastery_change = last.overall_mastery - first.overall_mastery
        
        if abs(mastery_change) < threshold:
            # Check if this is a sustained plateau
            middle_snapshots = snapshots[2:-2]
            
            if middle_snapshots:
                variance = statistics.variance(
                    [s.overall_mastery for s in snapshots]
                )
                
                return {
                    "is_plateau": True,
                    "mastery_change": mastery_change,
                    "variance": variance,
                    "window_days": window_days,
                    "recommendations": self._get_plateau_recommendations(student_id)
                }
        
        return None
    
    def generate_progress_report(
        self,
        student_id: str,
        period_days: int = 30
    ) -> ProgressReport:
        """
        Generate a comprehensive progress report.
        
        Creates a detailed report covering all aspects of student
        progress over the specified time period.
        
        Args:
            student_id: The student ID
            period_days: Number of days to include in report
            
        Returns:
            Comprehensive progress report
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Get snapshots
        snapshots = self._get_snapshots_in_range(student_id, period_days)
        
        # Analyze trends
        trends = []
        for metric in ProgressMetric:
            trend = self.analyze_trends(student_id, metric, period_days)
            if trend:
                trends.append(trend)
        
        # Calculate summary metrics
        if snapshots:
            latest = snapshots[-1]
            first = snapshots[0]
            
            summary = {
                "starting_mastery": first.overall_mastery,
                "current_mastery": latest.overall_mastery,
                "mastery_improvement": latest.overall_mastery - first.overall_mastery,
                "content_completed": latest.content_completed - first.content_completed,
                "time_spent": latest.total_time_spent - first.total_time_spent,
                "current_streak": latest.current_streak,
                "average_accuracy": latest.average_accuracy,
                "engagement_level": latest.engagement_level
            }
        else:
            summary = {
                "starting_mastery": 0.0,
                "current_mastery": 0.0,
                "mastery_improvement": 0.0,
                "content_completed": 0,
                "time_spent": 0,
                "current_streak": 0,
                "average_accuracy": 0.0,
                "engagement_level": "unknown"
            }
        
        # Generate recommendations
        recommendations = self._generate_progress_recommendations(
            student_id, summary, trends
        )
        
        return ProgressReport(
            student_id=student_id,
            report_period=(start_date, end_date),
            snapshots=snapshots,
            trends=trends,
            summary=summary,
            recommendations=recommendations,
            generated_at=datetime.now()
        )
    
    def predict_future_mastery(
        self,
        student_id: str,
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Predict future mastery levels.
        
        Uses current trends and velocity to project future mastery
        levels assuming continued similar learning patterns.
        
        Args:
            student_id: The student ID
            days_ahead: Number of days to predict ahead
            
        Returns:
            Prediction dictionary with confidence intervals
        """
        velocity = self.calculate_learning_velocity(student_id)
        
        snapshots = self._get_snapshots_in_range(student_id, 30)
        
        if not snapshots:
            return {
                "error": "Insufficient data for prediction"
            }
        
        current_mastery = snapshots[-1].overall_mastery
        velocity_rate = velocity["mastery_velocity"]
        
        # Simple linear projection
        predicted_mastery = current_mastery + (velocity_rate * days_ahead)
        predicted_mastery = max(0.0, min(1.0, predicted_mastery))
        
        # Calculate confidence based on data quality
        confidence = min(0.9, 0.5 + velocity["data_points"] * 0.05)
        
        # Estimate time to mastery
        time_to_80 = 0
        if velocity_rate > 0 and current_mastery < 0.8:
            time_to_80 = int((0.8 - current_mastery) / velocity_rate)
        
        time_to_90 = 0
        if velocity_rate > 0 and current_mastery < 0.9:
            time_to_90 = int((0.9 - current_mastery) / velocity_rate)
        
        return {
            "current_mastery": current_mastery,
            "predicted_mastery": predicted_mastery,
            "days_ahead": days_ahead,
            "velocity": velocity_rate,
            "confidence": confidence,
            "milestones": {
                "days_to_80_percent": time_to_80 if time_to_80 < 365 else None,
                "days_to_90_percent": time_to_90 if time_to_90 < 365 else None
            },
            "assumptions": [
                "Assumes continued learning pattern",
                "Does not account for content difficulty changes",
                "Confidence decreases for longer predictions"
            ]
        }
    
    def _get_recent_events(
        self,
        student_id: str,
        days: int
    ) -> List[LearningEvent]:
        """Get recent learning events for a student."""
        cutoff = datetime.now() - timedelta(days=days)
        
        events = self.student_history.get(student_id, [])
        
        return [e for e in events if e.timestamp >= cutoff]
    
    def _get_snapshots_in_range(
        self,
        student_id: str,
        days: int
    ) -> List[ProgressSnapshot]:
        """Get snapshots within a date range."""
        cutoff = datetime.now() - timedelta(days=days)
        
        snapshots = self.student_snapshots.get(student_id, [])
        
        return [s for s in snapshots if s.timestamp >= cutoff]
    
    def _calculate_total_time(self, student_id: str) -> int:
        """Calculate total learning time in minutes."""
        events = self.student_history.get(student_id, [])
        
        time_events = [
            e.metadata.get("duration_minutes", 0)
            for e in events
            if "duration_minutes" in e.metadata
        ]
        
        return sum(time_events)
    
    def _calculate_engagement_level(
        self,
        profile: StudentProfile,
        recent_events: List[LearningEvent]
    ) -> str:
        """Calculate current engagement level."""
        if profile.learning_streak and profile.learning_streak >= 5:
            return "high"
        
        engagement_scores = [
            e.metadata.get("engagement_score", 0.5)
            for e in recent_events
            if "engagement_score" in e.metadata
        ]
        
        if not engagement_scores:
            return "medium"
        
        avg_engagement = sum(engagement_scores) / len(engagement_scores)
        
        if avg_engagement >= 0.7:
            return "high"
        elif avg_engagement >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _linear_regression(
        self,
        x: List[int],
        y: List[float]
    ) -> Tuple[float, float]:
        """Perform simple linear regression."""
        n = len(x)
        
        if n < 2:
            return 0.0, y[0] if y else 0.0
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        return slope, intercept
    
    def _get_plateau_recommendations(self, student_id: str) -> List[str]:
        """Generate recommendations for overcoming a plateau."""
        return [
            "Try different content formats (videos, interactive exercises)",
            "Review foundational concepts before continuing",
            "Take a short break to prevent burnout",
            "Set specific, achievable sub-goals",
            "Consider peer learning or discussion groups"
        ]
    
    def _generate_progress_recommendations(
        self,
        student_id: str,
        summary: Dict[str, Any],
        trends: List[ProgressTrend]
    ) -> List[str]:
        """Generate recommendations based on progress analysis."""
        recommendations = []
        
        # Check for declining trends
        declining = [t for t in trends if t.direction == "declining"]
        if declining:
            recommendations.append(
                "Performance declining in some areas. Consider reviewing recent material."
            )
        
        # Check for improving trends
        improving = [t for t in trends if t.direction == "improving"]
        if improving:
            recommendations.append(
                "Strong progress! Consider taking on more challenging content."
            )
        
        # Check velocity
        velocity = self.calculate_learning_velocity(student_id)
        if velocity["mastery_velocity"] < 0.01:
            recommendations.append(
                "Learning pace has slowed. Try setting smaller, daily goals."
            )
        
        # Check engagement
        if summary.get("engagement_level") == "low":
            recommendations.append(
                "Engagement is low. Try mixing up your learning routine."
            )
        
        # Positive reinforcement
        if summary.get("mastery_improvement", 0) > 0.1:
            recommendations.append(
                "Great improvement! Keep up the consistent work."
            )
        
        if not recommendations:
            recommendations.append("Continue with your current learning plan.")
        
        return recommendations
