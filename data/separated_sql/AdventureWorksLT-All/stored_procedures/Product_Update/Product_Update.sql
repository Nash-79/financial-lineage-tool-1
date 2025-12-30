-- ============================================
-- Object Type: StoredProcedure
-- Object Name: [SalesLT].[Product_Update]
-- Source File: AdventureWorksLT-All.sql
-- Script Date: 4/7/2021 10:02:56 AM
-- Separated On: 2025-12-08 20:25:14
-- ============================================

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [SalesLT].[Product_Update]
	@Name nvarchar(50),
	@ProductNumber nvarchar(25),
	@Color nvarchar(15) null,
	@StandardCost money,
	@ListPrice money,
	@Size nvarchar(5) null,
	@Weight decimal(8,2) null,
	@ProductCategoryID int null,
	@ProductModelID int null,
	@SellStartDate datetime,
	@SellEndDate datetime null,
	@DiscontinuedDate datetime null,
	@ModifiedDate datetime,
	@ProductID int
AS
BEGIN
	UPDATE SalesLT.Product 
	SET [Name]=@Name, ProductNumber=@ProductNumber, Color=@Color, 
	    StandardCost=@StandardCost, ListPrice=@ListPrice, Size=@Size, 
		[Weight]=@Weight, ProductCategoryID=@ProductCategoryID, 
		ProductModelID=@ProductModelID, SellStartDate=@SellStartDate, 
		SellEndDate=@SellEndDate, DiscontinuedDate=@DiscontinuedDate, 
		ModifiedDate=@ModifiedDate 
    WHERE ProductID = @ProductID
END
GO
