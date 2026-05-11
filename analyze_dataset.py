import pandas as pd
import json

file_path = r'C:\Users\oussa.LAPTOP-THCQB19P\Downloads\e learning\ESPRIT_Dataset_Start-Smart.xlsx'
df = pd.read_excel(file_path)

stats = {
    "total_students": len(df),
    "avg_age": float(df['age'].mean()),
    "gender_dist": df['gender'].value_counts().to_dict(),
    "field_dist": df['field'].value_counts().to_dict(),
    "avg_bac_grade": float(df['bac_grade'].mean()),
    "avg_attendance": float(df['attendance_rate_avg'].mean()),
    "avg_quiz_perf": float(df['overall_quiz_performance'].mean()),
    "risk_dist": df['risk_level'].value_counts().to_dict() if 'risk_level' in df.columns else {},
    "avg_dropout_prob": float(df['dropout_probability'].mean()) if 'dropout_probability' in df.columns else 0.0,
}

# Correlations or other interesting stats
stats['engagement_vs_performance'] = df[['engagement_score', 'overall_quiz_performance']].corr().iloc[0, 1]

with open(r'C:\Users\oussa.LAPTOP-THCQB19P\.gemini\antigravity\scratch\stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

