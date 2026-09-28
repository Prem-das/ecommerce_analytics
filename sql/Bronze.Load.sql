USE DataWareHouse2;
GO

-- ===============================================================================
-- Stored Procedure: bronze.load_bronze
-- Description: Truncates and bulk inserts Olist E-commerce dataset CSV files
--              into the Bronze layer using SQL Server 2017+ CSV formatting options.
-- ===============================================================================

CREATE OR ALTER PROCEDURE bronze.load_bronze AS 
BEGIN 
    DECLARE @start_time DATETIME, @end_time DATETIME, @batch_start_time DATETIME, @batch_end_time DATETIME;
    BEGIN TRY 
        SET @batch_start_time = GETDATE();
        PRINT '====================================';
        PRINT 'Loading Bronze Layer';
        PRINT '====================================';

        PRINT '------------------------------------';
        PRINT 'Loading Olist E-commerce Tables';
        PRINT '------------------------------------';

        -- 1. Customers Dataset
        SET @start_time = GETDATE();
        PRINT '>> Truncating Table: bronze.olist_customers_dataset';
        TRUNCATE TABLE bronze.olist_customers_dataset;
        PRINT '>> Inserting Data into: bronze.olist_customers_dataset';

        BULK INSERT bronze.olist_customers_dataset 
        FROM 'C:\Users\premk\OneDrive\Documents\ecommerce_analytics\data\raw\olist_customers_dataset.csv'
        WITH (
            FIRSTROW = 2,
            FORMAT = 'CSV',
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '0x0a',
            TABLOCK
        );
        SET @end_time = GETDATE();
        PRINT '>> Load Duration: ' + CAST(DATEDIFF(second, @start_time, @end_time) AS NVARCHAR) + ' seconds'; 
        PRINT '--------------';

        -- 2. Geolocation Dataset
        SET @start_time = GETDATE();
        PRINT '>> Truncating Table: bronze.olist_geolocation_dataset';
        TRUNCATE TABLE bronze.olist_geolocation_dataset;
        PRINT '>> Inserting Data into: bronze.olist_geolocation_dataset';

        BULK INSERT bronze.olist_geolocation_dataset 
        FROM 'C:\Users\premk\OneDrive\Documents\ecommerce_analytics\data\raw\olist_geolocation_dataset.csv'
        WITH (
            FIRSTROW = 2,
            FORMAT = 'CSV',
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '0x0a',
            TABLOCK
        );
        SET @end_time = GETDATE();
        PRINT '>> Load Duration: ' + CAST(DATEDIFF(second, @start_time, @end_time) AS NVARCHAR) + ' seconds'; 
        PRINT '--------------';

        -- 3. Order Items Dataset
        SET @start_time = GETDATE();
        PRINT '>> Truncating Table: bronze.olist_order_items_dataset';
        TRUNCATE TABLE bronze.olist_order_items_dataset;
        PRINT '>> Inserting Data into: bronze.olist_order_items_dataset';

        BULK INSERT bronze.olist_order_items_dataset 
        FROM 'C:\Users\premk\OneDrive\Documents\ecommerce_analytics\data\raw\olist_order_items_dataset.csv'
        WITH (
            FIRSTROW = 2,
            FORMAT = 'CSV',
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '0x0a',
            TABLOCK
        );
        SET @end_time = GETDATE();
        PRINT '>> Load Duration: ' + CAST(DATEDIFF(second, @start_time, @end_time) AS NVARCHAR) + ' seconds'; 
        PRINT '--------------';

        -- 4. Order Payments Dataset
        SET @start_time = GETDATE();
        PRINT '>> Truncating Table: bronze.olist_order_payments_dataset';
        TRUNCATE TABLE bronze.olist_order_payments_dataset;
        PRINT '>> Inserting Data into: bronze.olist_order_payments_dataset';

        BULK INSERT bronze.olist_order_payments_dataset 
        FROM 'C:\Users\premk\OneDrive\Documents\ecommerce_analytics\data\raw\olist_order_payments_dataset.csv'
        WITH (
            FIRSTROW = 2,
            FORMAT = 'CSV',
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '0x0a',
            TABLOCK
        );
        SET @end_time = GETDATE();
        PRINT '>> Load Duration: ' + CAST(DATEDIFF(second, @start_time, @end_time) AS NVARCHAR) + ' seconds'; 
        PRINT '--------------';

        -- 5. Order Reviews Dataset
        SET @start_time = GETDATE();
        PRINT '>> Truncating Table: bronze.olist_order_reviews_dataset';
        TRUNCATE TABLE bronze.olist_order_reviews_dataset;
        PRINT '>> Inserting Data into: bronze.olist_order_reviews_dataset';

        BULK INSERT bronze.olist_order_reviews_dataset 
        FROM 'C:\Users\premk\OneDrive\Documents\ecommerce_analytics\data\processed\problems_while_load\olist_order_reviews_dataset_clean.csv'
        WITH (
            FIRSTROW = 2,
            FORMAT = 'CSV',
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '0x0a',
            TABLOCK
        );
        SET @end_time = GETDATE();
        PRINT '>> Load Duration: ' + CAST(DATEDIFF(second, @start_time, @end_time) AS NVARCHAR) + ' seconds'; 
        PRINT '--------------';

        -- 6. Orders Dataset
        SET @start_time = GETDATE();
        PRINT '>> Truncating Table: bronze.olist_orders_dataset';
        TRUNCATE TABLE bronze.olist_orders_dataset;
        PRINT '>> Inserting Data into: bronze.olist_orders_dataset';

        BULK INSERT bronze.olist_orders_dataset 
        FROM 'C:\Users\premk\OneDrive\Documents\ecommerce_analytics\data\raw\olist_orders_dataset.csv'
        WITH (
            FIRSTROW = 2,
            FORMAT = 'CSV',
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '0x0a',
            TABLOCK
        );
        SET @end_time = GETDATE();
        PRINT '>> Load Duration: ' + CAST(DATEDIFF(second, @start_time, @end_time) AS NVARCHAR) + ' seconds'; 
        PRINT '--------------';

        -- 7. Products Dataset
        SET @start_time = GETDATE();
        PRINT '>> Truncating Table: bronze.olist_products_dataset';
        TRUNCATE TABLE bronze.olist_products_dataset;
        PRINT '>> Inserting Data into: bronze.olist_products_dataset';

        BULK INSERT bronze.olist_products_dataset 
        FROM 'C:\Users\premk\OneDrive\Documents\ecommerce_analytics\data\raw\olist_products_dataset.csv'
        WITH (
            FIRSTROW = 2,
            FORMAT = 'CSV',
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '0x0a',
            TABLOCK
        );
        SET @end_time = GETDATE();
        PRINT '>> Load Duration: ' + CAST(DATEDIFF(second, @start_time, @end_time) AS NVARCHAR) + ' seconds'; 
        PRINT '--------------';

        -- 8. Sellers Dataset
        SET @start_time = GETDATE();
        PRINT '>> Truncating Table: bronze.olist_sellers_dataset';
        TRUNCATE TABLE bronze.olist_sellers_dataset;
        PRINT '>> Inserting Data into: bronze.olist_sellers_dataset';

        BULK INSERT bronze.olist_sellers_dataset 
        FROM 'C:\Users\premk\OneDrive\Documents\ecommerce_analytics\data\raw\olist_sellers_dataset.csv'
        WITH (
            FIRSTROW = 2,
            FORMAT = 'CSV',
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '0x0a',
            TABLOCK
        );
        SET @end_time = GETDATE();
        PRINT '>> Load Duration: ' + CAST(DATEDIFF(second, @start_time, @end_time) AS NVARCHAR) + ' seconds'; 
        PRINT '--------------';

        -- 9. Product Category Name Translation Dataset
        SET @start_time = GETDATE();
        PRINT '>> Truncating Table: bronze.product_category_name_translation';
        TRUNCATE TABLE bronze.product_category_name_translation;
        PRINT '>> Inserting Data into: bronze.product_category_name_translation';

        BULK INSERT bronze.product_category_name_translation 
        FROM 'C:\Users\premk\OneDrive\Documents\ecommerce_analytics\data\raw\product_category_name_translation.csv'
        WITH (
            FIRSTROW = 2,
            FORMAT = 'CSV',
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '0x0a',
            TABLOCK
        );
        SET @end_time = GETDATE();
        PRINT '>> Load Duration: ' + CAST(DATEDIFF(second, @start_time, @end_time) AS NVARCHAR) + ' seconds'; 
        PRINT '--------------';

        SET @batch_end_time = GETDATE();
        PRINT '===================================================';
        PRINT 'Loading Bronze Layer is Completed';
        PRINT '   - Total Load Duration: ' + CAST(DATEDIFF(SECOND, @batch_start_time, @batch_end_time) AS NVARCHAR) + ' seconds';
        PRINT '===================================================';
    END TRY 
    BEGIN CATCH 
        PRINT '====================================================';
        PRINT 'ERROR OCCURRED DURING LOADING BRONZE LAYER';
        PRINT 'Error Message: ' + ERROR_MESSAGE();
        PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS NVARCHAR);
        PRINT '====================================================';
    END CATCH 
END;
GO