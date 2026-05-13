from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


_model = None
_model_error = None


def get_sentence_model():
    global _model, _model_error

    if _model_error is not None:
        raise _model_error

    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as error:
            _model_error = error
            raise

    return _model


def calculate_semantic_score(cv_text, job_description):
    model = get_sentence_model()
    embeddings = model.encode([cv_text, job_description])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

    return round(similarity * 100, 2)


def calculate_tfidf_score(cv_text, job_description):
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([cv_text, job_description])
    similarity = cosine_similarity(vectors[0], vectors[1])[0][0]

    return round(similarity * 100, 2)


def calculate_match_score(cv_text, job_description):
    try:
        return calculate_semantic_score(cv_text, job_description)
    except Exception:
        return calculate_tfidf_score(cv_text, job_description)
