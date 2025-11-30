
import streamlit as st
import json
from typing import List, Dict, Any, Optional

st.set_page_config(page_title="University Scholarship Advisor", layout="centered")
st.title("University Scholarship Decision Support System")
st.markdown("### Rule-Based Expert System for Transparent Scholarship Allocation")

# Default rules (EXACTLY as given in the lab)
DEFAULT_RULES_JSON = '''
[
  {
    "name": "Top merit candidate",
    "priority": 100,
    "conditions": [
      ["cgpa", ">=", 3.7],
      ["co_curricular_score", ">=", 80],
      ["family_income", "<=", 8000],
      ["disciplinary_actions", "==", 0]
    ],
    "action": {
      "decision": "AWARD_FULL",
      "reason": "Excellent academic & co-curricular performance, with acceptable need"
    }
  },
  {
    "name": "Good candidate - partial scholarship",
    "priority": 80,
    "conditions": [
      ["cgpa", ">=", 3.3],
      ["co_curricular_score", ">=", 60],
      ["family_income", "<=", 12000],
      ["disciplinary_actions", "<=", 1]
    ],
    "action": {
      "decision": "AWARD_PARTIAL",
      "reason": "Good academic & involvement record with moderate need"
    }
  },
  {
    "name": "Need-based review",
    "priority": 70,
    "conditions": [
      ["cgpa", ">=", 2.5],
      ["family_income", "<=", 4000]
    ],
    "action": {
      "decision": "REVIEW",
      "reason": "High need but borderline academic score"
    }
  },
  {
    "name": "Low CGPA - not eligible",
    "priority": 95,
    "conditions": [
      ["cgpa", "<", 2.5]
    ],
    "action": {
      "decision": "REJECT",
      "reason": "CGPA below minimum scholarship requirement"
    }
  },
  {
    "name": "Serious disciplinary record",
    "priority": 90,
    "conditions": [
      ["disciplinary_actions", ">=", 2]
    ],
    "action": {
      "decision": "REJECT",
      "reason": "Too many disciplinary records"
    }
  }
]
'''

#JSON Rule Editor
st.sidebar.header("Rule Configuration (Editable JSON)")
rules_json = st.sidebar.text_area(
    "Edit rules below (must be valid JSON array):",
    value=DEFAULT_RULES_JSON.strip(),
    height=600
)

try:
    rules = json.loads(rules_json)
    st.sidebar.success("Rules loaded successfully!")
except json.JSONDecodeError as e:
    st.sidebar.error(f"Invalid JSON: {e}")
    rules = []

# Main form 
st.header("Applicant Information")
col1, col2 = st.columns(2)

with col1:
    cgpa = st.number_input("Cumulative GPA (CGPA)", min_value=0.0, max_value=4.0, step=0.01, value=3.5)
    family_income = st.number_input("Monthly Family Income (RM)", min_value=0, value=5000)
    co_curricular_score = st.slider("Co-curricular Involvement Score (0-100)", 0, 100, 70)

with col2:
    community_service = st.number_input("Community Service Hours", min_value=0, value=50)
    semester = st.number_input("Current Semester", min_value=1, max_value=14, value=5)
    disciplinary_actions = st.number_input("Number of Disciplinary Actions", min_value=0, value=0, step=1)

# Facts dictionary 
facts = {
    "cgpa": float(cgpa),
    "family_income": float(family_income),
    "co_curricular_score": float(co_curricular_score),
    "community_service_hours": float(community_service),
    "current_semester": float(semester),
    "disciplinary_actions": float(disciplinary_actions)
}

# Fixed Rule Engine
def evaluate_condition(condition: List[Any], facts: Dict[str, float]) -> bool:
    """
    Evaluate a single condition like ["field", "op", value].
    Fixed: Safely handles str/int/float for value (from JSON).
    """
    if len(condition) != 3:
        return False
    field, op, raw_value = condition
    val = facts.get(str(field))  # Ensure field is str
    if val is None:
        return False
    
    # Safely convert raw_value to float (handles str, int, float from JSON)
    try:
        if isinstance(raw_value, (int, float)):
            value = float(raw_value)
        else:  # Assume str
            value_str = str(raw_value).strip()
            if '.' in value_str or value_str.replace('-', '').replace('.', '').isdigit():
                value = float(value_str)
            else:
                value = value_str  # Non-numeric (e.g., for == string, but not used here)
    except (ValueError, TypeError):
        return False  # Invalid value
    
    # Numeric comparisons (all values are now float)
    if op == "==": return val == value
    if op == "!=": return val != value
    if op == ">":  return val > value
    if op == ">=": return val >= value
    if op == "<":  return val < value
    if op == "<=": return val <= value
    return False

def apply_rules(rules: List[Dict], facts: Dict[str, float]) -> Optional[Dict]:
    """
    Apply rules in priority order (highest first).
    Returns the action and rule name of the first matching rule.
    """
    # Sort by priority descending
    sorted_rules = sorted(rules, key=lambda x: x.get("priority", 0), reverse=True)
    for rule in sorted_rules:
        conditions = rule.get("conditions", [])
        if all(evaluate_condition(cond, facts) for cond in conditions):
            return rule.get("action"), rule.get("name")
    return None, None

if st.button("Evaluate Scholarship Eligibility", type="primary"):
    if not rules:
        st.error("Please fix JSON errors first.")
    else:
        result, rule_name = apply_rules(rules, facts)
        st.markdown("---")
        if result:
            decision = result["decision"]
            reason = result["reason"]
            color = {"AWARD_FULL": "🟢", "AWARD_PARTIAL": "🟠",
                     "REVIEW": "🔵", "REJECT": "🔴"}.get(decision, "⚪")
            st.markdown(f"### Decision: **{color} {decision.replace('_', ' ')}**")
            st.success(f"**Rule Triggered:** {rule_name}")
            st.info(f"**Reason:** {reason}")
            
            # Show matching facts for transparency
            st.subheader("Matching Facts")
            for cond in rules[int(rule_name.split()[-1]) - 1]["conditions"]:  # Approximate, for demo
                st.write(f"- {cond[0]} {cond[1]} {cond[2]}: ✓ (Actual: {facts.get(cond[0], 'N/A')})")
        else:
            st.warning("No rule matched – Default: **REJECT**")
            st.info("Reason: Applicant does not satisfy any scholarship criteria.")



