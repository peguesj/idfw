#!/usr/bin/env python3
import os
from openai import OpenAI
import argparse

# Set the OpenAI API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": question}],
            model="gpt-4"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

# Define the main function for the interpreter
def parse_arguments():
    parser = argparse.ArgumentParser(description="Ask questions to OpenAI")
    parser.add_argument("question", type=str, help="The question to ask the model")
    return parser.parse_args()

def main():
    """
    Main function to run the IDEA Framework Interpreter.
    It takes user input for an idea name and then allows the user to ask questions about the idea,
    receiving feedback from the OpenAI model.
    """
    args = parse_arguments()
    response = ask_question(args.question)
    print(response)

# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()
