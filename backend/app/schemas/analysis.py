from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class FilterCondition(BaseModel):
    column: str
    operator: str = Field(..., description="eq, neq, gt, gte, lt, lte, in, contains")
    value: Any

class SortCondition(BaseModel):
    column: str
    ascending: bool = True

class AnalysisSchema(BaseModel):
    """
    Formal AnalysisSchema intermediate representation passed from
    Query Understanding Agent to Planning Agent.
    """
    user_question: str
    detected_intent: str = Field(..., description="aggregation, group_comparison, trend_over_time, distribution, correlation, ranking, outlier_detection, overview")
    target_columns: List[str] = Field(default_factory=list, description="Target numerical or metric columns")
    group_by: List[str] = Field(default_factory=list, description="Dimension columns for grouping")
    filters: List[FilterCondition] = Field(default_factory=list, description="Filter predicates")
    aggregation: Optional[str] = Field(None, description="avg, sum, count, min, max, median")
    sorting: Optional[SortCondition] = None
    limit: Optional[int] = None
    time_granularity: Optional[str] = Field(None, description="day, month, quarter, year")
    comparison: Optional[Dict[str, Any]] = None
    statistical_operation: Optional[str] = None
    requested_visualization: Optional[str] = Field(None, description="bar, horizontal_bar, line, area, pie, donut, scatter, histogram, box_plot, heatmap, kpi_card, table")
    language: str = "en"
    privacy_constraints: List[str] = Field(default_factory=list)
