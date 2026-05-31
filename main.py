from fastapi import FastAPI

# Initialize the application
app = FastAPI()


@app.get("")
def health_check():
    return {"status": "Microservice is online and listening."}


@app.get("/")
def levenshtein_wrapper(string1: str, string2: str):
    distance = levenshtein(string1, string2)

    return {
        "string1": string1,
        "string2": string2,
        "levenshtein distance": distance,
        "recommended forgiveness threshold": -1
    }


def levenshtein(string1: str, string2: str, cache=None) -> int:
    """
    Based on https://medium.com/@ethannam/understanding-the-levenshtein-distance-equation-for-beginners-c4285a5604f0
    """
    # edits are insertions, deletions, or replacements
    # if one of the strings is empty, just do max_length(string1, string2)
    # else, do recursive call: minimum of:
    #   lev(i-1, j) + 1
    #   lev(i, j-1) + 1
    #   lev(i-1, j-1) + 1(ai != bj)

    """
    Ok, so we are using dynamic programming.
    make a 2d grid, row and column quantities driven by string lengths
    iterate through with simple nested for loop
    do the piecewise function at each step, mimicking recursion
    fill in the grid as we go
    """

    return -1
