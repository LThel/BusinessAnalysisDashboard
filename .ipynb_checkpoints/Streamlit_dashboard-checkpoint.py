import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy as sql
from collections import Counter
import mysql.connector

#Connect to Python
#connection = 'mysql://toyscie:WILD4Rdata!@51.178.25.157:23456/toys_and_models'
connection = mysql.connector.connect(user = 'toyscie', password = 'WILD4Rdata!', host = '51.178.25.157', port = '23456', database = 'toys_and_models', use_pure = True)
#sql_engine = sql.create_engine(connection)

#Connection to SQL
#Connect to finance query
query_finance1 = '''select c.country, # select the country because we want to see the amount per country
sum(od.quantityOrdered*od.priceEach) as amount_due, # calculate the amount (quantityOrdered * priceEach) to every orderLineNumber and then sum it (the idea is then to group it per country)
count(od.orderNumber) as Number_of_orders  #count the number of orders (the idea is then to group it per country)
from orderdetails as od 
inner join orders as o on o.orderNumber = od.orderNumber 
inner join customers as c on o.customerNumber = c.customerNumber
where o.orderDate >=  (NOW() - INTERVAL 2 MONTH)  # I want only the last two months
group by c.country; # I want to get the information per country'''



query_finance2 = '''with Finance_per_customer as (select o.customerNumber, c.phone, sum(od.quantityOrdered*od.priceEach) as Amount_that_have_to_be_paid, n.already_paid, (sum(od.quantityOrdered*od.priceEach) - n.already_paid) as Still_have_to_be_paid, round((((sum(od.quantityOrdered*od.priceEach) - n.already_paid)*100)/c.creditLimit)) as Proportion_of_credit_allows_already_reached, c.creditLimit
from orders as o
inner join orderdetails as od on o.orderNumber = od.orderNumber
inner join customers as c on o.customerNumber = c.customerNumber
inner join (select customerNumber, sum(amount) as already_paid
from payments group by customerNumber) as n on n.customerNumber = o.customerNumber #I did here a subquery to avoid the pollution by the differents paymentcheck and paymentDate
group by o.customerNumber)
Select * from Finance_per_customer as Fpc where Fpc.Still_have_to_be_paid <> 0; #Here is the where clause to only get the customers that still need to pay something'''

query_HR2 = '''with final_df as
(select concat(e.firstName,' ', e.lastName) as Employee_Name, e.employeeNumber, almFinal.Total_amount_of_money, almFinal.sales_rank, almFinal.month_year
from employees as e 
inner join 
(select almFinal.Employee_Number, almFinal.Total_amount_of_money, almFinal.month_year, 
rank () over (PARTITION BY almFinal.month_year ORDER BY almFinal.Total_amount_of_money DESC) as sales_rank
from
(SELECT almFinal.salesRepEmployeeNumber as Employee_Number, almFinal.amount_of_the_order_per_Employee as Total_amount_of_money, 
CONCAT(almFinal.month_of_order,'-',almFinal.year_of_order) as month_year
from (select c.salesRepEmployeeNumber, sum(apc.amount_of_the_order_per_customer) as amount_of_the_order_per_Employee, MONTH(apc.orderDate) as month_of_order, YEAR(apc.orderDate) as year_of_order
from customers as c
inner join 
(select o.customerNumber, o.orderDate as orderDate , sum(odBis.amount_of_the_order) as amount_of_the_order_per_customer
from orders as o
inner join (select orderNumber, sum(quantityOrdered*priceEach) as amount_of_the_order 
from orderdetails as od 
group by  od.orderNumber) as odBis
on o.orderNumber = odBis.orderNumber
group by o.orderDate, o.customerNumber) as apc
on c.customerNumber = apc.customerNumber
group by c.salesRepEmployeeNumber, MONTH(apc.orderDate), YEAR(apc.orderDate)) as almFinal) as almFinal) as almFinal 
on almFinal.Employee_Number = e.employeeNumber)
select * 
from final_df
where final_df.sales_rank = 1 OR final_df.sales_rank = 2
'''
HR_df = pd.read_sql_query(query_HR2, connection)
#HR_df = pd.read_csv('HR_tempo.csv')
#HR_df = HR_df.iloc[:,1:]

#Streamlite
st.set_page_config(
    page_title="Project 2 - Model company - Dashboarding ",
    page_icon=":smiley:",
    layout="wide",
)

dash = st.radio(
    "What dashboard do you want to see ?",
    ('Sales', 'Finance', 'Logistics', 'HR'))

 
#HR
if dash == 'HR':
    st.title('Welcome to the HR dashboard !')
    #Best employee
    top1 = HR_df.Employee_Name.value_counts().head(1).index
    st.write('Our best employee all time is', top1)
    
    #Select the name of the employee to see if he/she appears in the top2
    employee = st.selectbox(
    'Select the name of the employee to see if he/she appears in our monthly top 2',
    (HR_df.Employee_Name.unique()))
    st.write(employee, 'appears', HR_df['Employee_Name'][HR_df['Employee_Name']== employee].value_counts(), 'time in our monthly top 2.')
    
    #Select a date to see the top 2 employee
    date = st.selectbox(
    'Select the month to see the associated top 2 employees',
(HR_df.month_year.unique()))
    st.write('Our top 2 for the selected month are', HR_df['Employee_Name'][HR_df['month_year']== date])

