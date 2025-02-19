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