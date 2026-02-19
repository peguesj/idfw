import openai

# Set the OpenAI API key
openai.api_key = 'your-api-key-here'

# Define a function to ask questions and get feedback from OpenAI
def ask_question(question):
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=question,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Define the main function for the interpreter
def main():
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
