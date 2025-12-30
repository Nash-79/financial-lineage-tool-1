-- ============================================
-- Object Type: StoredProcedure
-- Object Name: [SalesLT].[SalesOrderDetail_GetBySalesOrderIDs]
-- Source File: AdventureWorksLT-All.sql
-- Script Date: 4/7/2021 10:02:56 AM
-- Separated On: 2025-12-08 20:25:14
-- ============================================

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE PROCEDURE [SalesLT].[SalesOrderDetail_GetBySalesOrderIDs]
	@SalesOrderIDs varchar(20)
AS
BEGIN
	SELECT SalesOrderID, SalesOrderDetailID, OrderQty,
	       sd.ProductID, UnitPrice, UnitPriceDiscount, LineTotal,
		   [Name], ProductNumber, Size, [Weight]
	FROM SalesLT.SalesOrderDetail sd
	INNER JOIN SalesLT.Product p ON (sd.ProductID = p.ProductID)
	WHERE SalesOrderID IN(@SalesOrderIDs)
END
GO
EXEC [AdventureWorksLT].sys.sp_addextendedproperty @name=N'MS_Description', @value=N'AdventureWorksLT Sample OLTP Database' 
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Table value function returning every product category and its parent, if applicable.' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'FUNCTION',@level1name=N'ufnGetAllCategories'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Input parameter for the table value function ufnGetCustomerInformation. Enter a valid CustomerID from the Sales.Customer table.' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'FUNCTION',@level1name=N'ufnGetCustomerInformation', @level2type=N'PARAMETER',@level2name=N'@CustomerID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Table value function returning the customer ID, first name, and last name for a given customer.' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'FUNCTION',@level1name=N'ufnGetCustomerInformation'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Input parameter for the scalar function ufnGetSalesOrderStatusText. Enter a valid integer.' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'FUNCTION',@level1name=N'ufnGetSalesOrderStatusText', @level2type=N'PARAMETER',@level2name=N'@Status'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Scalar function returning the text representation of the Status column in the SalesOrderHeader table.' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'FUNCTION',@level1name=N'ufnGetSalesOrderStatusText'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Collection of XML schemas for the CatalogDescription column in the Sales.ProductModel table.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'XML SCHEMA COLLECTION',@level1name=N'ProductDescriptionSchemaCollection'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Contains objects related to products, customers, sales orders, and sales territories.' , @level0type=N'SCHEMA',@level0name=N'SalesLT'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key for Address records.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Address', @level2type=N'COLUMN',@level2name=N'AddressID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'First street address line.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Address', @level2type=N'COLUMN',@level2name=N'AddressLine1'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Second street address line.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Address', @level2type=N'COLUMN',@level2name=N'AddressLine2'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Name of the city.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Address', @level2type=N'COLUMN',@level2name=N'City'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Name of state or province.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Address', @level2type=N'COLUMN',@level2name=N'StateProvince'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Postal code for the street address.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Address', @level2type=N'COLUMN',@level2name=N'PostalCode'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Address', @level2type=N'COLUMN',@level2name=N'rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of NEWID()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Address', @level2type=N'CONSTRAINT',@level2name=N'DF_Address_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Date and time the record was last updated.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Address', @level2type=N'COLUMN',@level2name=N'ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of GETDATE()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Address', @level2type=N'CONSTRAINT',@level2name=N'DF_Address_ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key (clustered) constraint' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Address', @level2type=N'CONSTRAINT',@level2name=N'PK_Address_AddressID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique nonclustered constraint. Used to support replication samples.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Address', @level2type=N'CONSTRAINT',@level2name=N'AK_Address_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Nonclustered index.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Address', @level2type=N'INDEX',@level2name=N'IX_Address_AddressLine1_AddressLine2_City_StateProvince_PostalCode_CountryRegion'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Nonclustered index.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Address', @level2type=N'INDEX',@level2name=N'IX_Address_StateProvince'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Street address information for customers.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Address'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key for Customer records.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'COLUMN',@level2name=N'CustomerID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'0 = The data in FirstName and LastName are stored in western style (first name, last name) order.  1 = Eastern style (last name, first name) order.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'COLUMN',@level2name=N'NameStyle'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of 0' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'CONSTRAINT',@level2name=N'DF_Customer_NameStyle'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'A courtesy title. For example, Mr. or Ms.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'COLUMN',@level2name=N'Title'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'First name of the person.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'COLUMN',@level2name=N'FirstName'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Middle name or middle initial of the person.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'COLUMN',@level2name=N'MiddleName'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Last name of the person.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'COLUMN',@level2name=N'LastName'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Surname suffix. For example, Sr. or Jr.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'COLUMN',@level2name=N'Suffix'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'The customer''s organization.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'COLUMN',@level2name=N'CompanyName'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'The customer''s sales person, an employee of AdventureWorks Cycles.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'COLUMN',@level2name=N'SalesPerson'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'E-mail address for the person.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'COLUMN',@level2name=N'EmailAddress'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Phone number associated with the person.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'COLUMN',@level2name=N'Phone'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Password for the e-mail account.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'COLUMN',@level2name=N'PasswordHash'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Random value concatenated with the password string before the password is hashed.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'COLUMN',@level2name=N'PasswordSalt'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'COLUMN',@level2name=N'rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of NEWID()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'CONSTRAINT',@level2name=N'DF_Customer_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Date and time the record was last updated.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'COLUMN',@level2name=N'ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of GETDATE()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'CONSTRAINT',@level2name=N'DF_Customer_ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key (clustered) constraint' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'CONSTRAINT',@level2name=N'PK_Customer_CustomerID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique nonclustered constraint. Used to support replication samples.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'CONSTRAINT',@level2name=N'AK_Customer_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Nonclustered index.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer', @level2type=N'INDEX',@level2name=N'IX_Customer_EmailAddress'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Customer information.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Customer'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key. Foreign key to Customer.CustomerID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'CustomerAddress', @level2type=N'COLUMN',@level2name=N'CustomerID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key. Foreign key to Address.AddressID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'CustomerAddress', @level2type=N'COLUMN',@level2name=N'AddressID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'The kind of Address. One of: Archive, Billing, Home, Main Office, Primary, Shipping' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'CustomerAddress', @level2type=N'COLUMN',@level2name=N'AddressType'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'CustomerAddress', @level2type=N'COLUMN',@level2name=N'rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of NEWID()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'CustomerAddress', @level2type=N'CONSTRAINT',@level2name=N'DF_CustomerAddress_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Date and time the record was last updated.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'CustomerAddress', @level2type=N'COLUMN',@level2name=N'ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key (clustered) constraint' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'CustomerAddress', @level2type=N'CONSTRAINT',@level2name=N'PK_CustomerAddress_CustomerID_AddressID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique nonclustered constraint. Used to support replication samples.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'CustomerAddress', @level2type=N'CONSTRAINT',@level2name=N'AK_CustomerAddress_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Cross-reference table mapping customers to their address(es).' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'CustomerAddress'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Foreign key constraint referencing Address.AddressID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'CustomerAddress', @level2type=N'CONSTRAINT',@level2name=N'FK_CustomerAddress_Address_AddressID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Foreign key constraint referencing Customer.CustomerID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'CustomerAddress', @level2type=N'CONSTRAINT',@level2name=N'FK_CustomerAddress_Customer_CustomerID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key for Product records.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'ProductID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Name of the product.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'Name'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique product identification number.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'ProductNumber'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Product color.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'Color'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Standard cost of the product.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'StandardCost'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Selling price.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'ListPrice'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Product size.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'Size'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Product weight.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'Weight'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Product is a member of this product category. Foreign key to ProductCategory.ProductCategoryID. ' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'ProductCategoryID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Product is a member of this product model. Foreign key to ProductModel.ProductModelID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'ProductModelID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Date the product was available for sale.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'SellStartDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Date the product was no longer available for sale.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'SellEndDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Date the product was discontinued.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'DiscontinuedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Small image of the product.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'ThumbNailPhoto'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Small image file name.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'ThumbnailPhotoFileName'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of NEWID()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'CONSTRAINT',@level2name=N'DF_Product_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Date and time the record was last updated.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'COLUMN',@level2name=N'ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of GETDATE()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'CONSTRAINT',@level2name=N'DF_Product_ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key (clustered) constraint' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'CONSTRAINT',@level2name=N'PK_Product_ProductID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique nonclustered constraint.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'CONSTRAINT',@level2name=N'AK_Product_Name'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique nonclustered constraint.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'CONSTRAINT',@level2name=N'AK_Product_ProductNumber'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique nonclustered constraint. Used to support replication samples.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'CONSTRAINT',@level2name=N'AK_Product_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Products sold or used in the manfacturing of sold products.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Foreign key constraint referencing ProductCategory.ProductCategoryID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'CONSTRAINT',@level2name=N'FK_Product_ProductCategory_ProductCategoryID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Foreign key constraint referencing ProductModel.ProductModelID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'CONSTRAINT',@level2name=N'FK_Product_ProductModel_ProductModelID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Check constraint [ListPrice] >= (0.00)' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'CONSTRAINT',@level2name=N'CK_Product_ListPrice'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Check constraint [SellEndDate] >= [SellStartDate] OR [SellEndDate] IS NULL' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'CONSTRAINT',@level2name=N'CK_Product_SellEndDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Check constraint [Weight] > (0.00)' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'Product', @level2type=N'CONSTRAINT',@level2name=N'CK_Product_Weight'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key for ProductCategory records.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductCategory', @level2type=N'COLUMN',@level2name=N'ProductCategoryID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Product category identification number of immediate ancestor category. Foreign key to ProductCategory.ProductCategoryID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductCategory', @level2type=N'COLUMN',@level2name=N'ParentProductCategoryID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Category description.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductCategory', @level2type=N'COLUMN',@level2name=N'Name'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductCategory', @level2type=N'COLUMN',@level2name=N'rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of NEWID()()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductCategory', @level2type=N'CONSTRAINT',@level2name=N'DF_ProductCategory_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Date and time the record was last updated.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductCategory', @level2type=N'COLUMN',@level2name=N'ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of GETDATE()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductCategory', @level2type=N'CONSTRAINT',@level2name=N'DF_ProductCategory_ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key (clustered) constraint' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductCategory', @level2type=N'CONSTRAINT',@level2name=N'PK_ProductCategory_ProductCategoryID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique nonclustered constraint.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductCategory', @level2type=N'CONSTRAINT',@level2name=N'AK_ProductCategory_Name'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique nonclustered constraint. Used to support replication samples.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductCategory', @level2type=N'CONSTRAINT',@level2name=N'AK_ProductCategory_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'High-level product categorization.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductCategory'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Foreign key constraint referencing ProductCategory.ProductCategoryID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductCategory', @level2type=N'CONSTRAINT',@level2name=N'FK_ProductCategory_ProductCategory_ParentProductCategoryID_ProductCategoryID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key for ProductDescription records.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductDescription', @level2type=N'COLUMN',@level2name=N'ProductDescriptionID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Description of the product.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductDescription', @level2type=N'COLUMN',@level2name=N'Description'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductDescription', @level2type=N'COLUMN',@level2name=N'rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of NEWID()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductDescription', @level2type=N'CONSTRAINT',@level2name=N'DF_ProductDescription_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Date and time the record was last updated.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductDescription', @level2type=N'COLUMN',@level2name=N'ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of GETDATE()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductDescription', @level2type=N'CONSTRAINT',@level2name=N'DF_ProductDescription_ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key (clustered) constraint' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductDescription', @level2type=N'CONSTRAINT',@level2name=N'PK_ProductDescription_ProductDescriptionID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique nonclustered constraint. Used to support replication samples.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductDescription', @level2type=N'CONSTRAINT',@level2name=N'AK_ProductDescription_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Product descriptions in several languages.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductDescription'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of NEWID()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductModel', @level2type=N'CONSTRAINT',@level2name=N'DF_ProductModel_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of GETDATE()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductModel', @level2type=N'CONSTRAINT',@level2name=N'DF_ProductModel_ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key (clustered) constraint' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductModel', @level2type=N'CONSTRAINT',@level2name=N'PK_ProductModel_ProductModelID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique nonclustered constraint.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductModel', @level2type=N'CONSTRAINT',@level2name=N'AK_ProductModel_Name'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique nonclustered constraint. Used to support replication samples.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductModel', @level2type=N'CONSTRAINT',@level2name=N'AK_ProductModel_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key. Foreign key to ProductModel.ProductModelID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductModelProductDescription', @level2type=N'COLUMN',@level2name=N'ProductModelID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key. Foreign key to ProductDescription.ProductDescriptionID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductModelProductDescription', @level2type=N'COLUMN',@level2name=N'ProductDescriptionID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'The culture for which the description is written' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductModelProductDescription', @level2type=N'COLUMN',@level2name=N'Culture'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Date and time the record was last updated.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductModelProductDescription', @level2type=N'COLUMN',@level2name=N'ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of GETDATE()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductModelProductDescription', @level2type=N'CONSTRAINT',@level2name=N'DF_ProductModelProductDescription_ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key (clustered) constraint' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductModelProductDescription', @level2type=N'CONSTRAINT',@level2name=N'PK_ProductModelProductDescription_ProductModelID_ProductDescriptionID_Culture'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique nonclustered constraint. Used to support replication samples.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductModelProductDescription', @level2type=N'CONSTRAINT',@level2name=N'AK_ProductModelProductDescription_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Cross-reference table mapping product descriptions and the language the description is written in.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductModelProductDescription'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Foreign key constraint referencing ProductDescription.ProductDescriptionID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductModelProductDescription', @level2type=N'CONSTRAINT',@level2name=N'FK_ProductModelProductDescription_ProductDescription_ProductDescriptionID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Foreign key constraint referencing ProductModel.ProductModelID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'ProductModelProductDescription', @level2type=N'CONSTRAINT',@level2name=N'FK_ProductModelProductDescription_ProductModel_ProductModelID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key. Foreign key to SalesOrderHeader.SalesOrderID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'COLUMN',@level2name=N'SalesOrderID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key. One incremental unique number per product sold.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'COLUMN',@level2name=N'SalesOrderDetailID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Quantity ordered per product.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'COLUMN',@level2name=N'OrderQty'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Product sold to customer. Foreign key to Product.ProductID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'COLUMN',@level2name=N'ProductID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Selling price of a single product.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'COLUMN',@level2name=N'UnitPrice'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Discount amount.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'COLUMN',@level2name=N'UnitPriceDiscount'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of 0.0' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'CONSTRAINT',@level2name=N'DF_SalesOrderDetail_UnitPriceDiscount'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Per product subtotal. Computed as UnitPrice * (1 - UnitPriceDiscount) * OrderQty.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'COLUMN',@level2name=N'LineTotal'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'COLUMN',@level2name=N'rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of NEWID()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'CONSTRAINT',@level2name=N'DF_SalesOrderDetail_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Date and time the record was last updated.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'COLUMN',@level2name=N'ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of GETDATE()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'CONSTRAINT',@level2name=N'DF_SalesOrderDetail_ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key (clustered) constraint' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'CONSTRAINT',@level2name=N'PK_SalesOrderDetail_SalesOrderID_SalesOrderDetailID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique nonclustered constraint. Used to support replication samples.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'CONSTRAINT',@level2name=N'AK_SalesOrderDetail_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Nonclustered index.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'INDEX',@level2name=N'IX_SalesOrderDetail_ProductID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Individual products associated with a specific sales order. See SalesOrderHeader.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Foreign key constraint referencing SalesOrderHeader.SalesOrderID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'CONSTRAINT',@level2name=N'FK_SalesOrderDetail_SalesOrderHeader_SalesOrderID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Check constraint [OrderQty] > (0)' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'CONSTRAINT',@level2name=N'CK_SalesOrderDetail_OrderQty'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Check constraint [UnitPrice] >= (0.00)' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'CONSTRAINT',@level2name=N'CK_SalesOrderDetail_UnitPrice'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Check constraint [UnitPriceDiscount] >= (0.00)' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderDetail', @level2type=N'CONSTRAINT',@level2name=N'CK_SalesOrderDetail_UnitPriceDiscount'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'SalesOrderID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Incremental number to track changes to the sales order over time.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'RevisionNumber'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of 0' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'DF_SalesOrderHeader_RevisionNumber'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Dates the sales order was created.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'OrderDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of GETDATE()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'DF_SalesOrderHeader_OrderDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Date the order is due to the customer.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'DueDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Date the order was shipped to the customer.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'ShipDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Order current status. 1 = In process; 2 = Approved; 3 = Backordered; 4 = Rejected; 5 = Shipped; 6 = Cancelled' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'Status'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of 1' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'DF_SalesOrderHeader_Status'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'0 = Order placed by sales person. 1 = Order placed online by customer.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'OnlineOrderFlag'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of 1 (TRUE)' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'DF_SalesOrderHeader_OnlineOrderFlag'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique sales order identification number.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'SalesOrderNumber'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Customer purchase order number reference. ' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'PurchaseOrderNumber'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Financial accounting number reference.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'AccountNumber'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Customer identification number. Foreign key to Customer.CustomerID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'CustomerID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'The ID of the location to send goods.  Foreign key to the Address table.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'ShipToAddressID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'The ID of the location to send invoices.  Foreign key to the Address table.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'BillToAddressID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Shipping method. Foreign key to ShipMethod.ShipMethodID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'ShipMethod'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Approval code provided by the credit card company.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'CreditCardApprovalCode'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Sales subtotal. Computed as SUM(SalesOrderDetail.LineTotal)for the appropriate SalesOrderID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'SubTotal'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of 0.0' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'DF_SalesOrderHeader_SubTotal'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Tax amount.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'TaxAmt'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of 0.0' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'DF_SalesOrderHeader_TaxAmt'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Shipping cost.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'Freight'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of 0.0' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'DF_SalesOrderHeader_Freight'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Total due from customer. Computed as Subtotal + TaxAmt + Freight.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'TotalDue'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Sales representative comments.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'Comment'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of NEWID()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'DF_SalesOrderHeader_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Date and time the record was last updated.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'COLUMN',@level2name=N'ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Default constraint value of GETDATE()' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'DF_SalesOrderHeader_ModifiedDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Primary key (clustered) constraint' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'PK_SalesOrderHeader_SalesOrderID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique nonclustered constraint. Used to support replication samples.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'AK_SalesOrderHeader_rowguid'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Unique nonclustered constraint.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'AK_SalesOrderHeader_SalesOrderNumber'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Nonclustered index.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'INDEX',@level2name=N'IX_SalesOrderHeader_CustomerID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'General sales order information.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Foreign key constraint referencing Address.AddressID for BillTo.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'FK_SalesOrderHeader_Address_BillTo_AddressID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Foreign key constraint referencing Address.AddressID for ShipTo.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'FK_SalesOrderHeader_Address_ShipTo_AddressID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Foreign key constraint referencing Customer.CustomerID.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'FK_SalesOrderHeader_Customer_CustomerID'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Check constraint [DueDate] >= [OrderDate]' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'CK_SalesOrderHeader_DueDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Check constraint [Freight] >= (0.00)' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'CK_SalesOrderHeader_Freight'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Check constraint [ShipDate] >= [OrderDate] OR [ShipDate] IS NULL' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'CK_SalesOrderHeader_ShipDate'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Check constraint [Status] BETWEEN (0) AND (8)' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'CK_SalesOrderHeader_Status'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Check constraint [SubTotal] >= (0.00)' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'CK_SalesOrderHeader_SubTotal'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Check constraint [TaxAmt] >= (0.00)' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'TABLE',@level1name=N'SalesOrderHeader', @level2type=N'CONSTRAINT',@level2name=N'CK_SalesOrderHeader_TaxAmt'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Clustered index on the view vProductAndDescription.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'VIEW',@level1name=N'vProductAndDescription', @level2type=N'INDEX',@level2name=N'IX_vProductAndDescription'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Product names and descriptions. Product descriptions are provided in multiple languages.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'VIEW',@level1name=N'vProductAndDescription'
GO
EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'Displays the content from each element in the xml column CatalogDescription for each product in the Sales.ProductModel table that has catalog data.' , @level0type=N'SCHEMA',@level0name=N'SalesLT', @level1type=N'VIEW',@level1name=N'vProductModelCatalogDescription'
GO
