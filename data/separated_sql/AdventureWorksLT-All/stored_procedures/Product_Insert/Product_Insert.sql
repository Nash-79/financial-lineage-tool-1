-- ============================================
-- Object Type: StoredProcedure
-- Object Name: [SalesLT].[Product_Insert]
-- Source File: AdventureWorksLT-All.sql
-- Script Date: 4/7/2021 10:02:56 AM
-- Separated On: 2025-12-08 20:25:14
-- ============================================

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [SalesLT].[Product_Insert]
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
	@ProductID int OUTPUT
AS
BEGIN
	INSERT INTO [SalesLT].[Product]
			   ([Name]
			   ,[ProductNumber]
			   ,[Color]
			   ,[StandardCost]
			   ,[ListPrice]
			   ,[Size]
			   ,[Weight]
			   ,[ProductCategoryID]
			   ,[ProductModelID]
			   ,[SellStartDate]
			   ,[SellEndDate]
			   ,[DiscontinuedDate]
			   ,[ModifiedDate])
		 VALUES
			   (@Name,
				@ProductNumber,
				@Color,
				@StandardCost,
				@ListPrice,
				@Size,
				@Weight,
				@ProductCategoryID,
				@ProductModelID,
				@SellStartDate,
				@SellEndDate,
				@DiscontinuedDate,
				@ModifiedDate);

	SELECT @ProductID = SCOPE_IDENTITY();
END
GO
