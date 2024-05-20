from flask import Flask, request, jsonify, session
from openai import OpenAI
import time
import nbformat

app = Flask(__name__)

client = OpenAI(api_key="")

# Create a vector store caled "Lecture Notes"
vector_store = client.beta.vector_stores.create(name="Lecture Notes")
 
# Ready the files for upload to OpenAI
file_paths = []
for i in range(1,11):
    file_paths.append("text_notes/"+str(i)+".txt")
file_streams = [open(path, "rb") for path in file_paths]
 
# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)

assistant = client.beta.assistants.create(
    name="Code Reviewer",
    instructions="As a code reviewer, you are given a list of ordered lecture notes in a vector store. Your context is you will be given a number represent the order of the lecture notes in the vector store that you can use its concepts and concepts in the previous lecture notes in order inside the vector store in your code review. Provide feedback for the codes attempt done for all the questions by the students in the code file based on the set of question in the question file using only the concepts in the context. Avoid introducing new concepts such as error handling if they are not included in the notes. Structure your generated feedback for each question under this format: 1) textual feedback (is solution good, is code efficient, any problems to watch out for, etc.), 2) alternative solution, 3) alternative approach (without solution). All of these feedback provided MUST only use the satisfied lecture notes' content in the context. DO NOT ask user for feedback preference for other remaining questions, give ALL the feedbacks for ALL the questions.",
    tools=[{"type": "file_search"},
            {"type": "code_interpreter"}],
    tool_resources={
        "file_search": {
            "vector_store_ids": [vector_store.id]
        }
    },
    # model="gpt-3.5-turbo-0125",
    model="gpt-4-turbo"
)

@app.route('/')
def home():
    return 'Welcome to the API!'

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content

# @app.route('/upload_notes', methods=['POST'])
# def upload_notes():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     # Optionally, check for file type
#     if not file.filename.endswith('.ipynb'):
#         return jsonify({'error': 'Invalid file type, expected .ipynb'}), 400

#     # Read the file data into memory (if the file is not too large)
#     file_data = file.read()

#     # Now pass the file data to OpenAI
#     note = client.files.create(file=file_data, purpose='assistants')
#     session['note_id'] = note.id  # Store note id in session
#     return jsonify({'note_id': note.id})

# @app.route('/upload_exercise', methods=['POST'])
# def upload_exercise():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     # Read the file data into memory (if the file is not too large)
#     file_data = file.read()

#     # Now pass the file data to OpenAI
#     exercise = client.files.create(file=file_data, purpose='assistants')
#     session['exercise_id'] = exercise.id  # Store note id in session
#     return jsonify({'exercise_id': exercise.id})

# @app.route('/upload_code', methods=['POST'])
# def upload_code():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     # Optionally, check for file type
#     if not file.filename.endswith('.ipynb'):
#         return jsonify({'error': 'Invalid file type, expected .ipynb'}), 400

#     # Read the file data into memory (if the file is not too large)
#     file_data = file.read()

#     # Now pass the file data to OpenAI
#     student = client.files.create(file=file_data, purpose='assistants')
#     session['student_id'] = student.id  # Store note id in session
#     return jsonify({'student_id': student.id})

# @app.route('/get_code_id', methods=['GET'])
# def get_code_id():
#     student_id = session.get('student_id')
#     return student_id

@app.route('/review_code', methods=['POST'])
def review_code():
    data = request.get_json()
    prompt_text = data['prompt_text']
    week = data['week']
    exercise = data['exercise']
    student = data['student']
    # note_id = session.get('note_id')
    # exercise_id = session.get('exercise_id')
    # student_id = session.get('student_id')
    # print(exercise_id)
    # print(student_id)

    print(str(exercise))

    print(str(student))

    content_text = "You are a code reviewer for university students taking intro to programming classes. You are designed with a list of sorted lecture notes according to week number in the vector store in your file_search under tool_resources. The context is you can only use concept taught from week 1 till week " + str(week) + " in your feedback. Avoid introducing new concepts such as error handling if they are not included in the notes. The question: " + str(exercise) + ". The code attempt by student: " + str(student) + "Structure your generated feedback for each question under this format: 1) textual feedback (is solution good, is code efficient, any problems to watch out for, etc.), 2) alternative solution, 3) alternative approach (without solution). All of these feedback provided MUST only use the satisfied lecture notes' content in the context. DO NOT ask user for feedback preference for other remaining questions, give ALL the feedbacks for ALL the questions."
    # content_text = "List out the concepts of the weeks in the lecture notes from week 1 till week " + str(week)

    thread = client.beta.threads.create()
    # message = client.beta.threads.messages.create(
    #     thread_id=thread.id,
    #     role="user",
    #     content=f"You are limited to lecture note of order {note_order} and before in the vector store. You are giving code review for student's code attempt in a jupyner notebook file with id {student_id}, for the set of exercise file under a .docx file with id {exercise_id}. Provide feedback for the codes attempt done for all the questions by the students in the code file based on the set of question in the question file using only the concepts in the context. Avoid introducing new concepts such as error handling if they are not included in the notes. Structure your generated feedback for each question under this format: 1) textual feedback (is solution good, is code efficient, any problems to watch out for, etc.), 2) alternative solution, 3) alternative approach (without solution). All of these feedback provided MUST only use the satisfied lecture notes' content in the context. DO NOT ask user for feedback preference for other remaining questions, give ALL the feedbacks for ALL the questions.",
    #     attachments=[
    #         {
    #             "file_id": student_id,
    #             "tools": [{"type": "code_interpreter"}]
    #         }, 
    #         {
    #             "file_id": exercise_id,
    #             "tools": [{"type": "code_interpreter"}]
    #         }, 
    #     ]
    # )

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content_text,
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Provide the exact steps to solve the problems"
    )
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            # return jsonify({'error': run_status.last_error}), 500
            # Assuming run_status.last_error contains attributes like message or code
            if hasattr(run_status.last_error, 'message'):
                error_details = {
                    'error': 'Execution failed',
                    'message': run_status.last_error.message,  # Extract the message attribute
                    'code': getattr(run_status.last_error, 'code', 'Unknown')  # Example if there's a code attribute
                }
            else:
                error_details = {'error': 'Execution failed', 'details': str(run_status.last_error)}
            return jsonify(error_details), 500
        time.sleep(2)
    
    messages = client.beta.threads.messages.list(thread_id=thread.id)

     # Serialize messages properly
    serialized_messages = []
    for message in messages.data:
        # Manually extract and construct a serializable object
        message_data = {
            'role': message.role,
            'content': [{'type': content.type, 'text': content.text.value if content.text else None} for content in message.content]
        }
        serialized_messages.append(message_data)

    return jsonify(serialized_messages)

if __name__ == '__main__':
    app.run(debug=True)
