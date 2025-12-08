import numpy as np
import pygame
import time
import random

# تأكد أن هذين الملفين موجودان ومحدثان (Robot.py و User.py)
from Robot import Robot 
from User import DeliveryQueue, DeliveryRequest 

# =======================================================
# ⚙️ إعدادات Pygame و الأبعاد
# =======================================================

ROWS, COLS = 30, 30
TILE_SIZE = 25 # حجم كل مربع بالبكسل
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE

# تعريف الألوان (تم إضافة GREEN)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0) # ✅ تم إضافة اللون الأخضر لحل المشكلة

# =======================================================
# 🗺️ بناء الخريطة (كما هو)
# =======================================================

original_grid_20x20 = np.array([
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,4,0,0,3,0,0,0,2,0,0,0,0,4,0,0,1],
    [1,0,1,2,1,0,1,0,0,1,0,0,0,1,2,0,1,0,0,1],
    [1,0,0,0,0,0,1,0,2,0,0,4,0,0,0,0,0,0,3,1],
    [1,4,1,1,0,0,0,0,0,0,1,1,0,0,0,1,1,0,0,1],
    [1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,1,0,2,1],
    [1,0,1,0,0,0,0,0,0,1,0,1,0,2,0,0,0,0,0,1],
    [1,0,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,1,0,1],
    [1,0,0,0,0,0,0,0,2,0,1,0,0,0,0,0,0,0,0,1],
    [1,1,1,0,0,1,1,0,0,0,0,0,1,1,0,0,1,0,0,1],
    [1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,3,1],
    [1,0,1,0,1,0,1,0,0,0,0,1,0,1,0,0,1,0,0,1],
    [1,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,1],
    [1,4,1,1,0,0,0,1,0,0,1,1,0,0,0,1,1,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,2,1],
    [1,0,1,0,0,0,0,2,0,0,1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,1],
    [1,3,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,3,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
])

grid = np.ones((ROWS, COLS), dtype=int)
original_inner = original_grid_20x20[1:19, 1:19] 
inner_size = original_inner.shape[0] # 18

grid[1:1+inner_size, 1:1+inner_size] = original_inner 
grid[1:1+inner_size, COLS - inner_size - 1:COLS - 1] = original_inner 
grid[ROWS - inner_size - 1:ROWS - 1, 1:1+inner_size] = original_inner 
grid[ROWS - inner_size - 1:ROWS - 1, COLS - inner_size - 1:COLS - 1] = original_inner 

restaurants = [(1,1), (28,1), (1,28), (28,28), (14, 14)] 
robot = Robot(start_pos=restaurants[0], grid=grid)

# -------- إشارات المرور --------
traffic_signals = {}
signal_positions = []
for y in range(ROWS):
    for x in range(COLS):
        if grid[y,x] == 3:
            traffic_signals[(x,y)] = 'red'
            signal_positions.append((x,y))

signal_groups = {
    'group_A': [pos for i, pos in enumerate(signal_positions) if i % 2 == 0],
    'group_B': [pos for i, pos in enumerate(signal_positions) if i % 2 != 0]
}

current_active_group = 'group_A'
for pos in signal_groups['group_A']: traffic_signals[pos] = 'green'
for pos in signal_groups['group_B']: traffic_signals[pos] = 'red'

signal_timer = 0
SIGNAL_CYCLE = 5 

def update_traffic_signals():
    """تناوب الإشارات"""
    global signal_timer, current_active_group
    signal_timer += 1
    
    if signal_timer >= SIGNAL_CYCLE:
        signal_timer = 0
        
        if current_active_group == 'group_A':
            current_active_group = 'group_B'
        else:
            current_active_group = 'group_A'
            
        inactive_group = 'group_A' if current_active_group == 'group_B' else 'group_B'

        for pos in signal_groups[current_active_group]:
            traffic_signals[pos] = 'green'
        for pos in signal_groups[inactive_group]:
            traffic_signals[pos] = 'red'
            
        print(f"🚦 Traffic signals switched. {current_active_group} is GREEN.")

# -------- سيارات --------
cars = []
for _ in range(30):
    while True:
        x, y = random.randint(1,COLS-2), random.randint(1,ROWS-2)
        if grid[y,x]==0:
            cars.append({'pos':(x,y),'dir':random.choice([(0,1),(1,0),(0,-1),(-1,0)])})
            break

def update_cars():
    """حركة السيارات"""
    current_occupancies = {tuple(c['pos']) for c in cars}
    current_occupancies.update({tuple(p['pos']) for p in people})

    for car in cars:
        cx, cy = car['pos']
        preferred_dx, preferred_dy = car['dir']
        directions = [(preferred_dx, preferred_dy)]
        other_directions = [d for d in [(-1,0),(1,0),(0,-1),(0,1)] if d != (preferred_dx, preferred_dy)]
        random.shuffle(other_directions) 
        directions.extend(other_directions)
        
        chosen_move = None
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            next_pos = (nx, ny)
            
            if (0 < nx < COLS-1 and 0 < ny < ROWS-1 and grid[ny, nx] != 1):
                if next_pos not in (current_occupancies - {car['pos']}):
                    chosen_move = (nx, ny, dx, dy)
                    break 
        
        if chosen_move:
            nx, ny, dx, dy = chosen_move
            car['pos'] = (nx, ny)
            car['dir'] = (dx, dy)
        else:
            pass

# -------- أشخاص --------
people = []
for _ in range(50):
    while True:
        x, y = random.randint(1,COLS-2), random.randint(1,ROWS-2)
        if grid[y,x]==0:
            people.append({'pos':(x,y),'target':(random.randint(1,COLS-2),random.randint(1,ROWS-2))})
            break

def update_people():
    """حركة الأشخاص"""
    all_obstacles = {tuple(c['pos']) for c in cars}
    all_obstacles.add(robot.pos)

    for person in people:
        px, py = person['pos']
        tx, ty = person['target']
        
        if (px, py) != (tx, ty):
            best_next_step = (px, py)
            min_dist = float('inf')
            
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = px + dx, py + dy
                next_pos = (nx, ny)

                if (0 < nx < COLS-1 and 0 < ny < ROWS-1 and grid[ny, nx] != 1 and next_pos not in all_obstacles):
                    dist = abs(tx-nx) + abs(ty-ny)
                    if dist < min_dist:
                        min_dist = dist
                        best_next_step = next_pos
            
            person['pos'] = best_next_step
        else:
            person['target'] = (random.randint(1,COLS-2),random.randint(1,ROWS-2))

# =======================================================
# 🎨 Pygame الرسم
# =======================================================
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Delivery Robot Simulation (Pygame)")
# FONT = pygame.font.Font(None, 24) # يمكن استخدامه لاحقاً لعرض النصوص

def draw_city(screen, agent_pos=None, target_pos=None):
    """
    يرسم المدينة باستخدام Pygame API.
    """
    screen.fill(WHITE)

    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            cell = grid[y,x]
            color = WHITE
            
            if cell == 1: color = GRAY
            elif cell == 2: color = LIGHT_GREEN
            elif cell == 3:
                # لون إشارة المرور
                state = traffic_signals.get((x,y), 'red')
                color = GREEN if state == 'green' else RED # تم تصحيح: استخدام GREEN
            elif cell == 4: color = DARK_GREEN 

            # رسم المربع الأساسي
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1) # حدود المربع

    # رسم المطاعم
    for rx,ry in restaurants:
        rect = pygame.Rect(rx * TILE_SIZE, ry * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, DARK_GREEN, rect)

    # رسم الأشخاص
    for person in people:
        px,py=person['pos']
        rect = pygame.Rect(px * TILE_SIZE, py * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.circle(screen, PINK, rect.center, TILE_SIZE // 3)

    # رسم السيارات
    for car in cars:
        cx,cy=car['pos']
        rect = pygame.Rect(cx * TILE_SIZE, cy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, ORANGE, rect)

    # رسم الروبوت
    if agent_pos:
        ax,ay=agent_pos
        rect = pygame.Rect(ax * TILE_SIZE, ay * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, BLUE, rect)

    # رسم الهدف
    if target_pos:
        tx,ty=target_pos
        rect = pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.circle(screen, YELLOW, rect.center, TILE_SIZE // 2 - 3)

    # تحديث الشاشة
    pygame.display.flip()

# =======================================================
# 🕹️ حلقة Pygame الرئيسية (Game Loop)
# =======================================================
delivery_queue = DeliveryQueue()

# --- جزء إدخال الطلبات ---

while True:
    print("\nEnter multiple delivery requests (X,Y,Customer,Details)")
    print("Type 'x' to finish input and start deliveries, or 'y' to exit program.")
    line = input("Enter request: ").strip().lower()
    
    if line == "y":
        print("❌ Program stopped by user.")
        pygame.quit() 
        exit(0)
    if line == "x":
        break

    try:
        parts = line.split(',')
        if len(parts) < 4:
            print("❌ Please enter all information: X,Y,Customer,Details")
            continue
        gx, gy = int(parts[0]), int(parts[1])
        customer_name = parts[2].strip()
        order_details = parts[3].strip()
        request = DeliveryRequest(gx, gy, customer_name, order_details)
        if not request.is_valid(grid):
            print("❌ Invalid destination.")
            continue
        delivery_queue.add_request(request)
        print(f"📍 Added request: {request}")
        delivery_queue.show_all_requests()
    except ValueError:
        print("❌ Make sure numbers are entered correctly.")


# --- حلقة المحاكاة الرئيسية (Game Loop) ---
print("\n🚀 Starting deliveries with Pygame simulation...")

delivery_count = 0
total_steps_taken = 0
total_delivery_time = 0

current_delivery_goal = None
delivery_in_progress = False
delivery_start_time = 0.0
initial_steps = 0

# التحكم في معدل الإطارات في الثانية (سلس)
FPS = 1
clock = pygame.time.Clock()

running = True
while running:
    # معالجة أحداث Pygame (للإغلاق)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. تحديث البيئة
    update_traffic_signals()
    update_cars()
    update_people()
    
    # 2. تجميع العقبات الديناميكية
    dynamic_obstacles = set()
    for car in cars:
        dynamic_obstacles.add(car['pos'])
    for person in people:
        dynamic_obstacles.add(person['pos'])
        
    # 3. إدارة الطلب
    if not delivery_in_progress:
        if not delivery_queue.has_requests():
            running = False 
            break
            
        next_req = delivery_queue.get_closest_request(robot.pos)
        print(f"\n\n🚚 Delivering: {next_req}")
        current_delivery_goal = next_req.destination
        delivery_in_progress = True
        delivery_start_time = time.time()
        initial_steps = len(robot.path_history)
        
    if delivery_in_progress:
        
        # 4. تنفيذ خطوة واحدة للروبوت
        reached_goal = robot.move_single_step(
            goal=current_delivery_goal, 
            dynamic_obstacles=dynamic_obstacles,
            traffic_signals=traffic_signals
        )
        
        # 5. فحص حالة التسليم
        if reached_goal:
            # حساب المقاييس
            delivery_end_time = time.time()
            delivery_time = delivery_end_time - delivery_start_time
            steps_taken = len(robot.path_history) - initial_steps
            total_steps_taken += steps_taken
            total_delivery_time += delivery_time
            delivery_count += 1
            print(f"\n✅ Delivery completed! Steps: {steps_taken}, Time: {delivery_time:.2f}s")
            
            # إعادة التعيين للطلب التالي
            current_delivery_goal = None
            delivery_in_progress = False
    
    # 6. تحديث الرسم والتحكم في FPS
    draw_city(SCREEN, agent_pos=robot.pos, target_pos=current_delivery_goal)
    clock.tick(FPS) 

# --- إنهاء Pygame والمقاييس ---
pygame.quit() 
print("\n--- 📊 Performance Summary ---")
if delivery_count > 0:
    print(f"Total Deliveries: {delivery_count}")
    print(f"Total Steps Taken: {total_steps_taken}")
    print(f"Total Simulation Time: {total_delivery_time:.2f} seconds")
    print(f"Average Steps per Delivery: {total_steps_taken / delivery_count:.2f}")
    print(f"Average Time per Delivery: {total_delivery_time / delivery_count:.2f} seconds")
else:
    print("No deliveries completed.")
