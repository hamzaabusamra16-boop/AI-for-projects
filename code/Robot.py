import time
import heapq

class Robot:
    def __init__(self, start_pos, grid, speed=1.0):
        self.pos = start_pos
        self.grid = grid
        self.speed = speed
        self.path_history = []

    def heuristic(self, a, b):
        """مسافة Manhattan"""
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    
    def calculate_dynamic_cost(self, pos, current_obstacles):
        """
        حساب التكلفة الإضافية بناءً على القرب من العقبات الديناميكية.
        تكلفة أعلى تعني أن الخوارزمية تفضل الابتعاد عن هذه النقطة.
        """
        x, y = pos
        penalty = 0
        
        # ⚠️ (1) عقوبة القرب من العقبات الديناميكية
        for obs_x, obs_y in current_obstacles:
            dist = abs(obs_x - x) + abs(obs_y - y)
            # كلما كانت المسافة أقل، كانت العقوبة أكبر.
            if dist < 3: # مسافة تأثير 3 خلايا
                penalty += (3 - dist) * 0.5 
                
        # 🚦 (2) عقوبة المرور في نقاط إشارات المرور (بغض النظر عن لونها)
        # لتشجيع الروبوت على تجنب التقاطعات المزدحمة
        if self.grid[y, x] == 3:
            penalty += 1.0 
            
        return penalty

    def a_star(self, goal, dynamic_obstacles=set()):
            """
            البحث عن المسار باستخدام A* مع تطبيق التكلفة الديناميكية.
            """
            # دمج العقبات الديناميكية في مجموعة واحدة لحساب التكلفة
            # (يتم استخدامها لحساب العقوبة، وليس للحظر المطلق)
            all_dynamic_objects = dynamic_obstacles.union({self.pos}) 
            
            ROWS, COLS = self.grid.shape
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
                    
                    # ✅ التعديل الأول: إزالة next_pos not in dynamic_obstacles
                    # نترك فقط فحص الحدود والعقبات الثابتة (1)
                    if (0<=nx<COLS and 0<=ny<ROWS and self.grid[ny,nx] != 1
                        and next_pos not in visited):
                        
                        # 🚀 تطبيق التكلفة الديناميكية هنا:
                        dynamic_penalty = self.calculate_dynamic_cost(next_pos, all_dynamic_objects)
                        
                        # ✅ التعديل الثاني: عقوبة عالية جداً إذا كانت النقطة محتلة حالياً
                        # هذا يجعل A* يفضل المسارات البديلة الطويلة قبل المرور بهذه النقطة.
                        if next_pos in all_dynamic_objects:
                            dynamic_penalty += 1000 # عقوبة عالية جداً (للتجنب وليس للحظر)
                            
                        # التكلفة الجديدة = التكلفة القديمة + 1 (تكلفة الخطوة) + عقوبة الازدحام
                        new_cost = cost + 1 + dynamic_penalty
                        
                        heapq.heappush(open_set, (new_cost+self.heuristic(next_pos, goal), new_cost, next_pos, path+[next_pos]))
                        visited.add(next_pos)
            return [self.pos]

    def move_to(self, goal, draw_callback=None, delay=0.5, dynamic_obstacles=set(), traffic_signals={}):
        """
        تحريك الروبوت مع تحديث المسار ديناميكيًا (لم يتغير المنطق هنا).
        """
        WAIT_TIME = 0.1 

        while self.pos != goal:
            
            # 1. تحديث العقبات الديناميكية لتشمل الإشارات الحمراء
            current_obstacles = set(dynamic_obstacles)
            for pos, state in traffic_signals.items():
                if state == 'red':
                    current_obstacles.add(pos)
            
            # 2. إعادة حساب المسار في كل خطوة
            # a_star الآن تأخذ العقبات في الحسبان لتجنبها *في التكلفة* وليس فقط *كعقبة مطلقة*
            path = self.a_star(goal, dynamic_obstacles=current_obstacles)
            
            if len(path) <= 1: 
                time.sleep(WAIT_TIME) 
                if draw_callback:
                    draw_callback(agent_pos=self.pos)
                continue
            
            next_step = path[1]
            
            # 3. التحقق والتوقف (القسري) عند الإشارة الحمراء أو العقبات الفعلية
            is_traffic_red = next_step in traffic_signals and traffic_signals[next_step] == 'red'
            is_physically_blocked = next_step in dynamic_obstacles
            
            if is_traffic_red or is_physically_blocked:
                time.sleep(WAIT_TIME)
                if draw_callback:
                    draw_callback(agent_pos=self.pos)
                continue
                
            # 5. الحركة الفعلية
            self.pos = next_step
            self.path_history.append(next_step)
            if draw_callback:
                draw_callback(agent_pos=self.pos)
            time.sleep(delay/self.speed)
