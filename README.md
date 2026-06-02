# CS361-Levenshtein-Microservice
## Description
Takes two string inputs and calculates the Levenshtein distance between them (the number of one-character edits necessary to make the strings equivalent). The service also provides a recommended "forgiveness threshold", the distance within which the response could be considered a misspelled correct answer.

## Calling the Microservice
Make an HTTP GET request to the microservice. Specify two strings.

Example:
```
https://cs361-levenshtein-microservice.onrender.com/?string1=hello&string2=shells
```

## Receiving Data
A JSON object will be returned.

Example:
```
{
  "string1": hello,
  "string2": shells,
  "levenshtein distance": 2
  "recommended forgiveness threshold" : 0
}
```
Note that the calculation of the forgiveness threshold is based on the assumption that the first string entered is the correct answer.