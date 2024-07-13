from transformers import AutoTokenizer, AutoModelForTokenClassification, AutoConfig

# Load the SciBERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
model = AutoModelForTokenClassification.from_pretrained(
    "allenai/scibert_scivocab_uncased")
config = AutoConfig.from_pretrained("allenai/scibert_scivocab_uncased")

# Print the label map
label_map = config.id2label
print(label_map)
