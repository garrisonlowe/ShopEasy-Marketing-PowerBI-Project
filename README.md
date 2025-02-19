[Try it out here!](https://app.powerbi.com/view?r=eyJrIjoiZDIwYzI5YTYtNTUyYy00NzJmLWE4MmMtMDhjYjY2ZDdlYTg4IiwidCI6ImJkMGNhZWQyLTBiNTctNDllNy1hMjY2LTYzMWZhNmE2YzIyYSJ9)

# ShopEasy Marketing Analysis Dashboard

ShopEasy, an online retail business, is facing reduced customer engagement and conversion rates despite launching several new online marketing campaigns. They are reaching out to you to help conduct a detailed analysis and identify areas for improvement in their marketing strategies. Jane at ShopEasy has provided us with requirements to develop a dashboard tailored for her sales team's use.

## Project Requirements

#### Project Steps
 1. Gather Requirements
 2. Data ETL
 3. Data Visualization

### Key Points:
- **Reduced Customer Engagement:** The number of customer interactions and engagement with the site and marketing content has declined.
- **Decreased Conversion Rates:** Fewer site visitors are converting into paying customers.
- **High Marketing Expenses:** Significant investments in marketing campaigns are not yielding expected returns.
- **Need for Customer Feedback Analysis:** Understanding customer opinions about products and services is crucial for improving engagement and conversions.

Let's take a look at the email from Jane, the Marketing Manager.

> Hi Data Analyst,
> 
> I hope this email finds you well. I’m the Marketing Manager at ShopEasy. We’ve been facing some challenges with our marketing campaigns lately, and I’m reaching out to request your
> expertise in data analysis to help us identify areas for improvement.
> Despite our increased investment in marketing, we’ve observed a decline in customer engagement and conversion rates. Our marketing expenses have gone up, but the return on investment 
> isn’t meeting our expectations. We need a comprehensive analysis to understand the effectiveness of our current strategies and to find opportunities to optimize our efforts.
> We have data from various sources, including customer reviews, social media comments, and campaign performance metrics. Your insights will be invaluable in helping us turn this situation
> around.
> 
> Looking forward to your response.
>
> Best regards,
> 
> Jane Doe
>
> Marketing Manager


Let's look at the email from John, the Customer Experience Manager.

> Hi Data Analyst,
> I’m the Customer Experience Manager at ShopEasy, and I’m writing to seek your help with analyzing our customer feedback. Over the past few months, we’ve noticed a drop in customer engagement and satisfaction, which is impacting our overall conversion rates.
> We’ve gathered a significant amount of customer reviews and social media comments that highlight various issues and sentiments. We believe that by thoroughly analyzing this feedback, we can gain a better understanding of our customers' needs and pain points.
> Your expertise in data analysis will be crucial in helping us decode this feedback and provide actionable insights. We hope this will guide us in improving our customer experience and ultimately boost our engagement and conversion rates.
> Thank you for your assistance.
> Best regards,
>
> John Smith
>
> Customer Experience Manager
>
> ShopEasy



### Key Performance Indicators (KPIs)

- **Conversion Rate:** Percentage of website visitors who make a purchase.
- **Customer Engagement Rate:** Level of interaction with marketing content *(clicks, likes, comments)*.
- **Customer Feedback Score:** Average rating from customer reviews.

### Goals

- **Increase Conversion Rates:**
    - **Goal:** Identify factors impacting the conversion rate and provide recommendations to improve it.
    - **Insight:** Highlight key stages where visitors drop off and suggest improvements to optimize the conversion funnel.
- **Enhance Customer Engagement:**
    - **Goal:** Determine which types of content drive the highest engagement. 
    - **Insight:** Analyze interaction levels with different types of marketing content to inform better content strategies.
- **Improve Customer Feedback Scores:**
    - **Goal:** Understand common themes in customer reviews and provide actionable insights.
    - **Insight:** Identify recurring positive and negative feedback to guide product and service improvements.

## Data ETL Process

For the Data ETL process, we'll run several queries to extract all the necessary columns from each table that will be utilized.

**Query 1:** The Customers table

```sql
SELECT
	c.CustomerID,
	c.CustomerName,
	c.Email,
	c.Gender,
	c.Age,
	g.Country,
	g.city
FROM
	dbo.customers as c
LEFT JOIN
	dbo.geography as g
ON
	c.GeographyID = g.GeographyID;
```



**Query 2:** The Products Table

```sql
SELECT
	c.CustomerID,
	c.CustomerName,
	c.Email,
	c.Gender,
	c.Age,
	g.Country,
	g.city
FROM
	dbo.customers as c
LEFT JOIN
	dbo.geography as g
ON
	c.GeographyID = g.GeographyID;
```

**Query 3:** The Customer Journey Table

```sql
SELECT
	JourneyID,
	CustomerID,
	ProductID,
	VisitDate,
	Stage,
	Action,
	COALESCE(Duration, avg_duration) AS Duration
FROM
	(
		SELECT
			JourneyID,
			CustomerID,
			ProductID,
			VisitDate,
			UPPER(Stage) AS Stage,
			Action, 
			Duration,
			AVG(Duration) OVER (PARTITION BY VisitDate) as avg_duration,
			ROW_NUMBER() OVER (
					PARTITION BY CustomerID, ProductID, VisitDate, UPPER(Stage), Action
					ORDER BY JourneyID
			) AS row_num
		FROM
			dbo.customer_journey
	) AS subquery
WHERE
	row_num = 1
;
```

**Query 4:** The Customer Reviews Table

```sql
SELECT
	ReviewID,
	CustomerID,
	ProductID,
	ReviewDate,
	Rating,
	REPLACE(ReviewText, '  ', ' ') AS ReviewText
FROM
	dbo.customer_reviews;
```



**Query 5:** The Engagement Date Table

```sql
SELECT
	EngagementID,
	ContentID,
	CampaignID,
	ProductID,
	UPPER(REPLACE(ContentType, 'SocialMedia', 'Social Media')) AS ContentType,
	LEFT(ViewsClicksCombined, CHARINDEX('-', ViewsClicksCombined) -1) AS Views,
	RIGHT(ViewsClicksCombined, LEN(ViewsClicksCombined) - CHARINDEX('-', ViewsClicksCombined)) AS Clicks,
	Likes,
	FORMAT(CONVERT(DATE, EngagementDate), 'MM-dd-yyyy') AS EngagementDate
FROM
	dbo.engagement_data
WHERE
	ContentType != 'NewsLetter';
```

## Sentiment Analysis for Customer Reviews

For the final table, the Sentiment Analysis table, I'm using the Customer Reviews table to run a Sentiment Analysis Python Program and create 5 buckets of Sentiment:
- Positive 
- Mixed Positive 
- Neutral
- Mixed Negative 
- Negative 

Here is the main bulk of the Python code using the NLTK Sentiment Intensity Analyzer package. Full code file will be in the files.

```python
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
```

## Visualize the Data

First, we need to set up the data model.

![image](https://github.com/user-attachments/assets/35470c3b-e8a2-4cd6-96d6-b84b085725e3)

## Pictures of the Dashboard:

Overview Screen:
![Image](https://github.com/user-attachments/assets/550aea58-1e4a-4cb5-ae03-d39a6fbb5e0d)

Conversion Screen:
![Image](https://github.com/user-attachments/assets/4bcd2765-1690-41b4-956c-0ef61b6aa279)

Social Media Screen:
![Image](https://github.com/user-attachments/assets/38f8aaed-df50-4cea-aa54-e0b33a33021e)


Customer Reviews Screen:
![Image](https://github.com/user-attachments/assets/9c253044-5956-40d5-aaae-8245dda57c20)


All measures and backgrounds will be in the repo files.
