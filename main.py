from fastapi import FastAPI

# Initialize the application
app = FastAPI()


@app.get("")
def health_check():
    return {"status": "Microservice is online and listening."}


@app.get("/")
def calculate_levenshtein_distance(string1: str, string2: str):
    return {
        "string1": string1,
        "string2": string2
    }


# 1. The Client sends an HTTP request to this URL endpoint
# The {user_input} part extracts info from the URL as a parameter
@app.get("/process/{user_input}")
def process_data(user_input: str):
    # 2. The microservice uses the parameter to inform its execution
    processed_string = user_input.upper()
    character_count = len(user_input)

    # 3. The microservice sends back the output
    # FastAPI automatically converts this Python dictionary into JSON format
    return {
        "original": user_input,
        "processed": processed_string,
        "length": character_count,
        "status": "success"
    }


@app.get("/subtract")
def subtract(num1: float, num2: float):
    """
    :param num1: Number to subtract from
    :param num2: Number to subtract by
    :return: dict describing inputs and output
    example call: https://cs361-add-subtract-microservice.onrender.com/subtract?num1=4&num2=1
    """
    difference = num1 - num2
    return {
        "num1": num1,
        "num2": num2,
        "difference": difference
    }


@app.get("/add")
def subtract(num1: float, num2: float):
    """
    :param num1: First number to add
    :param num2: Second number to add
    :return: dict describing inputs and output
    example call: https://cs361-add-subtract-microservice.onrender.com/add?num1=4&num2=1
    """
    sum = num1 + num2
    return {
        "num1": num1,
        "num2": num2,
        "sum": sum
    }
