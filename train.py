import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.exceptions import UndefinedMetricWarning
import warnings

# Load data from JSON file
with open('data/matching_info_raw_240715.json', 'r') as file:
    data = json.load(file)

# Convert JSON data to DataFrame
df = pd.DataFrame(data)

# Check data balance
print(df['evaluation'].value_counts())

# Combine title, abstract, and authors for feature extraction
df['authors_combined'] = df['authors'].apply(lambda authors: ' '.join(authors))
df['combined_features'] = df['title'] + \
    ' ' + df['abstract'] + ' ' + df['authors_combined']

# Feature and label extraction
X = df['combined_features']
y = df['evaluation']  # User feedback: liked (1) or not (0)

# Preprocess text data
vectorizer = TfidfVectorizer(max_features=5000)
X_tfidf = vectorizer.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_tfidf, y, test_size=0.2, random_state=42)

# Train model
model = LogisticRegression(class_weight='balanced', max_iter=1000)
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)

# Suppress warnings for undefined metrics
warnings.filterwarnings('ignore', category=UndefinedMetricWarning)

print(f'Accuracy: {accuracy_score(y_test, y_pred)}')
print(f'Precision: {precision_score(y_test, y_pred)}')
print(f'Recall: {recall_score(y_test, y_pred)}')
print(f'F1 Score: {f1_score(y_test, y_pred)}')

# Predict for new papers
with open('data/matching_info_raw.json', 'r') as file:
    new_papers = json.load(file)[len(data):]

# Convert new papers data to DataFrame
df_new = pd.DataFrame(new_papers)

# Transform new abstracts
X_new = vectorizer.transform(df_new['abstract'])
predictions = model.predict(X_new)

# Add predictions to the new papers DataFrame
df_new['predicted_evaluation'] = predictions

# Output predictions
print(df_new[['title', 'predicted_evaluation', 'evaluation']])
