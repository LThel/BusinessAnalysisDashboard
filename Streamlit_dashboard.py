import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
#import sqlalchemy as sql
from collections import Counter
import mysql.connector
from datetime import datetime

#Connect to Python
#connection = 'mysql://toyscie:WILD4Rdata!@51.178.25.157:23456/toys_and_models'
connection = mysql.connector.connect(user = 'toyscie', password = 'WILD4Rdata!', host = '51.178.25.157', port = '23456', database = 'toys_and_models', use_pure = True)
#sql_engine = sql.create_engine(connection)

#Connection to SQL
#Connect to finance query
query_finance1 = '''select c.country, 
sum(od.quantityOrdered*od.priceEach) as amount_due, 
count(od.orderNumber) as Number_of_orders  
from orderdetails as od 
inner join orders as o on o.orderNumber = od.orderNumber 
inner join customers as c on o.customerNumber = c.customerNumber
where o.orderDate >=  (NOW() - INTERVAL 2 MONTH)  
group by c.country; '''



query_finance2 = '''with Finance_per_customer as (select o.customerNumber, c.phone, sum(od.quantityOrdered*od.priceEach) as Amount_that_have_to_be_paid, n.already_paid, (sum(od.quantityOrdered*od.priceEach) - n.already_paid) as Still_have_to_be_paid, round((((sum(od.quantityOrdered*od.priceEach) - n.already_paid)*100)/c.creditLimit)) as Proportion_of_credit_allows_already_reached, c.creditLimit
from orders as o
inner join orderdetails as od on o.orderNumber = od.orderNumber
inner join customers as c on o.customerNumber = c.customerNumber
inner join (select customerNumber, sum(amount) as already_paid
from payments group by customerNumber) as n on n.customerNumber = o.customerNumber #I did here a subquery to avoid the pollution by the differents paymentcheck and paymentDate
group by o.customerNumber)
Select * from Finance_per_customer as Fpc where Fpc.Still_have_to_be_paid <> 0; '''

query_HR = '''with final_df as
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

query_HR2 = '''(select concat(e.firstName,' ', e.lastName) as Employee_Name, e.employeeNumber, almFinal.Total_amount_of_money, almFinal.sales_rank, almFinal.month_year
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
on almFinal.Employee_Number = e.employeeNumber)'''

query_log = '''select p.productCode, p.productName, AvgPerMonth.Total_Quantity_Ordered, p.quantityInStock,  AvgPerMonth.average_quantity_orders_by_month as Average_quantity_orders_by_month, quantityInStock/AvgPerMonth.average_quantity_orders_by_month as How_many_months_left_we_have 
from 
(select od.productCode, (sum(od.quantityOrdered)/(count(distinct(month(o.orderDate)))*count(distinct(year(o.orderDate))))) as Average_quantity_orders_by_month, sum(od.quantityOrdered) as Total_Quantity_Ordered
from orders as o 
inner join orderdetails as od on o.orderNumber = od.orderNumber 
where od.productCode in
(select odbis.productCode
from (select od.productCode 
from orderdetails as od 
group by productCode 
order by sum(od.quantityOrdered) desc limit 5) as odbis) 
group by productCode) as AvgPerMonth
inner join products as p on p.productCode = AvgPerMonth.productCode 
order by Total_Quantity_Ordered desc;'''




#HR
HR_df = pd.read_sql_query(query_HR, connection)
HR_df['month_year_bis'] = HR_df['month_year'].apply(lambda x: datetime.strptime(x, '%m-%Y'))
HR_df = HR_df.sort_values(by = 'month_year_bis')

#Finance
df_fin1 = pd.read_sql_query(query_finance1, connection)
df_fin2 = pd.read_sql_query(query_finance2, connection)
df_fin2 = df_fin2.iloc[:,[0,1,4,5]]
df_fin1 = df_fin1.rename(columns={"country":"Country", "amount_due":"Total sales (in $)", "Number_of_order" : "Total orders"})
df_fin2 = df_fin2.rename(columns={"customerNumber": "Customer Number", "phone": "Phone Number", "Still_have_to_be_paid": "Customer's debt  ($)", "Proportion_of_credit_allows_already_reached": "Proportion of credit authorized already reached (in %)"})

 #logistics
df_log = pd.read_sql_query(query_log, connection)

#Streamlite
st.set_page_config(
    page_title="Project 2 - Model company - Dashboarding ",
    page_icon=":smiley:",
    layout="wide",
)

dash = st.sidebar.radio(
    "What dashboard do you want to see ?",
    ('Sales', 'Finance', 'Logistics', 'HR'))
 
#HR
if dash == 'HR':
    st.title('Welcome to the HR dashboard !')
    #Best employee
    top1 = HR_df.Employee_Name.value_counts().head(1).index.format()
    to_write = 'Well done '+ str(top1[0]) + ' ! You are the best employee over the last years'
    st.write(to_write)
    col1, col2 = st.columns(2)
    col1.metric("Total sales ($)", round(sum(HR_df['Total_amount_of_money'][HR_df['Employee_Name']==str(top1[0])])))
    col2.metric("Number of times in top 2", HR_df.Employee_Name.value_counts().head(1))
    
    #Select the name of the employee to see if he/she appears in the top2
    employee = st.selectbox('Select the name of the employee to see if he/she appears in our monthly top 2',(HR_df.Employee_Name.unique()))
    st.write(employee, 'appears', HR_df['Employee_Name'][HR_df['Employee_Name']== employee].value_counts()[0], 'time in our monthly top 2. Have a look at the stats :')
    col1, col2 = st.columns(2)
    col1.metric("Total sales ($)", round(sum(HR_df['Total_amount_of_money'][HR_df['Employee_Name']==str(employee)])))
    col2.metric("Number of times in top 2", HR_df['Employee_Name'][HR_df['Employee_Name']==employee].value_counts())
    #if (HR_df['Employee_Name'][HR_df['Employee_Name']==employee].value_counts() > 5) :
    #   st.balloons()
    
                #Select a date to see the top 2 employee
    date = st.selectbox(
    'Select the month to see the associated top 2 employees',
(HR_df.month_year.unique()))
    st.write('The first employee of the month is', HR_df['Employee_Name'][(HR_df['month_year']== date) & (HR_df['sales_rank']== 1)].iloc[0])
    st.write('The second employee of the month is', HR_df['Employee_Name'][(HR_df['month_year']== date) & (HR_df['sales_rank']== 2)].iloc[0])

elif dash == 'Finance' :
    st.title('Welcome to the finance dashboard !')
    #Finance 1
    st.header('What is the turnover per country over the 2 last months ?')
    fig2, ax2 = plt.subplots()
    ax2.set_title('Total sales (in $) per country for the last two months')
    sns.barplot(x = df_fin1['Country'], y = df_fin1['Total sales (in $)'], order=df_fin1.sort_values('Total sales (in $)', ascending = False).Country, color = 'red')
    plt.xticks(rotation=90)
    st.pyplot(fig2)
    #Finance 2
    # Find the total debt 
    total_debt = sum(df_fin2["Customer's debt  ($)"]) 
    total_debt = round(total_debt)
    to_disp = 'But we still have $' + str(total_debt) + " to take back ! Where is our money then ?"
    st.header(to_disp)
    fig3, ax3 = plt.subplots()
    ax3.set_title('Debt (in $) per customer')
    ax3.set_ylabel('Amount (in $)')
    ax3.set_xlabel('Customer Number')
    my_cmap = plt.get_cmap("Reds")
    ordered_df = df_fin2.sort_values(by = "Customer's debt  ($)", ascending = False)
    plt.bar(x= ordered_df['Customer Number'].astype(str),
            height = ordered_df["Customer's debt  ($)"],
            color=my_cmap(ordered_df["Proportion of credit authorized already reached (in %)"]/100))
    st.pyplot(fig3)
    st.write("Maybe it's time to contact them ?")
    
    #Hide indexes
    # CSS to inject contained in a string
    hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    tempo_df = df_fin2.sort_values(by = "Customer's debt  ($)", ascending = False)
    tempo_df = tempo_df.loc[:,['Customer Number', 'Phone Number', "Proportion of credit authorized already reached (in %)"]]
    st.table(tempo_df)
    
   
elif dash == 'Logistics':

    st.title('This is the logistics dashboard !')
    
    st.header('these are the top 5 most products selled')
    
    fig, ax = plt.subplots(4, figsize=(30,20))
fig.suptitle('Orders Quantities and Stock Left', fontsize = 15, fontweight="bold")

ax[0].bar(df_log['productName'], df_log['Total_Quantity_Ordered'], color = ['red', 'blue', 'black', 'green', 'yellow'])
ax[0].set_title('Total Orders for the most ordered products', loc='left', fontweight = 'bold')
ax[0].set_ylabel('Quantities ordered')
ax[0].set_xlabel('products')


ax[1].bar(df_log['productName'], df_log['quantityInStock'], color = ['red', 'blue', 'black', 'green', 'yellow'])
ax[1].set_title('Left Stock', loc='left', fontweight='bold')
ax[1].set_ylabel('quantity')
ax[1].set_xlabel('products')

ax[2].bar(df_log['productName'], df_log['Average_quantity_orders_by_month'], color = ['red', 'blue', 'black', 'green', 'yellow'])
ax[2].set_title('Average orders by month', loc='left', fontweight='bold')
ax[2].set_ylabel('quantity')
ax[2].set_xlabel('products')

ax[3].bar(df_log['productName'], df_log['How_many_months_left_we_have'], color = ['red', 'blue', 'black', 'green', 'yellow'])
ax[3].set_title('How many month we have stock', loc='left', fontweight='bold')
ax[3].set_ylabel('months')
ax[3].set_xlabel('products')
st.pyplot(fig)