use toys_and_models;

-- Number of Command and the total ammount due per customerNumber
select c.country, # select the country because we want to see the amount per country
sum(od.quantityOrdered*od.priceEach) as amount_due, # calculate the amount (quantityOrdered * priceEach) to every orderLineNumber and then sum it (the idea is then to group it per country)
count(od.orderNumber) as Number_of_orders  #count the number of orders (the idea is then to group it per country)
from orderdetails as od 
inner join orders as o on o.orderNumber = od.orderNumber 
inner join customers as c on o.customerNumber = c.customerNumber
where o.orderDate >=  (NOW() - INTERVAL 2 MONTH)  # I want only the last two months
group by c.country; # I want to get the information per country


-- To get the customers that still have some stuff to pay 
-- I am still wroking on this place to get a proper way than distinct to get this table and above all to try to link the payments with the orderNumber and not the customerNumber

select c.customerNumber, count(distinct(o.orderNumber)) as Number_of_Command, sum(distinct(od.priceEach*od.quantityOrdered)) as total_amount_due, sum(distinct(p.amount)) as amount_paid, ((sum(distinct(od.priceEach*od.quantityOrdered))) - (sum(distinct(p.amount)))) as Still_have_to_be_paid
from customers as c 
inner join orders as o on c.customerNumber = o.customerNumber
inner join orderdetails as od on o.orderNumber = od.orderNumber
inner join payments as p on c.customerNumber = p.customerNumber
group by c.customerNumber;


select * -- o.customerNumber, sum(od.quantityOrdered*od.priceEach) as amount_due, sum(p.amount)
from orderdetails as od
inner join orders as o on o.orderNumber = od.orderNumber
inner join payments as p on o.customerNumber = p.customerNumber ;
-- group by o.customerNumber;

select customerNumber, sum(amount) from payments group by customerNumber;