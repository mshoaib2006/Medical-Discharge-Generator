import streamlit as st
from datetime import datetime

def render_patient_demographics_tab(patient_data):
    st.header("Patient Demographics")
    st.markdown("Enter the patient's basic information.")
    with st.form("patient_demographics_form"):
        patient_data['patient_name'] = st.text_input("Patient Name", value=patient_data.get('patient_name', ''))
        patient_data['patient_age'] = st.text_input("Age", value=patient_data.get('patient_age', ''))
        
        gender_options = ["Male", "Female", "Other"]
        current_gender = patient_data.get('patient_gender', 'Male')
        selected_index = gender_options.index(current_gender) if current_gender in gender_options else 0
        patient_data['patient_gender'] = st.selectbox("Gender", gender_options, index=selected_index)
        
        patient_data['patient_id'] = st.text_input("Patient ID", value=patient_data.get('patient_id', ''))
        submitted = st.form_submit_button("Save Demographics")
        if submitted:
            st.success("Patient demographics saved! Proceed to the next tab.")
    return patient_data

def render_medical_details_tab(patient_data):
    st.header("Medical Details")
    st.markdown("Provide details about the diagnosis, procedures, and medications.")
    with st.form("medical_details_form"):
        patient_data['diagnosis_summary'] = st.text_area("Diagnosis Summary", value=patient_data.get('diagnosis_summary', ''), height=100)
        patient_data['procedures_done'] = st.text_area("Procedures Done", value=patient_data.get('procedures_done', ''), height=100)

        st.subheader("Prescribed Medications")
        if not isinstance(patient_data.get('medications'), list):
            patient_data['medications'] = []

        num_meds_key = f"num_meds_input_{st.session_state.get('current_tab', 1)}"
        num_meds = st.number_input("Number of Medications", min_value=0, value=len(patient_data['medications']), key=num_meds_key)

        while len(patient_data['medications']) < num_meds:
            patient_data['medications'].append({"name": "", "dose": "", "frequency": "", "duration": ""})
        patient_data['medications'] = patient_data['medications'][:num_meds]

        for i in range(num_meds):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                patient_data['medications'][i]['name'] = st.text_input(f"Name {i+1}", value=patient_data['medications'][i].get('name', ''), key=f"med_name_{i}")
            with col2:
                patient_data['medications'][i]['dose'] = st.text_input(f"Dose {i+1}", value=patient_data['medications'][i].get('dose', ''), key=f"med_dose_{i}")
            with col3:
                patient_data['medications'][i]['frequency'] = st.text_input(f"Frequency {i+1}", value=patient_data['medications'][i].get('frequency', ''), key=f"med_freq_{i}")
            with col4:
                patient_data['medications'][i]['duration'] = st.text_input(f"Duration {i+1}", value=patient_data['medications'][i].get('duration', ''), key=f"med_dur_{i}")

        patient_data['lab_test_results'] = st.text_area("Lab Test Results (one per line)", value=patient_data.get('lab_test_results', ''), height=100)

        submitted = st.form_submit_button("Save Medical Details")
        if submitted:
            st.success("Medical details saved! Proceed to the next tab.")
    return patient_data

def render_post_discharge_tab(patient_data):
    st.header("Post-Discharge & Doctor Information")
    st.markdown("Enter post-care instructions and doctor's details.")
    with st.form("post_discharge_form"):
        current_date_str = patient_data.get('discharge_date', '') 
        current_date_val = None
        if current_date_str:
            try:
                current_date_val = datetime.strptime(current_date_str, "%Y-%m-%d").date()
            except ValueError:
                current_date_val = None

        if current_date_val is None:
            current_date_val = datetime.today().date()
            
        new_date = st.date_input("Discharge Date", value=current_date_val)
        patient_data['discharge_date'] = new_date.strftime("%Y-%m-%d") if new_date else ""

        patient_data['discharge_time'] = st.text_input("Discharge Time (e.g., 16:30)", value=patient_data.get('discharge_time', '16:30'))
        patient_data['follow_up_details'] = st.text_area("Follow-up Details", value=patient_data.get('follow_up_details', ''), height=100)
        patient_data['post_care_instructions'] = st.text_area("Post Discharge Instructions (one per line)", value=patient_data.get('post_care_instructions', ''), height=150)
        patient_data['doctor_name'] = st.text_input("Doctor's Name", value=patient_data.get('doctor_name', ''))
        submitted = st.form_submit_button("Save Post-Discharge Info")
        if submitted:
            st.success("Post-discharge information saved! Proceed to the next tab.")
    return patient_data

def render_ai_assistant_tab(patient_data, get_ai_summary_func):
    st.header("AI Assistant: Medical Notes Summarization")
    st.markdown("Paste raw medical notes here, and the AI will attempt to summarize key diagnosis and procedure details.")
    with st.form("ai_notes_summary_form"):
        patient_data['medical_notes_input'] = st.text_area(
            "Medical Notes (Free Text)",
            value=patient_data.get('medical_notes_input', ''),
            height=300,
            placeholder="Paste raw doctor's notes or clinical observations here for AI summarization"
        )
        submitted = st.form_submit_button("Generate AI Summary")
        if submitted and patient_data.get('medical_notes_input', ''): 
            with st.spinner("AI is analyzing notes..."):
                ai_prompt = f"Summarize the following medical notes, focusing on diagnosis and procedures. Keep it concise and clinical:\n\n{patient_data['medical_notes_input']}"
                summary_result = get_ai_summary_func(ai_prompt)
                if "Error:" in summary_result or "failed" in summary_result:
                    st.error(summary_result)
                    patient_data['ai_summary_output'] = "Error during summarization."
                else:
                    patient_data['ai_summary_output'] = summary_result
            st.subheader("AI-Generated Summary:")
            st.write(patient_data['ai_summary_output'])
            st.success("AI summary generated!")
        elif submitted and not patient_data.get('medical_notes_input', ''):
            st.warning("Please enter some medical notes to generate a summary.")
    return patient_data