import pandas as pd
import matplotlib.pyplot as plt
import os
os.makedirs("J:\\data Science projects\\ecommerce-sales-analysis\\charts", exist_ok=True)

orders    = pd.read_csv("J:\\data Science projects\\ecommerce-sales-analysis\\orders.csv")
items     = pd.read_csv("J:\\data Science projects\\ecommerce-sales-analysis\\order_items.csv")
products  = pd.read_csv("J:\\data Science projects\\ecommerce-sales-analysis\\products.csv")
customers = pd.read_csv("J:\\data Science projects\\ecommerce-sales-analysis\\customers.csv")

for name, df in [("orders", orders), ("items", items), ("products", products), ("customers", customers)]:
    print(name, df.shape, "| exact duplicate rows:", df.duplicated().sum())
    print(df.isna().sum(), "\n")

print(orders["order_id"].duplicated().sum(), "repeated order_ids")
print(orders["status"].value_counts(dropna=False))
print(orders["payment_method"].value_counts(dropna=False))
print(products["category"].value_counts(dropna=False))
print(customers["acquisition_channel"].value_counts(dropna=False))
print(customers["state"].value_counts(dropna=False))

# Trim whitespace in every text column
def strip_all(df):
    return df.apply(lambda s: s.str.strip())
orders, items, products, customers = map(strip_all, [orders, items, products, customers])

# Orders
status_map = {"completed": "completed", "complete": "completed",
              "canceled": "canceled", "cancelled": "canceled", "returned": "returned"}
orders["status"] = orders["status"].str.lower().map(status_map).fillna("unknown")
orders["payment_method"] = orders["payment_method"].str.lower()
orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")
orders["shipping_fee"] = pd.to_numeric(orders["shipping_fee"], errors="coerce").fillna(0)
orders = orders.dropna(subset=["order_date"]).drop_duplicates(subset="order_id", keep="first")

# Order items
items["quantity"] = pd.to_numeric(items["quantity"]).astype(int)
items["unit_price"] = pd.to_numeric(items["unit_price"])
items["discount_amount"] = pd.to_numeric(items["discount_amount"]).fillna(0)
items = items.drop_duplicates()
items = items[items["order_id"].isin(orders["order_id"])]   # drop orphans

# Products
products["category"] = products["category"].str.title()
products[["list_price", "unit_cost"]] = products[["list_price", "unit_cost"]].apply(pd.to_numeric)
products = products.drop_duplicates(subset="product_id", keep="first")

# Customers
customers["state"] = customers["state"].str.upper().fillna("Unknown")
customers["acquisition_channel"] = customers["acquisition_channel"].str.title().fillna("Unknown")
customers = customers.drop_duplicates(subset="customer_id", keep="first")

print(orders["status"].value_counts())   # should show only 3 statuses
# Create a single DataFrame with all the relevant information for analysis
sales = (items.merge(orders, on="order_id")
              .merge(products, on="product_id", how="left")
              .merge(customers, on="customer_id", how="left"))
sales["line_revenue"] = sales["quantity"] * sales["unit_price"] - sales["discount_amount"]
sales["line_cost"] = sales["quantity"] * sales["unit_cost"]
sales["year"] = sales["order_date"].dt.year
sales["month"] = sales["order_date"].dt.month
sales["quarter"] = sales["order_date"].dt.quarter
sales.to_csv("J:\\data Science projects\\ecommerce-sales-analysis/sales_clean.csv", index=False)

done = sales[sales["status"] == "completed"]   # revenue definition

# Q1 KPIs by year
kpi = done.groupby("year").agg(net_revenue=("line_revenue", "sum"),
                               orders=("order_id", "nunique"),
                               units=("quantity", "sum"))
kpi["aov"] = kpi["net_revenue"] / kpi["orders"]
print(kpi.round(2))

# Q2 Monthly revenue 2024 vs 2025 + YoY %
monthly = done.pivot_table(index="month", columns="year", values="line_revenue", aggfunc="sum")
monthly["yoy_pct"] = (monthly[2025] / monthly[2024] - 1) * 100
print(monthly.round(1))

# Q3 Seasonality: % of each year's revenue by quarter
q = done.pivot_table(index="quarter", columns="year", values="line_revenue", aggfunc="sum")
print((q / q.sum() * 100).round(1))

# Q4 Category revenue, share and gross margin
cat = done.groupby("category").agg(net_revenue=("line_revenue", "sum"), cost=("line_cost", "sum"))
cat["pct_of_total"] = cat["net_revenue"] / cat["net_revenue"].sum() * 100
cat["gross_margin_pct"] = (cat["net_revenue"] - cat["cost"]) / cat["net_revenue"] * 100
print(cat.sort_values("net_revenue", ascending=False).round(1))

# Q5 Top 10 products
top10 = (done.groupby(["product_name", "category"])
             .agg(units=("quantity", "sum"), net_revenue=("line_revenue", "sum"))
             .sort_values("net_revenue", ascending=False).head(10))
print(top10.round(2))

# Q6 Category mix by quarter (% of quarter)
mix = done.pivot_table(index="quarter", columns="category", values="line_revenue", aggfunc="sum")
print((mix.div(mix.sum(axis=1), axis=0) * 100).round(1))

# Q7 Return / cancellation rate by category (all statuses, % of order lines)
rates = sales.groupby("category")["status"].value_counts(normalize=True).unstack().fillna(0) * 100
print(rates[["returned", "canceled"]].round(1))

# Q8 Revenue per order by category
aov_cat = done.groupby("category").agg(rev=("line_revenue", "sum"), orders=("order_id", "nunique"))
aov_cat["revenue_per_order"] = aov_cat["rev"] / aov_cat["orders"]
print(aov_cat.sort_values("revenue_per_order", ascending=False).round(2))


# Chart 1: monthly trend, 2025 vs 2024
ax = monthly[[2024, 2025]].plot(marker="o", figsize=(10, 5))
ax.set_title("Monthly net revenue: 2025 vs 2024")
ax.set_xlabel("Month"); ax.set_ylabel("Net revenue ($)")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
ax.legend(title="Year"); plt.tight_layout()
plt.savefig("charts/01_monthly_revenue.png", dpi=150); plt.show()

# Chart 2: revenue by category
ax = cat["net_revenue"].sort_values().plot.barh(figsize=(8, 4))
ax.set_title("Net revenue by category (2024-2025)"); ax.set_xlabel("Net revenue ($)"); ax.set_ylabel("")
plt.tight_layout(); plt.savefig("charts/02_revenue_by_category.png", dpi=150); plt.show()

# Chart 3: return and cancellation rates
ax = rates[["returned", "canceled"]].plot.bar(figsize=(8, 4), rot=0)
ax.set_title("Return and cancellation rate by category"); ax.set_ylabel("% of order lines"); ax.set_xlabel("")
ax.legend(["Returned", "Canceled"]); plt.tight_layout()
plt.savefig("charts/03_return_cancel_rates.png", dpi=150); plt.show()

# Chart 4: top 10 products
ax = top10["net_revenue"].droplevel(1).sort_values().plot.barh(figsize=(8, 5))
ax.set_title("Top 10 products by net revenue"); ax.set_xlabel("Net revenue ($)"); ax.set_ylabel("")
plt.tight_layout(); plt.savefig("charts/04_top_products.png", dpi=150); plt.show()