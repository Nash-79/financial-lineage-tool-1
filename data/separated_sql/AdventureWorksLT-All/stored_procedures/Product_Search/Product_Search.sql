-- ============================================
-- Object Type: StoredProcedure
-- Object Name: [SalesLT].[Product_Search]
-- Source File: AdventureWorksLT-All.sql
-- Script Date: 4/7/2021 10:02:56 AM
-- Separated On: 2025-12-08 20:25:14
-- ============================================

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [SalesLT].[Product_Search]
	@Name nvarchar(50) null,
	@ProductNumber nvarchar(25) null,
	@BeginningCost money null,
	@EndingCost money null
AS
BEGIN
	SELECT *
	FROM SalesLT.Product
    WHERE (@Name IS NULL OR Name LIKE @Name + '%') 
    AND   (@ProductNumber IS NULL OR ProductNumber LIKE @ProductNumber + '%')
    AND   (@BeginningCost IS NULL OR StandardCost >= @BeginningCost)
	AND   (@EndingCost IS NULL OR StandardCost <= @EndingCost)
END
GO
