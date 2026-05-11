from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

BASE = os.path.dirname(__file__)

# Load models
clf        = joblib.load(f'{BASE}/models/classifier.pkl')
reg        = joblib.load(f'{BASE}/models/regressor.pkl')
scaler_cls = joblib.load(f'{BASE}/models/scaler_cls.pkl')
scaler_reg = joblib.load(f'{BASE}/models/scaler_reg.pkl')
encoders   = joblib.load(f'{BASE}/models/encoders.pkl')
feat_cls   = joblib.load(f'{BASE}/models/feature_cols.pkl')
feat_reg   = joblib.load(f'{BASE}/models/feature_cols_reg.pkl')
risk_cls   = joblib.load(f'{BASE}/models/risk_classes.pkl')

GENDER_MAP         = {'M': 1, 'F': 0}
FIELD_MAP          = {'Informatique': 2, 'Génie Civil': 1, 'Génie Électrique': 0, 'Génie Mécanique': 3, 'Mathématiques': 4}
LEARNING_MAP       = {'Auditory': 0, 'Kinesthetic': 1, 'Reading': 2, 'Visual': 3}
INITIAL_LEVEL_MAP  = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2}
EARLY_RISK_MAP     = {'Low_Risk': 1, 'Medium_Risk': 2, 'High_Risk': 0}

def encode_input(data):
    return {
        'age':                           float(data.get('age', 20)),
        'bac_grade':                     float(data.get('bac_grade', 12)),
        'gender_enc':                    GENDER_MAP.get(data.get('gender', 'M'), 1),
        'field_enc':                     FIELD_MAP.get(data.get('field', 'Informatique'), 2),
        'learning_style_enc':            LEARNING_MAP.get(data.get('learning_style', 'Visual'), 3),
        'initial_level_enc':             INITIAL_LEVEL_MAP.get(data.get('initial_level', 'Intermediate'), 1),
        'overall_quiz_performance':      float(data.get('overall_quiz_performance', 50)),
        'midterm_exam_score':            float(data.get('midterm_exam_score', 50)),
        'attendance_rate_avg':           float(data.get('attendance_rate_avg', 75)),
        'login_frequency_avg':           float(data.get('login_frequency_avg', 3)),
        'time_spent_platform_avg':       float(data.get('time_spent_platform_avg', 3)),
        'video_completion_rate_avg':     float(data.get('video_completion_rate_avg', 50)),
        'exercise_completion_rate_avg':  float(data.get('exercise_completion_rate_avg', 50)),
        'assignment_submission_rate_avg':float(data.get('assignment_submission_rate_avg', 70)),
        'engagement_score':              float(data.get('engagement_score', 10)),
        'brainrush_games_played_total':  float(data.get('brainrush_games_played_total', 50)),
        'brainrush_avg_score_avg':       float(data.get('brainrush_avg_score_avg', 40)),
        'ai_chat_sessions_total':        float(data.get('ai_chat_sessions_total', 20)),
        'ai_feedback_rating_avg':        float(data.get('ai_feedback_rating_avg', 3)),
        'concept_mastery_rate_final':    float(data.get('concept_mastery_rate_final', 50)),
        'early_avg_score':               float(data.get('early_avg_score', 50)),
        'early_login_frequency':         float(data.get('early_login_frequency', 3)),
        'early_attendance_rate':         float(data.get('early_attendance_rate', 75)),
        'early_dropout_probability':     float(data.get('early_dropout_probability', 0.3)),
        'performance_consistency':       float(data.get('performance_consistency', 5)),
    }

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        encoded = encode_input(data)

        # Classification
        x_cls = np.array([[encoded[f] for f in feat_cls]])
        x_cls_scaled = scaler_cls.transform(x_cls)
        risk_idx   = clf.predict(x_cls_scaled)[0]
        risk_proba = clf.predict_proba(x_cls_scaled)[0]
        risk_label = risk_cls[risk_idx]
        risk_proba_dict = {risk_cls[i]: round(float(p)*100, 1) for i, p in enumerate(risk_proba)}

        # Regression
        x_reg = np.array([[encoded[f] for f in feat_reg]])
        x_reg_scaled = scaler_reg.transform(x_reg)
        dropout_prob = float(reg.predict(x_reg_scaled)[0])
        dropout_prob = max(0.0, min(1.0, dropout_prob))

        # Recommendations
        recommendations = []
        if encoded['attendance_rate_avg'] < 70:
            recommendations.append({'type': 'warning', 'text': "Taux de présence critique (< 70%). Intervention immédiate recommandée."})
        if encoded['engagement_score'] < 8:
            recommendations.append({'type': 'warning', 'text': "Score d'engagement faible. Encourager l'utilisation de la plateforme BrainRush."})
        if encoded['concept_mastery_rate_final'] < 50:
            recommendations.append({'type': 'danger', 'text': "Maîtrise des concepts insuffisante. Séances de tutorat recommandées."})
        if encoded['overall_quiz_performance'] < 40:
            recommendations.append({'type': 'danger', 'text': "Performance quiz en dessous de la moyenne. Révision du programme nécessaire."})
        if dropout_prob > 0.5:
            recommendations.append({'type': 'danger', 'text': f"Probabilité d'abandon élevée ({dropout_prob*100:.1f}%). Suivi personnalisé urgent."})
        if not recommendations:
            recommendations.append({'type': 'success', 'text': "Profil satisfaisant. Maintenir le suivi régulier et encourager l'engagement continu."})

        return jsonify({
            'risk_level': risk_label,
            'risk_probabilities': risk_proba_dict,
            'dropout_probability': round(dropout_prob * 100, 2),
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def stats():
    df = pd.read_excel('ESPRIT_Dataset_Start-Smart.xlsx')
    return jsonify({
        'total_students': len(df),
        'risk_distribution': df['final_risk_level'].value_counts().to_dict(),
        'avg_dropout_probability': round(float(df['final_dropout_probability'].mean()), 3),
        'avg_engagement': round(float(df['engagement_score'].mean()), 2),
        'avg_attendance': round(float(df['attendance_rate_avg'].mean()), 2),
        'avg_quiz': round(float(df['overall_quiz_performance'].mean()), 2),
        'pass_rate': round(float((df['final_passing_status'] == 'Pass').mean() * 100), 1),
        'fields': df['field'].value_counts().to_dict(),
    })

@app.route('/api/health', methods=['GET'])

def health():
    return jsonify({'status': 'ok', 'models': ['classifier', 'regressor']})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
