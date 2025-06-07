
import streamlit as st
import re
import openai

response = openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🧠 Agentic Storyboard Builder")
st.markdown("Turn your idea blurb into a data-backed storyboard, with full control over facts.")

def identify_placeholders(blurb: str):
    prompt = f"""
You are a smart assistant. A user gives you a blurb with missing qualitative or quantitative data.
Your job is to rewrite the blurb with clear placeholder tags and produce a JSON list describing each missing piece.

Blurb:
{blurb}

Return output in this format:
---
[JSON]
---
Rewritten blurb:
"""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def fill_placeholders(rewritten_blurb, placeholder_labels):
    filled_blurb = rewritten_blurb
    for label in placeholder_labels:
        filled_blurb = re.sub(f"<{label}>", f"SIM_{label}", filled_blurb)
    return filled_blurb

def convert_to_storyboard(filled_blurb):
    parts = filled_blurb.split('.')
    return f"""
    ### Scene 1: Hook
    {parts[0].strip()}.

    ### Scene 2: Core Insight
    {parts[1].strip()}.

    ### Scene 3: Implications
    {' '.join(parts[2:]).strip()}.
    """

def simulate_verification(placeholder_labels):
    results = []
    for label in placeholder_labels:
        results.append({
            "label": label,
            "original": f"SIM_{label}",
            "verifier_agrees": False,
            "suggested": f"VERIFIED_{label}"
        })
    return results

user_blurb = st.text_area("✍️ Paste your blurb with missing facts:", height=200)

if st.button("🔍 Detect Missing Data"):
    with st.spinner("Thinking like a researcher..."):
        raw_output = identify_placeholders(user_blurb)
    st.subheader("🔧 Detected Placeholders & Rewritten Blurb")
    st.code(raw_output)

    rewritten_blurb = "Saudi Arabia invested <AMOUNT> in fintech in <YEAR>. That marked a <PERCENT> rise from <PREV_YEAR>."
    placeholder_labels = ["AMOUNT", "YEAR", "PERCENT", "PREV_YEAR"]

    filled = fill_placeholders(rewritten_blurb, placeholder_labels)
    storyboard = convert_to_storyboard(filled)
    st.subheader("📄 Initial Storyboard")
    st.markdown(storyboard)

    st.subheader("🧪 Verifier Agent Found Issues")
    verification_results = simulate_verification(placeholder_labels)

    final_values = {}
    for result in verification_results:
        st.markdown(f"**{result['label']}**")
        choice = st.radio(
            f"Choose value for {result['label']}",
            [result['original'], result['suggested']],
            key=result['label']
        )
        final_values[result['label']] = choice

    if st.button("✅ Finalize Storyboard"):
        final_blurb = rewritten_blurb
        for label, value in final_values.items():
            final_blurb = re.sub(f"<{label}>", value, final_blurb)
        final_storyboard = convert_to_storyboard(final_blurb)
        st.success("Final storyboard is ready!")
        st.markdown(final_storyboard)
