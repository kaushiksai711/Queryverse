; Medical domain knowledge base

; Basic facts about diabetes
(is_a "diabetes" "medical_condition")
(is_a "type_2_diabetes" "diabetes")
(is_a "type_1_diabetes" "diabetes")

; Treatments
(treats "insulin" "diabetes")
(treats "metformin" "type_2_diabetes")
(treats "diet_control" "type_2_diabetes")

; Symptoms and monitoring
(symptom_of "increased_thirst" "diabetes")
(symptom_of "frequent_urination" "diabetes")
(symptom_of "fatigue" "diabetes")
(required_for "glucose_monitoring" "diabetes_management")
(required_for "regular_exercise" "diabetes_management")

; Relationships and hierarchies
(is_a "chronic_disease" "medical_condition")
(is_a "diabetes" "chronic_disease")

; Risk factors
(risk_factor "obesity" "type_2_diabetes")
(risk_factor "family_history" "diabetes")
(risk_factor "age" "type_2_diabetes")

; Complications
(can_cause "diabetes" "heart_disease")
(can_cause "diabetes" "kidney_problems")
(can_cause "diabetes" "vision_problems") 