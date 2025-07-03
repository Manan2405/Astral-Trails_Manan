import streamlit as st
from datetime import datetime

# App configuration
st.set_page_config(
    page_title="Cosmic Radiation Research Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("Cosmic Radiation Research Dashboard")

# Intro section on homepage
st.markdown("""
Welcome to the *Cosmic Radiation Research Dashboard* — an interactive platform to explore real-time and simulated data on cosmic rays, their biological and technological effects, and mission safety.

---

*Select a feature tab below to begin your research:*
""")

# Main Feature Tabs
tabs = st.tabs([
    "Biological Effects Visualizer",
])

# Tab 3: Biological Effects
with tabs[0]:
    st.subheader("Biological Effects of Radiation")

    # Add Age and Gender Inputs
    st.write("---") # Separator for new inputs
    st.subheader("Customize for Individual Factors")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        age_slider = st.slider("Select Age (Years)", 0, 100, 30, key="age_slider")
    with col2:
        age_input = st.number_input(" ", min_value=0, max_value=100, value=age_slider, key="age_input")
    
    # Sync values
    if age_slider != age_input:
        age = age_input
    else:
        age = age_slider

    gender = st.selectbox("Select Gender", ["Male", "Female", "Prefer not to say"])

    st.write("---") # Separator for original content

    col3, col4 = st.columns([3, 1])
    with col3:
        dose_slider = st.slider("Select Radiation Dose (mSv)", 0, 10000, 200, key="dose_slider")
    with col4:
        dose_input = st.number_input(" ", min_value=0, max_value=10000, value=dose_slider, key="dose_input")
    
    # Sync values
    if dose_slider != dose_input:
        dose = dose_input
    else:
        dose = dose_slider


    # --- NEW: Calculate Age and Gender Risk Modifiers ---
    # These modifiers will influence the effective dose or risk threshold
    # Simplified approach based on general radiobiological understanding from ICRP/UNSCEAR
    
    # Base modifier: 1.0 (no change)
    age_modifier = 1.0
    gender_modifier = 1.0
    
    # Age-based modifier: Children are generally more radiosensitive
    # Sources: ICRP Publication 103, UNSCEAR reports (e.g., Sources and Effects of Ionizing Radiation)
    # The younger the age, the higher the sensitivity factor.
    if age < 10: # Very young children
        age_modifier = 1.4 # ~40% higher sensitivity
        st.warning("Note: Children under 10 are significantly more radiosensitive due to rapidly dividing cells and longer potential lifespan for cancer manifestation. The displayed effect considers this increased sensitivity. (Source: ICRP, UNSCEAR)")
    elif age < 20: # Adolescents
        age_modifier = 1.2 # ~20% higher sensitivity
        st.info("Note: Younger individuals (under 20) are generally more radiosensitive than adults. The displayed effect considers this increased sensitivity. (Source: ICRP, UNSCEAR)")
    elif age > 60: # Older adults might have some specific sensitivities/resiliencies depending on tissue
        # While overall cancer risk might be lower due to shorter remaining lifespan,
        # acute effects or specific organ responses can differ. For simplification, we'll make it slightly lower.
        age_modifier = 0.9 # Slightly less sensitive for long-term cancer risk, but acute effects still apply
        st.info("Note: For older adults, the long-term cancer risk from radiation may be slightly lower due to a shorter remaining lifespan. However, pre-existing health conditions can influence resilience to acute effects. (Source: General radiobiological principles)")

    # Gender-based modifier: Females generally have a slightly higher lifetime cancer risk from radiation.
    # Sources: ICRP Publication 103, EPA Radiation Protection guidance
    if gender == "Female":
        gender_modifier = 1.1 # ~10% higher sensitivity, primarily for cancer risk
        st.info("Note: Females generally have a slightly higher lifetime cancer risk from radiation exposure, particularly for breast and thyroid cancers. The displayed effect considers this increased sensitivity. (Source: ICRP, EPA)")
    elif gender == "Male":
        gender_modifier = 1.0 # Baseline
        st.info("Note: Males have a baseline sensitivity to radiation exposure. (Source: ICRP)")
    else: # "Prefer not to say" or any other value
        st.info("Individual biological responses to radiation can vary. Factors like age and gender can influence susceptibility, with younger individuals and females generally having slightly higher sensitivities to radiation-induced cancer risks. (Source: ICRP, WHO)")

    # Combine modifiers to get an "effective dose" for biological impact assessment
    # This is a simplified conceptual adjustment for the UI, not a precise dosimetric calculation.
    adjusted_dose = dose * age_modifier * gender_modifier
    st.markdown(f"Adjusted Biological Dose for your profile: {adjusted_dose:.2f} mSv** (This adjusted dose reflects an individual's relative sensitivity to radiation for biological effects)")

    # --- END NEW MODIFIERS ---


    # Define effect stage (MODIFIED to use adjusted_dose)
    if adjusted_dose < 100:
        effect = "No observable effects. Normal background exposure level."
    elif adjusted_dose < 500:
        effect = "Minor biological impact. Slight increase in cancer risk."
    elif adjusted_dose < 1000:
        effect = "Possible nausea, vomiting. Risk of Acute Radiation Syndrome (ARS)."
    elif adjusted_dose < 3000:
        effect = "Severe ARS symptoms. Temporary sterility possible."
    elif adjusted_dose < 6000:
        effect = "Life-threatening dose. Intensive treatment required."
    else:
        effect = "Fatal in most cases. Survival unlikely without immediate medical care."

    st.info(f"Biological Effect at *{dose} mSv* (Adjusted for your profile): *{effect}*")

    import plotly.graph_objects as go

    st.subheader("📊 Interactive Risk Severity Chart")
    
    # Define thresholds, labels, and colors
    thresholds = [0, 100, 500, 1000, 3000, 6000, 10000]
    labels = [
        "No Effects", "Minor Risk", "Mild ARS", "Severe ARS", "Lethal", "Extreme", "Fatal"
    ]
    colors = ["#2ecc71", "#f1c40f", "#f39c12", "#e67e22", "#e74c3c", "#c0392b"]
    
    # Create figure
    fig = go.Figure()
    
    # Add background colored zones with text annotations
    for i in range(len(thresholds) - 1):
        fig.add_shape(
            type="rect",
            x0=thresholds[i],
            x1=thresholds[i + 1],
            y0=0,
            y1=1,
            fillcolor=colors[i],
            opacity=0.3,
            layer="below",
            line_width=0,
        )
        fig.add_annotation(
            x=(thresholds[i] + thresholds[i + 1]) / 2,
            y=0.95,
            text=labels[i],
            showarrow=False,
            font=dict(size=12),
            opacity=0.8
        )
    
    # Plot dose markers
    fig.add_trace(go.Scatter(
        x=[dose],
        y=[0.5],
        mode='markers+text',
        name='Original Dose',
        marker=dict(color='blue', size=12),
        text=["Original"],
        textposition="bottom center"
    ))
    
    fig.add_trace(go.Scatter(
        x=[adjusted_dose],
        y=[0.5],
        mode='markers+text',
        name='Adjusted Dose',
        marker=dict(color='red', size=12),
        text=["Adjusted"],
        textposition="top center"
    ))
    
    # Layout cleanup
    fig.update_layout(
        xaxis=dict(title="Dose (mSv)", range=[0, 10000]),
        yaxis=dict(visible=False),  # hide useless Y axis
        title="Radiation Dose vs. Biological Risk",
        height=250,
        margin=dict(t=40, b=40),
        showlegend=True
    )
    
    # Display it
    st.plotly_chart(fig, use_container_width=True)

    import pandas as pd
    df = pd.DataFrame({
        "Organ": ["Bone Marrow", "GI Tract", "Skin", "Brain", "Reproductive Organs"],
        "Effect at 1000 mSv+": [
            "Reduced blood cell count", "Nausea, diarrhea", "Burns, hair loss",
            "Cognitive impairment", "Sterility"
        ]
    })
    st.dataframe(df)
# Footer
st.markdown(f"""
---
<p style='text-align: center; color: gray'>
Built by Tanmay Rajput | Last updated: {datetime.today().strftime('%B %d, %Y')}
</p>
""", unsafe_allow_html=True)
