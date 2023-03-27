SELECT*FROM orders; # In this table we can see the orders present in every year (2021,2022,2023)

SELECT COUNT(*) as total_orders_2021 FROM orders WHERE YEAR (orderDate) = 2021;
SELECT COUNT(*) as total_orders_2022 FROM orders WHERE YEAR (orderDate) = 2022;
SELECT COUNT(*) as total_orders_2023 FROM orders WHERE YEAR (orderDate) = 2023;

 /** In this phase we expanded the table "Order Details" so that we can see both sales numbers and sales quantities (by date) within the same table**/
 
SELECT month(orderDate), year(orderDate), sum(orderdetails.quantityOrdered*orderdetails.priceEach), productLine FROM orders
JOIN orderdetails ON orders.ordernumber = orderdetails.ordernumber
JOIN products ON orderdetails.productCode = products.productCode
GROUP BY year(orderDate), month(orderDate), productLine;

/** Here we will modify the table in order to include the exchange rates per category**/

with aggregated_data as (
    select month(o.orderDate)                       as month
    , year(o.orderDate)                             as year
    , sum(d.quantityOrdered * d.priceEach)           as sales
    , p.productLine                                 as productLine
    from orders o
    join orderdetails d on o.orderNumber = d.orderNumber
    join products p on d.productCode = p.productCode
    group by month(o.orderDate), year(o.orderDate), p.productLine  

)
select currentYear.month as month
, currentYear.year as year
, currentYear.sales as sales
, currentYear.productLine  as productLine
, lastYear.sales as last_year_sales
, if(lastYear.sales is null or lastYear.sales = 0 , 0, 
(((currentYear.sales - lastYear.sales) / lastYear.sales) *100) ) as exchange_Rate
from aggregated_data currentYear
left join aggregated_data lastYear on currentYear.month = lastYear.month 
                    and currentYear.year -1 = lastYear.year
                    and currentYear.productLine = lastYear.productLine
                    
/** In comparison with the year of 2021 (the previous table uses the previous year as reference year)**/

with aggregated_data as (
    select month(o.orderDate)                       as month
    , year(o.orderDate)                             as year
    , sum(d.quantityOrdered * d.priceEach)           as sales
    , p.productLine                                 as productLine
    from orders o
    join orderdetails d on o.orderNumber = d.orderNumber
    join products p on d.productCode = p.productCode
    group by month(o.orderDate), year(o.orderDate), p.productLine  

)
select currentYear.month as month
, currentYear.year as year
, currentYear.sales as sales
, currentYear.productLine  as productLine
, referenceYear.year as Reference_Year
, referenceYear.sales as reference_Year_sales
, if(referenceYear.sales is null or referenceYear.sales = 0 , 0, 
(((currentYear.sales - referenceYear.sales) / referenceYear.sales) *100) ) as exchange_Rate
from aggregated_data currentYear
left join aggregated_data referenceYear on currentYear.month = referenceYear.month 
                    and 2021 = referenceYear.year
                    and currentYear.productLine = referenceYear.productLine
