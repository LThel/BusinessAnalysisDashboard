-- 5 most ordered products with products joined
Use toys_and_models;
SELECT o.productCode, -- product codes on orderdetails table
	sum(quantityOrdered) as Total_Quantity, -- sum of all orders quantity w/ this product code
	quantityInStock -- quantity in stock on products table 
FROM orderdetails as o 
JOIN products as p on p.productCode = o.productCode
GROUP BY productCode 
ORDER BY Total_Quantity desc
LIMIT 5;









