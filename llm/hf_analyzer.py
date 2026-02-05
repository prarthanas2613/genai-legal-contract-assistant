from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load model and tokenizer once (for performance)
MODEL_NAME = "google/flan-t5-base"  # or "google/flan-t5-small" if low RAM
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def explain_clause(clause: str) -> str:
    """
    Explain a contract clause in simple business language, mention risk and one suggestion.
    Runs locally without API.
    """

    # ✅ Simplified prompt for cleaner output
    prompt = f"Explain this legal contract clause in plain English, mention risk and suggestion:\n{clause}"

    # Encode prompt
    inputs = tokenizer(prompt, return_tensors="pt")
    
    # Generate output
    outputs = model.generate(
        **inputs,
        max_new_tokens=100,  # smaller token count for concise output
        do_sample=True,
        temperature=0.2      # lower temperature for more coherent text
    )
    
    # Decode output
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Optional: keep only first 2–3 sentences for clarity
    explanation = ". ".join(text.split(".")[:3])
    
    return explanation
