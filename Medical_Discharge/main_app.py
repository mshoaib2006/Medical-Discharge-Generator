import streamlit as st
from discharge_summary_input import (
    render_patient_demographics_tab,
    render_medical_details_tab,
    render_post_discharge_tab,
    render_ai_assistant_tab)
from pdf_generator import create_discharge_summary_pdf, get_ai_summary

st.set_page_config(layout="wide", page_title="Medical Discharge Summary Generator")

st.title(" Medical Discharge Summary Generator")
st.markdown("Generate comprehensive and personalized discharge summaries for patients.")

# Initialize patient_data in session state if not already present
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {
        "patient_name": "",
        "patient_age": "",
        "patient_gender": "Male",
        "patient_id": "",
        "diagnosis_summary": "",
        "procedures_done": "", 
        "medications": [],
        "lab_test_results": "",
        "discharge_date": "",
        "discharge_time": "16:30",
        "follow_up_details": "",
        "post_care_instructions": "",
        "doctor_name": "",
        "medical_notes_input": "",
        "ai_summary_output": ""
    }

# Initialize current_tab in session state
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 0

tab_titles = [
    "1. Patient Demographics",
    "2. Medical Details",
    "3. Post-Discharge & Doctor",
    "4. AI Assistant",
    "5. Generate Summary"
]
tabs = st.tabs(tab_titles)

with tabs[0]:
    st.session_state.current_tab = 0
    st.session_state.patient_data = render_patient_demographics_tab(st.session_state.patient_data)

with tabs[1]:
    st.session_state.current_tab = 1
    st.session_state.patient_data = render_medical_details_tab(st.session_state.patient_data)

with tabs[2]:
    st.session_state.current_tab = 2
    st.session_state.patient_data = render_post_discharge_tab(st.session_state.patient_data)

with tabs[3]:
    st.session_state.current_tab = 3
    st.session_state.patient_data = render_ai_assistant_tab(st.session_state.patient_data, get_ai_summary)

with tabs[4]:
    st.session_state.current_tab = 4
    st.header("Generate & Download Discharge Summary")
    st.markdown("Review the entered data and generate the final PDF discharge summary.")

    st.subheader("Current Patient Data Summary:")
    st.json(st.session_state.patient_data) 

    if st.button("Generate PDF Summary"):
       
        if not all([st.session_state.patient_data.get('patient_name'),
                    st.session_state.patient_data.get('patient_id'),
                    st.session_state.patient_data.get('diagnosis_summary'),
                    st.session_state.patient_data.get('discharge_date'),
                    st.session_state.patient_data.get('doctor_name')]):
            st.error("Please fill in all mandatory fields (Name, ID, Diagnosis, Discharge Date, Doctor Name) across the tabs before generating the PDF.")
        else:
            pdf_output = create_discharge_summary_pdf(st.session_state.patient_data)
            
            if pdf_output:
                file_name_patient_id = st.session_state.patient_data.get('patient_id', 'UnknownPatient')
                file_name_discharge_date = st.session_state.patient_data.get('discharge_date', 'UnknownDate')
                
                st.download_button(
                    label="Download Discharge Summary PDF",
                    data=pdf_output,
                    file_name=f"Discharge_Summary_{file_name_patient_id}_{file_name_discharge_date}.pdf",
                    mime="application/pdf"
                )
                st.success("PDF summary generated and ready for download!")
            else:
                st.error("Failed to generate PDF. Please check your inputs and try again.")