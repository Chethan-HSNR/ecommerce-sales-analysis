# ecommerce-sales-analysis
Description: End-to-end analysis of 2 years of e-commerce orders: data cleaning and KPIs in SQL (PostgreSQL), analysis and charts in Python, and interactive dashboards in Tableau and Power BI.
# E-commerce Sales Analysis (2024-2025)

Tools: PostgreSQL, Python (pandas, matplotlib), Tableau Public, Power BI
Dashboard: <Tableau Public link>

## Revenue definition
Completed orders only (canceled and returned excluded).
Line revenue = quantity x unit_price - discount_amount. Shipping fees excluded.

## Data cleaning log
| Issue found | Rows affected | Decision |
| --- | --- | --- |
| Repeated order_ids | X | Kept first occurrence |
| Status spelled several ways (Completed, cancelled...) | X | Mapped to completed / canceled / returned |
| Category label case/spaces | X | Trimmed + Title Case |
| Blank shipping_fee / discount_amount | X | Treated as 0 |
| Blank state / channel | X | Labeled "Unknown" |

## Key findings
1. Net revenue was $X in 2025 vs $Y in 2024 (+/-Z%), driven by ...
2. Revenue peaks in <months>; Q4 is X% of annual revenue ...
3. <Category> brings X% of revenue but has the highest return rate (Y%) ...

## Recommendations for next year
1. <Action tied to finding> - expected impact ...
2. <Action tied to finding> - expected impact ...

## Charts
![Monthly revenue](charts/01_monthly_revenue.png)
![Revenue by category](charts/02_revenue_by_category.png)
![Return and cancel rates](charts/03_return_cancel_rates.png)

## How to run
1. SQL: run sql/01 -> 04 in order in psql
2. Python: jupyter notebook python/analysis.ipynb
