
import streamlit as st
import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import pickle
import spacy.cli
from spacy.util import is_package

if not is_package('en_core_web_sm'):
    spacy.cli.download("en_core_web_sm")

# Load spaCy model
@st.cache(allow_output_mutation=True)
def load_spacy_model():
    return spacy.load("en_core_web_sm")

nlp = load_spacy_model()

# Preprocessing function using spaCy
def preprocess(text):
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])

def classify_news(subject, df):
    subject_df = df[df['subject'] == subject]
    subject_df['processed_title'] = subject_df['title'].apply(preprocess)
    subject_df['features'] = subject_df['processed_title']

    # Feature extraction using TF-IDF
    tfidf = TfidfVectorizer(max_features=1000)
    X = tfidf.fit_transform(subject_df['features'])
    y = subject_df['action']

    # Splitting the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Model evaluation
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    return report['accuracy'], report['macro avg']['support'], model, tfidf

# Streamlit app
def main():
    st.title("News Classification App")

    # File uploader
    uploaded_file = st.file_uploader("Upload your News Price CSV File", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df = df.dropna(subset=['summary', 'title', 'action'])

        subject_counts = df['subject'].value_counts().to_dict()
        methods = ['randomforest']
        results = []
        models = {}

        # Train button
        if st.button('Train'):
            for subject in df['subject'].unique():
                st.write(f"Processing subject: {subject} with Random Forest")
                try:
                    accuracy, support, model, tfidf = classify_news(subject, df)
                    results.append({
                        'subject': subject,
                        'accuracy': accuracy,
                        'test_sample': support,
                        'total_sample': subject_counts[subject],
                        'method': 'Random Forest'
                    })
                    models[subject] = (model, tfidf)
                except Exception as e:
                    st.write(f"Error processing subject {subject}: {e}")

            results_df = pd.DataFrame(results)
            results_df = results_df.sort_values(by=['accuracy', 'method'], ascending=[False, True])
            st.write(results_df)

        # Saving models
        if st.button('Save Models'):
            for subject, (model, tfidf) in models.items():
                with open(f'model_{subject}.pkl', 'wb') as f:
                    pickle.dump((model, tfidf), f)
            st.success('Models saved successfully.')

        # Title classification section
        title = st.text_input("Enter a news title to classify")
        selected_subject = st.selectbox("Select the subject for classification", options=df['subject'].unique())
        
        if st.button('Classify'):
            if selected_subject in models:
                model, tfidf = models[selected_subject]
                processed_title = preprocess(title)
                X = tfidf.transform([processed_title])
                prediction = model.predict(X)
                st.write(f"The predicted action for the title is: {prediction[0]}")
            else:
                st.write("Model for the selected subject is not available. Please train the model first.")

if __name__ == "__main__":
    main()
