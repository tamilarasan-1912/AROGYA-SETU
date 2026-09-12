from backend.app.ai.triage.safety_rules import apply_safety_rules

def test_emergency_overrides_ai():
    result={'triage_level':'LEVEL_4_ROUTINE','confidence':0.99,'reason_codes':[],'red_flags':[],'recommended_action':''}
    out=apply_safety_rules(result,{'red_flags':['CHEST_PAIN']})
    assert out['triage_level']=='LEVEL_1_EMERGENCY'

def test_low_confidence_human_review():
    result={'triage_level':'LEVEL_3_PRIMARY_CARE','confidence':0.2,'reason_codes':[],'red_flags':[],'recommended_action':''}
    out=apply_safety_rules(result,{'red_flags':[]})
    assert out['recommended_action']=='Requires human review.'
