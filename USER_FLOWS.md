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

For this flow I need:
- How many endpoint from the API do I need?
- How is the flow of the PDF -> evaluation -> storage of the result?
- How do I trigger this sequence of event?
