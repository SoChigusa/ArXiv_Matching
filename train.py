import os
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.exceptions import UndefinedMetricWarning
import warnings
import joblib

# Model files
model_file = 'models/sgd_classifier_model.pkl'
vectorizer_file = 'models/tfidf_vectorizer.pkl'

# matching information
# matching_file = 'data/matching_info_raw.json'
matching_file = 'data/matching_info_raw_240715.json'
matching_new_file = 'data/matching_info_new_raw.json'


# Function to load and preprocess data
def load_and_preprocess_data(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    df = pd.DataFrame(data)
    df['authors_combined'] = df['authors'].apply(
        lambda authors: ' '.join(authors))
    df['combined_features'] = df['title'] + ' ' + \
        df['abstract'] + ' ' + df['authors_combined']
    X = df['combined_features']
    y = df['evaluation']
    return X, y


def perform_grid_search(X_train, y_train):
    # Define the model
    model = SGDClassifier(class_weight='balanced', max_iter=1000)

    # Hyperparameter tuning with GridSearchCV
    param_grid = {
        'alpha': [1e-4, 1e-3, 1e-2, 1e-1],
        'learning_rate': ['constant', 'optimal', 'invscaling', 'adaptive'],
        'loss': ['hinge', 'log', 'modified_huber', 'squared_hinge', 'perceptron'],
        'penalty': ['l2', 'l1', 'elasticnet']
    }

    grid_search = GridSearchCV(
        model, param_grid, cv=5, scoring='f1', n_jobs=-1, verbose=1)
    grid_search.fit(X_train, y_train)

    # Best model from grid search
    best_model = grid_search.best_estimator_

    return best_model, grid_search.best_params_


def save_model_and_vectorizer(model, vectorizer):
    joblib.dump(model, model_file)
    joblib.dump(vectorizer, vectorizer_file)
    print("Model and vectorizer saved successfully.")


if os.path.exists(model_file) and os.path.exists(vectorizer_file):
    # Load existing model and vectorizer
    model = joblib.load(model_file)
    vectorizer = joblib.load(vectorizer_file)
    print("Loaded existing model and vectorizer.")

    # Load and preprocess new data
    X_new, y_new = load_and_preprocess_data(matching_new_file)
    X_new_tfidf = vectorizer.transform(X_new)

    # Original prediction
    y_pred_orig = model.predict(X_new)

    # Continue training the model with new data using partial_fit
    model.partial_fit(X_new_tfidf, y_new, classes=[0, 1])

    # Updated prediction
    y_pred_new = model.predict(X_new)

    # Update the vectorizer!!!
    # Update the vectorizer!!!
    # Update the vectorizer!!!
    # Update the vectorizer!!!
    # Update the vectorizer!!!

    # Save the model and vectorizer
    save_model_and_vectorizer(model, vectorizer)
    print()
    print("Performed incremental learning with new data.")
else:
    # Load data for initial training
    X, y = load_and_preprocess_data(matching_file)

    # Preprocess text data
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_tfidf = vectorizer.fit_transform(X)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_tfidf, y, test_size=0.2, random_state=42, stratify=y)

    # Perform grid search for the initial training
    model, best_params = perform_grid_search(X_train, y_train)

    # Predict and evaluate using the best model
    y_pred = model.predict(X_test)

    # Suppress warnings for undefined metrics
    warnings.filterwarnings('ignore', category=UndefinedMetricWarning)

    print(f'Best Parameters: {best_params}')
    print(f'Accuracy: {accuracy_score(y_test, y_pred)}')
    print(f'Precision: {precision_score(y_test, y_pred, zero_division=1)}')
    print(f'Recall: {recall_score(y_test, y_pred)}')
    print(f'F1 Score: {f1_score(y_test, y_pred)}')

    # Save the model and vectorizer
    save_model_and_vectorizer(model, vectorizer)

# Periodically perform grid search to re-tune hyperparameters
if False:
    X, y = load_and_preprocess_data(matching_file)
    X_new, y_new = load_and_preprocess_data(matching_new_file)
    X_all = pd.concat([X, X_new])
    y_all = pd.concat([y, y_new])
    X_all_tfidf = vectorizer.fit_transform(X_all)

    model, best_params = perform_grid_search(X_all_tfidf, y_all)
    print(f'Periodic Grid Search Best Parameters: {best_params}')

    # Save the updated model and vectorizer
    save_model_and_vectorizer(model, vectorizer)
