import streamlit as st
import os
from groq import Groq


# -----------------------------
# Groq API connection
# -----------------------------

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)


# -----------------------------
# BMI calculation
# -----------------------------

def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 1)


# -----------------------------
# BMI category
# -----------------------------

def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Healthy weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obesity"


# -----------------------------
# Reference weight range
# -----------------------------

def healthy_weight_range(height_cm):
    height_m = height_cm / 100

    minimum = 18.5 * (height_m ** 2)
    maximum = 24.9 * (height_m ** 2)

    return round(minimum, 1), round(maximum, 1)


# -----------------------------
# BMR calculation
# -----------------------------

def calculate_bmr(weight, height_cm, age, gender):
    if gender.lower() == "female":
        bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) - 161
    else:
        bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) + 5

    return round(bmr)


# -----------------------------
# Activity multipliers
# -----------------------------

ACTIVITY_MULTIPLIERS = {
    "Sedentary": 1.2,
    "Lightly Active": 1.375,
    "Moderately Active": 1.55,
    "Very Active": 1.725
}


# -----------------------------
# TDEE calculation
# -----------------------------

def calculate_tdee(bmr, activity_level):
    multiplier = ACTIVITY_MULTIPLIERS[activity_level]
    return round(bmr * multiplier)


# -----------------------------
# Master health calculations
# -----------------------------

def calculate_health_metrics(
    name,
    gender,
    age,
    weight,
    height_cm,
    activity_level
):

    bmi = calculate_bmi(weight, height_cm)

    category = bmi_category(bmi)

    healthy_low, healthy_high = healthy_weight_range(height_cm)

    bmr = calculate_bmr(
        weight,
        height_cm,
        age,
        gender
    )

    tdee = calculate_tdee(
        bmr,
        activity_level
    )

    return {
        "name": name,
        "gender": gender,
        "age": age,
        "weight": weight,
        "height": height_cm,
        "activity_level": activity_level,
        "bmi": bmi,
        "bmi_category": category,
        "healthy_weight_low": healthy_low,
        "healthy_weight_high": healthy_high,
        "bmr": bmr,
        "tdee": tdee
    }


# -----------------------------
# AI roadmap generator
# -----------------------------

def generate_roadmap(data):

    prompt = f"""
Create a personalized wellness and weight-management roadmap.

User information:

Name: {data['name']}
Gender: {data['gender']}
Age: {data['age']}
Weight: {data['weight']} kg
Height: {data['height']} cm
Activity level: {data['activity_level']}

Calculated information:

BMI: {data['bmi']}
BMI category: {data['bmi_category']}
Estimated BMR: {data['bmr']} kcal/day
Estimated TDEE: {data['tdee']} kcal/day
Reference weight range: {data['healthy_weight_low']} kg - {data['healthy_weight_high']} kg

Create a practical 12-week wellness roadmap.

Include:

1. Starting-point summary
2. A realistic and sustainable progress goal
3. Weeks 1–2
4. Weeks 3–4
5. Weeks 5–8
6. Weeks 9–12
7. Healthy nutrition habits
8. Physical activity
9. Sleep and recovery
10. Weekly tracking checklist
11. Motivation tips

Important safety rules:

- Do not recommend starvation or extreme dieting.
- Do not recommend dangerous or excessive exercise.
- Do not promise a specific amount of weight loss.
- Do not diagnose medical conditions.
- Treat BMI, BMR and TDEE as estimates.
- Clearly state that this is general educational wellness information,
  not medical advice.
- Recommend consulting a qualified healthcare professional or registered
  dietitian when appropriate.

Use clear Markdown headings and bullet points.
Keep the advice practical, encouraging and easy to understand.
"""

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",
                "content": "You are a responsible wellness planning assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.4,
        max_tokens=2500
    )

    return response.choices[0].message.content


# -----------------------------
# Main application function
# -----------------------------

def create_roadmap(
    name,
    gender,
    age,
    weight,
    height,
    activity
):

    if not name:
        return "⚠️ Please enter your name."

    if not gender:
        return "⚠️ Please select your gender."

    if not age or not weight or not height:
        return "⚠️ Please complete your age, weight, and height."

    if not activity:
        return "⚠️ Please select your activity level."

    data = calculate_health_metrics(
        name=name,
        gender=gender,
        age=age,
        weight=weight,
        height_cm=height,
        activity_level=activity
    )

    return generate_roadmap(data)


# -----------------------------
# Gradio interface
# -----------------------------

with gr.Blocks(
    title="AI Weight-Loss Roadmap Generator"
) as app:

    gr.Markdown("""
    # 🥗 AI Weight-Loss Roadmap Generator

    Create a personalized wellness roadmap based on your basic information.

    **Note:** This tool provides general educational wellness information,
    not medical advice.
    """)

    with gr.Row():

        with gr.Column():

            gr.Markdown("### 👤 Your Information")

            name = gr.Textbox(
                label="Name",
                placeholder="Enter your name"
            )

            gender = gr.Dropdown(
                choices=["Male", "Female"],
                label="Gender"
            )

            age = gr.Number(
                label="Age",
                minimum=18,
                maximum=100
            )

            weight = gr.Number(
                label="Weight (kg)",
                minimum=30,
                maximum=300
            )

            height = gr.Number(
                label="Height (cm)",
                minimum=100,
                maximum=250
            )

            activity = gr.Dropdown(
                choices=[
                    "Sedentary",
                    "Lightly Active",
                    "Moderately Active",
                    "Very Active"
                ],
                label="Activity Level"
            )

            generate_button = gr.Button(
                "🚀 Generate My Roadmap"
            )

        with gr.Column():

            gr.Markdown(
                "### 📋 Your Personalized Roadmap"
            )

            results = gr.Markdown(
                "Your roadmap will appear here."
            )

    generate_button.click(
        fn=create_roadmap,
        inputs=[
            name,
            gender,
            age,
            weight,
            height,
            activity
        ],
        outputs=results
    )


# -----------------------------
# Launch
# -----------------------------

if __name__ == "__main__":
    app.launch()
