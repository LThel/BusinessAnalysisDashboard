#HR KPI:Monthly, the 2 sellers with the highest turnover
#just checking for changes
#just checking for changes in GitHub
#just checking for changes
select employeeNumber, firstName from employees order by employeeNumber desc;
select customerNumber, salesRepEmployeeNumber from customers 
where salesRepEmployeeNumber is not null;
#just checking for changes
select ordernumber, customerNumber from orders;
#just checking for changes in GitHub
select ordernumber, productCode, quantityordered, priceEach from orderdetails;
select productCode, quantityinstock, MSRP from products;
#just checking for changes
select productCode, quantityinstock, MSRP from products;

