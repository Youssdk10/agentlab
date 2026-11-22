import os

from openai import OpenAI

from agentlab.tools import TOOL_SCHEMAS

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

raw = client.chat.completions.with_raw_response.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": "What's the status of order 101?"}],
    tools=TOOL_SCHEMAS,
)

response = raw.parse()
print(response.choices[0].message)

for name, value in raw.headers.items():
    if name.lower().startswith(("x-ratelimit", "retry-after")):
        print(name, value)