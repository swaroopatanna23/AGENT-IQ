from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from typing import Tuple

class BaselineIntentClassifier:
    """
    TF-IDF + SVM baseline intent classification model.
    Directly fulfills Batch-08 Slide 9: 'TF-IDF + SVM (Baseline)'.
    """
    def __init__(self):
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), stop_words="english", lowercase=True)),
            ("clf", LinearSVC(random_state=42))
        ])
        self._train_baseline()

    def _train_baseline(self):
        # Curated analytical query training set
        X_train = [
            # group_comparison
            "Which region has the highest sales?",
            "What is average marks by age?",
            "Compare salary across departments",
            "Show average marks by gender",
            "Highest revenue by product category",
            "Which department has highest attendance?",
            "Compare treatment cost by diagnosis",
            
            # trend_over_time
            "Show the monthly sales trend",
            "How did revenue change over time?",
            "Quarterly sales progress",
            "Trend of admissions over months",
            "Show performance by month",
            "Time series of invoices",

            # ranking
            "What are the top five products?",
            "Top 10 highest marks students",
            "Rank departments by profit",
            "Bottom 5 performing stores",
            "Who are the top employees by salary?",

            # distribution
            "Show distribution of marks",
            "Histogram of employee age",
            "What is the spread of treatment cost?",
            "Distribution of study hours",

            # correlation
            "What is the relationship between attendance and marks?",
            "Correlation between study hours and exam score",
            "Does salary increase with experience?",
            "Relationship between blood pressure and age",

            # aggregation
            "What is the total sales amount?",
            "How many students are enrolled?",
            "Average salary of all employees",
            "Count total patients admitted",
            "Maximum marks scored in exam",

            # outlier_detection
            "Are there any outliers in salary?",
            "Find unusual treatment costs",
            "Detect anomalous test scores",

            # overview
            "Give me an overview of this dataset",
            "Summarize the data",
            "What is this dataset about?",
            "Show summary statistics"
        ]

        y_train = [
            "group_comparison", "group_comparison", "group_comparison", "group_comparison", "group_comparison", "group_comparison", "group_comparison",
            "trend_over_time", "trend_over_time", "trend_over_time", "trend_over_time", "trend_over_time", "trend_over_time",
            "ranking", "ranking", "ranking", "ranking", "ranking",
            "distribution", "distribution", "distribution", "distribution",
            "correlation", "correlation", "correlation", "correlation",
            "aggregation", "aggregation", "aggregation", "aggregation", "aggregation",
            "outlier_detection", "outlier_detection", "outlier_detection",
            "overview", "overview", "overview", "overview"
        ]

        self.pipeline.fit(X_train, y_train)

    def predict_intent(self, question: str) -> str:
        try:
            return str(self.pipeline.predict([question])[0])
        except Exception:
            return "group_comparison"
