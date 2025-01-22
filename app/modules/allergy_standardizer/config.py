import os


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BATCH_SIZE = int(os.environ.get("ALLERGY_STD_BATCH_SIZE"))
MEDLM_REQUEST_BATCH_SIZE = int(os.environ.get("MEDLM_REQUEST_BATCH_SIZE", "5"))