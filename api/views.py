from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
import json
from .serializers import AudioFileSerializer

import openai

# Create your views here.


def get_completion(prompt, model="gpt-3.5-turbo"):
    API_KEY = getattr(settings, "OPENAI_API_KEY", None)
    openai.api_key = API_KEY

    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def transcribe(file_path):
    API_KEY = getattr(settings, "OPENAI_API_KEY", None)
    model_id = "whisper-1"
    response = openai.Audio.transcribe(
        api_key=API_KEY, model=model_id, file=open(file_path, "rb"), language="ja"
    )
    return response.text


def correct_text(transcribed_text):
    prompt = f"""
    Your task is to proofread and correct text delimited by three backticks \ 
    and generate a conversation between the doctor and the client based on corrected text

    Maintain main content and avoid duplicate content for both doctors and clients.
    Use the following format:
    [doctor] ...
    [client] ...
    [doctor] ...

    ```{transcribed_text}```
    """
    response = get_completion(prompt)
    return response


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = AudioFileSerializer(data=request.data)

        if file_serializer.is_valid():
            audio = file_serializer.save()

            transcribed_text = transcribe(audio.file.name)
            corrected_text = correct_text(transcribed_text)

            data = {"fileName": audio.file.name, "text": corrected_text}

            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AiSummarize(APIView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        text = data.get("text", "")
        result = (
            self.summarize1(text)
            + self.summarize2(text)
            + self.summarize3(text)
            + self.summarize4(text)
            + self.summarize5(text)
            + self.summarize6(text)
        )

        data = {"text": result}

        return Response(data, status=status.HTTP_201_CREATED)

    def summarize1(self, transcribed_text):
        # 1. What a pet owner explains
        prompt = f"""
        Your task is to extract information from \ 
        a conversation between doctor and client.

        From the transcribed text below, delimited by triple quotes \ 
        extract the information relevant to what pet owners explain.

        ```{transcribed_text}```
        """

        response = get_completion(prompt)
        return "1. What a pet owner explains\n" + response

    def summarize2(self, transcribed_text):
        # 2. Regarding “pet owner”
        prompt = f"""
        Your task is to extract information relevant to pet owner from \ 
        a conversation between doctor and client.

        Focus on follow points:
        1. What do pet owner concerns on the most? 
        2. Pet owner's emotions, what does she care about?
        3. Is she satisfied with what she heard?
        4. Is she a new client or an old client?

        From the transcribed text below, delimited by triple quotes \ 
        extract the information relevant to above points.

        Keep the follow styles
        1)...
        2)...
        3)...
        
        ```{transcribed_text}```
        """

        response = get_completion(prompt)
        return "\n\n2. Regarding “pet owner\n" + response

    def summarize3(self, transcribed_text):
        # 3. Regarding “what they do”
        prompt = f"""
        Your task is to extract information relevant to what they do from \ 
        a conversation between doctor and client.

        Focus on follow points:
        1. In the medical inspections, what should to be tested, why is it necessary, the name/results of med testing?
        2. In the medical services or other things that they did to the pet animal, what they did, what happened?

        From the transcribed text below, delimited by triple quotes \ 
        extract the information relevant to above points and answer the follow questions.

        1. Was it the truth or was it a decision? (assertive content)
        2. Was it a mere discussion or undecided?
        3. Was it an explanation or a simple truthful explanation?
        4. Is it a plan or a result?

        Keep the follow styles
        1)...
        2)...
        3)...

        ```{transcribed_text}```
        """

        response = get_completion(prompt)
        return "\n\n3. Regarding “what they do\n" + response

    def summarize4(self, transcribed_text):
        # 4. Regarding “illness”
        prompt = f"""
        Your task is to extract information relevant to illness from \ 
        a conversation between doctor and client.

        Focus on follow points in illness:
        1. screening 
        2. suspicious disease (name, symptom) 
        3. diagnostic content 

        From the transcribed text below, delimited by triple quotes \ 
        extract the information relevant to above points and answer the follow questions.

        1. A specific disease/illness name?
        2. Was it preventive medical service like just a simple visit for a vaccination or nail clipping ?

        Keep the follow styles
        1)...
        2)...
        3)...

        ```{transcribed_text}```
        """

        response = get_completion(prompt)
        return "\n\n4. Regarding “illness”\n" + response

    def summarize5(self, transcribed_text):
        # 5.Regarding “plan”
        prompt = f"""
        Your task is to extract information relevant to plan from \ 
        a conversation between doctor and client.

        Focus on follow points in plan:
        1. medical treatment plan 
        2. schedule 
        3. next visit

        From the transcribed text below, delimited by triple quotes \ 
        extract the information relevant to above points and answer the follow questions.

        1. What is the plan(future schedule)?
        2. When is the ideally specific date?
        3. What is the conditions to move next like "if the white blood cell goes 00, then you can stop having antibiotic"?

        Keep the follow styles
        1)...
        2)...
        3)...

        ```{transcribed_text}```
        """

        response = get_completion(prompt)
        return "\n\n5.Regarding “plan”\n" + response

    def summarize6(self, transcribed_text):
        # 6. Regarding “prescription”
        prompt = f"""
        Your task is to extract information relevant to prescription from \ 
        a conversation between doctor and client.

        Focus on follow points in prescription:
        1. What is the name of medicine to dose and what is the purpose to dose?
        2. How long and how often should it be dosed?
        3. What is a repetitive prescription or new prescription?

        From the transcribed text below, delimited by triple quotes \ 
        extract the information relevant to above points and answer the follow questions.

        1. new prescription 
        2. repetitive prescription 
        3. increasing dose of medicine 
        4. decreasing dose of medicine 

        Keep the follow styles
        1)...
        2)...
        3)...

        ```{transcribed_text}```
        """

        response = get_completion(prompt)
        return "\n\n6. Regarding “prescription”\n" + response
