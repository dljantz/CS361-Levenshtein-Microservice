# CS361-Levenshtein-Microservice
## Description
Takes two string inputs and calculates the Levenshtein distance between them (the number of one-character edits necessary to make the strings equivalent)

## Calling the Microservice
Make an HTTP GET request to the microservice, specifying either the "add" or "subtract" endpoint. Specify two numbers. For subtraction, the second number will be subtracted from the first number. For addition, the two numbers will be added together.

Example:
```https://cs361-levenshtein-microservice.onrender.com/?string1=hello&string2=shells```

## Receiving Data
A JSON object will be returned.

Addition example:
```
{
  "num1": 4,
  "num2": 1,
  "sum": 5
}
```

Subtraction example:
```
{
  "num1": 4,
  "num2": 1,
  "difference": 3
}
```