

WITH DuplicateRecords AS (
	SELECT
		JourneyID,
		CustomerID,
		ProductID,
		VisitDate,
		Stage,
		Action,
		Duration,
		ROW_NUMBER() OVER(
			PARTITION BY CustomerID, ProductID, VisitDate, Stage, Action
			ORDER BY JourneyID
		) AS Row_Num
	FROM
		dbo.customer_journey
)
SELECT *
FROM
	DuplicateRecords
WHERE row_num > 1
ORDER BY JourneyID;



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