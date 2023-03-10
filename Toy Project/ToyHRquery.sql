#HR KPI:Monthly, the 2 sellers with the highest turnover

select employeeNumber, firstName from employees order by employeeNumber desc;
select customerNumber, salesRepEmployeeNumber from customers 
where salesRepEmployeeNumber is not null;
select ordernumber, customerNumber from orders;
select ordernumber, productCode, quantityordered, priceEach from orderdetails;
select productCode, quantityinstock, MSRP from products;

