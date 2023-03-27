use toys_and_models;

-- Finance 1 - Number of Command and the total ammount due per customerNumber
select c.country, # select the country because we want to see the amount per country
sum(od.quantityOrdered*od.priceEach) as amount_due, # calculate the amount (quantityOrdered * priceEach) to every orderLineNumber and then sum it (the idea is then to group it per country)
count(od.orderNumber) as Number_of_orders  #count the number of orders (the idea is then to group it per country)
from orderdetails as od 
inner join orders as o on o.orderNumber = od.orderNumber 
inner join customers as c on o.customerNumber = c.customerNumber
where o.orderDate >=  (NOW() - INTERVAL 2 MONTH)  # I want only the last two months
group by c.country; # I want to get the information per country


-- Finance 2 - To get the customers that still have some stuff to pay 

# I use a with to create a temporary table to be able to put a where clause at the end
with Finance_per_customer as (select o.customerNumber, c.phone, sum(od.quantityOrdered*od.priceEach) as Amount_that_have_to_be_paid, n.already_paid, (sum(od.quantityOrdered*od.priceEach) - n.already_paid) as Still_have_to_be_paid, round((((sum(od.quantityOrdered*od.priceEach) - n.already_paid)*100)/c.creditLimit)) as Proportion_of_credit_allows_already_reached, c.creditLimit
from orders as o
inner join orderdetails as od on o.orderNumber = od.orderNumber
inner join customers as c on o.customerNumber = c.customerNumber
inner join (select customerNumber, sum(amount) as already_paid
from payments group by customerNumber) as n on n.customerNumber = o.customerNumber #I did here a subquery to avoid the pollution by the differents paymentcheck and paymentDate
group by o.customerNumber)
Select * from Finance_per_customer as Fpc where Fpc.Still_have_to_be_paid <> 0; #Here is the where clause to only get the customers that still need to pay something

#Here are the customerNumber which are not linked to any payment and to any order. I didn't find any explication about them yet.
# Here the customers that are not linked to any paymentpostalCode
select customerNumber from customers where not exists (SELECT checkNumber FROM payments where payments.customerNumber = customers.customerNumber); 
#But then, if you look for any command from them, you can't find anything.
select orders.orderNumber, orders.customerNumber, orders.status from orders where orders.customerNumber in (select customerNumber from customers where not exists (SELECT checkNumber FROM payments where payments.customerNumber = customers.customerNumber));