# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 19:18:43 2024

@author: misht
"""

import yfinance as yf
import pandas as pd

# Define the ticker symbol for United Health
ticker = "UNH"

# Fetch financial data
stock = yf.Ticker(ticker)
balance_sheet = stock.balance_sheet.iloc[:,0:4]
income_statement = stock.financials.iloc[:,0:4]
cash_flow = stock.cashflow.iloc[:,0:4]
history = stock.history(period="5y")
market_price = history['Close'][0]
summary = stock.info
balance_sheet.to_csv("balance_sheet.csv")
income_statement.to_csv("income_statement.csv")
cash_flow.to_csv("cash_flow.csv")
history.to_csv("history.csv")
pd.DataFrame(summary).to_csv("summary.csv")
# Define functions to calculate ratios
def activity_ratios(balance_sheet, income_statement):
    ratios = {}
    # Inventory Turnover = COGS / Average Inventory
    #ratios['Inventory Turnover'] = income_statement.loc['Cost Of Revenue'] / balance_sheet.loc['Inventory'].mean()
    # Receivables Turnover = Revenue / Average Receivables
    ratios['Receivables Turnover'] = income_statement.loc['Total Revenue'] / balance_sheet.loc['Accounts Receivable'].mean()
    
    # Days of Sales Outstanding (DSO)
    ratios['dso'] = 365 / ratios['Receivables Turnover']

    # Payables Turnover
    purchases = (income_statement.loc['Cost Of Revenue'] ) + (cash_flow.loc['Capital Expenditure'] )
    average_trade_payables = balance_sheet.loc['Accounts Payable'].mean()
    payables_turnover = purchases / average_trade_payables
    ratios['payables_turnover']=payables_turnover
    # Number of Days of Payables
    ratios['days_of_payables'] = 365 / payables_turnover
    
    # Working Capital Turnover
    average_working_capital = balance_sheet.loc['Current Assets'].mean() - balance_sheet.loc['Current Liabilities'].mean()
    ratios['working_capital_turnover'] = income_statement.loc['Total Revenue'] / average_working_capital

    # Total Asset Turnover
    average_total_assets = balance_sheet.loc['Total Assets'].mean()
    ratios['total_asset_turnover'] = income_statement.loc['Total Revenue'] / average_total_assets

    return ratios

def liquidity_ratios(balance_sheet):
    ratios = {}
    # Current Ratio = Current Assets / Current Liabilities
    ratios['Current Ratio'] = balance_sheet.loc['Current Assets'] / balance_sheet.loc['Current Liabilities']
    # Quick Ratio = (Current Assets - Inventory) / Current Liabilities
    current_liabilities = balance_sheet.loc['Current Liabilities']

    cash = balance_sheet.loc['Cash And Cash Equivalents']
    short_term_investments = balance_sheet.loc['Cash Cash Equivalents And Short Term Investments']
    receivables = balance_sheet.loc['Accounts Receivable']
    # Fetch the total operating expenses from the income statement
    operating_expenses = income_statement.loc['Operating Expense']+income_statement.loc['Other Operating Expenses'] 

    # Calculate daily cash expenditures
    daily_cash_expenditures = operating_expenses / 365

    # Calculate the Quick Ratio
    ratios['quick_ratio'] = (cash + short_term_investments + receivables) / current_liabilities
    ratios['cash_ratio'] = (cash + short_term_investments ) / current_liabilities
    ratios['Defensive Interval Ratio'] = (cash + short_term_investments + receivables) / daily_cash_expenditures
    #ratios['Quick Ratio'] = (balance_sheet.loc['Current Assets'] ) / balance_sheet.loc['Total Current Liabilities']
    return ratios

def solvency_ratios(balance_sheet, cash_flow):
    ratios = {}
    # Debt to Equity Ratio = Total Debt / Total Equity
    # Define the potential liability components
    liability_components = [
    'Short Long Term Debt', 
    'Long Term Debt', 
    'Other Current Liab', 
    'Total Current Liabilities', 
    'Total Non Current Liabilities', 
    'Deferred Long Term Liab', 
    'Other Liab', 
    'Total Liab'
    ]

    # Extracting the liability data and calculating total liabilities
    total_liabilities = 0
    for component in liability_components:
        if component in balance_sheet.index:
            # Summing up the components if 'Total Liab' is not available
            total_liabilities += balance_sheet.loc[component][0]

    total_debt = balance_sheet.loc['Total Debt']
    total_assets = balance_sheet.loc['Total Assets']
    total_equity = balance_sheet.loc['Stockholders Equity']
    avg_total_assets = total_assets.mean()
    avg_total_equity = total_equity.mean()
    # Calculate the Debt-to-Assets Ratio
    ratios['Debt to Assets ratio'] = total_debt / total_assets
    
    # Calculate the Debt-to-Capital Ratio
    ratios['Debt to Capital Ratio'] = total_debt / (total_debt + total_equity)
    ratios['Debt to Equity'] = total_liabilities / balance_sheet.loc['Stockholders Equity']
    EBIT = income_statement.loc['EBIT']
    Interest_Expense = income_statement.loc['Interest Expense']
    # Calculate the Financial Leverage Ratio
    ratios['Financial Leverage Ratio']=avg_total_assets / avg_total_equity
    # Interest Coverage Ratio = EBIT / Interest Expense

    ratios['Interest Coverage'] = EBIT / Interest_Expense
    

   
    return ratios

def profitability_ratios(income_statement):
    ratios = {}
    revenue = income_statement.loc['Total Revenue']
    gross_profit = income_statement.loc['Gross Profit']
    operating_income = income_statement.loc['Operating Income']
    ebt = income_statement.loc['EBIT']  
    net_income = income_statement.loc['Net Income']
    
    # Calculate Gross Profit Margin
    gross_profit_margin = gross_profit / revenue
    ratios['Gross Profit Margin']= gross_profit_margin
    # Calculate Operating Profit Margin
    operating_profit_margin = operating_income / revenue
    ratios['Operating Profit Margin']=operating_profit_margin
    # Calculate Pretax Margin
    pretax_margin = ebt / revenue
    ratios['Pretax Margin']=pretax_margin
    
    # Calculate Operating ROA
    total_assets = balance_sheet.loc['Total Assets']
    avg_total_assets = total_assets.mean()
    ratios['Operating ROA'] = operating_income / avg_total_assets
    # Net Profit Margin = Net Income / Revenue
    ratios['Net Profit Margin'] = income_statement.loc['Net Income'] / income_statement.loc['Total Revenue']
    # Return on Assets (ROA) = Net Income / Total Assets
    ratios['ROA'] = income_statement.loc['Net Income'] / balance_sheet.loc['Total Assets']
    # Return on Equity (ROE) = Net Income / Total Equity
    ratios['ROE'] = income_statement.loc['Net Income'] / balance_sheet.loc['Stockholders Equity']
    total_debt = balance_sheet.loc['Total Debt']
    total_equity = balance_sheet.loc['Stockholders Equity']
  
  
    # Calculate Return on Total Capital
    return_on_total_capital = ebt / (total_debt + total_equity)
    ratios['Return on Total Capital']=return_on_total_capital
    return ratios



def valuation_ratios(cash_flow, summary, market_price):
    ratios = {}
    operating_cash_flow = cash_flow.loc['Cash Flow From Continuing Operating Activities']
  
    # Fetch the number of shares outstanding
    shares_outstanding = summary['sharesOutstanding']
  
    # Calculate cash flow per share
    cash_flow_per_share = operating_cash_flow / shares_outstanding
    ratios['cash flow per share']=cash_flow_per_share
   
    # P/E Ratio = Market Price per Share / Earnings per Share
    ratios['P/E Ratio'] = summary['trailingPE']
    # P/S Ratio = Market Price per Share / Sales per Share
    ratios['P/S Ratio'] = market_price / (summary['totalRevenue'] / summary['sharesOutstanding'])
    # P/BV Ratio = Market Price per Share / Book Value per Share
    ratios['P/BV Ratio'] = market_price / (summary['bookValue'] / summary['sharesOutstanding'])
    return ratios



# Calculate and display ratios
activity = activity_ratios(balance_sheet, income_statement)
liquidity = liquidity_ratios(balance_sheet)
solvency = solvency_ratios(balance_sheet, cash_flow)
profitability = profitability_ratios(income_statement)
valuation = valuation_ratios(cash_flow, summary, market_price)
# Combine all ratios into a single DataFrame for easy viewing
all_ratios = {**activity, **liquidity, **solvency, **profitability, **valuation}
ratios_df = pd.DataFrame(all_ratios)

# Display the ratios
df1=ratios_df.reset_index()
df1.to_csv("FinanceData.csv")
print(ratios_df.reset_index())
