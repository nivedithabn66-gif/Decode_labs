import re
import string
from typing import List, Optional

# Standard English Stopwords list (lightweight, zero dependency)
ENGLISH_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into",
    "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
    "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's",
    "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs",
    "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves"
}

class TextPreprocessor:
    """
    Production-ready NLP Preprocessing Pipeline.
    Ensures identical text transformation across training, evaluation, and live API inference.
    """

    def __init__(
        self,
        lowercase: bool = True,
        remove_whitespace: bool = True,
        remove_punctuation: bool = False,
        remove_stopwords: bool = True,
        custom_stopwords: Optional[List[str]] = None
    ):
        self.lowercase = lowercase
        self.remove_whitespace = remove_whitespace
        self.remove_punctuation = remove_punctuation
        self.remove_stopwords = remove_stopwords
        self.stopwords = set(ENGLISH_STOPWORDS)
        if custom_stopwords:
            self.stopwords.update(custom_stopwords)

    def preprocess_text(self, text: Optional[str]) -> str:
        """Processes a single raw text string into a clean normalized tokenized text string."""
        if not text or not isinstance(text, str):
            return ""

        # 1. Lowercase normalization
        if self.lowercase:
            text = text.lower()

        # 2. Whitespace normalization (tabs, newlines, multiple spaces)
        if self.remove_whitespace:
            text = re.sub(r"\s+", " ", text).strip()

        # 3. Punctuation handling (retains technical terms like POST, GET, 500, NullPointerException if disabled)
        if self.remove_punctuation:
            text = text.translate(str.maketrans("", "", string.punctuation))

        # 4. Tokenization & Stopword removal
        tokens = text.split()
        if self.remove_stopwords:
            tokens = [t for t in tokens if t not in self.stopwords and len(t) > 1]

        return " ".join(tokens)

    def preprocess_series(self, series: List[str]) -> List[str]:
        """Applies preprocessing to a collection or pandas Series of strings."""
        return [self.preprocess_text(t) for t in series]

    def to_dict(self) -> dict:
        return {
            "lowercase": self.lowercase,
            "remove_whitespace": self.remove_whitespace,
            "remove_punctuation": self.remove_punctuation,
            "remove_stopwords": self.remove_stopwords,
            "num_stopwords": len(self.stopwords)
        }

try:
    from sklearn.base import BaseEstimator, TransformerMixin

    class TextPreprocessorTransformer(BaseEstimator, TransformerMixin):
        """Scikit-learn compliant transformer wrapper for TextPreprocessor."""
        def __init__(
            self,
            lowercase: bool = True,
            remove_whitespace: bool = True,
            remove_punctuation: bool = False,
            remove_stopwords: bool = True
        ):
            self.lowercase = lowercase
            self.remove_whitespace = remove_whitespace
            self.remove_punctuation = remove_punctuation
            self.remove_stopwords = remove_stopwords
            self.preprocessor_ = TextPreprocessor(
                lowercase=self.lowercase,
                remove_whitespace=self.remove_whitespace,
                remove_punctuation=self.remove_punctuation,
                remove_stopwords=self.remove_stopwords
            )

        def fit(self, X, y=None):
            return self

        def transform(self, X):
            if isinstance(X, list):
                return self.preprocessor_.preprocess_series(X)
            elif hasattr(X, "tolist"):
                return self.preprocessor_.preprocess_series(X.tolist())
            else:
                return [self.preprocessor_.preprocess_text(str(x)) for x in X]
except ImportError:
    pass

if __name__ == "__main__":
    prep = TextPreprocessor(lowercase=True, remove_stopwords=True)
    sample = "Application crashes when uploading a large file! Traceback: NullPointerException."
    clean = prep.preprocess_text(sample)
    print("Raw sample:", sample)
    print("Clean sample:", clean)
