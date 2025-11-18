import json
import requests
import streamlit as st
from pathlib import Path
from streamlit.logger import get_logger

FASTAPI_BACKEND_ENDPOINT = "http://localhost:8000"
FASTAPI_WINE_MODEL_LOCATION = Path(__file__).resolve().parent / 'model' / 'wine_model.pkl'
LOGGER = get_logger(__name__)

def run():
    st.set_page_config(
        page_title="Wine Classification Demo",
        page_icon="🍷",
    )
    
    # Sidebar configuration
    with st.sidebar:
        st.title("🍷 Wine Classifier")
        
        # Backend health check
        try:
            backend_request = requests.get(FASTAPI_BACKEND_ENDPOINT)
            if backend_request.status_code == 200:
                st.success("Backend online ✅")
            else:
                st.warning("Problem connecting 😭")
        except requests.ConnectionError as ce:
            LOGGER.error(ce)
            LOGGER.error("Backend offline 😱")
            st.error("Backend offline 😱")
        
        st.info("Configure parameters")
        
        # File uploader for JSON test data
        test_input_file = st.file_uploader('Upload test prediction file', type=['json'])
        if test_input_file:
            st.write('Preview file')
            test_input_data = json.load(test_input_file)
            st.json(test_input_data)
            st.session_state["IS_JSON_FILE_AVAILABLE"] = True
            st.session_state["JSON_DATA"] = test_input_data
        else:
            st.session_state["IS_JSON_FILE_AVAILABLE"] = False
        
        # Option to choose input method
        st.divider()
        input_method = st.radio(
            "Input Method",
            ["Manual Input (Sliders)", "Use Uploaded JSON"],
            disabled=not st.session_state.get("IS_JSON_FILE_AVAILABLE", False) if st.session_state.get("IS_JSON_FILE_AVAILABLE", False) else True
        )
        
        st.divider()
        
        # Wine feature sliders (based on wine dataset ranges)
        if not st.session_state.get("IS_JSON_FILE_AVAILABLE", False) or input_method == "Manual Input (Sliders)":
            alcohol = st.slider("Alcohol", 11.0, 15.0, 13.0, 0.1, help="Alcohol content (%)")
            malic_acid = st.slider("Malic Acid", 0.5, 6.0, 2.0, 0.1, help="Malic acid (g/L)")
            ash = st.slider("Ash", 1.3, 3.5, 2.3, 0.1, help="Ash content (g/L)")
            alcalinity_of_ash = st.slider("Alcalinity of Ash", 10.0, 30.0, 19.0, 0.5, help="Alcalinity of ash")
            magnesium = st.slider("Magnesium", 70.0, 162.0, 100.0, 1.0, help="Magnesium (mg/L)")
            total_phenols = st.slider("Total Phenols", 0.9, 4.0, 2.3, 0.1, help="Total phenols")
            flavanoids = st.slider("Flavanoids", 0.3, 5.1, 2.0, 0.1, help="Flavanoids")
            nonflavanoid_phenols = st.slider("Nonflavanoid Phenols", 0.1, 0.7, 0.3, 0.05, help="Nonflavanoid phenols")
            proanthocyanins = st.slider("Proanthocyanins", 0.4, 3.6, 1.5, 0.1, help="Proanthocyanins")
            color_intensity = st.slider("Color Intensity", 1.0, 13.0, 5.0, 0.5, help="Color intensity")
            hue = st.slider("Hue", 0.4, 1.7, 1.0, 0.05, help="Hue")
            od280_od315 = st.slider("OD280/OD315", 1.2, 4.0, 2.5, 0.1, help="OD280/OD315 of diluted wines")
            proline = st.slider("Proline", 278.0, 1680.0, 750.0, 10.0, help="Proline (mg/L)")
        
        predict_button = st.button('Predict', type="primary", use_container_width=True)
    
    # Main content area
    st.write("# Wine Classification Prediction! 🍷")
    st.write("This application predicts the wine cultivar class based on 13 chemical features.")
    
    st.divider()
    
    # Prediction logic
    if predict_button:
        if FASTAPI_WINE_MODEL_LOCATION.is_file():
            # Prepare input data
            if st.session_state.get("IS_JSON_FILE_AVAILABLE", False) and input_method == "Use Uploaded JSON":
                json_data = st.session_state["JSON_DATA"]
                client_input = json.dumps(json_data)
            else:
                client_input = json.dumps({
                    "alcohol": alcohol,
                    "malic_acid": malic_acid,
                    "ash": ash,
                    "alcalinity_of_ash": alcalinity_of_ash,
                    "magnesium": magnesium,
                    "total_phenols": total_phenols,
                    "flavanoids": flavanoids,
                    "nonflavanoid_phenols": nonflavanoid_phenols,
                    "proanthocyanins": proanthocyanins,
                    "color_intensity": color_intensity,
                    "hue": hue,
                    "od280_od315_of_diluted_wines": od280_od315,
                    "proline": proline
                })
            
            try:
                result_container = st.empty()
                with st.spinner('🔮 Predicting wine class...'):
                    predict_wine_response = requests.post(
                        f'{FASTAPI_BACKEND_ENDPOINT}/predict', 
                        client_input,
                        headers={'Content-Type': 'application/json'}
                    )
                
                if predict_wine_response.status_code == 200:
                    wine_content = json.loads(predict_wine_response.content)
                    predicted_class = wine_content["response"]
                    
                    # Display results
                    st.balloons()
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Predicted Class", f"Class {predicted_class}")
                    
                    with col2:
                        class_names = {
                            0: "Cultivar 1",
                            1: "Cultivar 2",
                            2: "Cultivar 3"
                        }
                        st.metric("Wine Type", class_names.get(predicted_class, "Unknown"))
                    
                    with col3:
                        st.metric("Status", "✅ Success")
                    
                    # Detailed result box
                    if predicted_class == 0:
                        result_container.success("🍇 The wine is predicted to be: **Class 0 (Cultivar 1)**")
                    elif predicted_class == 1:
                        result_container.success("🍷 The wine is predicted to be: **Class 1 (Cultivar 2)**")
                    elif predicted_class == 2:
                        result_container.success("🍾 The wine is predicted to be: **Class 2 (Cultivar 3)**")
                    else:
                        result_container.error("⚠️ Some problem occurred while predicting")
                        LOGGER.error("Problem during prediction")
                    
                    # Show input data used
                    with st.expander("📊 View Input Data Used"):
                        st.json(json.loads(client_input))
                
                else:
                    st.toast(
                        f'🔴 Status from server: {predict_wine_response.status_code}. Refresh page and check backend status',
                        icon="🔴"
                    )
                    st.error(f"Server returned status code: {predict_wine_response.status_code}")
            
            except Exception as e:
                st.toast('🔴 Problem with backend. Refresh page and check backend status', icon="🔴")
                st.error(f"Error connecting to backend: {str(e)}")
                LOGGER.error(e)
        
        else:
            LOGGER.warning('wine_model.pkl not found. Make sure to run train.py to generate the model.')
            st.toast('🔥 Model wine_model.pkl not found. Please run the train.py file to train the model', icon="🔥")
            st.error("⚠️ Model file not found. Please train the model first by running `train.py`")

if __name__ == "__main__":
    run()