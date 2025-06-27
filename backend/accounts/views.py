from rest_framework import generics, status
from .serializers import RegisterSerializer
from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView
from .serializers import SendOTPSerializer, ResetPasswordWithOTPSerializer
from django.views import View
from django.http import JsonResponse
from openai import OpenAI
import json
from .models import MCQTestResult, ClassSessionData
from .models import EssayResult
from .models import SubjectiveTestResult
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import SubjectiveQuestion, MCQQuestion
from .helper import parse_mcqs
import re
import requests
import logging
from django.conf import settings
import os
import logging
import docx
from PyPDF2 import PdfReader
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
#otp view
#class SendOTPView(CreateAPIView):
    #serializer_class = SendOTPSerializer
@method_decorator(csrf_exempt, name='dispatch')

def generate_otp(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

@method_decorator(csrf_exempt, name='dispatch')
class SendOTPView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return JsonResponse({"error": "Email is required"}, status=400)

            # ✅ Generate OTP
            otp = generate_otp()

            # ✅ Send OTP via email
            send_mail(
                subject="Your OTP for Password Reset",
                message=f"Your One-Time Password (OTP) is: {otp}",
                from_email="noreply@cssportal.com",
                recipient_list=[email],
                fail_silently=False,
            )

            # ✅ Store OTP in session (you can replace this with DB or cache)
            request.session["otp"] = otp
            request.session["otp_email"] = email

            return JsonResponse({"message": "OTP sent successfully to your email."})

        except Exception as e:
            print("OTP error:", str(e))  # optional for debugging
            return JsonResponse({"error": str(e)}, status=500)
class ResetPasswordWithOTPView(CreateAPIView):
    serializer_class = ResetPasswordWithOTPSerializer

#registerview
@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
        def post(self, request):
            try:
                data = json.loads(request.body)
                print(data)
                username = data.get("username")
                email = data.get("email")
                password = data.get("password")
                print("gwt")

                if not username or not email or not password:
                    return JsonResponse({"error": "Username, email, and password are required"}, status=400)
                print("not username")
                if User.objects.filter(username=username).exists():
                    return JsonResponse({"error": "Username already exists"}, status=400)
                print("not username")

                if User.objects.filter(email=email).exists():
                    return JsonResponse({"error": "Email already registered"}, status=400)
                print("user create")
                user = User.objects.create_user(username=username, email=email, password=password, first_name="test", last_name="last")

                return JsonResponse({
                    "message": "User registered successfully",
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email
                })

            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)



@method_decorator(csrf_exempt, name='dispatch')
#This model generate mcqs
class GenerateTestView(View):
    def post(self, request):
       # print("Testing breakpoint")
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
        )

        prompt = """
        You are an expert English language teacher preparing CSS exam content.


        Your task is to generate a total of **20 multiple-choice questions (MCQs)** based on English vocabulary. The questions should follow the official format of the CSS (Central Superior Services) exam of Pakistan.


        ---


        (a) Choose the word that is nearly most similar in meaning to the capitalized words. 
        [10 MCQs - Synonyms]


        Example format:
        partAQuestions:[
                           id: A1
                           question: UBIQUITOUS:
                           options:[Scarce, Present everywhere, Unique, Limited]
                           ]


        ---


        (b) Choose the word that is nearly most opposite in meaning to the capitalized words. 
        [10 MCQs - Antonyms]


        Example format:
        partBQuestions:[
                           id: B1
                           question: ESOTERIC
                           options: [Obvious, Understood by few, Extraneous, Common] 
                           ]


        ---


        Instructions:
        - Follow the same format exactly.
        - Do not explain the answers.
        - Make the vocabulary formal and CSS-level.
        - Make two separate lists for partAQuestions and partBQuestions
        - Only return the full list of 20 MCQs in clean, readable JSON format.
        """

        try:
            completion = client.chat.completions.create(
                model="deepseek/deepseek-r1-0528-qwen3-8b:free",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "CSS Success Path"
                }
            )

            raw_text = completion.choices[0].message.content
            clean_str = raw_text.strip().replace("```json\n", "").replace("```", "").strip()
            mcqs_test = json.loads(clean_str)
            mcqs_test = json.loads(clean_str)

            if "partAQuestions" in mcqs_test and "partBQuestions" in mcqs_test:
                part_a = mcqs_test["partAQuestions"]
                part_b = mcqs_test["partBQuestions"]
                #print("Part A MCQs:", len(part_a))
                #print("Part B MCQs:", len(part_b))
            else:
                print("Missing keys! Got:", mcqs_test.keys())

            return JsonResponse({"mcqs": mcqs_test}, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


#this model generate essay
@method_decorator(csrf_exempt, name='dispatch')
class GenerateEssayTestView(View):
    def post(self, request):

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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"
        )

        prompt = """
You are a CSS (Central Superior Services) English examiner in Pakistan.

Your task is to generate **10 original, formal, and thought-provoking essay topics** suitable for the CSS English Essay Paper.

Instructions:
- Topics should reflect CSS exam standards
- Topics should cover diverse themes like politics, education, ethics, society, technology, philosophy, and environment
- Avoid casual or overly simple topics
- Each topic should be 8–15 words long
- Do NOT write the essays — only list the topics
- Format the response as a numbered list

Return only the list of topics.
"""


        try:
            completion = client.chat.completions.create(
                model="deepseek/deepseek-r1-0528-qwen3-8b:free",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,  # ✅ Added max token limit here
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "CSS Success Path"
                }
            )

            content = completion.choices[0].message.content
            # Extract lines starting with number + dot
            topics = re.findall(r'\d+\.\s+(.*)', content)

            return JsonResponse({"alltopics":topics}, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)



#this model used for subjective test generation
def generate_css_subjective_prompt():
    return """
You are an expert paper setter for the CSS English (Precis & Composition) exam.

Your task is to generate a full **Subjective Test (Part-II)**, containing high-quality CSS-style questions similar to the official paper.

Include the following sections, in order:

1. Create the Precis Writing section as follows:
   "section": "Precis Writing",
   "id": 1,
   "marks": Please add the marks as integer for this section.
   "Question":Provide a ~250-word paragraph for precis. Do not write the precis — only provide the paragraph for the student to summarize.

2. Create the Reading Comprehension section as follows:
   "section": "Reading Comprehension",
   "id": 2,
   "marks": Please add the marks as integer for this section.
   "Question": Provide a ~300-word English passage as question,
   "sub_section":5 short questions with sub_id, marks, Question keys


3. Create the Grammar Correction section as follows:
   "section": "Grammar Correction",
   "id": 3,
   "marks": Please add the marks as integer for this section.
   "Question":Give 5 grammatically incorrect sentences. Ask the student to correct them.


4. Create the Sentence Construction section as follows:
   "section": "Sentence Construction",
   "id": 4,
   "marks": Please add the marks as integer for this section.
   "Question":Provide 5 short phrases or expressions. Ask the student to use each one in their own sentence.

5. Create the Vocabulary – Analogies/Synonyms/Antonyms section as follows:
   "section": "Vocabulary – Analogies/Synonyms/Antonyms",
   "id": 5,
   "marks": Please add the marks as integer for this section.
   "Question": Give:
   - 5 analogy questions (A:B :: C:__ format)
   - 5 pairs of words to be matched (synonyms or antonyms)


6. Create the Translation section as follows:
   "section": "Translation",
   "id": 6,
   "marks": Please add the marks as integer for this section.
   "Question":Give 2 simple Urdu sentences to be translated into English.

Formatting rules:
- Number all questions
- Use clear headings for each section
- Do NOT provide answers — only the questions
Do not include any text, explanations, Markdown formatting, or backticks. 
Return ONLY the JSON.

"""


def transform_json(txt):
    # Split by question blocks
    blocks = txt.strip().split('\n\n---\n\n')
    print(blocks)
    questions = []

    for block in blocks:
        # Match ID, title, and marks
        header_match = re.search(r'\*\*(\d+)\.\s*(.*?)\s*\((\d+)\s*Marks\)\*\*', block, re.DOTALL)

        if header_match:
            q_id = int(header_match.group(1))
            title = header_match.group(2).strip()
            marks = int(header_match.group(3))

            # Extract the description after the matched header
            parts = re.split(r'\*\*\d+\.\s*.*?\(\d+\s*Marks\)\*\*', block, maxsplit=1, flags=re.DOTALL)
            description = parts[1].strip() if len(parts) > 1 else ""

            questions.append({
                "id": q_id,
                "marks": marks,
                "title": title,
                "description": description
            })
            print(questions)
    return json.dumps(questions, indent=2)


@method_decorator(csrf_exempt, name='dispatch')
class GenerateSubjectiveTestView(View):
    def post(self, request):
        prompt = generate_css_subjective_prompt()

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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"
        )

        try:
            completion = client.chat.completions.create(
                model="deepseek/deepseek-r1-0528-qwen3-8b:free",
                messages=[{"role": "user", "content": prompt}],
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "CSS Success Path"
                }
            )

            content = completion.choices[0].message.content
            clean_str = content.strip().replace("```json\n", "").replace("```", "").strip()
            subjective_test = json.loads(clean_str)
            return JsonResponse({"subjective_test": subjective_test}, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

#mcqs feedback
def generate_mcq_feedback_prompt(mcq_data):
    prompt = """
You are an AI evaluator for CSS MCQ tests.

Evaluate the following multiple-choice questions.

Instructions:
- For each question, indicate if the student's selected option is correct.
- Include the correct answer and a short explanation (if incorrect).
- At the end, return the total score, total questions, percentage, and overall performance rating:
  - Excellent (90-100%)
  - Good (70-89%)
  - Average (50-69%)
  - Needs Improvement (<50%)

👉 Output Format (IMPORTANT):
Return the entire response as JSON:
{
  "results": [
    {
      "question": "...",
      "selected_option": "A",
      "correct_answer": "B",
      "is_correct": false,
      "explanation": "..."
    },
    ...
  ],
  "score": 7,
  "total": 10,
  "percentage": 70,
  "performance": "Good"
}

Now evaluate:
"""
    for i, item in enumerate(mcq_data, 1):
        prompt += f"""
{i}. Question: {item['question']}
Options: {item['options']}
Correct Answer: {item['correct_answer']}
Student Selected: {item['selected_option']}
"""
    return prompt


class EvaluateMCQsAIView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            answers = data.get("answers", [])
        except Exception:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Prepare prompt
        mcq_data = []
        for ans in answers:
            try:
                question = MCQQuestion.objects.get(id=ans["question_id"])
                mcq_data.append({
                    "question": question.question_text,
                    "options": question.options,
                    "correct_answer": question.correct_answer,
                    "selected_option": ans["selected_option"]
                })
            except MCQQuestion.DoesNotExist:
                continue

        prompt = generate_mcq_feedback_prompt(mcq_data)

        # AI call
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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"
        )

        try:
            completion = client.chat.completions.create(
                model="deepseek/deepseek-r1-0528-qwen3-8b:free",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "CSS Success Path"
                }
            )

            response_text = completion.choices[0].message.content

            # ✅ Try parsing AI response as JSON
            try:
                response_data = json.loads(response_text)
                score = response_data["score"]
                total = response_data["total"]
                percentage = response_data["percentage"]
                performance = response_data["performance"]

                # Replace with real logged-in user in production
                user = request.user if request.user.is_authenticated else User.objects.get(username="testuser")

                # ✅ Save to DB
                MCQTestResult.objects.create(
                    user=user,
                    subject="English",  # You can make this dynamic too
                    score=score,
                    total_questions=total,
                    percentage=percentage,
                    performance=performance
                )

                return JsonResponse(response_data, safe=False)

            except Exception as parse_error:
                return JsonResponse({"error": "AI response could not be parsed", "raw_response": response_text}, status=500)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

#Essay feedback
def generate_essay_evaluation_prompt(topic, essay):
    return f"""
You are a CSS essay evaluator.

Below is a student's essay for the topic:

**{topic}**

Essay:
{essay}

Evaluate it and return this JSON format:

{{
  "score": 33,
  "performance": "Good",
  "feedback": "Well-structured, but introduction was weak. Improve transitions."
}}

Give honest, constructive feedback as if it's a real CSS paper. Only return the JSON.
"""


@method_decorator(csrf_exempt, name='dispatch')
class EvaluateEssayView(View):
    def post(self, request):
        print("evaluate")
        topic = request.POST.get("topic")
        essay = request.POST.get("essay")
        print(topic)
        if not topic or not essay:
            return JsonResponse({"error": "Topic and essay are required"}, status=400)

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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"
        )

        prompt = generate_essay_evaluation_prompt(topic, essay)

        try:
            completion = client.chat.completions.create(
                model="deepseek/deepseek-r1-0528-qwen3-8b:free",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "CSS Success Path"
                }
            )

            # Parse AI JSON
            try:
                result_json = json.loads(completion.choices[0].message.content)

                # Get user
                user = request.user if request.user.is_authenticated else User.objects.get(username="testuser")

                # Save to DB
                EssayResult.objects.create(
                    user=user,
                    topic=topic,
                    essay_text=essay,
                    score=result_json["score"],
                    performance=result_json["performance"],
                    feedback=result_json["feedback"]
                )

                return JsonResponse(result_json, safe=False)

            except Exception as parse_error:
                return JsonResponse({
                    "error": "Could not parse AI response as JSON",
                    "raw_response": completion.choices[0].message.content
                }, status=500)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


#subjective feedback
def generate_subjective_feedback_prompt(test_title, answers):
    return f"""
You are a CSS subjective test examiner.

Below is a student's response to the CSS English subjective test titled: **{test_title}**.

Student's Answer:
{answers}

Instructions:
- Evaluate each section (Comprehension, Precis, Grammar, Vocabulary, etc.)
- Give brief feedback
- Assign a score out of 40
- Label the performance as:
  - Excellent (35–40)
  - Good (28–34)
  - Average (20–27)
  - Needs Improvement (<20)

👉 Return the result strictly in this JSON format:

{{
  "score": 33,
  "performance": "Good",
  "feedback": "Comprehension and grammar strong. Translation weak. Improve sentence construction."
}}

Do not include explanations. Only return valid JSON.
"""


class EvaluateSubjectiveTestView(View):
    def post(self, request):
        test_title = request.POST.get("test_title")
        user_answers = request.POST.get("answers")

        if not test_title or not user_answers:
            return JsonResponse({"error": "Missing test_title or answers"}, status=400)

        # DeepSeek AI Client
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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"
        )

        prompt = generate_subjective_feedback_prompt(test_title, user_answers)

        try:
            completion = client.chat.completions.create(
                model="deepseek/deepseek-r1-0528-qwen3-8b:free",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "CSS Success Path"
                }
            )

            content = completion.choices[0].message.content

            try:
                feedback_json = json.loads(content)

                user = request.user if request.user.is_authenticated else User.objects.get(username="testuser")

                SubjectiveTestResult.objects.create(
                    user=user,
                    test_title=test_title,
                    user_answers=user_answers,
                    ai_feedback=feedback_json["feedback"],
                    score=feedback_json["score"],
                    performance=feedback_json["performance"]
                )

                return JsonResponse(feedback_json, safe=False)

            except Exception:
                return JsonResponse({
                    "error": "AI response could not be parsed as JSON",
                    "raw": content
                }, status=500)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


#admin dashboard summary
@method_decorator(csrf_exempt, name='dispatch')
class AdminDashboardSummaryView(View):
    def get(self, request):
        return JsonResponse({
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "pending_requests": User.objects.filter(is_active=False).count(),
        })


#user management
@method_decorator(csrf_exempt, name='dispatch')
class UserManagementView(View):
    def get(self, request):
        users = list(User.objects.values("id", "username", "email", "is_active", "date_joined"))
        return JsonResponse({"users": users})

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON. Must be application/json"}, status=400)
    def put(self, request):
        data = json.loads(request.body)
        user = User.objects.get(id=data["id"])
        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        user.is_active = data.get("is_active", user.is_active)
        user.save()
        return JsonResponse({"message": "User updated"})

    def delete(self, request):
        data = json.loads(request.body)
        User.objects.get(id=data["id"]).delete()
        return JsonResponse({"message": "User deleted"})


#subject management
@method_decorator(csrf_exempt, name='dispatch')
class SubjectManagementView(View):
    def get(self, request):
        subjects = list(Subject.objects.values("id", "name"))
        return JsonResponse({"subjects": subjects})

    def post(self, request):
        data = json.loads(request.body)
        subject = Subject.objects.create(name=data["name"])
        return JsonResponse({"message": "Subject created", "id": subject.id})

    def put(self, request):
        data = json.loads(request.body)
        subject = Subject.objects.get(id=data["id"])
        subject.name = data["name"]
        subject.save()
        return JsonResponse({"message": "Subject updated"})

    def delete(self, request):
        data = json.loads(request.body)
        Subject.objects.get(id=data["id"]).delete()
        return JsonResponse({"message": "Subject deleted"})

#question management
@method_decorator(csrf_exempt, name='dispatch')
class QuestionManagementView(View):
    def get(self, request):
        questions = list(MCQQuestion.objects.values("id", "subject", "question_text", "correct_answer"))
        return JsonResponse({"questions": questions})

    def post(self, request):
        data = json.loads(request.body)
        question = MCQQuestion.objects.create(
            subject=data["subject"],
            question_text=data["question_text"],
            options=data["options"],
            correct_answer=data["correct_answer"]
        )
        return JsonResponse({"message": "Question created", "id": question.id})

    def put(self, request):
        data = json.loads(request.body)
        question = MCQQuestion.objects.get(id=data["id"])
        question.subject = data.get("subject", question.subject)
        question.question_text = data.get("question_text", question.question_text)
        question.options = data.get("options", question.options)
        question.correct_answer = data.get("correct_answer", question.correct_answer)
        question.save()
        return JsonResponse({"message": "Question updated"})

    def delete(self, request):
        data = json.loads(request.body)
        MCQQuestion.objects.get(id=data["id"]).delete()
        return JsonResponse({"message": "Question deleted"})


#chatbot views

@method_decorator(csrf_exempt, name='dispatch')
class ChatbotView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            if not user_message:
                return JsonResponse({"error": "Message is required"}, status=400)

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key="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"
            )

            system_prompt = """
You are an intelligent CSS exam chatbot assistant. You support two functions:
1. 🧭 User Guidance — Help users navigate the test system, explain how to prepare, how to take MCQs, essays, and subjective tests.
2. 📝 Test Generation — If the user asks to generate a test (e.g., "generate MCQs", "give me essay", "subjective practice"), then generate a small CSS-style test using your knowledge.

Use a helpful, concise, and formal tone.

Always return only the answer or the test content.
"""

            completion = client.chat.completions.create(
                model="deepseek/deepseek-r1-0528-qwen3-8b:free",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=800,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "CSS Success Path Chatbot"
                }
            )

            response = completion.choices[0].message.content
            return JsonResponse({"reply": response}, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# evaluate test (MCQ, Essay, or Subjective - only one type at a time)
# views.py


logger = logging.getLogger(__name__)

AI_Model_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct:free"

def extract_text_from_file(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[-1].lower()
    if ext == '.txt':
        return uploaded_file.read().decode('utf-8')
    elif ext == '.pdf':
        reader = PdfReader(uploaded_file)
        return " ".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif ext == '.docx':
        doc = docx.Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    return ""

@csrf_exempt
def evaluate_test(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST requests are allowed."}, status=405)

    try:
        # Check for uploaded file
        if request.FILES.get("file"):
            uploaded_file = request.FILES["file"]
            extracted_text = extract_text_from_file(uploaded_file)
            if not extracted_text:
                return JsonResponse({"error": "File uploaded but text could not be extracted."}, status=400)

            # Treat uploaded file as a single subjective question
            data = {
                "questions": [{
                    "type": "subjective",
                    "question": "Evaluate this descriptive answer for CSS subjective exam.",
                    "answer": extracted_text
                }]
            }
        else:
            try:
                body_unicode = request.body.decode('utf-8')
                data = json.loads(body_unicode)
            except Exception:
                return JsonResponse({"error": "Invalid JSON or empty body."}, status=400)

        questions_list = data.get("questions", [])

        if not questions_list and data.get("question") and data.get("answer"):
            questions_list = [ {
                "type": data.get("type", "short"),
                "question": data.get("question"),
                "answer": data.get("answer"),
                "options": data.get("options", []),
                "correct_answer": data.get("correct_answer")
            }]

        if not questions_list:
            return JsonResponse({"error": "No questions or answers provided."}, status=400)

        api_key = getattr(settings, 'MODEL_API_KEY', None)
        if not api_key:
            return JsonResponse({"error": "API key not configured."}, status=500)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        results = []
        score_by_type = {
            "mcq": {"scored": 0, "total": 0},
            "essay": {"scored": 0, "total": 0},
            "short": {"scored": 0, "total": 0},
            "subjective": {"scored": 0, "total": 0}
        }

        for item in questions_list:
            q_type = item.get("type", "short").lower()
            question = item.get("question", "").strip()
            answer = item.get("answer", "").strip()
            options = item.get("options", [])
            correct_answer = item.get("correct_answer")

            if not question or not answer:
                continue

            if q_type == "mcq":
                options_text = "\n".join(options)
                prompt = f"""
Evaluate the following MCQ.

Question: {question}

Options:
{options_text}

Student's Answer: {answer}
Correct Answer: {correct_answer}

Return:
Correct: Yes or No
Explanation: One line
Score: 1 or 0

Format:
Correct: ...
Explanation: ...
Score: ...
"""
            elif q_type == "subjective":
                prompt = f"""
You are an examiner evaluating a subjective descriptive answer from a CSS English exam.

Question: {question}

Student's Answer: {answer}

Give feedback and score out of 20. Format strictly as:
Feedback: ...
Score: ...
"""
            else:
                prompt = f"""
Evaluate the student's answer briefly.

Question: {question}

Student's Answer: {answer}

Give only:
1. A one-line feedback.
2. A score out of 10.

Format:
Feedback: ...
Score: ...
"""

            payload = {
                "model": DEFAULT_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
            }

            try:
                response = requests.post(AI_Model_API_URL, headers=headers, json=payload, timeout=15)
                response.raise_for_status()
                result = response.json()
                ai_text = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

                score = 0
                feedback = "No feedback"

                if q_type == "mcq":
                    correct_match = re.search(r"Correct:\s*(Yes|No)", ai_text, re.IGNORECASE)
                    explanation_match = re.search(r"Explanation:\s*(.*)", ai_text)
                    score_match = re.search(r"Score:\s*(\d+)", ai_text)

                    score = int(score_match.group(1)) if score_match else 0
                    feedback = explanation_match.group(1).strip() if explanation_match else "No feedback"

                    score_by_type["mcq"]["total"] += 1
                    score_by_type["mcq"]["scored"] += score

                    results.append({
                        "type": "mcq",
                        "question": question,
                        "user_answer": answer,
                        "correct_answer": correct_answer,
                        "ai_feedback": feedback,
                        "correct": correct_match.group(1).strip() if correct_match else None,
                        "score": score
                    })

                elif q_type == "subjective":
                    feedback_match = re.search(r"Feedback:\s*(.*)", ai_text)
                    score_match = re.search(r"Score:\s*(\d+)", ai_text)

                    score = int(score_match.group(1)) if score_match else 0
                    feedback = feedback_match.group(1).strip() if feedback_match else "No feedback"

                    score_by_type["subjective"]["total"] += 20
                    score_by_type["subjective"]["scored"] += score

                    results.append({
                        "type": "subjective",
                        "question": question,
                        "user_answer": answer,
                        "ai_feedback": feedback,
                        "score": score
                    })

                else:
                    feedback_match = re.search(r"Feedback:\s*(.*)", ai_text)
                    score_match = re.search(r"Score:\s*(\d+)", ai_text)

                    score = int(score_match.group(1)) if score_match else 0
                    feedback = feedback_match.group(1).strip() if feedback_match else "No feedback"

                    score_by_type[q_type]["total"] += 10
                    score_by_type[q_type]["scored"] += score

                    results.append({
                        "type": q_type,
                        "question": question,
                        "user_answer": answer,
                        "ai_feedback": feedback,
                        "score": score
                    })

            except Exception as e:
                logger.error(f"Error processing question: {e}")
                results.append({
                    "question": question,
                    "user_answer": answer,
                    "ai_feedback": "Error from AI or network.",
                    "score": None
                })

        attempted_type = next((k for k, v in score_by_type.items() if v["total"] > 0), None)

        if attempted_type:
            scored = score_by_type[attempted_type]["scored"]
            total = score_by_type[attempted_type]["total"]
            percentage = round((scored / total) * 100, 2) if total > 0 else 0

            return JsonResponse({
                "test_type": attempted_type,
                "user_score": scored,
                "total_score_of_test": total,
                "percentage": percentage,
                "feedback": results
            })

        return JsonResponse({"error": "Could not determine test type."}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)






#admin-register-view
@method_decorator(csrf_exempt, name='dispatch')
class adminRegisterView(View):
        def post(self, request):
            try:
                data = json.loads(request.body)
                print(data)
                username = data.get("username")
                email = data.get("email")
                password = data.get("password")
                print("gwt")

                if not username or not email or not password:
                    return JsonResponse({"error": "Username, email, and password are required"}, status=400)
                print("not username")
                if User.objects.filter(username=username).exists():
                    return JsonResponse({"error": "Username already exists"}, status=400)
                print("not username")

                if User.objects.filter(email=email).exists():
                    return JsonResponse({"error": "Email already registered"}, status=400)
                print("user create")
                user = User.objects.create_user(username=username, email=email, password=password, first_name="test", last_name="last")

                return JsonResponse({
                    "message": "Admin User registered successfully",
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email
                })

            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)



from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate
import json
@method_decorator(csrf_exempt, name='dispatch')
class AdminLoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return JsonResponse({"error": "Username and password are required"}, status=400)

            user = authenticate(username=username, password=password)

            if user is not None:
                return JsonResponse({
                    "message": "Login successful",
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email
                })
            else:
                return JsonResponse({"error": "Invalid username or password"}, status=401)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)




#videoupload



# views.py
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from .models import Video

@method_decorator(csrf_exempt, name='dispatch')
class VideoUploadView(View):
    def post(self, request):
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        video_file = request.FILES.get('video_file')

        if not title or not video_file:
            return JsonResponse({"error": "Title and video file are required."}, status=400)

        video = Video.objects.create(
            title=title,
            description=description,
            video_file=video_file,
            uploaded_at=timezone.now()
        )

        return JsonResponse({
            "message": "Video uploaded successfully",
            "video_id": video.id,
            "title": video.title,
            "file_url": video.video_file.url
        }, status=201)



class VideoListView(View):
    def get(self, request):
        videos = Video.objects.all().order_by('-uploaded_at')
        data = [
            {
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "file_url": video.video_file.url,
                "uploaded_at": video.uploaded_at
            }
            for video in videos
        ]
        return JsonResponse(data, safe=False)



@method_decorator(csrf_exempt, name='dispatch')
class VideoDeleteView(View):
    def delete(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id)
            video.video_file.delete()  # Delete the actual file
            video.delete()             # Delete the database record
            return JsonResponse({"message": "Video deleted successfully."}, status=200)
        except Video.DoesNotExist:
            return JsonResponse({"error": "Video not found."}, status=404)








from django.views import View
from django.http import JsonResponse
from django.db import models
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import json


# --- Model: ClassSession ---
class ClassSession(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    meet_link = models.URLField(help_text="Google Meet link")
    scheduled_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.scheduled_at}"


from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class VideoDeleteView(View):
    def delete(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id)
            video.video_file.delete()  # Remove file from storage
            video.delete()             # Remove record from DB
            return JsonResponse({"message": "Video deleted successfully."}, status=200)
        except Video.DoesNotExist:
            return JsonResponse({"error": "Video not found."}, status=404)


# --- View: API to Upload Meet Link ---
@method_decorator(csrf_exempt, name='dispatch')
class UploadMeetLinkView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            title = data.get("title")
            description = data.get("description", "")
            meet_link = data.get("meet_link")
            scheduled_at_str = data.get("scheduled_at")

            # Validate required fields
            if not title or not meet_link or not scheduled_at_str:
                return JsonResponse({"error": "title, meet_link, and scheduled_at are required."}, status=400)

            # Parse datetime
            scheduled_at = parse_datetime(scheduled_at_str)
            if not scheduled_at:
                return JsonResponse({"error": "Invalid datetime format for scheduled_at."}, status=400)

            # Create and save
            session = ClassSession.objects.create(
                title=title,
                description=description,
                meet_link=meet_link,
                scheduled_at=scheduled_at,
                created_at=timezone.now()
            )

            return JsonResponse({
                "message": "Meet link uploaded successfully",
                "session_id": session.id,
                "title": session.title,
                "meet_link": session.meet_link,
                "scheduled_at": session.scheduled_at
            }, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ClassSessionData
from .serializers import ClassSessionDataSerializer

class MeetLinksListView(APIView):
    def get(self, request):
        sessions = ClassSession.objects.all().order_by('-scheduled_at')
        serializer = ClassSessionDataSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import ClassSessionData

@method_decorator(csrf_exempt, name='dispatch')
class DeleteClassSessionView(View):
    def delete(self, request, session_id):
        try:
            session = ClassSession.objects.get(id=session_id)
            session.delete()
            return JsonResponse({'message': 'Session deleted successfully.'}, status=200)
        except ClassSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found.'}, status=404)

