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
