FACILITIES = [
    {"id":"demo-emergency","name":"Demo District Emergency Centre","level":"EMERGENCY","telemedicine_available":True},
    {"id":"demo-phc","name":"Demo Primary Health Centre","level":"PHC","telemedicine_available":True},
    {"id":"demo-dh","name":"Demo District Hospital","level":"DISTRICT","telemedicine_available":True},
]

def recommend_referral(triage_level, symptoms=None, location="", specialty=None):
    if triage_level == "LEVEL_1_EMERGENCY": f = FACILITIES[0]
    elif specialty: f = FACILITIES[2]
    else: f = FACILITIES[1]
    return {"recommended_facility":f,"specialty":specialty or "General Medicine","reason":"Routing based on triage level and requested specialty; facility directory is synthetic demo data.","urgency":triage_level,"telemedicine_available":f["telemedicine_available"]}
