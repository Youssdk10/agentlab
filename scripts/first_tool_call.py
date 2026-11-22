from ollama import chat

MODEL = "qwen3:4b"

def get_age(name:str) -> dict:
    fake_ages = {"Alice": 25, "Moussa" : 19, "Rama" : 15, "Youss": 30}
    return {"name": name, "age": fake_ages.get(name, "name not found")}

tools = [{
    "type": "function",
    "function": {
        "name": "get_age",
        "description": "Find the a person's age using their first name",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"Type": "String", "description": "first name of a person. e.g. 'Alice'"}
            },
            "required": ["name"],
        },

    },
}]

messages = [{"role": "user", "content": "How old is Youss"}]

response = chat(model=MODEL, messages=messages, tools=tools)
print("MODEL SAID:", response.message)

if response.message.tool_calls:
    messages.append(response.message)
    for call in response.message.tool_calls:
        name = call.function.name
        args = call.function.arguments        # a dict, e.g. {"order_id": 1042}
        result = get_age(**args)     # ** unpacks the dict into keyword args
        messages.append({"role": "tool", "tool_name": name, "content": str(result)})

    final = chat(model=MODEL, messages=messages, tools=tools)
    print("FINAL ANSWER:", final.message.content)
else:
    print("No tool call:", response.message.content)