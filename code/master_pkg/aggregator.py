# worker_pkg/aggregator.py
from collections import Counter, defaultdict
import statistics

class Aggregator:
    def __init__(self):
        self.per_id = {}
        # Thêm dictionary để lưu star cho mỗi id
        self.id_to_star = {}
    
    def add_id_star(self, item_id, star):
        """Lưu star cho mỗi id (gọi từ master)"""
        self.id_to_star[item_id] = star
    
    def add_worker_result(self, data):
        for row in data:  # {"id":..., "labels":[...]}
            self.per_id[row["id"]] = row["labels"]
    
    def top_causes(self, topk=5):
        c = Counter()
        # Dictionary để lưu tất cả stars cho mỗi label
        label_stars = defaultdict(list)
        
        for item_id, labels in self.per_id.items():
            # Lấy star từ id_to_star
            star = self.id_to_star.get(item_id)
            if star is None:
                continue
                
            for label in labels:
                c.update([label])
                label_stars[label].append(star)
        
        # Tính trung bình star cho mỗi label
        result = []
        for label, count in c.most_common(topk):
            stars = label_stars[label]
            avg_star = statistics.mean(stars) if stars else 0
            result.append((label, count, avg_star))
        
        return result