import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# Đọc dữ liệu từ file CSV
file_path = 'reports/chart_data.csv'

# Kiểm tra xem file có tồn tại không
if not os.path.exists(file_path):
    # Nếu không tìm thấy, tạo dữ liệu mẫu từ dữ liệu bạn cung cấp
    print(f"File {file_path} không tìm thấy. Tạo dữ liệu mẫu từ dữ liệu đã cung cấp...")
    data = {
        'cause': ['product quality & defects', 'shopping experience', 
                  'shipping & packaging', 'customer support', 'pricing & costs'],
        'freq': [18, 6, 2, 2, 2],
        'avg_star': [2.33, 2.50, 2.50, 1.50, 2.00]
    }
    df = pd.DataFrame(data)
    
    # Lưu file CSV mẫu để sử dụng sau này
    os.makedirs('reports', exist_ok=True)
    df.to_csv(file_path, index=False)
    print(f"Đã tạo file mẫu tại: {file_path}")
else:
    # Đọc dữ liệu từ file CSV
    df = pd.read_csv(file_path)
    print(f"Đã đọc dữ liệu từ: {file_path}")

# Kiểm tra cấu trúc dữ liệu
print("\nCấu trúc dữ liệu:")
print(df.head())
print(f"\nCác cột có sẵn: {list(df.columns)}")

# Đảm bảo các cột cần thiết tồn tại
required_columns = ['cause', 'freq', 'avg_star']
for col in required_columns:
    if col not in df.columns:
        print(f"Warning: Cột '{col}' không tìm thấy trong dữ liệu")

# Tính toán Impact và Effort
# Có thể điều chỉnh công thức này tùy theo yêu cầu của bạn
df['impact'] = df['freq']

# Tính effort: đánh giá sao thấp thường chỉ ra vấn đề phức tạp cần nhiều effort
# Có thể điều chỉnh thang điểm nếu cần (ở đây giả định thang 1-5 sao)
df['effort'] = 5 - df['avg_star']

# Ngưỡng phân loại - sử dụng trung vị hoặc có thể tùy chỉnh
impact_threshold = df['impact'].median()
effort_threshold = df['effort'].median()

print("\n" + "="*60)
print("THÔNG TIN PHÂN TÍCH")
print("="*60)
print(f"Số lượng vấn đề: {len(df)}")
print(f"Ngưỡng Impact (trung vị): {impact_threshold}")
print(f"Ngưỡng Effort (trung vị): {effort_threshold:.2f}")
print("\nChi tiết dữ liệu:")
for i, row in df.iterrows():
    print(f"{row['cause']}: Freq={row['freq']}, Star={row['avg_star']}, Impact={row['impact']}, Effort={row['effort']:.2f}")

# Tạo màu sắc cho các điểm dữ liệu
colors = plt.cm.Set3(np.linspace(0, 1, len(df)))

# Tạo figure với nhiều subplot để hiển thị thông tin
fig = plt.figure(figsize=(16, 12))

# 1. Biểu đồ chính: Impact Matrix
ax1 = plt.subplot(2, 2, (1, 2))

# Vẽ các vùng của ma trận
# Quick Wins (High Impact, Low Effort)
ax1.fill_between([0, effort_threshold], [impact_threshold, impact_threshold], 
                 [df['impact'].max()*1.1, df['impact'].max()*1.1], 
                 alpha=0.2, color='green', label='Quick Wins')

# Major Projects (High Impact, High Effort)
ax1.fill_between([effort_threshold, df['effort'].max()*1.1], 
                 [impact_threshold, impact_threshold], 
                 [df['impact'].max()*1.1, df['impact'].max()*1.1], 
                 alpha=0.2, color='blue', label='Major Projects')

# Fill-Ins (Low Impact, Low Effort)
ax1.fill_between([0, effort_threshold], [0, 0], 
                 [impact_threshold, impact_threshold], 
                 alpha=0.2, color='orange', label='Fill-Ins')

# Thankless Tasks (Low Impact, High Effort)
ax1.fill_between([effort_threshold, df['effort'].max()*1.1], 
                 [0, 0], [impact_threshold, impact_threshold], 
                 alpha=0.2, color='red', label='Thankless Tasks')

# Vẽ các điểm dữ liệu
scatter = ax1.scatter(df['effort'], df['impact'], 
                      s=df['freq']*80, 
                      c=colors, 
                      alpha=0.8, 
                      edgecolors='black', 
                      linewidth=1.5,
                      zorder=5)

# Thêm nhãn cho các điểm
for i, row in df.iterrows():
    # Rút gọn tên nếu quá dài
    label = row['cause']
    if len(label) > 20:
        label = label[:18] + "..."
    
    ax1.annotate(label, 
                 (row['effort'], row['impact']),
                 xytext=(8, 5), 
                 textcoords='offset points',
                 fontsize=9,
                 fontweight='bold',
                 bbox=dict(boxstyle="round,pad=0.3", 
                          facecolor="white", 
                          alpha=0.9,
                          edgecolor='gray'))

# Vẽ đường phân chia
ax1.axhline(y=impact_threshold, color='gray', linestyle='--', alpha=0.7, linewidth=1)
ax1.axvline(x=effort_threshold, color='gray', linestyle='--', alpha=0.7, linewidth=1)

# Cấu hình trục
ax1.set_xlabel('EFFORT (Low ← → High)\n(5 - Average Star Rating)', 
               fontsize=12, fontweight='bold')
ax1.set_ylabel('IMPACT (Low ← → High)\n(Frequency of Occurrence)', 
               fontsize=12, fontweight='bold')
ax1.set_title('ACTION PRIORITY MATRIX\nCustomer Feedback Analysis', 
              fontsize=14, fontweight='bold', pad=20)

# Điều chỉnh giới hạn trục
ax1.set_xlim(0, df['effort'].max() * 1.15)
ax1.set_ylim(0, df['impact'].max() * 1.15)

# Thêm grid
ax1.grid(True, alpha=0.3, linestyle='--')

# Thêm chú giải
ax1.legend(loc='upper right', fontsize=10)

# 2. Biểu đồ 2: Bar chart tần suất
ax2 = plt.subplot(2, 2, 3)
bars = ax2.barh(range(len(df)), df['freq'], color=colors)
ax2.set_yticks(range(len(df)))
ax2.set_yticklabels([c[:20] + "..." if len(c) > 20 else c for c in df['cause']])
ax2.set_xlabel('Frequency', fontweight='bold')
ax2.set_title('Frequency of Issues', fontweight='bold')
ax2.bar_label(bars, padding=3, fontsize=9)

# 3. Biểu đồ 3: Average Star Ratings
ax3 = plt.subplot(2, 2, 4)
stars_bars = ax3.barh(range(len(df)), df['avg_star'], color=colors)
ax3.set_yticks(range(len(df)))
ax3.set_yticklabels([c[:20] + "..." if len(c) > 20 else c for c in df['cause']])
ax3.set_xlabel('Average Star Rating (1-5)', fontweight='bold')
ax3.set_title('Customer Satisfaction (Stars)', fontweight='bold')
ax3.set_xlim(0, 5)  # Giới hạn từ 0-5 sao
ax3.bar_label(stars_bars, padding=3, fontsize=9, fmt='%.2f')

# Thêm đường mốc 2.5 sao (trung bình)
ax3.axvline(x=2.5, color='red', linestyle='--', alpha=0.5, label='Average (2.5)')
ax3.legend(fontsize=9)

plt.tight_layout()

# Lưu biểu đồ
output_path = 'reports/action_priority_matrix.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\nĐã lưu biểu đồ tại: {output_path}")

# Hiển thị biểu đồ
plt.show()

# Phân tích chi tiết từng vấn đề
print("\n" + "="*60)
print("PHÂN TÍCH ƯU TIÊN CHI TIẾT")
print("="*60)

for i, row in df.iterrows():
    # Phân loại
    if row['impact'] >= impact_threshold and row['effort'] <= effort_threshold:
        category = "QUICK WIN"
        priority = "Ưu tiên cao"
        recommendation = "Xử lý ngay - tác động lớn, dễ thực hiện"
        color = "🟢"
    elif row['impact'] >= impact_threshold and row['effort'] > effort_threshold:
        category = "MAJOR PROJECT"
        priority = "Ưu tiên trung bình"
        recommendation = "Cần kế hoạch chi tiết và nguồn lực"
        color = "🔵"
    elif row['impact'] < impact_threshold and row['effort'] <= effort_threshold:
        category = "FILL-IN"
        priority = "Ưu tiên thấp"
        recommendation = "Xử lý khi có thời gian rảnh"
        color = "🟡"
    else:
        category = "THANKLESS TASK"
        priority = "Ưu tiên rất thấp"
        recommendation = "Cân nhắc lợi ích vs chi phí"
        color = "🔴"
    
    print(f"\n{color} {row['cause'].upper()}:")
    print(f"   • Phân loại: {category}")
    print(f"   • Mức độ ưu tiên: {priority}")
    print(f"   • Tần suất: {row['freq']} lần")
    print(f"   • Đánh giá trung bình: {row['avg_star']}/5 sao")
    print(f"   • Độ khó (Effort): {row['effort']:.2f}")
    print(f"   • Đề xuất: {recommendation}")

# Thống kê tổng quát
print("\n" + "="*60)
print("THỐNG KÊ TỔNG QUÁT")
print("="*60)

category_counts = {
    "Quick Wins": 0,
    "Major Projects": 0,
    "Fill-Ins": 0,
    "Thankless Tasks": 0
}

for i, row in df.iterrows():
    if row['impact'] >= impact_threshold and row['effort'] <= effort_threshold:
        category_counts["Quick Wins"] += 1
    elif row['impact'] >= impact_threshold and row['effort'] > effort_threshold:
        category_counts["Major Projects"] += 1
    elif row['impact'] < impact_threshold and row['effort'] <= effort_threshold:
        category_counts["Fill-Ins"] += 1
    else:
        category_counts["Thankless Tasks"] += 1

for category, count in category_counts.items():
    print(f"{category}: {count} vấn đề")

# Xuất báo cáo CSV
report_df = df.copy()
report_df['category'] = ""
report_df['priority_score'] = 0

for i, row in report_df.iterrows():
    if row['impact'] >= impact_threshold and row['effort'] <= effort_threshold:
        report_df.at[i, 'category'] = "Quick Win"
        report_df.at[i, 'priority_score'] = 1
    elif row['impact'] >= impact_threshold and row['effort'] > effort_threshold:
        report_df.at[i, 'category'] = "Major Project"
        report_df.at[i, 'priority_score'] = 2
    elif row['impact'] < impact_threshold and row['effort'] <= effort_threshold:
        report_df.at[i, 'category'] = "Fill-In"
        report_df.at[i, 'priority_score'] = 3
    else:
        report_df.at[i, 'category'] = "Thankless Task"
        report_df.at[i, 'priority_score'] = 4

# Sắp xếp theo mức độ ưu tiên
report_df = report_df.sort_values('priority_score')

# Lưu báo cáo
report_path = 'reports/priority_analysis_report.csv'
report_df.to_csv(report_path, index=False)
print(f"\nĐã lưu báo cáo phân tích chi tiết tại: {report_path}")

# Hiển thị bảng tổng hợp
print("\n" + "="*60)
print("BẢNG TỔNG HỢP PHÂN TÍCH ƯU TIÊN")
print("="*60)
print(report_df[['cause', 'freq', 'avg_star', 'category', 'priority_score']].to_string(index=False))