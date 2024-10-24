import sys
import gradio as gr
from dotenv import load_dotenv
from ask_repo import ask_question

load_dotenv()


def main(repo):
    with gr.Blocks() as demo:
        gr.Markdown("# Chat Interface with Repository")

        # Second row: Question input
        question = gr.Textbox(
            label="Question", placeholder="Enter your question")

        # Output display for the response.
        output = gr.Markdown(label="Response")

        # Wrapper function to include the repo name as a constant parameter
        def ask_with_repo(question):
            return ask_question(repo, question)

        # Submit button to call the function
        submit_btn = gr.Button("Ask")

        # Function call for the output panel
        submit_btn.click(
            fn=ask_with_repo,
            inputs=question,
            outputs=output
        )

        # Allow pressing enter in the question box to trigger the same function.
        question.submit(
            fn=ask_with_repo,
            inputs=question,
            outputs=output
        )

    # Launch the Gradio app.
    demo.launch()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        repo_name = sys.argv[1]
        main(repo_name)
    else:
        print("Usage: python app.py <repo_name>")
