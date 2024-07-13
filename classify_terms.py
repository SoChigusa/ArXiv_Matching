from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

# Load SciBERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
model = AutoModelForTokenClassification.from_pretrained(
    "allenai/scibert_scivocab_uncased")


def classify_terms_sciBERT(text):
    tokens = tokenizer(text, return_tensors="pt",
                       truncation=True, padding=True)
    outputs = model(**tokens)
    predictions = torch.argmax(outputs.logits, dim=2)

    # Get the predicted labels and corresponding words
    predicted_labels = predictions[0].tolist()
    tokenized_text = tokenizer.convert_ids_to_tokens(tokens.input_ids[0])

    classified_nouns = {'physics': [], 'common': []}

    for token, label in zip(tokenized_text, predicted_labels):
        # Assuming label 1 is for domain-specific terms (adjust based on the model's labels)
        if label == 1:
            classified_nouns['physics'].append(token)
        else:
            classified_nouns['common'].append(token)

    # Remove duplicates and clean tokens
    for key in classified_nouns:
        classified_nouns[key] = list(set(classified_nouns[key]))
        classified_nouns[key] = [token.replace(
            "##", "") for token in classified_nouns[key]]

    return classified_nouns


# Example usage
text = "We present a method to directly detect the axion dark matter using nitrogen vacancy centers in diamonds. In particular, we use metrology leveraging the nuclear spin of nitrogen to detect axion-nucleus couplings. This is achieved through protocols designed for dark matter searches, which introduce a novel approach of quantum sensing techniques based on the nitrogen vacancy center. Although the coupling strength of the magnetic fields with nuclear spins is three orders of magnitude smaller than that with electron spins for conventional magnetometry, the axion interaction strength with nuclear spins is the same order of magnitude as that with electron spins. Furthermore, we can take advantage of the long coherence time by using the nuclear spins for the axion dark matter detection. We show that our method is sensitive to a broad frequency range ≲100Hz corresponding to the axion mass ma≲4×10−13eV. We present the detection limit of our method for both the axion-neutron and the axion-proton couplings and discuss its significance in comparison with other proposed ideas."
classified_nouns = classify_terms_sciBERT(text)
print(classified_nouns)
