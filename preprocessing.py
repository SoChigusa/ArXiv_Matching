import json
from collections import defaultdict
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk import pos_tag, RegexpParser
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

# Initialize stop words list, stemmer, and lemmatizer
stop_words = set(stopwords.words('english'))
ps = PorterStemmer()
lemmatizer = WordNetLemmatizer()


def preprocess_text(text):
    # Tokenization
    words = word_tokenize(text.lower())

    # # Stemming (optional)
    # words_stemmed = [ps.stem(word) for word in words]

    # # Lemmatization (optional)
    # words_lemmatized = [lemmatizer.lemmatize(word) for word in words]

    return words


def extract_compound_nouns(text):
    # Preprocess text
    words = preprocess_text(text)

    # POS tagging
    tagged_words = pos_tag(words)

    # Define chunk grammar
    grammar = r"""
        NP: {<DT>?<JJ>*<NN.*>+}   # Chunk sequences of DT, JJ, NN
    """

    # Create chunk parser
    chunk_parser = RegexpParser(grammar)

    # Chunking
    tree = chunk_parser.parse(tagged_words)

    # Extract compound nouns
    compound_nouns = []
    for subtree in tree:
        if isinstance(subtree, nltk.Tree) and subtree.label() == 'NP':
            compound_noun = ' '.join(word for word, tag in subtree.leaves())
            compound_nouns.append(compound_noun)

    return compound_nouns


def remove_stop_words_from_compound_nouns(compound_nouns, use_lemmatization=True):
    processed_compound_nouns = []
    for noun_phrase in compound_nouns:
        words = word_tokenize(noun_phrase)
        # Remove stop words
        filtered_words = [
            word for word in words if word.lower() not in stop_words]
        # Apply lemmatization
        processed_words = [lemmatizer.lemmatize(
            word) for word in filtered_words]
        processed_compound_noun = ' '.join(processed_words)
        processed_compound_nouns.append(processed_compound_noun)
    return processed_compound_nouns


def extract_nouns(text):
    compound_nouns = extract_compound_nouns(text)
    processed_compound_nouns = remove_stop_words_from_compound_nouns(
        compound_nouns)
    return processed_compound_nouns


def rate_words(title, authors, abstract):
    word_ratings = defaultdict(int)

    # Rate words in title
    title_words = extract_compound_nouns(title)
    for word in title_words:
        word_ratings[word] += 10

    # Rate author names
    for author in authors:
        word_ratings[author] += 1

    # Rate words in abstract
    abstract_words = extract_compound_nouns(abstract)
    for word in abstract_words:
        word_ratings[word] += 1

    return word_ratings


def aggregate_ratings(json_file_path):
    with open(json_file_path, 'r') as file:
        papers = json.load(file)

    total_ratings = defaultdict(int)

    for paper in papers:
        title = paper["title"]
        authors = paper["authors"]
        abstract = paper["abstract"]
        evaluation = paper["evaluation"]
        sign = 1 if evaluation == "like" else -1

        word_ratings = rate_words(title, authors, abstract)
        for word, rating in word_ratings.items():
            total_ratings[word] += sign * rating

    return total_ratings


def sort_and_save_ratings(ratings, output_file_path):
    sorted_ratings = sorted(
        ratings.items(), key=lambda item: item[1], reverse=True)
    sorted_ratings_dict = {word: rating for word, rating in sorted_ratings}

    with open(output_file_path, 'w') as file:
        json.dump(sorted_ratings_dict, file, indent=4)


# Example usage
input_file_path = "data/matching_info_raw.json"
output_file_path = "data/matching_info.json"
total_ratings = aggregate_ratings(input_file_path)
sort_and_save_ratings(total_ratings, output_file_path)
