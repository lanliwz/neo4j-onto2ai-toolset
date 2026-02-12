---
description: add a new LLM model to the Onto2AI Model Manager
---

1. **Update Backend Model List**
   Modify `model_manager/api/schemas.py` to include the new model's official technical name in the `AVAILABLE_LLMS` list.
   
2. **Add CLI Shorthand**
   In `model_manager/main.py`, add a case for the new model shorthand in the `main` function to map it to the official technical name. Update the `--model` argument's `choices` list.

3. **Prettify Frontend Label**
   In `model_manager/static/js/app.js`, update the logic that populates the LLM selector to provide a human-friendly label for the new model (e.g., mapping `gemini-3-flash-preview-001` to "Gemini 3 Flash Preview").

4. **Verify Connectivity**
   Start the server with the new model using the shorthand (e.g., `python main.py --model mymodel`) and verify the selector correctly displays the pretty name and that chat functionality works.
