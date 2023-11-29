# Roadmap

## Todo

- Add a 'category' to the job description
  - This category modifies the type of prompt that is used to parse the skills from the job description itself but also from the CV
  - So we can focus more on certain 'styles' of jobs and decide what to extract.
    - Maybe in the future use a toggle to understand how much soft skills vs. hard skills to extract for each job description?
-

## User Flows

This is an API dedicated to offering the backend of a simple website to evaluate CV/resumes using LLMs.

For now I only have one user flow.

User flow 1
- Assume:
  - `job_id` (the ID of the job description to which the resume refers to) is already known and sent by the frontend
- User uploads the CV/resume in PDF form:
  - API loads the PDF to a PostgreSQL database
- Once the pdf is loaded a process needs to be triggered
  - API starts the openai service flow:
    - Converts the PDF into JPG and saves it
    - Converts each JPG into text and saves it
    - Retrieves the correct job description
