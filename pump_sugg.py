import streamlit as st
from openai import OpenAI
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

# Initialize the OpenAI client with your API key
client = OpenAI()

# Set page config to wide mode
st.set_page_config(layout="wide")

# Define a function to generate chat responses based on the context
def chat_with_assistant(messages, pump_data):
    try:
        # Prepare the context with all pump data
        context = (
            f"Pump Data: Head - {pump_data['head']}, Flow - {pump_data['flow']}, Material - {pump_data['material']}, "
            f"Type of Fluid - {pump_data['fluid_type']}, Pumping Temperature - {pump_data['pumping_temperature']}, "
            f"Type of Pump - {pump_data['type_of_pump']}, Sealing System - {pump_data['sealing_system']}, "
            f"Area of Installation - {pump_data['area_of_installation']}, Ambient Temperature - {pump_data['ambient_temperature']}, "
            f"Description - {pump_data['description']}\n"
        )
        
        # Add the context to the beginning of the conversation
        messages_with_context = [{"role": "system", "content": context}] + messages

        # Call to OpenAI's API with the conversation history including context
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_with_context
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"

def generate_solution(head, flow, material, fluid_type, pumping_temperature, type_of_pump, sealing_system, area_of_installation, ambient_temperature, description):
    # Combine the inputs into a prompt for the AI
    prompt = (
        f"Head: {head}\n"
        f"Flow: {flow}\n"
        f"Material: {material}\n"
        f"Type of Fluid: {fluid_type}\n"
        f"Pumping Temperature: {pumping_temperature}\n"
        f"Type of Pump: {type_of_pump}\n"
        f"Sealing System: {sealing_system}\n"
        f"Area of Installation: {area_of_installation}\n"
        f"Ambient Temperature: {ambient_temperature}\n"
        f"Description: {description}\n\n"
        "Suggest a suitable pump solution:"
    )

    try:
        # Call to OpenAI's API
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant knowledgeable in pump selection."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"

def create_pdf(content):
    # Create a byte stream buffer
    pdf_buffer = io.BytesIO()
    
    # Create a canvas
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter

    # Add content to PDF
    c.drawString(72, height - 72, content)

    # Save PDF
    c.showPage()
    c.save()

    # Move the buffer's pointer to the beginning
    pdf_buffer.seek(0)
    return pdf_buffer

def main():
    # Use columns to layout the pump selection and chat side by side with different sizes
    col1, col2, col3 = st.columns([2, 3, 2])

    with col1:
        st.header("Pump Selection Assistant")
        with st.container():
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                head = st.number_input("Head (in meters)", min_value=0.0, step=0.1)
                flow = st.number_input("Flow (in cubic meters per hour)", min_value=0.0, step=0.1)
                material = st.selectbox("Material", ["Steel", "Copper", "Aluminum", "Plastic"])
            with col1_2:
                fluid_type = st.selectbox("Type of Fluid", ["Water", "Oil", "Chemicals", "Other"])
                pumping_temperature = st.number_input("Pumping Temperature (in Celsius)", min_value=-273, step=1)
                pump_type = st.selectbox("Type of Pump", ["Centrifugal", "Positive Displacement", "Submersible", "Other"])
            sealing_system = st.selectbox("Sealing System", ["Mechanical Seal", "Packing Seal", "Seal-less"])
            area_of_installation = st.text_input("Area of Installation")
            ambient_temperature = st.number_input("Ambient Temperature (in Celsius)", min_value=-273, step=1)
            description = st.text_area("Describe your application")

            if st.button("Generate Solution"):
                solution = generate_solution(
                    head, flow, material, fluid_type, pumping_temperature,
                    pump_type, sealing_system, area_of_installation,
                    ambient_temperature, description
                )
                # Store all pump parameters in session state for the chat context
                st.session_state['pump_data'] = {
                    "head": head,
                    "flow": flow,
                    "material": material,
                    "fluid_type": fluid_type,
                    "pumping_temperature": pumping_temperature,
                    "type_of_pump": pump_type,
                    "sealing_system": sealing_system,
                    "area_of_installation": area_of_installation,
                    "ambient_temperature": ambient_temperature,
                    "description": description
                }
                st.text_area("Suggested Solution", solution, height=300)
                pdf = create_pdf(solution)
                st.download_button(
                    label="Download Solution as PDF",
                    data=pdf,
                    file_name="pump_solution.pdf",
                    mime="application/pdf"
                )

    with col2:
        st.header("Chat with the Assistant")
        # Initialize session state variables for chat and pump data if they don't exist
        if 'messages' not in st.session_state:
            st.session_state['messages'] = []
        if 'user_message' not in st.session_state:
            st.session_state['user_message'] = ""
        if 'pump_data' not in st.session_state:
            st.session_state['pump_data'] = {"head": 0, "flow": 0, "material": "", "description": ""}

        # Display the chat history
        for idx, message in enumerate(st.session_state['messages']):
            if message["role"] == "user":
                st.text_area(f"You: {idx}", value=message["content"], height=80, key=f"user_{idx}")
            else:
                st.text_area(f"Assistant: {idx}", value=message["content"], height=80, key=f"assistant_{idx}")

        # User sends a new message
        user_message = st.text_input("Your message", value=st.session_state['user_message'], key="user_message")

        def send_message():
            # Append user message to the conversation history and clear the input
            if st.session_state['user_message'].strip() != "":
                st.session_state['messages'].append({"role": "user", "content": st.session_state['user_message']})
                # Generate a response from the assistant using pump data
                chat_response = chat_with_assistant(st.session_state['messages'], st.session_state['pump_data'])
                # Append assistant's response to the conversation history
                st.session_state['messages'].append({"role": "assistant", "content": chat_response})
                # Clear the message input
                st.session_state['user_message'] = ""

        # Button to send the message
        if st.button("Send", on_click=send_message):
            # Just calling the callback function here
            pass

if __name__ == "__main__":
    main()
           
