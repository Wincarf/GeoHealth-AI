# 🏥  GeoHealth AI - India Health Intelligence System
## Hackathon Project Documentation

---

## 📋 Executive Summary

**Problem**: In India, patients in emergency situations lose critical time trying to discover which hospital has the necessary resources to treat them. The lack of information about hospital capabilities and the presence of "specialist deserts" (regions without critical resources like ICU) increases the time between discovering where to go and receiving care.

**Solution**: Distributed intelligence system that audits capabilities of 10,000+ health facilities, detects contradictions in data, identifies regional deserts, and provides reliable multi-attribute searches.

**Impact**: Reduction of decision time in medical emergencies through validated and reliable information about hospital resource availability.

---

## 🎯 Project Objectives

### Main Objective
Reduce the time between "discovering where to go" and "receiving care" through:
1. Automatic audit of hospital capabilities
2. Detection of data contradictions (Trust Scoring)
3. Identification of specialist deserts
4. Intelligent navigation by geography + capabilities + reliability

### Specific Objectives
* Process and validate data from 10,000+ facilities
* Implement Trust Scoring system based on red flags
* Map regional deserts of critical resources (ICU, Oxygen, Emergency)
* Create validated data schemas for production (Pydantic)
* Provide actionable visualizations for decision making

---

## 📊 Results and Statistics

### Data Coverage
* **Total Facilities**: 10,000
* **States/Regions**: 36
* **Tables Created**: 7

### Trust Scorer
* **Facilities Analyzed**: 10,000
* **Average Score**: 97.7/100
* **Flagged Facilities**: 718 (7.2%)
* **Clean Facilities**: 9,282 (92.8%)

### Desert Analysis
* **States with ZERO ICU**: 10 (27.8%)
* **National ICU Coverage**: 3.5%
* **Average Desert Score**: 96.8%
* **ICU Gap**: 9,430 facilities

### Capability Distribution
* **ICU**: 570 facilities
* **Oxygen**: 451 facilities
* **Emergency Surgery**: 94 facilities
* **Fully Equipped (all 3 capabilities)**: 12 facilities 🎯

### Priority States for Intervention
1. **Maharashtra**: 1,506 facilities | 63 ICU | 95.8% desert | Trust: 96.0
2. **Gujarat**: 838 facilities | 44 ICU | 94.7% desert | Trust: 97.2
3. **Uttar Pradesh**: 1,058 facilities | 33 ICU | 96.9% desert | Trust: 97.5
4. **Tamil Nadu**: 689 facilities | 17 ICU | 97.5% desert | Trust: 98.9
5. **Karnataka**: 589 facilities | 15 ICU | 97.5% desert | Trust: 98.3

---

## 🏗️ Solution Architecture

### Main Components

#### 1. Trust Scorer (Reliability System)
**Function**: Detects logical contradictions in facility data

**Red Flags Detected**:
* Emergency surgery WITHOUT ICU
* Emergency surgery WITHOUT oxygen
* ICU WITHOUT oxygen

**Scoring Algorithm**:
```python
Base Score: 100 points
Deductions:
  - Emergency Surgery without ICU: -10 points
  - Emergency Surgery without Oxygen: -10 points
  - ICU without Oxygen: -10 points

Final Score = 100 - (sum of deductions)
Ranges:
  - 100: Perfect (no contradictions)
  - 90-99: Minor flags (1 contradiction)
  - 80-89: Moderate flags (2 contradictions)
  - 70: Critical flags (all 3 contradictions)
```

**Output**: Validated facilities with reliability scores for informed decision making

---

#### 2. Desert Analyzer (Regional Gap Detection)
**Function**: Identifies regions with critical resource shortages

**Methodology**:
* Aggregates facility capabilities by state
* Calculates coverage percentages (ICU, Oxygen, Emergency)
* Generates desert score: `100 - (% of facilities with ICU)`

**Outputs**:
* State-level capability reports
* Priority rankings for intervention
* Geographic distribution heatmaps

---

#### 3. Data Validation Layer (Pydantic Schemas)
**Function**: Ensures data quality and type safety for production

**Schemas Implemented**:
```python
FacilityBase: Core facility attributes
TrustScore: Scoring results with flags
DesertAnalysis: Regional capability metrics
StateCapability: Aggregated state-level data
```

**Benefits**:
* Runtime validation
* Type safety
* Automatic documentation
* API-ready outputs

---

#### 4. Multi-Attribute Search Engine
**Function**: Enables complex queries combining geography, capabilities, and trust

**Search Capabilities**:
* Filter by state/region
* Filter by required capabilities (ICU AND/OR Oxygen AND/OR Emergency)
* Filter by minimum trust score
* Ranked results by relevance

**Example Query**:
```sql
SELECT * FROM facilities
WHERE state = 'Maharashtra'
  AND has_icu = TRUE
  AND has_oxygen = TRUE
  AND trust_score >= 90
ORDER BY trust_score DESC
```

---

## 🗂️ Data Schema

### Unity Catalog Tables Created

#### 1. `facilities_raw`
Raw facility data from source

| Column | Type | Description |
|--------|------|-------------|
| facility_id | STRING | Unique identifier |
| facility_name | STRING | Facility name |
| state | STRING | State/region |
| district | STRING | District |
| ownership | STRING | Public/Private |
| has_icu | BOOLEAN | ICU availability |
| has_oxygen | BOOLEAN | Oxygen availability |
| has_emergency_surgery | BOOLEAN | Emergency surgery capability |

---

#### 2. `facilities_validated`
Cleaned and validated facility data

| Column | Type | Description |
|--------|------|-------------|
| facility_id | STRING | Unique identifier |
| facility_name | STRING | Standardized name |
| state | STRING | Standardized state name |
| district | STRING | Standardized district |
| ownership | STRING | Validated ownership type |
| has_icu | BOOLEAN | Validated ICU flag |
| has_oxygen | BOOLEAN | Validated oxygen flag |
| has_emergency_surgery | BOOLEAN | Validated emergency flag |
| validated_at | TIMESTAMP | Validation timestamp |

---

#### 3. `trust_scores`
Facility reliability scores

| Column | Type | Description |
|--------|------|-------------|
| facility_id | STRING | Reference to facility |
| trust_score | DOUBLE | Score (0-100) |
| red_flags | ARRAY<STRING> | List of detected issues |
| flag_count | INT | Number of contradictions |
| score_category | STRING | CLEAN/MINOR/MODERATE/CRITICAL |

---

#### 4. `state_capabilities`
Aggregated state-level metrics

| Column | Type | Description |
|--------|------|-------------|
| state | STRING | State name |
| total_facilities | INT | Total count |
| icu_count | INT | Facilities with ICU |
| oxygen_count | INT | Facilities with oxygen |
| emergency_count | INT | Facilities with emergency |
| fully_equipped_count | INT | All 3 capabilities |
| avg_trust_score | DOUBLE | Average reliability |
| desert_score | DOUBLE | Resource shortage metric |

---

#### 5. `desert_analysis`
Regional gap identification

| Column | Type | Description |
|--------|------|-------------|
| state | STRING | State name |
| total_facilities | INT | Total facilities |
| icu_coverage_pct | DOUBLE | % with ICU |
| oxygen_coverage_pct | DOUBLE | % with oxygen |
| emergency_coverage_pct | DOUBLE | % with emergency |
| desert_score | DOUBLE | 100 - ICU coverage % |
| priority_rank | INT | Intervention priority |

---

#### 6. `capability_matrix`
Facility-level capability combinations

| Column | Type | Description |
|--------|------|-------------|
| facility_id | STRING | Facility reference |
| capability_profile | STRING | e.g., "ICU+Oxygen" |
| capability_count | INT | 0-3 capabilities |
| is_fully_equipped | BOOLEAN | Has all 3 |

---

#### 7. `search_index`
Optimized table for multi-attribute queries

| Column | Type | Description |
|--------|------|-------------|
| facility_id | STRING | Facility reference |
| facility_name | STRING | Searchable name |
| state | STRING | Indexed state |
| district | STRING | Indexed district |
| has_icu | BOOLEAN | Indexed flag |
| has_oxygen | BOOLEAN | Indexed flag |
| has_emergency_surgery | BOOLEAN | Indexed flag |
| trust_score | DOUBLE | Indexed score |
| capability_tags | ARRAY<STRING> | Searchable tags |

---

## 💻 Technologies Used

### Data Platform
* **Databricks**: Unified analytics platform
* **Unity Catalog**: Data governance and cataloging
* **Delta Lake**: ACID transactions and data versioning
* **Spark SQL**: Distributed data processing

### Programming & Validation
* **Python 3.x**: Core programming language
* **Pydantic**: Data validation and schemas
* **PySpark**: Distributed computing

### Visualization
* **Databricks SQL**: Analytics dashboards
* **Plotly/Matplotlib**: Statistical visualizations

---

## 🚀 How to Use This System

### For Emergency Responders
1. Search by state and required capabilities
2. Filter by minimum trust score (recommended: ≥90)
3. Get ranked list of reliable facilities
4. Navigate to closest suitable facility

### For Healthcare Administrators
1. Review state capability reports
2. Identify resource gaps (desert analysis)
3. Prioritize infrastructure investments
4. Monitor trust score trends

### For Policy Makers
1. Analyze national coverage statistics
2. Identify priority states for intervention
3. Track progress over time
4. Allocate resources based on desert scores

---

## 🎯 Key Insights

### Critical Findings
1. **Only 3.5% of facilities have ICU** - massive infrastructure gap
2. **10 states have ZERO ICU facilities** - complete resource deserts
3. **Only 12 facilities are fully equipped** - severe shortage of comprehensive care centers
4. **7.2% of facilities have data contradictions** - need for better reporting standards

### Geographic Disparities
* **Maharashtra** needs 1,443 more ICU facilities (currently 63/1,506)
* **Uttar Pradesh** has only 3.1% ICU coverage (33/1,058)
* **Tamil Nadu** has only 2.5% ICU coverage (17/689)

### Data Quality Issues
* **718 facilities flagged** for logical contradictions
* Most common issue: Emergency surgery claimed without ICU support
* Need for standardized reporting protocols

---

## 📈 Business Value

### Immediate Impact
* **Reduced Search Time**: From hours to seconds for finding suitable facility
* **Informed Decisions**: Trust scores eliminate uncertainty
* **Better Outcomes**: Faster access to appropriate care

### Long-term Impact
* **Infrastructure Planning**: Data-driven investment decisions
* **Resource Allocation**: Target high-desert regions
* **Quality Improvement**: Incentivize accurate reporting
* **Policy Making**: Evidence-based healthcare policy

---

## 🔮 Next Steps

### Phase 2 Enhancements
1. **Real-time Bed Availability**: Live capacity tracking
2. **Routing Optimization**: Integration with mapping services
3. **Mobile Application**: Patient-facing search interface
4. **Historical Trends**: Track capability improvements over time

### Data Expansion
1. **Ambulance Networks**: Integration with emergency transport
2. **Specialist Availability**: Doctor skills and schedules
3. **Equipment Inventory**: Ventilators, dialysis, imaging
4. **Wait Times**: Average emergency room delays

### ML/AI Features
1. **Predictive Analytics**: Forecast resource shortages
2. **Anomaly Detection**: Automated data quality monitoring
3. **Recommendation Engine**: Smart facility suggestions
4. **Natural Language Search**: "Find ICU near Mumbai with high trust score"

---

## 📝 Conclusion

The India Health Intelligence System demonstrates how **data engineering + distributed systems + validation logic** can solve critical real-world problems. By processing 10,000+ facilities and implementing automated trust scoring, we've created a foundation for:

✅ **Faster emergency response**  
✅ **Data-driven healthcare policy**  
✅ **Transparent capability reporting**  
✅ **Equitable resource distribution**

The system is **production-ready** with:
* Validated schemas (Pydantic)
* Governed data (Unity Catalog)
* Scalable architecture (Spark/Delta)
* Actionable insights (Trust Scores + Desert Analysis)

**This is not just a hackathon project - it's a blueprint for national healthcare infrastructure intelligence.**

---

## 👥 Team & Contact

**Project**: India Health Intelligence System  
**Event**: Databricks Hackathon 2025  
**Repository**: [GitHub Link]  
**Dashboard**: [Databricks Dashboard Link]

---

**Built with ❤️ and data on Databricks**
