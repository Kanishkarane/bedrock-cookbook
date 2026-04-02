from strands import Agent,tool

@tool
def get_current_year():
    from datetime import datetime
    return datetime.now().year

@tool
def calculate(expression:str)-> float:
    allowed_chars = "0123456789+-*/()."
    if not all(char in allowed_chars for char in expression):
        return "Invalid Expression"
    return eval(expression)

agent = Agent(model="amazon.nova-pro-v1:0",tools=[get_current_year, calculate])

print("Question 1: What year is it?")
response1 = agent("What year is it?")
print(f"Answer: {response1}\n")

print("Question 2: What's 15% of 850?")
response2 = agent("What's 15% of 850?")
print(f"Answer: {response2}\n")

print("Question 3: Just say hello")
response3 = agent("Just say hello")
print(f"Answer: {response3}\n")