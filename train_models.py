import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import os

# Create models directory
if not os.path.exists('models'):
    os.makedirs('models')

print("Loading dataset...")
df = pd.read_excel('ESPRIT_Dataset_Start-Smart.xlsx')

# Maps from app_flask.py
GENDER_MAP         = {'M': 1, 'F': 0}
FIELD_MAP          = {'Informatique': 2, 'Génie Civil': 1, 'Génie Électrique': 0, 'Génie Mécanique': 3, 'Mathématiques': 4}
LEARNING_MAP       = {'Auditory': 0, 'Kinesthetic': 1, 'Reading': 2, 'Visual': 3}
INITIAL_LEVEL_MAP  = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2}
# EARLY_RISK_MAP     = {'Low_Risk': 1, 'Medium_Risk': 2, 'High_Risk': 0}

# Apply mappings
df['gender_enc'] = df['gender'].map(GENDER_MAP).fillna(1)
df['field_enc'] = df['field'].map(FIELD_MAP).fillna(2)
df['learning_style_enc'] = df['learning_style'].map(LEARNING_MAP).fillna(3)
df['initial_level_enc'] = df['initial_level'].map(INITIAL_LEVEL_MAP).fillna(1)

# Features list exactly as in app_flask.py encode_input
feature_cols = [
    'age', 'bac_grade', 'gender_enc', 'field_enc', 'learning_style_enc', 'initial_level_enc',
    'overall_quiz_performance', 'midterm_exam_score', 'attendance_rate_avg',
    'login_frequency_avg', 'time_spent_platform_avg', 'video_completion_rate_avg',
    'exercise_completion_rate_avg', 'assignment_submission_rate_avg', 'engagement_score',
    'brainrush_games_played_total', 'brainrush_avg_score_avg', 'ai_chat_sessions_total',
    'ai_feedback_rating_avg', 'concept_mastery_rate_final', 'early_avg_score',
    'early_login_frequency', 'early_attendance_rate', 'early_dropout_probability',
    'performance_consistency'
]

# Ensure all columns are present and numeric
X = df[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

target_cls = 'final_risk_level'
target_reg = 'final_dropout_probability'

# Target encoding for classification
le_risk = LabelEncoder()
# We want to match early_risk_map logic if possible, but the backend uses risk_cls[risk_idx]
# So let's just fit it.
y_cls = le_risk.fit_transform(df[target_cls])
risk_classes = le_risk.classes_

y_reg = df[target_reg]

# Split
X_train, X_test, y_train_cls, y_test_cls = train_test_split(X, y_cls, test_size=0.2, random_state=42)
_, _, y_train_reg, y_test_reg = train_test_split(X, y_reg, test_size=0.2, random_state=42)

# Scaling
scaler_cls = StandardScaler()
X_train_scaled = scaler_cls.fit_transform(X_train)

scaler_reg = StandardScaler()
X_train_reg_scaled = scaler_reg.fit_transform(X_train)

print("Training Classifier...")
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train_scaled, y_train_cls)

print("Training Regressor...")
reg = RandomForestRegressor(n_estimators=100, random_state=42)
reg.fit(X_train_reg_scaled, y_train_reg)

# Save everything
print("Saving models...")
joblib.dump(clf, 'models/classifier.pkl')
joblib.dump(reg, 'models/regressor.pkl')
joblib.dump(scaler_cls, 'models/scaler_cls.pkl')
joblib.dump(scaler_reg, 'models/scaler_reg.pkl')
joblib.dump({'gender': GENDER_MAP, 'field': FIELD_MAP, 'learning_style': LEARNING_MAP, 'initial_level': INITIAL_LEVEL_MAP}, 'models/encoders.pkl')
joblib.dump(feature_cols, 'models/feature_cols.pkl')
joblib.dump(feature_cols, 'models/feature_cols_reg.pkl')
joblib.dump(risk_classes, 'models/risk_classes.pkl')

print("Models trained successfully!")
