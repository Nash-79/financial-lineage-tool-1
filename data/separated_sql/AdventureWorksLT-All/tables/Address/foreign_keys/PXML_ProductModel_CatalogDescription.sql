-- ============================================
-- Object Type: Index
-- Constraint/Index Name: PXML_ProductModel_CatalogDescription
-- Parent Object: Address
-- Source File: AdventureWorksLT-All.sql
-- Script Date: 4/7/2021 10:02:56 AM
-- Separated On: 2025-12-08 20:25:14
-- ============================================

CREATE PRIMARY XML INDEX [PXML_ProductModel_CatalogDescription] ON [SalesLT].[ProductModel]
(
	[CatalogDescription]
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)
GO
ALTER TABLE [SalesLT].[Address] ADD  CONSTRAINT [DF_Address_rowguid]  DEFAULT (newid()) FOR [rowguid]
GO
ALTER TABLE [SalesLT].[Address] ADD  CONSTRAINT [DF_Address_ModifiedDate]  DEFAULT (getdate()) FOR [ModifiedDate]
GO
ALTER TABLE [SalesLT].[Customer] ADD  CONSTRAINT [DF_Customer_NameStyle]  DEFAULT ((0)) FOR [NameStyle]
GO
ALTER TABLE [SalesLT].[Customer] ADD  CONSTRAINT [DF_Customer_rowguid]  DEFAULT (newid()) FOR [rowguid]
GO
ALTER TABLE [SalesLT].[Customer] ADD  CONSTRAINT [DF_Customer_ModifiedDate]  DEFAULT (getdate()) FOR [ModifiedDate]
GO
ALTER TABLE [SalesLT].[CustomerAddress] ADD  CONSTRAINT [DF_CustomerAddress_rowguid]  DEFAULT (newid()) FOR [rowguid]
GO
ALTER TABLE [SalesLT].[CustomerAddress] ADD  CONSTRAINT [DF_CustomerAddress_ModifiedDate]  DEFAULT (getdate()) FOR [ModifiedDate]
GO
ALTER TABLE [SalesLT].[Product] ADD  CONSTRAINT [DF_Product_rowguid]  DEFAULT (newid()) FOR [rowguid]
GO
ALTER TABLE [SalesLT].[Product] ADD  CONSTRAINT [DF_Product_ModifiedDate]  DEFAULT (getdate()) FOR [ModifiedDate]
GO
ALTER TABLE [SalesLT].[ProductCategory] ADD  CONSTRAINT [DF_ProductCategory_rowguid]  DEFAULT (newid()) FOR [rowguid]
GO
ALTER TABLE [SalesLT].[ProductCategory] ADD  CONSTRAINT [DF_ProductCategory_ModifiedDate]  DEFAULT (getdate()) FOR [ModifiedDate]
GO
ALTER TABLE [SalesLT].[ProductDescription] ADD  CONSTRAINT [DF_ProductDescription_rowguid]  DEFAULT (newid()) FOR [rowguid]
GO
ALTER TABLE [SalesLT].[ProductDescription] ADD  CONSTRAINT [DF_ProductDescription_ModifiedDate]  DEFAULT (getdate()) FOR [ModifiedDate]
GO
ALTER TABLE [SalesLT].[ProductModel] ADD  CONSTRAINT [DF_ProductModel_rowguid]  DEFAULT (newid()) FOR [rowguid]
GO
ALTER TABLE [SalesLT].[ProductModel] ADD  CONSTRAINT [DF_ProductModel_ModifiedDate]  DEFAULT (getdate()) FOR [ModifiedDate]
GO
ALTER TABLE [SalesLT].[ProductModelProductDescription] ADD  CONSTRAINT [DF_ProductModelProductDescription_rowguid]  DEFAULT (newid()) FOR [rowguid]
GO
ALTER TABLE [SalesLT].[ProductModelProductDescription] ADD  CONSTRAINT [DF_ProductModelProductDescription_ModifiedDate]  DEFAULT (getdate()) FOR [ModifiedDate]
GO
ALTER TABLE [SalesLT].[SalesOrderDetail] ADD  CONSTRAINT [DF_SalesOrderDetail_UnitPriceDiscount]  DEFAULT ((0.0)) FOR [UnitPriceDiscount]
GO
ALTER TABLE [SalesLT].[SalesOrderDetail] ADD  CONSTRAINT [DF_SalesOrderDetail_rowguid]  DEFAULT (newid()) FOR [rowguid]
GO
ALTER TABLE [SalesLT].[SalesOrderDetail] ADD  CONSTRAINT [DF_SalesOrderDetail_ModifiedDate]  DEFAULT (getdate()) FOR [ModifiedDate]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] ADD  CONSTRAINT [DF_SalesOrderHeader_RevisionNumber]  DEFAULT ((0)) FOR [RevisionNumber]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] ADD  CONSTRAINT [DF_SalesOrderHeader_OrderDate]  DEFAULT (getdate()) FOR [OrderDate]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] ADD  CONSTRAINT [DF_SalesOrderHeader_Status]  DEFAULT ((1)) FOR [Status]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] ADD  CONSTRAINT [DF_SalesOrderHeader_OnlineOrderFlag]  DEFAULT ((1)) FOR [OnlineOrderFlag]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] ADD  CONSTRAINT [DF_SalesOrderHeader_SubTotal]  DEFAULT ((0.00)) FOR [SubTotal]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] ADD  CONSTRAINT [DF_SalesOrderHeader_TaxAmt]  DEFAULT ((0.00)) FOR [TaxAmt]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] ADD  CONSTRAINT [DF_SalesOrderHeader_Freight]  DEFAULT ((0.00)) FOR [Freight]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] ADD  CONSTRAINT [DF_SalesOrderHeader_rowguid]  DEFAULT (newid()) FOR [rowguid]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] ADD  CONSTRAINT [DF_SalesOrderHeader_ModifiedDate]  DEFAULT (getdate()) FOR [ModifiedDate]
GO
ALTER TABLE [SalesLT].[CustomerAddress]  WITH CHECK ADD  CONSTRAINT [FK_CustomerAddress_Address_AddressID] FOREIGN KEY([AddressID])
REFERENCES [SalesLT].[Address] ([AddressID])
GO
ALTER TABLE [SalesLT].[CustomerAddress] CHECK CONSTRAINT [FK_CustomerAddress_Address_AddressID]
GO
ALTER TABLE [SalesLT].[CustomerAddress]  WITH CHECK ADD  CONSTRAINT [FK_CustomerAddress_Customer_CustomerID] FOREIGN KEY([CustomerID])
REFERENCES [SalesLT].[Customer] ([CustomerID])
GO
ALTER TABLE [SalesLT].[CustomerAddress] CHECK CONSTRAINT [FK_CustomerAddress_Customer_CustomerID]
GO
ALTER TABLE [SalesLT].[Product]  WITH CHECK ADD  CONSTRAINT [FK_Product_ProductCategory_ProductCategoryID] FOREIGN KEY([ProductCategoryID])
REFERENCES [SalesLT].[ProductCategory] ([ProductCategoryID])
GO
ALTER TABLE [SalesLT].[Product] CHECK CONSTRAINT [FK_Product_ProductCategory_ProductCategoryID]
GO
ALTER TABLE [SalesLT].[Product]  WITH CHECK ADD  CONSTRAINT [FK_Product_ProductModel_ProductModelID] FOREIGN KEY([ProductModelID])
REFERENCES [SalesLT].[ProductModel] ([ProductModelID])
GO
ALTER TABLE [SalesLT].[Product] CHECK CONSTRAINT [FK_Product_ProductModel_ProductModelID]
GO
ALTER TABLE [SalesLT].[ProductCategory]  WITH CHECK ADD  CONSTRAINT [FK_ProductCategory_ProductCategory_ParentProductCategoryID_ProductCategoryID] FOREIGN KEY([ParentProductCategoryID])
REFERENCES [SalesLT].[ProductCategory] ([ProductCategoryID])
GO
ALTER TABLE [SalesLT].[ProductCategory] CHECK CONSTRAINT [FK_ProductCategory_ProductCategory_ParentProductCategoryID_ProductCategoryID]
GO
ALTER TABLE [SalesLT].[ProductModelProductDescription]  WITH CHECK ADD  CONSTRAINT [FK_ProductModelProductDescription_ProductDescription_ProductDescriptionID] FOREIGN KEY([ProductDescriptionID])
REFERENCES [SalesLT].[ProductDescription] ([ProductDescriptionID])
GO
ALTER TABLE [SalesLT].[ProductModelProductDescription] CHECK CONSTRAINT [FK_ProductModelProductDescription_ProductDescription_ProductDescriptionID]
GO
ALTER TABLE [SalesLT].[ProductModelProductDescription]  WITH CHECK ADD  CONSTRAINT [FK_ProductModelProductDescription_ProductModel_ProductModelID] FOREIGN KEY([ProductModelID])
REFERENCES [SalesLT].[ProductModel] ([ProductModelID])
GO
ALTER TABLE [SalesLT].[ProductModelProductDescription] CHECK CONSTRAINT [FK_ProductModelProductDescription_ProductModel_ProductModelID]
GO
ALTER TABLE [SalesLT].[SalesOrderDetail]  WITH CHECK ADD  CONSTRAINT [FK_SalesOrderDetail_Product_ProductID] FOREIGN KEY([ProductID])
REFERENCES [SalesLT].[Product] ([ProductID])
GO
ALTER TABLE [SalesLT].[SalesOrderDetail] CHECK CONSTRAINT [FK_SalesOrderDetail_Product_ProductID]
GO
ALTER TABLE [SalesLT].[SalesOrderDetail]  WITH CHECK ADD  CONSTRAINT [FK_SalesOrderDetail_SalesOrderHeader_SalesOrderID] FOREIGN KEY([SalesOrderID])
REFERENCES [SalesLT].[SalesOrderHeader] ([SalesOrderID])
ON DELETE CASCADE
GO
ALTER TABLE [SalesLT].[SalesOrderDetail] CHECK CONSTRAINT [FK_SalesOrderDetail_SalesOrderHeader_SalesOrderID]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader]  WITH CHECK ADD  CONSTRAINT [FK_SalesOrderHeader_Address_BillTo_AddressID] FOREIGN KEY([BillToAddressID])
REFERENCES [SalesLT].[Address] ([AddressID])
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] CHECK CONSTRAINT [FK_SalesOrderHeader_Address_BillTo_AddressID]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader]  WITH CHECK ADD  CONSTRAINT [FK_SalesOrderHeader_Address_ShipTo_AddressID] FOREIGN KEY([ShipToAddressID])
REFERENCES [SalesLT].[Address] ([AddressID])
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] CHECK CONSTRAINT [FK_SalesOrderHeader_Address_ShipTo_AddressID]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader]  WITH CHECK ADD  CONSTRAINT [FK_SalesOrderHeader_Customer_CustomerID] FOREIGN KEY([CustomerID])
REFERENCES [SalesLT].[Customer] ([CustomerID])
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] CHECK CONSTRAINT [FK_SalesOrderHeader_Customer_CustomerID]
GO
ALTER TABLE [SalesLT].[Product]  WITH CHECK ADD  CONSTRAINT [CK_Product_ListPrice] CHECK  (([ListPrice]>=(0.00)))
GO
ALTER TABLE [SalesLT].[Product] CHECK CONSTRAINT [CK_Product_ListPrice]
GO
ALTER TABLE [SalesLT].[Product]  WITH CHECK ADD  CONSTRAINT [CK_Product_SellEndDate] CHECK  (([SellEndDate]>=[SellStartDate] OR [SellEndDate] IS NULL))
GO
ALTER TABLE [SalesLT].[Product] CHECK CONSTRAINT [CK_Product_SellEndDate]
GO
ALTER TABLE [SalesLT].[Product]  WITH CHECK ADD  CONSTRAINT [CK_Product_StandardCost] CHECK  (([StandardCost]>=(0.00)))
GO
ALTER TABLE [SalesLT].[Product] CHECK CONSTRAINT [CK_Product_StandardCost]
GO
ALTER TABLE [SalesLT].[Product]  WITH CHECK ADD  CONSTRAINT [CK_Product_Weight] CHECK  (([Weight]>(0.00)))
GO
ALTER TABLE [SalesLT].[Product] CHECK CONSTRAINT [CK_Product_Weight]
GO
ALTER TABLE [SalesLT].[SalesOrderDetail]  WITH CHECK ADD  CONSTRAINT [CK_SalesOrderDetail_OrderQty] CHECK  (([OrderQty]>(0)))
GO
ALTER TABLE [SalesLT].[SalesOrderDetail] CHECK CONSTRAINT [CK_SalesOrderDetail_OrderQty]
GO
ALTER TABLE [SalesLT].[SalesOrderDetail]  WITH CHECK ADD  CONSTRAINT [CK_SalesOrderDetail_UnitPrice] CHECK  (([UnitPrice]>=(0.00)))
GO
ALTER TABLE [SalesLT].[SalesOrderDetail] CHECK CONSTRAINT [CK_SalesOrderDetail_UnitPrice]
GO
ALTER TABLE [SalesLT].[SalesOrderDetail]  WITH CHECK ADD  CONSTRAINT [CK_SalesOrderDetail_UnitPriceDiscount] CHECK  (([UnitPriceDiscount]>=(0.00)))
GO
ALTER TABLE [SalesLT].[SalesOrderDetail] CHECK CONSTRAINT [CK_SalesOrderDetail_UnitPriceDiscount]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader]  WITH CHECK ADD  CONSTRAINT [CK_SalesOrderHeader_DueDate] CHECK  (([DueDate]>=[OrderDate]))
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] CHECK CONSTRAINT [CK_SalesOrderHeader_DueDate]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader]  WITH CHECK ADD  CONSTRAINT [CK_SalesOrderHeader_Freight] CHECK  (([Freight]>=(0.00)))
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] CHECK CONSTRAINT [CK_SalesOrderHeader_Freight]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader]  WITH CHECK ADD  CONSTRAINT [CK_SalesOrderHeader_ShipDate] CHECK  (([ShipDate]>=[OrderDate] OR [ShipDate] IS NULL))
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] CHECK CONSTRAINT [CK_SalesOrderHeader_ShipDate]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader]  WITH CHECK ADD  CONSTRAINT [CK_SalesOrderHeader_Status] CHECK  (([Status]>=(0) AND [Status]<=(8)))
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] CHECK CONSTRAINT [CK_SalesOrderHeader_Status]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader]  WITH CHECK ADD  CONSTRAINT [CK_SalesOrderHeader_SubTotal] CHECK  (([SubTotal]>=(0.00)))
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] CHECK CONSTRAINT [CK_SalesOrderHeader_SubTotal]
GO
ALTER TABLE [SalesLT].[SalesOrderHeader]  WITH CHECK ADD  CONSTRAINT [CK_SalesOrderHeader_TaxAmt] CHECK  (([TaxAmt]>=(0.00)))
GO
ALTER TABLE [SalesLT].[SalesOrderHeader] CHECK CONSTRAINT [CK_SalesOrderHeader_TaxAmt]
GO
