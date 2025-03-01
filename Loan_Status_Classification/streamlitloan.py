# -*- coding: utf-8 -*-
"""Untitled13.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1iBGaMx-WAvFsA_cESXheeuUyMEK1oYIb
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder

with open('loan_status_model_new.pkl', 'rb') as file:
    svc_model = pickle.load(file)

with open('scaler.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

with open('selector.pkl', 'rb') as selector_file:
    selector = pickle.load(selector_file)

encoders = {
    'Gender': LabelEncoder().fit(['Male', 'Female']),
    'Married': LabelEncoder().fit(['Yes', 'No']),
    'Dependents': LabelEncoder().fit(['0', '1', '2', '3+']),
    'Education': LabelEncoder().fit(['Graduate', 'Not Graduate']),
    'Self_Employed': LabelEncoder().fit(['Yes', 'No']),
    'Property_Area': LabelEncoder().fit(['Urban', 'Rural', 'Semiurban'])
}

def preprocess_data(train):
    st.write("Raw Input Data:", train)

    if train['LoanAmount'].values[0] <= 0:
        st.error("LoanAmount must be a positive number.")
        return None
    if train['ApplicantIncome'].values[0] <= 0 and train['CoapplicantIncome'].values[0] <= 0:
        st.error("Both ApplicantIncome and CoapplicantIncome cannot be zero or negative.")
        return None

    for column, encoder in encoders.items():
        if column in train.columns:
            train[column] = encoder.transform(train[column])

    train['ApplicantIncome'] = np.where(train['ApplicantIncome'] <= 0, 1, train['ApplicantIncome'])
    train['CoapplicantIncome'] = np.where(train['CoapplicantIncome'] <= 0, 1, train['CoapplicantIncome'])

    train['Total_Income'] = train['ApplicantIncome'] + train['CoapplicantIncome']

    if train['Total_Income'].values[0] <= 0:
        st.error("Total Income cannot be zero or negative.")
        return None

    train.drop(columns=['ApplicantIncome', 'CoapplicantIncome'], inplace=True)

    train['LoanAmount'] = np.where(train['LoanAmount'] <= 0, 1, train['LoanAmount'])
    train['Total_Income'] = np.where(train['Total_Income'] <= 0, 1, train['Total_Income'])

    train['LoanAmount'] = np.log1p(train['LoanAmount'])
    train['Total_Income'] = np.log1p(train['Total_Income'])

    try:
        train_scaled = scaler.transform(train)
        train_selected = selector.transform(train_scaled)

        return pd.DataFrame(train_selected, columns=train.columns[selector.get_support()])
    except Exception as e:
        st.error(f"Error in scaling: {str(e)}")
        return None

# Streamlit app
st.title("Loan Status Prediction")

gender = st.selectbox("Gender", options=["Male", "Female"])
married = st.selectbox("Married", options=["Yes", "No"])
dependents = st.selectbox("Dependents", options=["0", "1", "2", "3+"])
education = st.selectbox("Education", options=["Graduate", "Not Graduate"])
self_employed = st.selectbox("Self Employed", options=["Yes", "No"])
loan_amount_term = st.number_input("Loan Amount Term (in months)", min_value=0)
credit_history = st.selectbox("Credit History", options=["1", "0"])
property_area = st.selectbox("Property Area", options=["Urban", "Rural", "Semiurban"])
applicant_income = st.number_input("Applicant Income", min_value=0)
coapplicant_income = st.number_input("Coapplicant Income", min_value=0)
loan_amount = st.number_input("Loan Amount", min_value=0)

if st.button("Predict"):
    input_data = pd.DataFrame({
        'Gender': [gender],
        'Married': [married],
        'Dependents': [dependents],
        'Education': [education],
        'Self_Employed': [self_employed],
        'Loan_Amount_Term': [loan_amount_term],
        'Credit_History': [credit_history],
        'Property_Area': [property_area],
        'ApplicantIncome': [applicant_income],
        'CoapplicantIncome': [coapplicant_income],
        'LoanAmount': [loan_amount]
    })

    processed_input = preprocess_data(input_data)

    if processed_input is not None:
        st.write("Processed Input:", processed_input)

        prediction = svc_model.predict(processed_input)
        prediction_label = "Y - Loan Approved" if prediction[0] == 1 else "N - Loan Not Approved"

        st.write(f'Predicted Class: {prediction_label}')
    else:
        st.error("There was an error processing the input data.")