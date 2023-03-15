-- 5 most ordered products, with their stock quantity, their monthly average quantity ordered, estimation of how many month left we have with our stock

-- The action of every subquery is explain after the second bracket wich will appears in yellow if you dowload the file.

select p.productCode, AvgPerMonth.Total_Quantity_Ordered, p.quantityInStock,  AvgPerMonth.average_quantity_orders_by_month as Average_quantity_orders_by_month, quantityInStock/AvgPerMonth.average_quantity_orders_by_month as How_many_months_left_we_have -- The columns that I want to see
from (select od.productCode, (sum(od.quantityOrdered)/(count(distinct(month(o.orderDate)))*count(distinct(year(o.orderDate))))) as Average_quantity_orders_by_month, sum(od.quantityOrdered) as Total_Quantity_Ordered
from orders as o inner join orderdetails as od on o.orderNumber = od.orderNumber 
where od.productCode in (select odbis.productCode 
from (select od.productCode, sum(od.quantityOrdered) from orderdetails as od group by productCode order by sum(od.quantityOrdered) desc limit 5) -- Here, I get the top 5 most ordered products
as odbis) -- Here, I select the productCode of the top 5 most ordered products
group by productCode) as AvgPerMonth -- Here, I have the productCode of the top 5 and the monthly average number of orders for each product of the top 5
inner join products as p on p.productCode = AvgPerMonth.productCode -- Here I join the productCode to be able to display it in my result table
order by Total_Quantity_Ordered desc;





