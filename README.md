# 🛒 E-Commerce Product Analysis (Vietnam)

This project scrapes product data from a well-known Vietnamese e-commerce website, performs exploratory data analysis (EDA), and visualizes key insights using Tableau.

---

## 📌 Objectives

- Scrape product listings including title, price, category, rating, and sales
- Clean and preprocess the data
- Generate insights through analysis
- Visualize trends and patterns with Tableau dashboards

---

## 🧰 Technologies Used

- **Python** (BeautifulSoup, Requests, Pandas)
- **Jupyter Notebook** for data exploration
- **Tableau Public** for interactive visualizations

---

## 📦 Data Description

| Column Name     | Description                          |
|------------------|--------------------------------------|
| `title`          | Product name                         |
| `url`            | Link to product                      |
| `img_url`        | Image URL                            |
| `price`          | Product price (VND)                  |
| `category`       | Main category                        |
| `sub_category`   | Sub-category                         |
| `brand`          | Product brand                        |
| `description`    | Text description                     |
| `star`           | Average rating                       |
| `star_reviewers` | Number of reviewers                  |
| `sold`           | Estimated sales                      |
| `performance`    | Custom metric (e.g. `sold * star`)   |
| `price_group`    | Price range bin                      |

---

## 📊 Key Insights & Visualizations

All dashboards are built using Tableau and include:

### 💰 Price & Performance
- Histogram of price distribution
- Boxplot: Price by Category
- Bubble Chart: Performance vs Price & Rating
- Scatter plot: Price vs Rating (colored by category, sized by sales)

### 🏷️ Brands & Product Groups
- Bar chart: Avg performance by brand
- Heatmap: Sub-category vs Brand (avg performance)

### 🔍 Quality Analysis
- Rating distribution (1–5 stars)
- Sold vs Rating scatter plot (find high-selling low-rated products)

### 🥇 Top Products
- Table of top 10 products by performance, rating, and sales
- Hover tooltip includes image and description

---

## 📈 Tableau Dashboard

🔗 [View Interactive Dashboard on Tableau Public](https://public.tableau.com/shared/G75KCFYKM?:display_count=n&:origin=viz_share_link)  

---

## 🧹 Data Cleaning Steps

- Removed duplicates and empty fields
- Extracted numeric values from messy strings
- Created `performance` score (e.g. `star * sold`)
- Grouped prices into bins for analysis





