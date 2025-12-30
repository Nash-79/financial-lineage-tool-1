-- ============================================
-- Object Type: StoredProcedure
-- Object Name: [SalesLT].[MultipleResultsColors]
-- Source File: AdventureWorksLT-All.sql
-- Script Date: 4/7/2021 10:02:56 AM
-- Separated On: 2025-12-08 20:25:14
-- ============================================

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [SalesLT].[MultipleResultsColors]
AS
BEGIN
	SELECT * FROM SalesLT.Product
	WHERE Color = 'Black';

	SELECT * FROM SalesLT.Product
	WHERE Color = 'Red';
END
GO
