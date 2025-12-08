import numpy as np
import matplotlib.pyplot as plt
from collections import deque
# يجب التأكد من أن كود Robot.py المعدل موجود في ملف Robot.py
from Robot import Robot 
import time
import random
# تأكد من أن كلاسات DeliveryQueue, DeliveryRequest موجودة في ملف User.py
from User import DeliveryQueue, DeliveryRequest 

ROWS, COLS = 30, 30
# =======================================================

# 📌 بناء الخريطة المعقدة 30x30 بتكرار النمط
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

# تكرار النمط لملء الخريطة
grid[1:1+inner_size, 1:1+inner_size] = original_inner # الربع العلوي الأيسر
grid[1:1+inner_size, COLS - inner_size - 1:COLS - 1] = original_inner # الربع العلوي الأيمن
grid[ROWS - inner_size - 1:ROWS - 1, 1:1+inner_size] = original_inner # الربع السفلي الأيسر
grid[ROWS - inner_size - 1:ROWS - 1, COLS - inner_size - 1:COLS - 1] = original_inner # الربع السفلي الأيمن

# نقاط المطاعم الجديدة (في الزوايا)
restaurants = [(1,1), (28,1), (1,28), (28,28), (14, 14)] 
robot = Robot(start_pos=restaurants[0], grid=grid)
# -------- إشارات المرور (تعديل 1: تقسيم المجموعات) --------
traffic_signals = {}
signal_positions = []
for y in range(ROWS):
    for x in range(COLS):
        if grid[y,x] == 3:
            traffic_signals[(x,y)] = 'red'
            signal_positions.append((x,y))

# تقسيم الإشارات إلى مجموعات لواقعية أكبر في التناوب (تقاطعات أفقية ورأسية)
signal_groups = {
    'group_A': [pos for i, pos in enumerate(signal_positions) if i % 2 == 0],
    'group_B': [pos for i, pos in enumerate(signal_positions) if i % 2 != 0]
}

# الحالة الابتدائية: مجموعة خضراء ومجموعة حمراء
current_active_group = 'group_A'
for pos in signal_groups['group_A']: traffic_signals[pos] = 'green'
for pos in signal_groups['group_B']: traffic_signals[pos] = 'red'

# 🚦 التعديل المطلوب: تغيير الإشارة كل 5 خطوات محاكاة
signal_timer = 0
SIGNAL_CYCLE = 5 

def update_traffic_signals():
    """تناوب واقعي للإشارات بين مجموعتين."""
    global signal_timer, current_active_group
    signal_timer += 1
    
    if signal_timer >= SIGNAL_CYCLE:
        signal_timer = 0
        
        # تبديل المجموعة النشطة
        if current_active_group == 'group_A':
            current_active_group = 'group_B'
        else:
            current_active_group = 'group_A'
            
        # تحديث الحالات
        inactive_group = 'group_A' if current_active_group == 'group_B' else 'group_B'

        for pos in signal_groups[current_active_group]:
            traffic_signals[pos] = 'green'
        for pos in signal_groups[inactive_group]:
            traffic_signals[pos] = 'red'
            
        print(f"🚦 Traffic signals switched. {current_active_group} is GREEN.")

# -------- سيارات مع مسار محدد --------
cars = []
for _ in range(30):
    while True:
        x, y = random.randint(1,COLS-2), random.randint(1,ROWS-2)
        if grid[y,x]==0:
            cars.append({'pos':(x,y),'dir':random.choice([(0,1),(1,0),(0,-1),(-1,0)])})
            break

def update_cars():
    """تحسين حركة السيارات لتجنب الاصطدام."""
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

# -------- أشخاص مع هدف عشوائي --------
people = []
for _ in range(50):
    while True:
        x, y = random.randint(1,COLS-2), random.randint(1,ROWS-2)
        if grid[y,x]==0:
            people.append({'pos':(x,y),'target':(random.randint(1,COLS-2),random.randint(1,ROWS-2))})
            break

def update_people():
    """تحسين بسيط لحركة الأشخاص نحو هدفهم."""
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

# -------- رسم المدينة (كما هي) --------
def draw_city(agent_pos=None, target_pos=None):
    plt.clf()
    for y in range(ROWS):
        for x in range(COLS):
            cell = grid[y,x]
            color = 'white'
            if cell==1: color='gray'
            elif cell==2: color='lightgreen'
            elif cell==3: 
                color=traffic_signals.get((x,y),'red') 
            elif cell==4: color='green'
            plt.fill_between([x,x+1],[y,y],[y+1,y+1],color=color)

    for rx,ry in restaurants:
        plt.fill_between([rx,rx+1],[ry,ry],[ry+1,ry+1],color='darkgreen')

    for person in people:
        px,py=person['pos']
        plt.fill_between([px,px+1],[py,py],[py+1,py+1],color='pink')

    for car in cars:
        cx,cy=car['pos']
        plt.fill_between([cx,cx+1],[cy,cy],[cy+1,cy+1],color='orange')

    if agent_pos:
        ax,ay=agent_pos
        plt.fill_between([ax,ax+1],[ay,ay],[ay+1,ay+1],color='blue')

    if target_pos:
        tx,ty=target_pos
        plt.fill_between([tx,tx+1],[ty,ty],[ty+1,ty+1],color='red')

    plt.xlim(0,COLS)
    plt.ylim(0,ROWS)
    plt.gca().invert_yaxis()
    plt.axis('off')
    plt.pause(0.001)

plt.ion()
draw_city(agent_pos=robot.pos)

delivery_queue = DeliveryQueue()

# --- جزء إدخال الطلبات (كما هو) ---

while True:
    print("\nEnter multiple delivery requests (X,Y,Customer,Details)")
    print("Type 'x' to finish input and start deliveries, or 'y' to exit program.")
    line = input("Enter request: ").strip().lower()
    
    if line == "y":
        print("❌ Program stopped by user.")
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

# --- Step 2: تنفيذ كل الطلبات (حلقة محاكاة مستمرة) ---
print("\n🚀 Starting deliveries with enhanced realistic environment simulation...")

delivery_count = 0
total_steps_taken = 0
total_delivery_time = 0

FRAME_DELAY = 0.1 # تأخير زمني أساسي لكل خطوة محاكاة (لتصبح الحركة مرئية وسريعة)

current_delivery_goal = None
delivery_in_progress = False
delivery_start_time = 0.0
initial_steps = 0

# حلقة المحاكاة الرئيسية
while delivery_queue.has_requests() or delivery_in_progress:
    
    # 1. تحديث البيئة (يتم كل FRAME_DELAY)
    update_traffic_signals()
    update_cars()
    update_people()
    
    # 2. تجميع العقبات الديناميكية
    dynamic_obstacles = set()
    for car in cars:
        dynamic_obstacles.add(car['pos'])
    for person in people:
        dynamic_obstacles.add(person['pos'])
        
    # 3. إدارة الطلب الحالي
    if not delivery_in_progress:
        next_req = delivery_queue.get_closest_request(robot.pos)
        if next_req:
            print(f"\n\n🚚 Delivering: {next_req}")
            current_delivery_goal = next_req.destination
            delivery_in_progress = True
            delivery_start_time = time.time()
            initial_steps = len(robot.path_history)
        else:
            break # لا توجد طلبات أخرى
            
    if delivery_in_progress:
        
        # 4. تنفيذ خطوة واحدة للروبوت
        reached_goal = robot.move_single_step(
            goal=current_delivery_goal, 
            dynamic_obstacles=dynamic_obstacles,
            traffic_signals=traffic_signals
        )
        
        # 5. فحص حالة التسليم
        if reached_goal:
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
    
    # 6. تحديث الرسم والتأخير الزمني (يجب أن يتم الرسم في كل خطوة محاكاة)
    draw_city(agent_pos=robot.pos, target_pos=current_delivery_goal)
    time.sleep(FRAME_DELAY)


# --- مقاييس الأداء النهائية ---
print("\n--- 📊 Performance Summary ---")
if delivery_count > 0:
    print(f"Total Deliveries: {delivery_count}")
    print(f"Total Steps Taken: {total_steps_taken}")
    print(f"Total Simulation Time: {total_delivery_time:.2f} seconds")
    print(f"Average Steps per Delivery: {total_steps_taken / delivery_count:.2f}")
    print(f"Average Time per Delivery: {total_delivery_time / delivery_count:.2f} seconds")
else:
    print("No deliveries completed.")
