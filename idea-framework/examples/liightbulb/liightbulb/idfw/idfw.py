#!/usr/bin/env python3
import openai
import os

# Set the OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Check if the OpenAI API key is set
if not openai.api_key:
    raise ValueError("OpenAI API key not found. Please set the 'OPENAI_API_KEY' environment variable.")

# Define a function to ask questions and get feedback from OpenAI
def ask_question(question):
    """
    Asks a question to the OpenAI model and returns the response.
    
    Args:
        question (str): The question to ask the model.
    
    Returns:
        str: The model's response to the question.
    """
    try:
        response = openai.Completion.create( # Correct method call for the latest OpenAI API
            model="text-davinci-003",
            prompt=question,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred while querying OpenAI: {e}")
        return "Sorry, I couldn't get a response from OpenAI."

# Define the main function for the interpreter
def main():
    """
    Main function to run the IDEA Framework Interpreter.
    It takes user input for an idea name and then allows the user to ask questions about the idea,
    receiving feedback from the OpenAI model.
    """
    print("Welcome to the IDEA Framework Interpreter!")
    idea_name = input("Enter the name of your IDEA: ")
    print(f"Great! Let's explore the IDEA: {idea_name}")

    # Ask questions and provide feedback
    while True:
        question = input("Ask a question about your IDEA or type 'exit' to quit: ")
        if question.lower() == 'exit':
            break
        feedback = ask_question(question)
        print(f"Feedback: {feedback}")

# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()
