#HR KPI: Each monthly, the 2 sellers with the highest turnover
show databases;
use toys_and_models;
show tables;
#the sellers are found in employee table
SELECT lastname FROM employees; #23 rows returned
#sellers link to Total sales: Emp > Cs > Ord > OrdDet

select lastname as Seller, OrderNumber as Ord, quantityOrdered as Qts
from employees as Emp
join customers as Cs on Emp.employeeNumber = Cs.salesRepEmployeeNumber #Connect Sellers info to Cs info by the EmpNumb
join orders as Ords on Cs.customerNumber = Ords.customerNumber #Connect with Ords info by csNumb
join orderdetails as OrdDets on Ords.orderNumber = OrdDets.orderNumber; #Connect with OrdDets info (qty & prices) by
#group by lastname
#order by TotalAmount desc
#limit 2;

select lastname as Seller /**count(customerName), count(orderDate)**/ , sum(quantityOrdered*priceEach) as TotalAmount 
from employees as Emp
join customers as Cs on Emp.employeeNumber = Cs.salesRepEmployeeNumber #Connect Sellers info to Cs info by the EmpNumb
join orders as Ords on Cs.customerNumber = Ords.customerNumber #Connect with Ords info by csNumb
join orderdetails as OrdDets on Ords.orderNumber = OrdDets.orderNumber; #Connect with OrdDets info (qty & prices) by
#group by lastname
#order by TotalAmount desc
#limit 2;

select * from orderdetails;

select orderNumber, sum(quantityOrdered*priceEach) as TotalAmount from orderdetails
group by orderNumber
order by orderNumber;

select ordernumber, productCode, quantityordered, priceEach from orderdetails;
select productCode, quantityinstock, MSRP from products;

select productCode, quantityinstock, MSRP from products;