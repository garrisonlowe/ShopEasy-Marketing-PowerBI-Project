import pandas as pd
import pyodbc
import os
import nltk
import dotenv
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Load environment variables.
dotenv.load_dotenv()

# download the VADER lexicon for sentiment analysis.
nltk.download('vader_lexicon')
 
 # Function to fetch data from th SQL Server database using a query string.
 
def fetch_data():
    # Set up connection to MySQL database with environment variables.
    server_name = os.getenv("servername")
    database_name = os.getenv("database")

    # Creating the connection string
    connection_string = f"Driver={{ODBC Driver 17 for SQL Server}};Server={server_name};Database={database_name};Trusted_Connection=yes;"

    # Connecting to SQL Server
    conn = pyodbc.connect(connection_string)
    
    query = "SELECT ReviewID, CustomerID, ProductID, ReviewDate, Rating, ReviewText FROM dbo.customer_reviews"
    
    # Execute the query and fetch the data into a DataFrame
    df = pd.read_sql(query, conn)
    
    # Close the connection to free up resources
    conn.close()
    
    # Return the fetched data as a DataFrame
    return df

# Fetch the customer reviews data from the SQL database
customer_reviews_df = fetch_data()

# Initialize the VADER sentiment intensity analyzer for analyzing the sentiment of text data
sia = SentimentIntensityAnalyzer()

# Define a function to calculate sentiment scores using VADER
def calculate_sentiment(review):
    # Get the sentiment scores for the review text
    sentiment = sia.polarity_scores(review)
    # Return the compound score, which is a normalized score between -1 (most negative) and 1 (most positive)
    return sentiment['compound']

# Define a function to categorize sentiment using both the sentiment score and the review rating
def categorize_sentiment(score, rating):
    # Use both the text sentiment score and the numerical rating to determine sentiment category
    if score > 0.05:  # Positive sentiment score
        if rating >= 4:
            return 'Positive'  # High rating and positive sentiment
        elif rating == 3:
            return 'Mixed Positive'  # Neutral rating but positive sentiment
        else:
            return 'Mixed Negative'  # Low rating but positive sentiment
    elif score < -0.05:  # Negative sentiment score
        if rating <= 2:
            return 'Negative'  # Low rating and negative sentiment
        elif rating == 3:
            return 'Mixed Negative'  # Neutral rating but negative sentiment
        else:
            return 'Mixed Positive'  # High rating but negative sentiment
    else:  # Neutral sentiment score
        if rating >= 4:
            return 'Positive'  # High rating with neutral sentiment
        elif rating <= 2:
            return 'Negative'  # Low rating with neutral sentiment
        else:
            return 'Neutral'  # Neutral rating and neutral sentiment

# Define a function to bucket sentiment scores into text ranges
def sentiment_bucket(score):
    if score >= 0.5:
        return '0.5 to 1.0'  # Strongly positive sentiment
    elif 0.0 <= score < 0.5:
        return '0.0 to 0.49'  # Mildly positive sentiment
    elif -0.5 <= score < 0.0:
        return '-0.49 to 0.0'  # Mildly negative sentiment
    else:
        return '-1.0 to -0.5'  # Strongly negative sentiment

# Apply sentiment analysis to calculate sentiment scores for each review
customer_reviews_df['SentimentScore'] = customer_reviews_df['ReviewText'].apply(calculate_sentiment)

# Apply sentiment categorization using both text and rating
customer_reviews_df['SentimentCategory'] = customer_reviews_df.apply(
    lambda row: categorize_sentiment(row['SentimentScore'], row['Rating']), axis=1)

# Apply sentiment bucketing to categorize scores into defined ranges
customer_reviews_df['SentimentBucket'] = customer_reviews_df['SentimentScore'].apply(sentiment_bucket)

# Display the first few rows of the DataFrame with sentiment scores, categories, and buckets
print(customer_reviews_df.head())

# Save the DataFrame with sentiment scores, categories, and buckets to a new CSV file
customer_reviews_df.to_csv(r'C:\Users\garri\OneDrive\Desktop\AW Marketing Portfolio Project\fact_customer_reviews_with_sentiment.csv', index=False)
