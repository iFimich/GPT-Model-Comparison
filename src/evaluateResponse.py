ML_KEY_TERMS = [
    "accuracy", "precision", "recall", "f1", "overfitting", "underfitting",
    "confusion matrix", "ROC", "hyperparameter", "cross-validation", "model", "data"
]

def evaluate_response(answer: str, tokens: int):
    word_count = len(answer.split())
    key_terms_found = [term for term in ML_KEY_TERMS if term.lower() in answer.lower()]
    key_term_coverage = len(key_terms_found)
    
    # Clarity score (naive heuristic): lower = better
    avg_words_per_sentence = word_count / max(answer.count("."), 1)
    clarity_score = round(avg_words_per_sentence / (1 + key_term_coverage), 2)

    return {
        "words": word_count,
        "key_terms": key_term_coverage,
        "clarity": clarity_score,
        "keywords": key_terms_found
    }

def get_cost_per_1k(selected_model: str):
    if "gpt-3.5" in selected_model:
        return 0.0015
    elif "gpt-4o" in selected_model:
        return 0.005  # avg of input/output
    elif "gpt-4" in selected_model:
        return 0.03  # avg of input/output
    else:
        return 0.02  # fallback
