# ============================================================
# Task 4: Website Traffic Sources Analysis
# Internship: CodTech IT Solutions - Data Analytics
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ── Styling ──────────────────────────────────────────────────
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "figure.facecolor": "#f8f9fa",
    "axes.facecolor":   "#ffffff",
    "font.family":      "DejaVu Sans",
    "axes.spines.top":  False,
    "axes.spines.right":False,
})

# ── Traffic Source Color Map ─────────────────────────────────
SOURCE_COLORS = {
    "Organic Search": "#4C72B0",
    "Direct":         "#DD8452",
    "Social Media":   "#55A868",
    "Referral":       "#C44E52",
    "Email":          "#8172B2",
    "Paid Search":    "#937860",
}

# ── 1. Load & Prepare Data ───────────────────────────────────
df = pd.read_csv("website_traffic_data.csv", parse_dates=["Date"])

df["Month"]   = df["Date"].dt.to_period("M")
df["Quarter"] = df["Date"].dt.to_period("Q")
df["Month_Label"] = df["Date"].dt.strftime("%b %Y")

print("=" * 55)
print("  WEBSITE TRAFFIC SOURCES — DATA OVERVIEW")
print("=" * 55)
print(f"  Records       : {len(df)}")
print(f"  Date Range    : {df['Date'].min().date()} → {df['Date'].max().date()}")
print(f"  Traffic Sources: {df['Traffic_Source'].nunique()}")
print(f"  Sources       : {list(df['Traffic_Source'].unique())}")
print("=" * 55)
print(df[["Sessions","Users","Bounce_Rate","Conversions","Revenue"]].describe().round(2))

# ── 2. Aggregations ──────────────────────────────────────────
# Overall by source
source_agg = df.groupby("Traffic_Source").agg(
    Total_Sessions  = ("Sessions",   "sum"),
    Total_Users     = ("Users",      "sum"),
    Total_Conversions=("Conversions","sum"),
    Total_Revenue   = ("Revenue",    "sum"),
    Avg_Bounce_Rate = ("Bounce_Rate","mean"),
    Avg_Session_Dur = ("Avg_Session_Duration","mean"),
    Avg_Pages       = ("Pages_Per_Session","mean"),
).reset_index()
source_agg["Conversion_Rate"] = (
    source_agg["Total_Conversions"] / source_agg["Total_Sessions"] * 100
).round(2)

# Monthly trend per source
monthly = df.groupby(["Month","Traffic_Source"]).agg(
    Sessions    = ("Sessions",    "sum"),
    Conversions = ("Conversions", "sum"),
    Revenue     = ("Revenue",     "sum"),
).reset_index()
monthly["Month_Label"] = monthly["Month"].dt.strftime("%b %Y")

# Quarter aggregation
quarterly = df.groupby(["Quarter","Traffic_Source"])["Sessions"].sum().reset_index()
quarterly_pivot = quarterly.pivot(index="Quarter", columns="Traffic_Source", values="Sessions").fillna(0)

# Bounce rate comparison
bounce = source_agg.sort_values("Avg_Bounce_Rate")

# Monthly total sessions (all sources)
monthly_total = df.groupby("Month").agg(
    Sessions    = ("Sessions",    "sum"),
    Conversions = ("Conversions", "sum"),
).reset_index()
monthly_total["Month_Label"] = monthly_total["Month"].dt.strftime("%b %Y")

# ── 3. Create 8-Panel Dashboard ──────────────────────────────
fig = plt.figure(figsize=(22, 26))
fig.suptitle(
    "Website Traffic Sources Analysis Dashboard — 2024\n"
    "CodTech IT Solutions Internship | Task 4",
    fontsize=19, fontweight="bold", y=0.99, color="#1a1a2e"
)

# ─── Chart 1: Sessions by Source — Pie ──────────────────────
ax1 = fig.add_subplot(4, 2, 1)
colors_pie = [SOURCE_COLORS[s] for s in source_agg["Traffic_Source"]]
wedges, texts, autotexts = ax1.pie(
    source_agg["Total_Sessions"],
    labels=source_agg["Traffic_Source"],
    autopct="%1.1f%%",
    colors=colors_pie,
    startangle=140,
    wedgeprops={"edgecolor":"white","linewidth":1.8},
    pctdistance=0.78,
)
for t in texts:    t.set_fontsize(8)
for at in autotexts: at.set_fontsize(8); at.set_fontweight("bold")
ax1.set_title("Total Sessions by Traffic Source", fontsize=12, fontweight="bold", pad=10)

# ─── Chart 2: Revenue by Source — Horizontal Bar ─────────────
ax2 = fig.add_subplot(4, 2, 2)
rev_sorted = source_agg.sort_values("Total_Revenue")
bar_colors = [SOURCE_COLORS[s] for s in rev_sorted["Traffic_Source"]]
bars = ax2.barh(rev_sorted["Traffic_Source"], rev_sorted["Total_Revenue"],
                color=bar_colors, edgecolor="white", linewidth=0.8, height=0.55)
ax2.set_title("Total Revenue by Traffic Source", fontsize=12, fontweight="bold")
ax2.set_xlabel("Revenue (₹)")
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"₹{x/1e6:.1f}M"))
for bar in bars:
    ax2.text(bar.get_width()+5000, bar.get_y()+bar.get_height()/2,
             f"₹{bar.get_width()/1e6:.2f}M", va="center", fontsize=8, fontweight="bold")

# ─── Chart 3: Monthly Sessions Trend — Multi-Line ────────────
ax3 = fig.add_subplot(4, 2, 3)
months_ordered = sorted(monthly["Month"].unique())
month_labels   = [m.strftime("%b %Y") for m in months_ordered]

for source in df["Traffic_Source"].unique():
    sub = monthly[monthly["Traffic_Source"]==source].set_index("Month")
    y = [sub.loc[m,"Sessions"] if m in sub.index else 0 for m in months_ordered]
    ax3.plot(range(len(months_ordered)), y,
             marker="o", markersize=4, linewidth=2,
             color=SOURCE_COLORS[source], label=source)

ax3.set_title("Monthly Sessions Trend by Source", fontsize=12, fontweight="bold")
ax3.set_xlabel("Month")
ax3.set_ylabel("Sessions")
ax3.set_xticks(range(len(month_labels)))
ax3.set_xticklabels(month_labels, rotation=45, ha="right", fontsize=7)
ax3.legend(fontsize=7, loc="upper left", framealpha=0.8)
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1e3:.0f}K"))

# ─── Chart 4: Bounce Rate Comparison — Bar ───────────────────
ax4 = fig.add_subplot(4, 2, 4)
b_colors = [SOURCE_COLORS[s] for s in bounce["Traffic_Source"]]
bars4 = ax4.bar(bounce["Traffic_Source"], bounce["Avg_Bounce_Rate"],
                color=b_colors, edgecolor="white", linewidth=0.8, width=0.55)
ax4.set_title("Average Bounce Rate by Source (%)", fontsize=12, fontweight="bold")
ax4.set_xlabel("Traffic Source")
ax4.set_ylabel("Bounce Rate (%)")
ax4.set_xticklabels(bounce["Traffic_Source"], rotation=20, ha="right", fontsize=8)
ax4.axhline(y=bounce["Avg_Bounce_Rate"].mean(), color="red",
            linestyle="--", linewidth=1.2, label=f"Avg: {bounce['Avg_Bounce_Rate'].mean():.1f}%")
ax4.legend(fontsize=9)
for bar in bars4:
    ax4.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
             f"{bar.get_height():.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")

# ─── Chart 5: Stacked Bar — Sessions by Quarter & Source ─────
ax5 = fig.add_subplot(4, 2, 5)
quarters = [str(q) for q in quarterly_pivot.index]
bottom = np.zeros(len(quarters))
for col in quarterly_pivot.columns:
    vals = quarterly_pivot[col].values
    ax5.bar(quarters, vals, bottom=bottom,
            color=SOURCE_COLORS.get(col,"#888888"),
            label=col, edgecolor="white", linewidth=0.6)
    bottom += vals
ax5.set_title("Quarterly Sessions by Traffic Source (Stacked)", fontsize=12, fontweight="bold")
ax5.set_xlabel("Quarter")
ax5.set_ylabel("Sessions")
ax5.legend(fontsize=8, loc="upper left", framealpha=0.8)
ax5.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1e3:.0f}K"))

# ─── Chart 6: Conversion Rate by Source — Bar ─────────────────
ax6 = fig.add_subplot(4, 2, 6)
cr_sorted = source_agg.sort_values("Conversion_Rate", ascending=False)
c_colors = [SOURCE_COLORS[s] for s in cr_sorted["Traffic_Source"]]
bars6 = ax6.bar(cr_sorted["Traffic_Source"], cr_sorted["Conversion_Rate"],
                color=c_colors, edgecolor="white", linewidth=0.8, width=0.55)
ax6.set_title("Conversion Rate by Traffic Source (%)", fontsize=12, fontweight="bold")
ax6.set_xlabel("Traffic Source")
ax6.set_ylabel("Conversion Rate (%)")
ax6.set_xticklabels(cr_sorted["Traffic_Source"], rotation=20, ha="right", fontsize=8)
for bar in bars6:
    ax6.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.02,
             f"{bar.get_height():.2f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")

# ─── Chart 7: Avg Session Duration vs Pages/Session ──────────
ax7 = fig.add_subplot(4, 2, 7)
sc_colors = [SOURCE_COLORS[s] for s in source_agg["Traffic_Source"]]
scatter = ax7.scatter(
    source_agg["Avg_Session_Dur"],
    source_agg["Avg_Pages"],
    s=source_agg["Total_Sessions"]/80,
    c=sc_colors, alpha=0.85, edgecolors="white", linewidths=1.5
)
for _, row in source_agg.iterrows():
    ax7.annotate(row["Traffic_Source"],
                 (row["Avg_Session_Dur"], row["Avg_Pages"]),
                 textcoords="offset points", xytext=(8, 4), fontsize=8)
ax7.set_title("Session Duration vs Pages/Session\n(Bubble size = Total Sessions)",
              fontsize=12, fontweight="bold")
ax7.set_xlabel("Avg Session Duration (min)")
ax7.set_ylabel("Avg Pages per Session")

# ─── Chart 8: Monthly Total Sessions + Conversions (Dual Axis)─
ax8 = fig.add_subplot(4, 2, 8)
x = range(len(monthly_total))
x_labels = monthly_total["Month_Label"].tolist()
ax8.bar(x, monthly_total["Sessions"], color="#4C72B0", alpha=0.7, label="Sessions")
ax8_r = ax8.twinx()
ax8_r.plot(x, monthly_total["Conversions"], color="#C44E52",
           marker="D", markersize=5, linewidth=2.2, label="Conversions")
ax8.set_title("Overall Monthly Sessions vs Conversions", fontsize=12, fontweight="bold")
ax8.set_xlabel("Month")
ax8.set_ylabel("Total Sessions", color="#4C72B0")
ax8_r.set_ylabel("Total Conversions", color="#C44E52")
ax8.set_xticks(list(x))
ax8.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=7)
ax8.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1e3:.0f}K"))
lines1, labels1 = ax8.get_legend_handles_labels()
lines2, labels2 = ax8_r.get_legend_handles_labels()
ax8.legend(lines1+lines2, labels1+labels2, fontsize=8, loc="upper left")

# ── Save ─────────────────────────────────────────────────────
plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig("website_traffic_analysis.png", dpi=150, bbox_inches="tight")
plt.show()
print("\n✅ Dashboard saved as 'website_traffic_analysis.png'")

# ── 4. Summary Report ────────────────────────────────────────
print("\n" + "="*55)
print("  WEBSITE TRAFFIC SUMMARY REPORT")
print("="*55)
print(f"  Total Sessions      : {source_agg['Total_Sessions'].sum():,}")
print(f"  Total Users         : {source_agg['Total_Users'].sum():,}")
print(f"  Total Conversions   : {source_agg['Total_Conversions'].sum():,}")
print(f"  Total Revenue       : ₹{source_agg['Total_Revenue'].sum():,}")
print(f"  Top Source (Sessions): {source_agg.loc[source_agg['Total_Sessions'].idxmax(),'Traffic_Source']}")
print(f"  Top Source (Revenue) : {source_agg.loc[source_agg['Total_Revenue'].idxmax(),'Traffic_Source']}")
print(f"  Best Conv. Rate      : {source_agg.loc[source_agg['Conversion_Rate'].idxmax(),'Traffic_Source']} "
      f"({source_agg['Conversion_Rate'].max():.2f}%)")
print(f"  Lowest Bounce Rate   : {source_agg.loc[source_agg['Avg_Bounce_Rate'].idxmin(),'Traffic_Source']} "
      f"({source_agg['Avg_Bounce_Rate'].min():.1f}%)")
print("="*55)
print("\nPer-Source Breakdown:")
print(source_agg[["Traffic_Source","Total_Sessions","Total_Revenue","Conversion_Rate","Avg_Bounce_Rate"]].to_string(index=False))
