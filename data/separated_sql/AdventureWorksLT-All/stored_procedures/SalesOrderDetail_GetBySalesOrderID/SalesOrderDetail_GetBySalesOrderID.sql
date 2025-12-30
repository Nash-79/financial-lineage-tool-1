-- ============================================
-- Object Type: StoredProcedure
-- Object Name: [SalesLT].[SalesOrderDetail_GetBySalesOrderID]
-- Source File: AdventureWorksLT-All.sql
-- Script Date: 4/7/2021 10:02:56 AM
-- Separated On: 2025-12-08 20:25:14
-- ============================================

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [SalesLT].[SalesOrderDetail_GetBySalesOrderID]
	@SalesOrderID int
AS
BEGIN
	SELECT SalesOrderID, SalesOrderDetailID, OrderQty,
	       sd.ProductID, UnitPrice, UnitPriceDiscount, LineTotal,
		   [Name], ProductNumber, Size, [Weight]
	FROM SalesLT.SalesOrderDetail sd
	INNER JOIN SalesLT.Product p ON (sd.ProductID = p.ProductID)
	WHERE SalesOrderID = @SalesOrderID
END
GO
