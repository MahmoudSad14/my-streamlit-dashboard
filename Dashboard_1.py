# Dashboard_1
import streamlit as st
import pandas as pd
import pyodbc

# Connection parameters
server = '192.168.0.188\\MSSQLSERVER1'
database = 'SDM_PROD'
username = 'sdm_prod'
password = '|DaBa@20$88KiSm}'

conn_str = (
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
    f'TrustServerCertificate=Yes;'
)

conn = pyodbc.connect(conn_str)

# SQL Queries
sql_query_brand_performance = """
SELECT
    CASE WHEN GROUPING(CON_NAME) = 1 THEN 'Total' ELSE CON_NAME END AS Brand,
    COUNT(DISTINCT ORDR_STOREID) AS Active_Store,
    COUNT(DISTINCT ORDR_ID) AS TRX,
    COUNT(DISTINCT CASE WHEN ODRSTS_NAME IN ('Closed', 'Force Closed') THEN ORDR_ID END) AS Closed_TRX,
    CAST(SUM(ORDR_SALES_AMOUNT) AS INT) AS SALES,
    CAST(SUM(CASE WHEN ODRSTS_NAME IN ('Closed', 'Force Closed') THEN ORDR_SALES_AMOUNT END) AS INT) AS Closed_Sales,
    FORMAT(SUM(ORDR_SALES_AMOUNT) / NULLIF(COUNT(DISTINCT ORDR_ID), 0), 'N1') AS GCA,
    FORMAT(SUM(CASE WHEN ODRSTS_NAME IN ('Closed', 'Force Closed') THEN ORDR_SALES_AMOUNT END) / NULLIF(COUNT(DISTINCT CASE WHEN ODRSTS_NAME IN ('Closed', 'Force Closed') THEN ORDR_ID END), 0), 'N1') AS Closed_GCA,
    COUNT(DISTINCT CASE WHEN ODRSTS_NAME IN ('Future','In Kitchen','Ready','Request for cancel','Suspended','Assigned','Dispatched') THEN ORDR_ID END) AS Total_Pending,
    COUNT(DISTINCT CASE WHEN ODRSTS_NAME IN ('Future','In Kitchen','Ready','Request for cancel','Suspended') THEN ORDR_ID END) AS Store_Pending,
    COUNT(DISTINCT CASE WHEN ODRSTS_NAME ='In Kitchen' THEN ORDR_ID END) AS In_Kitchen
FROM
    CC_ORDER ord
LEFT OUTER JOIN 
    CC_CONCEPT CPT ON CON_ID = ORDR_CONCEPTID
LEFT OUTER JOIN 
    CC_ORDER_STATUS ON ODRSTS_CODE = ORDR_STATUS
WHERE
    ORDR_STATUS NOT IN (512, 8192) 
    AND ORDR_TOTAL >= 0 
    AND CONVERT(DATETIME, ORDR_DOB, 112) BETWEEN CONVERT(DATE, DATEADD(dd, 0, GETDATE()), 112) AND CONVERT(DATE, DATEADD(dd, 0, GETDATE()), 112)
GROUP BY
    CON_NAME WITH ROLLUP
ORDER BY
    CASE WHEN CON_NAME = 'Burger King' THEN 1
         WHEN CON_NAME = 'Pizza Hut' THEN 2
         WHEN CON_NAME = 'Subway' THEN 3
         WHEN CON_NAME = 'Taco Bell' THEN 4
         WHEN CON_NAME = 'Kababji KW' THEN 5
         WHEN CON_NAME = 'APB' THEN 6
         ELSE 7 END;
"""

sql_query_Burger_King_performance_top_5_stores = """
SELECT Top 6
    CASE WHEN ORDR_STOREname IS NULL THEN 'Total_Brand' ELSE ORDR_STOREname END AS ORDR_STOREname,
    COUNT(DISTINCT CASE WHEN ODRSTS_NAME IN ('Future','In Kitchen','Ready','Request for cancel','Suspended','Assigned','Dispatched') THEN ORDR_ID END) AS Total_Pending,
    COUNT(DISTINCT CASE WHEN ODRSTS_NAME IN ('Future','In Kitchen','Ready','Request for cancel','Suspended') THEN ORDR_ID END) AS Store_Pending,
    COUNT(DISTINCT CASE WHEN ODRSTS_NAME ='In Kitchen' THEN ORDR_ID END) AS In_Kitchen
FROM
    CC_ORDER ord
LEFT OUTER JOIN 
    CC_CONCEPT CPT ON CPT.CON_ID = ord.ORDR_CONCEPTID
LEFT OUTER JOIN 
    CC_ORDER_STATUS ON CC_ORDER_STATUS.ODRSTS_CODE = ord.ORDR_STATUS
WHERE
    ord.ORDR_STATUS NOT IN (512, 8192) 
    AND ord.ORDR_TOTAL >= 0   
    AND CPT.CON_NAME = 'Burger King' 
    AND CONVERT(DATETIME, ord.ORDR_DOB, 112) BETWEEN CONVERT(DATE, DATEADD(dd, 0, GETDATE()), 112) AND CONVERT(DATE, DATEADD(dd, 0, GETDATE()), 112)
GROUP BY
    ORDR_STOREname WITH ROLLUP
ORDER BY
    Total_Pending DESC;
"""

sql_query_pizza_hut_performance_top_5_stores = """
SELECT Top 6
    CASE WHEN ORDR_STOREname IS NULL THEN 'Total_Brand' ELSE ORDR_STOREname END AS ORDR_STOREname,
    COUNT(DISTINCT CASE WHEN ODRSTS_NAME IN ('Future','In Kitchen','Ready','Request for cancel','Suspended','Assigned','Dispatched') THEN ORDR_ID END) AS Total_Pending,
    COUNT(DISTINCT CASE WHEN ODRSTS_NAME IN ('Future','In Kitchen','Ready','Request for cancel','Suspended') THEN ORDR_ID END) AS Store_Pending,
    COUNT(DISTINCT CASE WHEN ODRSTS_NAME ='In Kitchen' THEN ORDR_ID END) AS In_Kitchen
FROM
    CC_ORDER ord
LEFT OUTER JOIN 
    CC_CONCEPT CPT ON CPT.CON_ID = ord.ORDR_CONCEPTID
LEFT OUTER JOIN 
    CC_ORDER_STATUS ON CC_ORDER_STATUS.ODRSTS_CODE = ord.ORDR_STATUS
WHERE
    ord.ORDR_STATUS NOT IN (512, 8192) 
    AND ord.ORDR_TOTAL >= 0   
    AND CPT.CON_NAME = 'Pizza Hut' 
    AND CONVERT(DATETIME, ord.ORDR_DOB, 112) BETWEEN CONVERT(DATE, DATEADD(dd, 0, GETDATE()), 112) AND CONVERT(DATE, DATEADD(dd, 0, GETDATE()), 112)
GROUP BY
    ORDR_STOREname WITH ROLLUP
ORDER BY
    Total_Pending DESC;
"""

# Fetch and display data
def fetch_data(query):
    return pd.read_sql(query, conn)

# Streamlit dashboard
st.title("Brand and Store Performance Dashboard")

# Display general brand performance
st.header("General Brand Performance")
brand_performance_data = fetch_data(sql_query_brand_performance)
st.dataframe(brand_performance_data)

# Display top 5 stores for Burger King
st.header("Top 5 Stores - Burger King")
burger_king_data = fetch_data(sql_query_Burger_King_performance_top_5_stores)
st.dataframe(burger_king_data)

# Display top 5 stores for Pizza Hut
st.header("Top 5 Stores - Pizza Hut")
pizza_hut_data = fetch_data(sql_query_pizza_hut_performance_top_5_stores)
st.dataframe(pizza_hut_data)