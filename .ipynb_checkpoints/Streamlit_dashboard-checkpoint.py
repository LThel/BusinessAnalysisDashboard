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
if dash == 'HR':
    st.title('Welcome to the HR dashboard !')
    #Best employee
    top1 = HR_df.Employee_Name.value_counts().head(1).index.format()
    to_write = 'Well done '+ str(top1[0]) + ' ! You are the best employee over the last years'
    st.subheader(to_write)
    col1, col2 = st.columns(2)
    col1.metric("Total sales ($)", round(sum(HR_df['Total_amount_of_money'][HR_df['Employee_Name']==str(top1[0])])))
    col2.metric("Number of times in top 2", HR_df.Employee_Name.value_counts().head(1))
    
    #Top employees table
    top_x = st.slider('Do you want to see our top employees ?', 0, 20, 5)
    year_top_x = st.radio(    "Select the year",
    ('All the years', 2023, 2022, 2021))
    if year_top_x == 'All the years' :
        st.table(HR_df.Employee_Name.value_counts().head(top_x).index.format())
    else :
        st.table(HR_df['Employee_Name'][HR_df['month_year_bis'].dt.year==year_top_x].value_counts().head(top_x).index.format())
    
    
    #Select the name of the employee to see if he/she appears in the top2
    employee = st.selectbox('Select the name of the employee to see if he/she appears in our monthly top 2',(HR_df.Employee_Name.unique()))
    to_write_selemployee = str(employee) + ' appears ' + str(HR_df['Employee_Name'][HR_df['Employee_Name']== employee].value_counts()[0]) +  ' time in our monthly top 2.'
    #st.write(employee, 'appears', HR_df['Employee_Name'][HR_df['Employee_Name']== employee].value_counts()[0], 'time in our monthly top 2. Have a look at the stats :')
    st.subheader(to_write_selemployee)
    st.write('Have a look at its stats :')
    col1, col2 = st.columns(2)
    col1.metric("Total sales ($)", round(sum(HR_df['Total_amount_of_money'][HR_df['Employee_Name']==str(employee)])))
    col2.metric("Number of times in top 2", HR_df['Employee_Name'][HR_df['Employee_Name']==employee].value_counts())
    #if (HR_df['Employee_Name'][HR_df['Employee_Name']==employee].value_counts() > 5) :
    #st.balloons()
    
                #Select a date to see the top 2 employee
    date = st.selectbox(
    'Select the month to see the associated top 2 employees',
(HR_df.month_year.unique()))

    fst = 'The first employee of the month is ' + str(HR_df['Employee_Name'][(HR_df['month_year']== date) & (HR_df['sales_rank']== 1)].iloc[0])
    scnd = 'The second employee of the month is ' + str(HR_df['Employee_Name'][(HR_df['month_year']== date) & (HR_df['sales_rank']== 2)].iloc[0])
    
    st.subheader(fst)
    st.subheader(scnd)
    
    details = st.radio ('Do you want to see the amount of the sales for the selected month ?', ('Yes', 'No'))
    if details == 'Yes':
        fig10, ax10 = plt.subplots(figsize=(3, 1.5))
        sns.barplot(x = HR_df['Employee_Name'][(HR_df['month_year']== date)], y = HR_df['Total_amount_of_money'][(HR_df['month_year']== date)], color = 'red') 
        ax10.set_title('Total sales (in $) for the best two employee of the month')
        ax10.set_ylabel('Total sales (in $)')
        ax10.set_xlabel('Name of the employee')
        plt.yticks(fontsize = 7)
        plt.xticks(fontsize = 7)
    #order=df_fin1.sort_values('Total_amount_of_money', ascending = False), color = 'red')
        st.pyplot(fig10)
    
elif dash == 'Finance' :
    st.title('Welcome to the finance dashboard !')
    #Finance 1
    st.header('What is the turnover per country over the 2 last months ?')
    fig2, ax2 = plt.subplots(figsize=(3, 1.5))
    ax2.set_title('Total sales (in $) per country for the last two months')
    sns.barplot(x = df_fin1['Country'], y = df_fin1['Total sales (in $)'], order=df_fin1.sort_values('Total sales (in $)', ascending = False).Country, color = 'red')
    plt.xticks(rotation=90, fontsize = 7)
    plt.yticks(fontsize = 7)
    st.pyplot(fig2)
    total_turnover = sum(df_fin1['Total sales (in $)'])
    write_turnover = "The total turnover for the last 2 months reaches $" + str(round(total_turnover)) + "."
    st.subheader(write_turnover)
    #Finance 2
    # Find the total debt 
    total_debt = sum(df_fin2["Customer's debt  ($)"]) 
    total_debt = round(total_debt)
    to_disp = 'But we still have $' + str(total_debt) + " to take back ! Where is our money then ?"
    st.subheader(to_disp)
    fig3, ax3 = plt.subplots(figsize=(3, 1.5))
    ax3.set_title('Debt (in $) per customer')
    ax3.set_ylabel('Amount (in $)')
    ax3.set_xlabel('Customer Number')
    plt.xticks(rotation=90, fontsize = 7)
    plt.yticks(fontsize = 7)
    my_cmap = plt.get_cmap("Reds")
    ordered_df = df_fin2.sort_values(by = "Customer's debt  ($)", ascending = False)
    ax3.bar(x= ordered_df['Customer Number'].astype(str),
            height = ordered_df["Customer's debt  ($)"],
            color=my_cmap(ordered_df["Proportion of credit authorized already reached (in %)"]/100), label = True)
    
    #fig3.colorbar(ax3.pcolor(ordered_df["Proportion of credit authorized already reached (in %)"]))
    st.pyplot(fig3)

    st.write("Maybe it's time to contact them ?")    


    #tempo_df = df_fin2.sort_values(by = "Customer's debt  ($)", ascending = False)
    #tempo_df = tempo_df.loc[:,['Customer Number', 'Phone Number', "Proportion of credit authorized already reached (in %)"]]
    st.table(ordered_df.loc[:,['Customer Number', 'Phone Number', "Proportion of credit authorized already reached (in %)"]])

elif dash == 'Logistics':
    st.title ('This is the logistics dashboard !')
    fig_to_disp = st.radio(
    "You can see four different graphics",
    ('Total Quantity ordered', 'Stock left', 'Average orders by month', 'how many month we have stock'))
    if fig_to_disp == 'Total Quantity ordered':
        fig_orders, ax_orders = plt.subplots(figsize=(3, 1.5))
        plt.bar(df_log['productName'], df_log['Total_Quantity_Ordered'], color = 'red')
        plt.title('Total Orders for the most ordered products', loc='left', fontweight = 'bold')
        plt.xticks(rotation=90, fontsize = 7)
        plt.yticks(fontsize = 7)
        st.pyplot(fig_orders)
   
    elif fig_to_disp == 'Stock left':
        fig_stockLeft, ax_stockL = plt.subplots(figsize=(3, 1.5))
        plt.bar(df_log['productName'], df_log['quantityInStock'], color = 'red')
        plt.title('Left Stock', loc='left', fontweight='bold')
        plt.xticks(rotation=90, fontsize = 7)
        plt.yticks(fontsize = 7)
        st.pyplot(fig_stockLeft)
   
    elif fig_to_disp == 'Average orders by month':
        fig_ordersByMonth, ax_ordersM = plt.subplots(figsize=(3, 1.5))
        plt.bar(df_log['productName'], df_log['Average_quantity_orders_by_month'], color = 'red')
        plt.title('Average orders by month', loc='left', fontweight='bold')
        plt.xticks(rotation=90, fontsize = 7)
        plt.yticks(fontsize = 7)
        st.pyplot(fig_ordersByMonth)

    elif fig_to_disp == 'how many month we have stock':
        fig_monthsWstock, ax_monthsStock = plt.subplots(figsize=(3, 1.5))
        plt.bar(df_log['productName'], df_log['How_many_months_left_we_have'], color = 'red')
        plt.title('How many month we have stock', loc='left', fontweight='bold')
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

    
    
