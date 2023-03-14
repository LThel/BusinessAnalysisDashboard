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


-- I did this to add the idea I told you yesterday (about having the average sales per months for the top 5 items to have a more precise idea about the stock left)

# I use subqueries as we saw today to build it => The action of the subquery is explain after the second bracket (I mean the bracket which the subquery)wich will appears in yellow if you dowload the file

select p.productCode, AvgPerMonth.Total_Quantity_Ordered, p.quantityInStock,  AvgPerMonth.average_quantity_orders_by_month as Average_quantity_orders_by_month, quantityInStock/AvgPerMonth.average_quantity_orders_by_month as How_many_months_left_we_have -- The columns that I want to see in my result table
from (select od.productCode, (sum(od.quantityOrdered)/(count(distinct(month(o.orderDate)))*count(distinct(year(o.orderDate))))) as Average_quantity_orders_by_month, sum(od.quantityOrdered) as Total_Quantity_Ordered
from orders as o inner join orderdetails as od on o.orderNumber = od.orderNumber 
where od.productCode in (select odbis.productCode 
from (select od.productCode, sum(od.quantityOrdered) from orderdetails as od group by productCode order by sum(od.quantityOrdered) desc limit 5) -- Here, I get the top 5 most ordered products
as odbis) -- Here, I select the productCode of the top 5 most ordered products
group by productCode) as AvgPerMonth -- Here, I have the productCode of the top 5 and the monthly average number of orders for each product of the top 5
inner join products as p on p.productCode = AvgPerMonth.productCode -- Here I join the productCode to be able to display it in my result table
order by Total_Quantity_Ordered desc;






