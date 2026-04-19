# from groq import Groq
# from db.config import settings
# from handlers.redis_handlers import *

# async def send_request_dialogue(system_prompt: str, text:str):
#     client = Groq(api_key=settings.GROQ_API_KEY)

#     completion = client.chat.completions.create(
#         model="openai/gpt-oss-120b",
#         messages=[
#             {
#                 "role": "system",
#                 "content":f"{system_prompt}"
#             },
#             {
#                 "role": "user",
#                 "content": f"{text}"
#             }
#         ],
#         temperature=1,
#         max_completion_tokens=800,
#         top_p=1,
#         reasoning_effort="low",
#         stream=True,
#         stop=None
#     )

#     for chunk in completion:
#         print(chunk.choices[0].delta.content or "", end="")


# async def generate_sentences(tg_ig: int):
#     session = 