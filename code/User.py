import time

class DeliveryRequest:
    _counter = 0

    def __init__(self, x, y, customer_name=None, order_details=None):
        self.destination = (x, y)
        self.customer_name = customer_name
        self.order_details = order_details
        DeliveryRequest._counter += 1
        self.id = DeliveryRequest._counter  # request number
        self.timestamp = time.time()

    def is_valid(self, grid):
        x, y = self.destination
        ROWS, COLS = grid.shape
        return 0 <= x < COLS and 0 <= y < ROWS and grid[y, x] != 1

    def __str__(self):
        return (f"Request #{self.id} to {self.destination} | "
                f"Customer: {self.customer_name or 'Unknown'} | "
                f"Details: {self.order_details or 'None'} | "
                f"Time: {time.strftime('%H:%M:%S', time.localtime(self.timestamp))}")

class DeliveryQueue:
    """
    Manage delivery requests based on closest distance to robot
    """
    def __init__(self):
        self.queue = []

    def add_request(self, request):
        self.queue.append(request)

    def has_requests(self):
        return len(self.queue) > 0

    def get_closest_request(self, robot_pos):
        """
        Return the request closest to the robot's current position
        """
        if not self.queue:
            return None
        closest = min(self.queue, key=lambda r: abs(r.destination[0]-robot_pos[0]) + abs(r.destination[1]-robot_pos[1]))
        self.queue.remove(closest)
        return closest

    def show_all_requests(self):
        print("📝 Current delivery requests:")
        for req in self.queue:
            print(f"  - {req}")
