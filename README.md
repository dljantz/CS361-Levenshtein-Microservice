# CS361-Levenshtein-Microservice
## Description
Takes two string inputs and calculates the Levenshtein distance between them (the number of one-character edits necessary to make the strings equivalent)

## Calling the Microservice
Make an HTTP GET request to the microservice. Specify two strings.

Example:
```https://cs361-levenshtein-microservice.onrender.com/?string1=hello&string2=shells```

## Receiving Data
A JSON object will be returned.

Example:
```
{
  "string1": hello,
  "string2": shells,
  "levenshtein distance": __
  "recommended forgiveness threshold" : __
}
```