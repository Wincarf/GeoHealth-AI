"""Virtue Foundation Schema - Pydantic models for Indian Health Facilities

Standardized data models for structuring health facility capability extraction.
Used by India Health Intelligence hackathon project.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


class TrustLevel(str, Enum):
    """Trust level categorization"""
    CRITICAL = "critical"  # score < 60
    LOW = "low"  # 60-75
    MEDIUM = "medium"  # 75-85
    HIGH = "high"  # 85-95
    EXCELLENT = "excellent"  # 95-100


class FacilityCapabilities(BaseModel):
    """Core facility capabilities extracted from unstructured data"""
    
    facility_id: str = Field(
        ..., 
        description="Unique facility identifier",
        min_length=1
    )
    
    name: str = Field(
        ..., 
        description="Facility name",
        min_length=1
    )
    
    has_icu: bool = Field(
        default=False,
        description="Has Intensive Care Unit (ICU) capability"
    )
    
    has_oxygen: bool = Field(
        default=False,
        description="Has oxygen supply/ventilator support"
    )
    
    has_emergency_surgery: bool = Field(
        default=False,
        description="Can perform emergency surgical procedures"
    )
    
    extraction_method: Optional[Literal[
        "keywords", "embeddings", "vector_search", "gemini", "agent_bricks"
    ]] = Field(
        default=None,
        description="Method used for capability extraction"
    )
    
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score for extraction (0.0 - 1.0)"
    )
    
    extracted_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of capability extraction"
    )
    
    class Config:
        validate_assignment = True
        json_schema_extra = {
            "example": {
                "facility_id": "12345",
                "name": "Braham Jyoti Hospital",
                "has_icu": True,
                "has_oxygen": True,
                "has_emergency_surgery": True,
                "extraction_method": "agent_bricks",
                "confidence_score": 0.95
            }
        }


class TrustScore(BaseModel):
    """Trust score and data quality flags for facilities"""
    
    facility_id: str = Field(..., description="Unique facility identifier")
    
    trust_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall trust score (0-100)"
    )
    
    trust_level: TrustLevel = Field(
        ...,
        description="Categorical trust level"
    )
    
    red_flags: List[str] = Field(
        default_factory=list,
        description="List of detected data quality issues"
    )
    
    has_critical_issues: bool = Field(
        default=False,
        description="Has critical contradictions requiring verification"
    )
    
    @field_validator('red_flags')
    @classmethod
    def validate_flags(cls, v: List[str]) -> List[str]:
        """Ensure red flags are non-empty strings"""
        return [flag.strip() for flag in v if flag and flag.strip()]
    
    @model_validator(mode='after')
    def set_trust_level(self):
        """Automatically set trust level based on score"""
        if self.trust_score < 60:
            object.__setattr__(self, 'trust_level', TrustLevel.CRITICAL)
            object.__setattr__(self, 'has_critical_issues', True)
        elif self.trust_score < 75:
            object.__setattr__(self, 'trust_level', TrustLevel.LOW)
        elif self.trust_score < 85:
            object.__setattr__(self, 'trust_level', TrustLevel.MEDIUM)
        elif self.trust_score < 95:
            object.__setattr__(self, 'trust_level', TrustLevel.HIGH)
        else:
            object.__setattr__(self, 'trust_level', TrustLevel.EXCELLENT)
        return self
    
    class Config:
        validate_assignment = True
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "facility_id": "12345",
                "trust_score": 60,
                "trust_level": "low",
                "red_flags": [
                    "Emergency surgery without ICU",
                    "Surgery capability without oxygen"
                ],
                "has_critical_issues": False
            }
        }


class FacilityWithTrust(FacilityCapabilities):
    """Combined model: capabilities + trust score"""
    
    address_state: Optional[str] = Field(
        default=None,
        description="State or region where facility is located"
    )
    
    trust_score: int = Field(
        default=100,
        ge=0,
        le=100,
        description="Trust score (0-100) - auto-calculated if red flags detected"
    )
    
    trust_level: str = Field(
        default="excellent",
        description="Categorical trust level - auto-set based on score"
    )
    
    red_flags: List[str] = Field(
        default_factory=list,
        description="List of red flags detected"
    )
    
    @model_validator(mode='before')
    @classmethod
    def calculate_trust_before(cls, values):
        """Calculate trust score and flags BEFORE model creation"""
        flags = []
        score = 100
        
        has_emergency = values.get('has_emergency_surgery', False)
        has_icu = values.get('has_icu', False)
        has_oxygen = values.get('has_oxygen', False)
        
        # Red Flag 1: Emergency Surgery without ICU
        if has_emergency and not has_icu:
            flags.append("⚠️ Emergency surgery without ICU (high risk)")
            score -= 25
        
        # Red Flag 2: ICU without Oxygen
        if has_icu and not has_oxygen:
            flags.append("⚠️ ICU without oxygen support (critical gap)")
            score -= 20
        
        # Red Flag 3: Emergency Surgery without Oxygen
        if has_emergency and not has_oxygen:
            flags.append("⚠️ Surgery capability without oxygen (unsafe)")
            score -= 15
        
        # Only override if not explicitly set
        if 'red_flags' not in values or not values['red_flags']:
            values['red_flags'] = flags
        
        if 'trust_score' not in values or values['trust_score'] == 100:
            values['trust_score'] = score
        
        # Set trust level
        calc_score = values.get('trust_score', 100)
        if calc_score < 60:
            values['trust_level'] = 'critical'
        elif calc_score < 75:
            values['trust_level'] = 'low'
        elif calc_score < 85:
            values['trust_level'] = 'medium'
        elif calc_score < 95:
            values['trust_level'] = 'high'
        else:
            values['trust_level'] = 'excellent'
        
        return values
    
    class Config:
        validate_assignment = True


class RegionalDesertAnalysis(BaseModel):
    """Regional healthcare desert analysis metrics"""
    
    state: str = Field(..., description="State or region name")
    
    total_facilities: int = Field(
        ...,
        ge=0,
        description="Total number of facilities in region"
    )
    
    icu_count: int = Field(
        ...,
        ge=0,
        description="Number of facilities with ICU"
    )
    
    oxygen_count: int = Field(
        ...,
        ge=0,
        description="Number of facilities with oxygen"
    )
    
    emergency_count: int = Field(
        ...,
        ge=0,
        description="Number of facilities with emergency surgery"
    )
    
    icu_desert_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Desert score for ICU (100 = complete desert, 0 = full coverage)"
    )
    
    avg_trust_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Average trust score of facilities in region"
    )
    
    is_critical_desert: bool = Field(
        default=False,
        description="Is this region a critical healthcare desert?"
    )
    
    priority_level: Optional[Literal["low", "medium", "high", "critical"]] = Field(
        default=None,
        description="Priority level for intervention"
    )
    
    @model_validator(mode='after')
    def set_criticality(self):
        """Set critical desert flag and priority level"""
        # Critical desert: zero ICU facilities
        object.__setattr__(self, 'is_critical_desert', (self.icu_count == 0))
        
        # Determine priority level
        if self.icu_desert_score >= 95 and self.total_facilities >= 100:
            object.__setattr__(self, 'priority_level', "critical")
        elif self.icu_desert_score >= 85 and self.total_facilities >= 50:
            object.__setattr__(self, 'priority_level', "high")
        elif self.icu_desert_score >= 70:
            object.__setattr__(self, 'priority_level', "medium")
        else:
            object.__setattr__(self, 'priority_level', "low")
        
        return self
    
    class Config:
        validate_assignment = True
        json_schema_extra = {
            "example": {
                "state": "Maharashtra",
                "total_facilities": 1506,
                "icu_count": 63,
                "oxygen_count": 45,
                "emergency_count": 89,
                "icu_desert_score": 95.8,
                "avg_trust_score": 97.8,
                "is_critical_desert": False,
                "priority_level": "critical"
            }
        }


# Utility functions for conversion
def dict_to_facility(data: dict) -> FacilityCapabilities:
    """Convert dictionary to FacilityCapabilities with validation"""
    return FacilityCapabilities(**data)


def dict_to_trust_score(data: dict) -> TrustScore:
    """Convert dictionary to TrustScore with validation"""
    return TrustScore(**data)


def dict_to_facility_with_trust(data: dict) -> FacilityWithTrust:
    """Convert dictionary to FacilityWithTrust with validation"""
    return FacilityWithTrust(**data)


def dict_to_desert_analysis(data: dict) -> RegionalDesertAnalysis:
    """Convert dictionary to RegionalDesertAnalysis with validation"""
    return RegionalDesertAnalysis(**data)
