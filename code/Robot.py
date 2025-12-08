import time
import heapq

class Robot:
    def __init__(self, start_pos, grid, speed=1.0):
        self.pos = start_pos
        self.grid = grid
        self.speed = speed
        self.path_history = []
        # COLS, ROWS سيتم تعريفهم لاحقا من الـ grid
        self.COLS = grid.shape[1]
        self.ROWS = grid.shape[0]

    def heuristic(self, a, b):
        """مسافة Manhattan"""
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    
    def calculate_dynamic_cost(self, pos, current_obstacles):
        """
        حساب التكلفة الإضافية بناءً على القرب من العقبات الديناميكية.
        """
        x, y = pos
        penalty = 0
        
        # ⚠️ (1) عقوبة القرب من العقبات الديناميكية
        for obs_x, obs_y in current_obstacles:
            dist = abs(obs_x - x) + abs(obs_y - y)
            if dist < 3: 
                penalty += (3 - dist) * 0.5 
                
        # 🚦 (2) عقوبة المرور في نقاط إشارات المرور
        if self.grid[y, x] == 3:
            penalty += 1.0 
            
        return penalty

    def a_star(self, goal, dynamic_obstacles=set()):
        """
        البحث عن المسار باستخدام A* مع تطبيق التكلفة الديناميكية (إزالة الحظر المطلق).
        """
        all_dynamic_objects = dynamic_obstacles # لا نضم self.pos للعقبات هنا
        
        open_set = []
        heapq.heappush(open_set, (0+self.heuristic(self.pos, goal), 0, self.pos, [self.pos]))
        visited = set([self.pos])

        while open_set:
            _, cost, current, path = heapq.heappop(open_set)
            if current == goal:
                return path
            x, y = current
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                next_pos = (nx, ny)
                
                # التحقق من الحدود والعقبات الثابتة (1)
                if (0<=nx<self.COLS and 0<=ny<self.ROWS and self.grid[ny,nx] != 1
                    and next_pos not in visited):
                    
                    dynamic_penalty = self.calculate_dynamic_cost(next_pos, all_dynamic_objects)
                    
                    # عقوبة عالية جداً إذا كانت النقطة محتلة حالياً (للتجنب وليس للحظر)
                    if next_pos in all_dynamic_objects:
                        dynamic_penalty += 1000 
                            
                    new_cost = cost + 1 + dynamic_penalty
                    
                    heapq.heappush(open_set, (new_cost+self.heuristic(next_pos, goal), new_cost, next_pos, path+[next_pos]))
                    visited.add(next_pos)
        return [self.pos]

    def move_single_step(self, goal, dynamic_obstacles=set(), traffic_signals={}):
        """
        تنفذ خطوة واحدة فقط نحو الهدف (إن أمكن) وتعود.
        """
        if self.pos == goal:
            return True # تم الوصول

        # 1. تحديث العقبات الديناميكية لتشمل الإشارات الحمراء
        current_obstacles = set(dynamic_obstacles)
        for pos, state in traffic_signals.items():
            if state == 'red':
                current_obstacles.add(pos)
        
        # 2. إعادة حساب المسار لخطوة واحدة
        path = self.a_star(goal, dynamic_obstacles=current_obstacles)
        
        if len(path) <= 1: 
            # لا يوجد مسار أو الروبوت محاصر، يبقى في مكانه (لا حركة)
            return False
        
        next_step = path[1]
        
        # 3. التحقق والتوقف (القسري) عند الإشارة الحمراء أو العقبات الفعلية
        is_traffic_red = next_step in traffic_signals and traffic_signals[next_step] == 'red'
        is_physically_blocked = next_step in dynamic_obstacles
        
        if is_traffic_red or is_physically_blocked:
            # عالق، لا تتحرك
            return False 
            
        # 4. الحركة الفعلية لخطوة واحدة
        self.pos = next_step
        self.path_history.append(next_step)
        
        return self.pos == goal # إرجاع حالة الوصول (True/False)
