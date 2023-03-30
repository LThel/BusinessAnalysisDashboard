SELECT * FROM orders;
SHOW tables
DESCRIBE tables

/** Question to be answered **/
/** The number of products sold by category and by month, with comparison and rate of change compared to the same month of the previous year.**/

SELECT * FROM products;

/** By observing the available data we can classify the products by the following categories: 
1- product line (if it is a car, airplane, boat)
2- product scale (smallest to biggest, from 1:700 to 1:10)
3 -product vendor (basically the distributor) **/

/** Afterwards lets have a look at the monhtly sales figures **/

SELECT*FROM orders;

SELECT*FROM orders WHERE comments IS NOT NULL;

SELECT COUNT(*) FROM orders;

SELECT COUNT(*) FROM orders WHERE shippedDate BETWEEN '2021-01-01' AND '2021-12-31';

SELECT COUNT(*) FROM orders WHERE comments IS NOT NULL;

/** There are 283 orders in total. In 2021 there were 110, in 2022 there were 173**/

SELECT COUNT(*) FROM orders WHERE status = 'Shipped' AND shippedDate BETWEEN '2021-01-01' AND '2021-12-31';

SELECT COUNT(*) FROM orders WHERE status = 'Shipped' AND shippedDate BETWEEN '2022-01-01' AND '2022-12-31';

/**--------------------------------------------------------------------------------------------------------------**/

/** In 2021, there have been 108 shipped orders. In 2022 there have been 145 shipped orders**/

SELECT COUNT(*) FROM orders WHERE status = 'Cancelled' AND shippedDate BETWEEN '2021-01-01' AND '2021-12-31';

SELECT COUNT(*) FROM orders WHERE status = 'Cancelled' AND shippedDate BETWEEN '2022-01-01' AND '2022-12-31';

/**--------------------------------------------------------------------------------------------------------------**/

SELECT COUNT(*) FROM orders WHERE status = 'On Hold' AND shippedDate BETWEEN '2021-01-01' AND '2021-12-31';

SELECT COUNT(*) FROM orders WHERE status = 'On Hold' AND shippedDate BETWEEN '2021-01-01' AND '2021-12-31';

/**--------------------------------------------------------------------------------------------------------------**/

SELECT COUNT(*) FROM orders WHERE status = 'Resolved' AND shippedDate BETWEEN '2021-01-01' AND '2021-12-31';

SELECT COUNT(*) FROM orders WHERE status = 'Resolved' AND shippedDate BETWEEN '2021-01-01' AND '2021-12-31';