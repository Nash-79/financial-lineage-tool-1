-- ============================================
-- Object Type: Index
-- Constraint/Index Name: IX_Address_AddressLine1_AddressLine2_City_StateProvince_PostalCode_CountryRegion
-- Parent Object: Address
-- Source File: AdventureWorksLT-All.sql
-- Script Date: 4/7/2021 10:02:56 AM
-- Separated On: 2025-12-08 20:25:14
-- ============================================

CREATE NONCLUSTERED INDEX [IX_Address_AddressLine1_AddressLine2_City_StateProvince_PostalCode_CountryRegion] ON [SalesLT].[Address]
(
	[AddressLine1] ASC,
	[AddressLine2] ASC,
	[City] ASC,
	[StateProvince] ASC,
	[PostalCode] ASC,
	[CountryRegion] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
