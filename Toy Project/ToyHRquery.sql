#HR KPI:Monthly, the 2 sellers with the highest turnover
show databases;
use toys_and_models;
#show tables;
select count(employeeNumber) from employees; #there are 23 Emp#
select salesrepemployeenumber, count(customername) from customers group by salesrepemployeenumber;#how many cs per sales rep?

select firstName, lastname as SalesRep, customerName #, orderNumber
from customers join employees on customers.salesRepEmployeeNumber = employees.employeeNumber
order by customerName;
#join orders on customers.customernumber = orders.customerNumber;

select firstName, lastname as SalesRep, customerName , orderDate, orderNumber
from customers join employees on customers.salesRepEmployeeNumber = employees.employeeNumber
join orders on customers.customernumber = orders.customerNumber
order by orderDate;

select orderNumber, sum(quantityOrdered*priceEach) as TotalAmount from orderdetails
group by orderNumber
order by orderNumber;

select ordernumber, productCode, quantityordered, priceEach from orderdetails;
select productCode, quantityinstock, MSRP from products;

select productCode, quantityinstock, MSRP from products;

