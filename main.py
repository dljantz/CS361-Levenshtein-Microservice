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
