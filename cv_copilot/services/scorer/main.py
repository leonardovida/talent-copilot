# # One Evaluation at the time
# # Get the evalutation JSON from database

# NOT NOW BUT LATER
# # Get the weights from either settings or frontend (if available)
# # - One weight for required-skills
# #    - One weight for soft-skills
# #    - One weight for hard skills
# # - One weight for the nice-to-have skills
# #    - One weight for soft-skills
# #    - One weight for hard skills


# # Compute YES/NO/PARTIAL per section
# # Apply weights to get score
# # Save score to database

# # Create endpoint that retreives score for a given evaluation/PDF

# # On frontend we need to have

# # In your scoring service file
# from settings import settings


# async def compute_score(pdf_id: int) -> float:
#     # TODO: we could in theory run the scorer already with widely
#     # differing weights and then surface the best CV across the board
#     evaluation = await get_evaluation_json_from_db(pdf_id)

#     # Compute score based on evaluation and weights
#     score = 0.0
#     for category, skills in evaluation.items():
#         for skill_type, results in skills.items():
#             for result in results:
#                 score += compute_individual_score(
#                     result, settings.weights[category][skill_type]
#                 )

#     # Save score to database
#     await save_score_to_db(pdf_id, score)

#     return score


# def compute_individual_score(result: str, weight: float) -> float:
#     # Convert YES/NO/PARTIAL to numerical values and apply weight
#     score_map = {"YES": 1, "PARTIAL": 0.5, "NO": 0}
#     return score_map.get(result, 0) * weight
