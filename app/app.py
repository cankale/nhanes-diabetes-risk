import streamlit as st
import joblib 
import pandas as pd 
from pathlib import Path

@st.cache_resource
def load_model(path):
    return joblib.load(path)

st.title("Undiagnosed diabetes risk")
st.write('Estimates the probability of having diabetes without knowing it, based on a model trained on 6,644 US adults (NHANES 2017-2020).')
st.warning("Portfolio project, not medical advice. A blood test (HbA1c) is the only way to know.")

basic_model_path = Path(__file__).parent.parent / 'models' / 'basic_model.joblib'
lab_model_path = Path(__file__).parent.parent / 'models' / 'lab_model.joblib'

basic_model = load_model(basic_model_path)
lab_model = load_model(lab_model_path)

prep = basic_model.named_steps['prep']


for name, transformer, columns in prep.transformers_:
    if name == 'cat':
        cat_columns = columns


categories = prep.named_transformers_['cat'].named_steps['encoder'].categories_
options = dict(zip(cat_columns, categories))

race = st.selectbox('Race / ethnicity', list(options['race']))
sex = st.selectbox('Sex', list(options['sex']))
birth_place = st.selectbox('Birth place', list(options['birth_place']), format_func=lambda v: v.replace("_", " ").capitalize())
education = st.selectbox('Level of education', list(options['level_of_education']), format_func=lambda v: v.replace('_', ' ').capitalize())
smoking = st.selectbox('Smoking status', list(options['smoking_status']))

age = st.number_input('Age (years)', min_value=20, max_value=80, value=50, step=1)
bmi = st.number_input('BMI (kg/m²)', min_value=14.0, max_value=93.0, value=27.0, step=0.1)
waist = st.number_input('Waist circumference (cm)', min_value=57, max_value=188 , value=95,step=1)

told_high_bp = st.radio('Has a doctor ever told you that you have high blood pressure?', ['No', 'Yes'], horizontal=True)
if told_high_bp == 'Yes':
    takes_bp_meds = st.radio('Do you take medication for high blood pressure?', ['No', 'Yes'], horizontal=True)
else:
    takes_bp_meds = 'No'

told_high_chol = st.radio('Has a doctor ever told you that you have high cholesterol?', ['No', 'Yes'], horizontal=True)
if told_high_chol == 'Yes':
    takes_chol_meds = st.radio('Do you take medication for high cholesterol?', ['No', 'Yes'], horizontal=True)
else:
    takes_chol_meds = 'No'
family_history_diabetes = st.radio('Does a parent, brother or sister have diabetes?', ['No', 'Yes'], horizontal=True)
active_leisure = st.radio('Do you do sports or exercise in your free time?', ['No', 'Yes'], horizontal=True)

know_values = st.checkbox('I know my blood pressure and cholesterol values')
if know_values:
    systolic = st.number_input('Systolic blood pressure (mmHg)', min_value= 76.0 ,max_value=218.0 , value= 123.0, step=1.0)
    diastolic = st.number_input('Diastolic blood pressure (mmHg)', min_value=41.0 , max_value= 135.0, value=75.0 , step=1.0)
    hdl_chol = st.number_input('HDL cholesterol (mg/dL)', min_value=10, max_value=190, value=54, step=1)
    total_chol = st.number_input('Total cholesterol (mg/dL)', min_value=79, max_value=430, value=188, step=1)

high_bp_number = 1.0 if told_high_bp == 'Yes' else 0.0
bp_meds_number = 1.0 if takes_bp_meds == 'Yes' else 0.0
high_chol_number = 1.0 if told_high_chol == 'Yes' else 0.0
chol_meds_number = 1.0 if takes_chol_meds == 'Yes' else 0.0
family_number = 1.0 if family_history_diabetes == 'Yes' else 0.0
active_leisure_number = 1.0 if active_leisure == 'Yes' else 0.0

row = pd.DataFrame([{
    'age_at_screening': age,
    'sex': sex,
    'race': race,
    'birth_place': birth_place,
    'level_of_education': education,
    'smoking_status': smoking,
    'bmi' : bmi,
    'waist_circ': waist,
    'told_high_bp': high_bp_number,
    'told_high_chol': high_chol_number,
    'takes_bp_meds': bp_meds_number,
    'takes_chol_meds': chol_meds_number,
    'family_history_diabetes': family_number,
    'active_leisure': active_leisure_number,

}])

if know_values:
    row['systolic_bp'] = systolic
    row['diastolic_bp'] = diastolic
    row['hdl_chol'] = hdl_chol
    row['total_chol'] = total_chol

model = lab_model if know_values else basic_model
model_name = "Estimate based on your answers and your measured values." if know_values else "Estimate based on your answers only. Adding your blood pressure and cholesterol makes it more reliable."
assert set(row.columns) == set(model.feature_names_in_)

risk = model.predict_proba(row)[0,1]
st.metric('Estimated risk of undiagnosed diabetes', f'{risk:.0%}')


st.caption(f'You are currently using the {model_name}')
if risk > 0.036:
    st.caption(f'Your risk is {risk / 0.036:.1f} times the average (3.6%).')
else:
    st.caption('Your risk is below the average (3.6%).')
