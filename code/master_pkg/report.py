import os, csv, matplotlib.pyplot as plt, config
import numpy as np

def write_csv(per_id, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "report.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "labels"])
        
        # FIX: Sort the keys (IDs) explicitly before iterating
        # Convert keys to integers for proper numeric sorting, then back to strings
        sorted_keys = sorted(per_id.keys(), key=lambda x: int(x))
        
        for k in sorted_keys: # Iterate over sorted keys
            v = per_id[k]
            w.writerow([k, ";".join(v)])
            
    return path

def write_chart_data_csv(top_data, out_dir):
    """
    Ghi dữ liệu biểu đồ vào file CSV riêng biệt
    top_data: list of tuples (cause, freq, avg_star)
    """
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "chart_data.csv")
    
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["cause", "freq", "avg_star"])
        
        for cause, freq, avg_star in top_data:
            writer.writerow([cause, freq, f"{avg_star:.2f}"])
    
    print(f"Đã tạo file dữ liệu biểu đồ: {path}")
    return path

def write_bar_chart(top_data, out_dir):
    """
    top_data: list of tuples (cause, count, avg_star)
    """
    os.makedirs(out_dir, exist_ok=True)
    
    # Đầu tiên, tạo file CSV chứa dữ liệu biểu đồ
    write_chart_data_csv(top_data, out_dir)
    
    causes = [p[0] for p in top_data]
    counts = [p[1] for p in top_data]
    avg_stars = [p[2] for p in top_data]
    
    x = np.arange(len(causes))  # vị trí của các nhóm
    width = 0.35  # độ rộng của mỗi cột
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Cột 1: Tần suất (màu xanh)
    bars1 = ax1.bar(x - width/2, counts, width, label='Tần suất', color='#4e79a7', alpha=0.8)
    ax1.set_xlabel('Nguyên nhân')
    ax1.set_ylabel('Tần suất', color='#4e79a7')
    ax1.tick_params(axis='y', labelcolor='#4e79a7')
    ax1.set_xticks(x)
    ax1.set_xticklabels(causes, rotation=30, ha='right')
    
    # Thêm số trên đầu cột tần suất
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    # Tạo trục thứ 2 cho số sao trung bình
    ax2 = ax1.twinx()
    # Cột 2: Số sao trung bình (màu cam)
    bars2 = ax2.bar(x + width/2, avg_stars, width, label='Số sao trung bình', color='#f28e2b', alpha=0.8)
    ax2.set_ylabel('Số sao trung bình', color='#f28e2b')
    ax2.tick_params(axis='y', labelcolor='#f28e2b')
    # Đặt giới hạn cho trục số sao (1-4)
    ax2.set_ylim(0.5, 4.5)
    
    # Thêm số trên đầu cột số sao
    for bar in bars2:
        height = bar.get_height()
        ax2.annotate(f'{height:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    # Thêm tiêu đề và legend
    plt.title('Top 5 nguyên nhân feedback tiêu cực - Tần suất & Số sao trung bình')
    
    # Kết hợp legend từ cả 2 trục
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.tight_layout()
    path = os.path.join(out_dir, "top5_with_stars.png")
    plt.savefig(path, dpi=300)
    plt.close()
    
    return path