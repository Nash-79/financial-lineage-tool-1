-- ============================================
-- Object Type: StoredProcedure
-- Object Name: [SalesLT].[Product_Get]
-- Source File: AdventureWorksLT-All.sql
-- Script Date: 4/7/2021 10:02:56 AM
-- Separated On: 2025-12-08 20:25:14
-- ============================================

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [SalesLT].[Product_Get]
	@ProductID int
AS
BEGIN
	SELECT * 
	FROM SalesLT.Product
	WHERE ProductID = @ProductID;
END
GO
