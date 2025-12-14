import heapq

class Robot:
    def __init__(self, start_pos, grid, speed=1.0):
        self.pos = start_pos
        self.grid = grid
        self.speed = speed
        self.path_history = []
        self.COLS = grid.shape[1]
        self.ROWS = grid.shape[0]

    def heuristic(self, a, b):
        """مسافة Manhattan"""
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def calculate_dynamic_cost(self, pos, current_obstacles):
        """
        تحظر أي موقع فيه سيارة أو شخص تمامًا،
        وتضيف عقوبة على المرور عند الإشارات.
        """
        x, y = pos

        # 🚫 لا يمكن المرور على العقبات الفعلية
        if pos in current_obstacles:
            return float('inf')  # حظر مطلق

        penalty = 0

        # 🚦 عقوبة المرور عند إشارات المرور
        if self.grid[y, x] == 3:
            penalty += 1.0

        return penalty

    def a_star(self, goal, dynamic_obstacles=set()):
        """
        البحث عن المسار باستخدام A* مع العقبات الديناميكية.
        """
        open_set = []
        heapq.heappush(open_set, (0+self.heuristic(self.pos, goal), 0, self.pos, [self.pos]))
        visited = set([self.pos])

        while open_set:
            _, cost, current, path = heapq.heappop(open_set)
            if current == goal:
                return path
            x, y = current
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x + dx, y + dy
                next_pos = (nx, ny)

                # تحقق من الحدود والخريطة
                if (0 <= nx < self.COLS and 0 <= ny < self.ROWS and self.grid[ny,nx] != 1
                    and next_pos not in visited):

                    dynamic_penalty = self.calculate_dynamic_cost(next_pos, dynamic_obstacles)

                    # إذا العقبة غير قابلة للمرور، تجاهل هذا المسار
                    if dynamic_penalty == float('inf'):
                        continue

                    new_cost = cost + 1 + dynamic_penalty
                    heapq.heappush(open_set, (new_cost + self.heuristic(next_pos, goal), new_cost, next_pos, path + [next_pos]))
                    visited.add(next_pos)
        return [self.pos]

    def move_single_step(self, goal, dynamic_obstacles=set(), traffic_signals={}):
        """
        تنفيذ خطوة واحدة نحو الهدف.
        """
        if self.pos == goal:
            return True

        # 1. إنشاء مجموعة العقبات الديناميكية: سيارات، أشخاص، إشارات حمراء
        current_obstacles = set(dynamic_obstacles)
        for pos, state in traffic_signals.items():
            if state == 'red':
                current_obstacles.add(pos)

        # 2. حساب المسار
        path = self.a_star(goal, dynamic_obstacles=current_obstacles)

        if len(path) <= 1:
            # محاصر، يبقى في مكانه
            return False

        next_step = path[1]
        self.pos = next_step
        self.path_history.append(next_step)

        return self.pos == goal

