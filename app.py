#import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime



# Load the dataset
df= pd.read_csv("startfile_cleaned.csv")




#Adding new columns and converting formats
df['Date']=pd.to_datetime(df['Date'],errors='coerce')
df['year']=df['Date'].dt.year
df['mont']=df['Date'].dt.month



investor_list=set(df['Investors Name'].str.split(',').sum())#making list of investor of each row and then making it a big list and then set
il=sorted(list(investor_list))
il.remove('')



#Function for ALL sidebars
def investor_detail(name):

    n=st.selectbox("Select number of records to display", [x for x in range(len(df[df['Investors Name'].str.contains(name)]),0,-1)])#select box from total number of investor rows to 1
    investor_details=df[df['Investors Name'].str.contains(name)][['Startup','Date','type','city','Amount cr']].head(n)#showing df of invesotor acc to select box of n 
    return investor_details

def biggest_inv(name):
    fig, ax = plt.subplots()
    return df[df['Investors Name'].str.contains(name)].groupby('Startup')['Amount cr'].sum().sort_values(ascending=False)#sorted list of amount of startup by investor name

def load_overall_data():
    st.title("Overall Analysis")
    st.write("This section provides an overall analysis of the startup data.")
    st.metric("Total funding amount",str(round(df['Amount cr'].sum(),2)), "in crores")
    st.metric("Total startup",str(df['Startup'].nunique()), "in counts")
    st.metric("Average funding amount",str(round(df.groupby('Startup')['Amount cr'].sum().mean(),2)), "in crores")
    max_fund=df.groupby('Startup')['Amount cr'].sum().sort_values(ascending=False)#highest funding startup
    st.metric("Max funded startup",str(max_fund.iloc[0]), max_fund.index[0])


    #month to month analysis+
    st.header("Month to month number of startups and funding amount")
   
    temp=df.groupby(['year','mont'])['Startup'].count()
    temp_df=temp.reset_index()
    temp_df['year']=temp_df['year'].astype('int')
    temp_df['mont']=temp_df['mont'].astype('int')
    temp_df['x axis']=temp_df['year'].astype('str')+'/'+temp_df['mont'].astype('str')
    chart_values=temp_df[['x axis','Startup']]
    plt.plot(chart_values['x axis'], chart_values['Startup'], marker='o')
    plt.title("Month to Month Number of Startups")
    plt.xlabel('Year/Month', fontsize=24)
    plt.ylabel('Number of Startups', fontsize=24)
    plt.xticks(rotation=45, fontsize=3)
    plt.yticks(fontsize=14)
    plt.grid()
    st.pyplot(plt.gcf())
    plt.close('all')  # Close all figures to free memory

    temp=df.groupby(['year','mont'])['Amount cr'].sum()
    temp_df=temp.reset_index()
    temp_df['year']=temp_df['year'].astype('int')
    temp_df['mont']=temp_df['mont'].astype('int')
    temp_df['x axis']=temp_df['year'].astype('str')+'/'+temp_df['mont'].astype('str')
    chart_values=temp_df[['x axis','Amount cr']]
            
    plt.plot(chart_values['x axis'], chart_values['Amount cr'], marker='o')
    plt.title("Month to Month Funding Amount")
    plt.xlabel('Year/Month', fontsize=24)
    plt.ylabel('Funding Amount (in crores)', fontsize=24)
    plt.xticks(rotation=45, fontsize=3)
    plt.yticks(fontsize=14)
    plt.grid()
    st.pyplot(plt.gcf())
    


def load_startup():
    st.title("Startup Analysis")
    st.write("This section provides an analysis of the startups.")
    startups_name=st.sidebar.selectbox("Select company name",sorted(df['Startup'].unique().tolist()))
    st.write("Date of funding for the startup:")
    date_startup=df[df['Startup'].str.contains(startups_name)]['Date'].dropna()
    if not date_startup.empty:
        for p,i in enumerate(date_startup):
            st.markdown(f"**📅 Startup Date** {p+1} :{i.strftime('%B %d, %Y')}")

    else:
        st.write("No funding date available for this startup.")

    st.markdown("## If funding amount is not available, it will be shown as 0")
    st.write('Startup  : ',startups_name)
    st.metric("Funding amount",df[df['Startup'].str.contains(startups_name)]['Amount cr'].sum(),"in crores")
    st.write("Cities where the startup is located:")
    st.dataframe(df[df['Startup'].str.contains(startups_name)]['city'].unique().tolist(), width=1000)
    st.markdown("### Startup Type:")
    items=list(set(df[df['Startup'].str.contains(startups_name)]['type']))

    for item in items:
        st.markdown(f"- {item}")


    st.markdown("### Investors:")
    startup_investor_total=df.groupby('Startup').agg({'Investors Name':lambda x :','.join(x)})
    investor_list_each=startup_investor_total[startup_investor_total.index==startups_name]['Investors Name'].values[0].split(',')
    for i in investor_list_each:
        st.markdown(f"- {i}")



#main page functions  and features
st.title("Startup app Display ")
st.write("This app is used to display the startup data.")
st.sidebar.title("START UP DETAILS")

# Sidebar options
option=st.sidebar.selectbox("Select the startup", ["Overall analysis", "Startup", "Investor"])

if option=="Startup":#startup analysis
    load_startup()

elif option=="Investor":#investor analysis
    st.title("Investor Analysis")
    selected_inv=st.sidebar.selectbox("Select Investor name",il)
    st.write('Investor details : ')
    st.dataframe(investor_detail(selected_inv))
    st.write('\n\n\n')
    big_inv_val=st.selectbox("Select number of startups to display", [x for x in range(3,len(biggest_inv(selected_inv))+1)])
    st.dataframe(biggest_inv(selected_inv).head(big_inv_val),width=1000)
    

    #graph of biggest investment by investor and pie chart of type of investment and city
    col1, col2 = st.columns(2)
    with col1:
        
        fig, ax = plt.subplots()
        sns.barplot(data=biggest_inv(selected_inv).head(big_inv_val).reset_index(), x='Startup', y='Amount cr', ax=ax)
        st.pyplot(fig)
    with col2:
        fig1, ax1 = plt.subplots()
        inv_more=(df[df['Investors Name'].str.contains(selected_inv)].groupby('type')['Amount cr'].sum().head(5).sort_values(ascending=False))
        labels = inv_more.index


        plt.pie(inv_more, labels=labels,autopct='%1.1f%%')
        plt.axis('equal')
        plt.figure(figsize=(14,15))
        st.pyplot(fig1)  # Equal aspect ratio ensures that pie is drawn as a circle


    fig2, ax2 = plt.subplots()
    
    # Investment by City chart
    st.title("Investment by City")
    st.write("This section shows the investment distribution by city for the selected investor.")
    st.dataframe(df[df['Investors Name'].str.contains(selected_inv)].groupby('city')['Amount cr'].sum().sort_values(ascending=False).reset_index(), width=1000)
    city_more=(df[df['Investors Name'].str.contains(selected_inv)].groupby('city')['Amount cr'].sum().head(5).sort_values(ascending=False))
    labels2=city_more.index
    ax2.pie(city_more, labels=labels2,autopct='%1.1f%%',textprops={'fontsize': 4})
    plt.axis('equal')
    plt.figure(figsize=(25,25))
    st.pyplot(fig2)  # Equal aspect ratio ensures that pie is drawn as a circle

    
    # Investment by Date chart
    st.title("Investment by Date")
    st.write("This section shows the investment distribution by date for the selected investor.")
    year_top_inv=(df[df['Investors Name'].str.contains(selected_inv)].groupby('year')['Amount cr'].sum().sort_values(ascending=False))
    st.dataframe(year_top_inv.reset_index(), width=1000)
    plt.plot(year_top_inv.index, year_top_inv.values, marker='o')
    plt.title(f"Investment by Year for {selected_inv}")
    plt.xlabel('Year',fontsize=24)
    plt.ylabel('Amount (in crores)', fontsize=24)
    plt.xticks(rotation=45,fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid()
    st.pyplot(plt.gcf())
elif option=="Overall analysis":
    btn=st.sidebar.button("Load Overall Data")
    if btn:
        load_overall_data()