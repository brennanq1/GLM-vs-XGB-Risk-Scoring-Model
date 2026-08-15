import joblib
import pandas as pd
from flask import Flask, request, jsonify
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.json.sort_keys = False
model = joblib.load(os.path.join(BASE_DIR, 'xgb_risk_model.pkl'))
baseline_applicant = joblib.load(os.path.join(BASE_DIR, 'baseline_applicant.pkl'))
baseline_prediction = joblib.load(os.path.join(BASE_DIR, 'baseline_prediction.pkl'))
ceiling_prediction = joblib.load(os.path.join(BASE_DIR, 'ceiling_prediction.pkl'))

def assign_risk_tier(predicted_claim_amt):
    if predicted_claim_amt <= 60:
        return 'Tier 0: Low Risk'
    elif predicted_claim_amt <= 100:
        return 'Tier 1: Standard Risk'
    elif predicted_claim_amt <= 300:
        return 'Tier 2: Elevated Risk'
    elif predicted_claim_amt <= 750:
        return 'Tier 3: High Risk'
    elif predicted_claim_amt <= 1500:
        return 'Tier 4: Severe Risk'
    else:
        return 'Tier 5: Extreme Outlier'


@app.route('/predict', methods=['POST'])
def predict_risk():
    try:
        user_input = request.get_json()
        if not user_input:
            return jsonify({'status': 'error', 'message': 'No input provided'})

        if 'ClaimNb' not in user_input or user_input['ClaimNb'] is None:
            return jsonify({'status': 'error', 'message': 'ClaimNb is requried. Please provide the number of claims'})

        # Convert Area to integer
        area_map = {'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':6}
        if 'Area' in user_input and isinstance(user_input['Area'], str):
            user_input['Area'] = area_map.get(user_input['Area'])

        processed_input = {}
        for k, v in user_input.items():
            if k == 'VehBrand':
                processed_input[f"VehBrand_{v}"] = True
            elif k == 'VehGas':
                processed_input[f"VehGas_{v}"] = True
            elif k == 'Region':
                processed_input[f"Region_{v}"] = True
            else:
                processed_input[k] = v

        # merge input and baseline data
        complete_applicant = {**baseline_applicant, **processed_input}
        applicant_df = pd.DataFrame([complete_applicant])

        for col in model.feature_names_in_:
            if col not in applicant_df.columns:
                applicant_df[col] = 0
        applicant_df = applicant_df[model.feature_names_in_]

        prediction = model.predict(applicant_df)[0]

        # calculate the risk percentage
        percentage_score = (prediction / ceiling_prediction) * 100

        # calculate risk score
        relativity_multiplier = prediction / baseline_prediction

        # determine business risk tier
        business_risk = assign_risk_tier(prediction)

        return jsonify({'status': 'success',
                        'Predicted Claim Amount_USD': round(float(prediction), 2),
                        'Risk Severity Score 1-100': min(round(percentage_score, 2), 100),
                        'Predicted Business Risk Level': business_risk,
                       'Pure Premium Relativity': round(float(relativity_multiplier), 2)})

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug = True, port = 5000)