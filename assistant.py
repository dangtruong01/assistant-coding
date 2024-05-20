from openai import OpenAI
from docx import Document
import time

client = OpenAI(
    #Paste in openai api key
    api_key = "",
)

# Upload notes with an "assistants" purpose
note = client.files.create(
  file=open("lecture_notes/3.ipynb", "rb"),
  purpose='assistants'
)
print(note)

# Upload student's code attempt with an "assistants" purpose
student = client.files.create(
  file=open("code_attempts_1/attempt3.ipynb", "rb"),
  purpose='assistants'
)
print(student)

# # Upload exercise with an "assistants" purpose
# exercise = client.files.create(
#   file=open("sample_exercises/exercise_1.docx", "rb"),
#   purpose='assistants'
# )
# print(exercise)

# def docx_to_text(path):
#     # Open the .docx file
#     doc = Document(path)
#     full_text = []
#     # Iterate through the paragraphs to extract text
#     for para in doc.paragraphs:
#         full_text.append(para.text)
#     # Combine all paragraphs into a single string
#     return '\n'.join(full_text)

# # Example usage
# text_content = docx_to_text("sample_exercises/exercise_1.docx")
# print(text_content)

# Get the file IDs
note_file_id = note.id
student_file_id = student.id

assistant = client.beta.assistants.create(
  name="Code Reviewer",
  instructions="You are a university students' code review assistant. You are given a note file as context of the concepts taught in class. I need you to base on only the concept mentioned in these notes, then read the code attempt done by the students and provide feedback for the students.",
  model="gpt-3.5-turbo",
  tools=[{"type": "code_interpreter"}],
  # tool_resources={
  #     "code_interpreter": {
  #         "file_ids": [note_file_id, student_file_id]
  #     }
  # }
)

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content=f"You received a lecture note as an input file for the context of the prompt with id {note_file_id}. By using only concepts mentioned in the notes given, provide feedback for the codes attempt done for all the questions by the students in the code file with id: {student_file_id}. Avoid introducing new concepts such as error handling if they are not included in the notes. Structure your generated feedback for each question under this format: 1) textual feedback (is solution good, is code efficient, any problems to watch out for, etc.), 2) alternative solution, 3) alternative approach (without solution). All of these feedback provided MUST only use the lecture notes' content. DO NOT ask user for feedback preference for other remaining questions, give ALL the feedbacks for ALL the questions.",
  file_ids=[note_file_id, student_file_id]
)

# WITHOUT STREAMING

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please provide the exact steps to solve the problems"
)

# Waits for the run to be completed. 
while True:
    run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, 
                                                   run_id=run.id)
    if run_status.status == "completed":
        break
    elif run_status.status == "failed":
        print("Run failed:", run_status.last_error)
        break
    time.sleep(2)  # wait for 2 seconds before checking again

# Parse the Assistant's Response to Print the Results
messages = client.beta.threads.messages.list(
    thread_id=thread.id
)

# Prints the messages with the latest message at the bottom
number_of_messages = len(messages.data)
print( f'Number of messages: {number_of_messages}')

with open('responses35.txt', 'w') as file:
    for message in reversed(messages.data):
        role = message.role  
        for content in message.content:
            if content.type == 'text':
                response = content.text.value 
                # print(f'\n{role}: {response}')
                file.write(f'\n{role}: {response}')
