import streamlit as st
import openai

def generate_solution(head, flow, material, description):
    # Combine the inputs into a prompt for the AI
    prompt = f"Head: {head}\nFlow: {flow}\nMaterial: {material}\nDescription: {description}\n\nSuggest a suitable pump solution:"

# Load the API key from an environment variable
openai.api_key = os.getenv('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')
    
    # Call to OpenAI's API (replace 'YOUR_API_KEY' with your actual API key)
    response = openai.Completion.create(
        engine="gpt-4-1106-preview 3",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def main():
    st.title("Pump Selection Assistant")

    # Input fields
    head = st.number_input("Head (in meters)", min_value=0.0, step=0.1)
    flow = st.number_input("Flow (in cubic meters per hour)", min_value=0.0, step=0.1)
    material = st.selectbox("Material", ["Steel", "Copper", "Aluminum", "Plastic"])

    # Description field
    description = st.text_area("Describe your application")

    # Button to generate solution
    if st.button("Generate Solution"):
        solution = generate_solution(head, flow, material, description)
        st.text_area("Suggested Solution", solution, height=300)

if __name__ == "__main__":
    main()
