import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
#import sqlalchemy as sql
from collections import Counter
import mysql.connector
from datetime import datetime
from matplotlib.dates import date2num
from matplotlib.pyplot import figure

#Connect to Python
#connection = 'mysql://toyscie:WILD4Rdata!@51.178.25.157:23456/toys_and_models'
connection = mysql.connector.connect(user = 'toyscie', password = 'WILD4Rdata!', host = '51.178.25.157', port = '23456', database = 'toys_and_models', use_pure = True)
#sql_engine = sql.create_engine(connection)

#Connection to SQL

#Connect to Sales query
query_sales = '''with aggregated_data as (
    select month(o.orderDate)                       as month
    , year(o.orderDate)                             as year
    , sum(d.quantityOrdered * d.priceEach)           as sales
    , p.productLine                                 as productLine
    from orders o
    join orderdetails d on o.orderNumber = d.orderNumber
    join products p on d.productCode = p.productCode
    group by month(o.orderDate), year(o.orderDate), p.productLine  

)
select currentYear.month as month
, currentYear.year as year
, currentYear.sales as sales
, currentYear.productLine  as productLine
, lastYear.sales as last_year_sales
, if(lastYear.sales is null or lastYear.sales = 0 , 0, 
(((currentYear.sales - lastYear.sales) / lastYear.sales) *100) ) as exchange_Rate
from aggregated_data currentYear
left join aggregated_data lastYear on currentYear.month = lastYear.month 
                    and currentYear.year -1 = lastYear.year
                    and currentYear.productLine = lastYear.productLine'''

# Connecting the SQL table to the Python
df_sales = pd.read_sql_query(query_sales,connection)
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

#Connect to Sales query
query_sales = '''with aggregated_data as (
    select month(o.orderDate)                       as month
    , year(o.orderDate)                             as year
    , sum(d.quantityOrdered * d.priceEach)           as sales
    , p.productLine                                 as productLine
    from orders o
    join orderdetails d on o.orderNumber = d.orderNumber
    join products p on d.productCode = p.productCode
    group by month(o.orderDate), year(o.orderDate), p.productLine  

)
select currentYear.month as month
, currentYear.year as year
, currentYear.sales as sales
, currentYear.productLine  as productLine
, lastYear.sales as last_year_sales
, if(lastYear.sales is null or lastYear.sales = 0 , 0, 
(((currentYear.sales - lastYear.sales) / lastYear.sales) *100) ) as exchange_Rate
from aggregated_data currentYear
left join aggregated_data lastYear on currentYear.month = lastYear.month 
                    and currentYear.year -1 = lastYear.year
                    and currentYear.productLine = lastYear.productLine'''

# Connecting the SQL table to the Python
df_sales = pd.read_sql_query(query_sales,connection)



#HR
HR_df = pd.read_sql_query(query_HR, connection)
HR_df['month_year_bis'] = HR_df['month_year'].apply(lambda x: datetime.strptime(x, '%m-%Y'))
HR_df = HR_df.sort_values(by = 'month_year_bis')

HR_df2 = pd.read_sql_query(query_HR2, connection)
HR_df2['month_year_bis'] = HR_df2['month_year'].apply(lambda x: datetime.strptime(x, '%m-%Y'))
HR_df2 = HR_df2.sort_values(by = 'month_year_bis')

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
    ('Finance (Louis)', 'HR (Louis)', 'Sales','Logistics'))
 
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
    
#HR
if dash == 'HR (Louis)':
    st.title('Welcome to the HR dashboard ! ✍️')
    employee = st.selectbox('Select the name of an employee',(HR_df2.Employee_Name.unique()))
    
    #Metrics of the employee
    subH1 = 'The stats of ' + employee + ' 📊'
    st.subheader(subH1)
    col1, col2 = st.columns(2)
    col1.metric("Total sales 💵", round(sum(HR_df2['Total_amount_of_money'][HR_df2['Employee_Name']==employee])))
    col2.metric("Number of times in top 2 🏆", HR_df2['Employee_Name'][(HR_df2['Employee_Name']==employee) & (HR_df2['sales_rank']<=2)].value_counts())
    
    
    #Plot of the sales of the employee in comparison to the top2
    subH2 = 'The monthly sales of ' + employee + ' 💰'
    st.subheader(subH2)
    wr1 = 'Have a look to ' + employee + ' monthly perfomances in comparison to our best employees 🥇 🥈 🥉'
    st.write(wr1)
    dates_employee = HR_df2['month_year_bis'][HR_df2['Employee_Name']==employee]                         
    HR_correspondingDates = HR_df2[HR_df2['month_year_bis'].isin(dates_employee)]
    tempo_df = HR_correspondingDates[(HR_correspondingDates['Employee_Name']==employee) | (HR_correspondingDates['sales_rank']<=2)][['Total_amount_of_money', 'Employee_Name', 'sales_rank', 'month_year_bis']]
    fig1, ax = plt.subplots(figsize=(16, 6), dpi=80)
    x = tempo_df['month_year_bis'].sort_values().unique()
    x = date2num(x)
    y = tempo_df['Total_amount_of_money'][tempo_df['Employee_Name']==employee]
    y1 = tempo_df['Total_amount_of_money'][tempo_df['sales_rank']==1]
    y2 = tempo_df['Total_amount_of_money'][tempo_df['sales_rank']==2]
    bar1 = ax.bar(x-6, y, width=6, color='b', align='center')
    bar2 = ax.bar(x, y1, width=6, color='g', align='center')
    bar3 = ax.bar(x+6, y2, width=6, color='r', align='center')
    ax.xaxis_date()
    ax.legend((bar1[0], bar2[0], bar3[0]), (str(employee), '1st employee of the month', '2nd employee of the month') )
    ax.set_ylabel('Total sales (in $)', fontsize = 14)
    ax.set_xlabel('Date', fontsize = 14)
    ax.set_title('Monthly sales of the selected employee in comparison to our best employees', fontsize = 14)
    plt.xticks(rotation=90)
    st.pyplot(fig1)
                                                                        

elif dash == 'Finance (Louis)':
    st.title('Welcome to the finance dashboard ! 💸')
    ordered_df = df_fin2.sort_values(by = "Customer's debt  ($)", ascending = False)
    # create two columns for charts
    fig_col1, fig_col2 = st.columns(2)
    
    with fig_col1:
        st.markdown(" **Turnover (in $) over the last two months** ")
        fig2, ax2 = plt.subplots(figsize=(3, 1.5))
        sns.barplot(x = df_fin1['Country'], y = df_fin1['Total sales (in $)'], order=df_fin1.sort_values('Total sales (in $)', ascending = False).Country, color = 'red')
        plt.xticks(rotation=90, fontsize = 7)
        plt.yticks(fontsize = 7)
        plt.ylabel('Total sales (in $)', fontsize=8)
        plt.xlabel('Country', fontsize=8)
        st.write(fig2)

    with fig_col2:
        st.markdown("**Debt (in $) per customer**")
        # Find the total debt 
        total_debt = sum(df_fin2["Customer's debt  ($)"]) 
        total_debt = round(total_debt)
        to_disp = 'But we still have $' + str(total_debt) + " to take back ! Where is our money then ?"
        #st.subheader(to_disp)
        fig3, ax3 = plt.subplots(figsize=(3, 1.5))
        #ax3.set_title('Debt (in $) per customer')
        ax3.set_ylabel('Amount (in $)')
        ax3.set_xlabel('Customer Number')
        plt.xticks(rotation=90, fontsize = 7)
        plt.yticks(fontsize = 7)
        plt.ylabel('Debt (in $)', fontsize=8)
        plt.xlabel('Customer number', fontsize=8)
        my_cmap = plt.get_cmap("Reds")
        ordered_df = df_fin2.sort_values(by = "Customer's debt  ($)", ascending = False)
        ax3.bar(x= ordered_df['Customer Number'].astype(str),
                height = ordered_df["Customer's debt  ($)"],
                color=my_cmap(ordered_df["Proportion of credit authorized already reached (in %)"]/100), label = True)
        st.write(fig3)  

    selected_customer = st.selectbox ('Select a customer number to have the relative informations', ordered_df.loc[:,['Customer Number']])   
    # create three columns
    kpi1, kpi2, kpi3 = st.columns(3)    
    # fill in those three columns with respective metrics or KPIs
    kpi1.metric(
        label="Customer number 🙍‍♂️🙍‍♀️",
        value=selected_customer,
    )
    kpi2.metric(
        label="Phone number 📞",
        value=str(ordered_df['Phone Number'][ordered_df['Customer Number']==selected_customer])[1:16],
    )
    kpi3.metric(
        label="Credit reached (in %)💸",
        value=ordered_df['Proportion of credit authorized already reached (in %)'][ordered_df['Customer Number']==selected_customer],
    )
    
elif dash == 'Logistics':
    st.title ('Welcome to the logistics dashboard !')
    fig_to_disp = st.radio(
    "Choose a graphics",
    ('Total quantity ordered', 'Stock left', 'Average orders by month', 'How many month we have stock'))
    if fig_to_disp == 'Total quantity ordered':
        fig_orders, ax_orders = plt.subplots(figsize=(3, 1.5))
        plt.bar(df_log['productName'], df_log['Total_Quantity_Ordered'], color = 'red')
        plt.title('Total orders for the most ordered products', loc='left', fontweight = 'bold', fontsize = 10)
        plt.xticks(rotation=90, fontsize = 7)
        plt.yticks(fontsize = 7)
        st.pyplot(fig_orders)
   
    elif fig_to_disp == 'Stock left':
        fig_stockLeft, ax_stockL = plt.subplots(figsize=(3, 1.5))
        plt.bar(df_log['productName'], df_log['quantityInStock'], color = 'red')
        plt.title('Left stock', loc='left', fontweight='bold', fontsize = 10)
        plt.xticks(rotation=90, fontsize = 7)
        plt.yticks(fontsize = 7)
        st.pyplot(fig_stockLeft)
   
    elif fig_to_disp == 'Average orders by month':
        fig_ordersByMonth, ax_ordersM = plt.subplots(figsize=(3, 1.5))
        plt.bar(df_log['productName'], df_log['Average_quantity_orders_by_month'], color = 'red')
        plt.title('Average orders by month', loc='left', fontweight='bold', fontsize = 10)
        plt.xticks(rotation=90, fontsize = 7)
        plt.yticks(fontsize = 7)
        st.pyplot(fig_ordersByMonth)

    elif fig_to_disp == 'How many month we have stock':
        fig_monthsWstock, ax_monthsStock = plt.subplots(figsize=(3, 1.5))
        plt.bar(df_log['productName'], df_log['How_many_months_left_we_have'], color = 'red')
        plt.title('How many month we have stock', loc='left', fontweight='bold', fontsize = 10)
        plt.xticks(rotation=90, fontsize = 7)
        plt.yticks(fontsize = 7)
        st.pyplot(fig_monthsWstock)
#Sales
elif dash == 'Sales':
    st.title ('Welcome to the Sales Dashboard')
    fig_sale1, ax_sale1 = plt.subplots(figsize=(3, 1.5))
    plt.bar(df_sales ['productLine'], df_sales['sales'], color = 'red')
    plt.title('Sales per product line')
    plt.xticks(rotation=90, fontsize = 7)
    plt.yticks(fontsize = 7)
    st.pyplot(fig_sale1)
    
    #Sales by month for the year 2021 and 2022 (SELECTBOX #2)
              
    options = ['Sales by month for the year of 2021','Sales by month for the year of 2022']
    selected_optionsalespm = st.selectbox ('Select a table to view', options)
    if selected_optionsalespm == 'Sales by month for the year of 2021':
        fig_Salesbymonth2021, ax_Salesbymonth2021 = plt.subplots(figsize=(3, 2))
        ax_Salesbymonth2021.bar(df_sales ['month'][df_sales['year'] == 2021] , df_sales ['sales'][df_sales['year'] == 2021], color = 'red')
        plt.title ('Sales by month for the year of 2021')
        plt.yticks(fontsize = 7)
        plt.xticks(fontsize = 7)
        st.pyplot(fig_Salesbymonth2021)
    
    elif selected_optionsalespm == 'Sales by month for the year of 2022':
        fig_Salesbymonth2022, ax_Salesbymonth2022 = plt.subplots(figsize=(3, 2))
        plt.bar(df_sales ['month'][df_sales['year'] == 2022] , df_sales ['sales'][df_sales['year'] == 2022], color = 'red')
        plt.title ('Sales by month for the year of 2022')
        plt.yticks(fontsize = 7)
        plt.xticks(fontsize = 7)
        st.pyplot(fig_Salesbymonth2022)

    st.write ("We can observe very high orders during the last months of the year. Considering that the product being sold by our company performs very similarly to the products sold by the physical toy market it is expected that Christmas turns out to be a considerably profitable period of the year")

    
    
