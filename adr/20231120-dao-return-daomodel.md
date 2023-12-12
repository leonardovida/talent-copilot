# DB DAO models always return DAOModel Classes

## Context and Problem Statements

The DAO functions classes need to return something to the API functions that called them. The APIs talk to the frontend and to the backend using DTO classes.
We need to decide whether the DAO functions return DAOModels or DTOModels

## Considered Options

- DAOModels: more complex models resebling the exact types and classes we have in the DB
- DTOModels: much simpler models resembling what is sent to and from the frontend

## Decision Outcome

The DAO classes return DAOModels which will then get converted later in the stack (e.g. at the API level).
This means that a DAOClass function gets:
- input: DTOInput
- output: DTOOuput

And that an API function gets:
- input: DTOInput
- output: DTOOutput
