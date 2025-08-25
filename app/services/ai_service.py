import os
from typing import cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_student(student):
    content = f"""
    Student: {student.full_name} 
    Absences: {student.absences},
    Notes: {student.notes or "No additional notes"}
"""
    messages = cast(list[ChatCompletionMessageParam], [
        {"role": "system", "content": "You are an assistant summarizing student performance."},
        {"role": "user", "content": f"Summarize this student:\n{content}"}
    ])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content

def summarize_student_with_question(question:str, context):

    messages = cast(list[ChatCompletionMessageParam], [
        {"role": "system", "content": "You are an assistant summarizing student performance."},
        {"role": "user", "content": f"Question:{question}\n\nNotes: \n"+ "\n".join(context)}
    ])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content