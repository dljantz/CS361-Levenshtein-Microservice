from fastapi import FastAPI

# Initialize the application
app = FastAPI()


@app.get("")
def health_check():
    return {"status": "Microservice is online and listening."}


@app.get("/")
def levenshtein_wrapper(string1: str, string2: str):
    distance = levenshtein(string1, string2)
    recommended_forgiveness = recommend_forgiveness(string1)

    return {
        "string1": string1,
        "string2": string2,
        "levenshtein distance": distance,
        "recommended forgiveness threshold": recommended_forgiveness
    }


def levenshtein(string1: str, string2: str) -> int:
    """
    Based on https://medium.com/@ethannam/understanding-the-levenshtein-distance-equation-for-beginners-c4285a5604f0
    returns the minimum number of single-character edits necessary to make two strings identical
    """
    cache = [[-1 for _ in range(len(string2) + 1)] for _ in range(len(string1) + 1)]
    for i in range(len(string1) + 1):
        for j in range(len(string2) + 1):
            # base case: if min(i,j) == 0, then do max(i,j) for this cell
            #   because it's just that many deletions
            if min(i, j) == 0:
                cache[i][j] = max(i, j)
            else:
                a = cache[i - 1][j] + 1
                b = cache[i][j - 1] + 1
                c = cache[i - 1][j - 1]
                if string1[i - 1] != string2[j - 1]:
                    c += 1
                result = min(a, b, c)
                cache[i][j] = result
    return cache[len(string1)][len(string2)]


def recommend_forgiveness(correct_answer) -> int:
    l = len(correct_answer)
    return l - (l * 8 // 10 + 1)
