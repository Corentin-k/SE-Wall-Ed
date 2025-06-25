#from robot.main import Robot
import time

def array_gaussian_blur(array, sigma=1):
    kernel_size = int(6 * sigma + 1)

    def gaussian(x, sigma):
        return (1 / (sigma ** 2 * (2 * 3.14159) ** 0.5)) * (2.71828 ** (-0.5 * (x / sigma) ** 2))
    
    kernel = [gaussian(x - kernel_size // 2, sigma) for x in range(kernel_size)]
    kernel_sum = sum(kernel)
    kernel = [x / kernel_sum for x in kernel]  # Normalize the kernel

    blurred_array = []
    for i in range(len(array)):
        start = max(0, i - kernel_size // 2)
        end = min(len(array), i + kernel_size // 2 + 1)
        weighted_sum = sum([(array[j] * kernel[j - start]) for j in range(start, end)])
        blurred_array.append(weighted_sum)
    return blurred_array

def sobel_filter(array):
    kernel = [-1, 0, 1]
    
    filtered_array = []
    for i in range(1, len(array) - 1):
        x = sum(array[i + j] * kernel[j + 1] for j in range(-1, 2))
        filtered_array.append(x)
    
    # Handle the edges
    filtered_array.insert(0, 0)  # First element
    filtered_array.append(0)  # Last element
    filtered_array = [abs(x) for x in filtered_array]  # Take absolute value

    return filtered_array

class ScanResult:
    def __init__(self, array_result, min_angle, max_angle):
        self.array_result = array_result
        self.min_angle = min_angle
        self.max_angle = max_angle
    
    def get_range_limits_farther(self, min_range_size, min_distance, scan_result):
        start_limit = self.min_angle
        start_index = 0
        end_limit = self.min_angle
        end_index = 0

        angle_step = (self.max_angle - self.min_angle) / len(self.array_result)        

        while end_limit - start_limit < min_range_size:
            start_index = end_index
            start_limit = end_limit

            if self.array_result[start_index] < min_distance: # find the next valid start index
                while start_index < len(self.array_result) and self.array_result[start_index] < min_distance:
                    start_index += 1
                
            if start_index < len(self.array_result): # if we found a valid start index
                start_limit = self.min_angle + start_index * angle_step
                end_index = start_index
                end_limit = start_limit
            else:
                return None, None

            while end_index < len(self.array_result) and self.array_result[end_index] < min_distance: # find the next valid end index
                end_index += 1
            
            if end_index < len(self.array_result): # if we found a valid end index
                end_limit = self.min_angle + end_index * angle_step
            else:
                return None, None
        
        if end_limit - start_limit >= min_range_size:
            return start_limit, end_limit
        
        return None, None

    def get_nearest_obstacle_limits(self):
        min_distance = float('inf')
        min_distance_index = -1
        start_limit = self.min_angle
        end_limit = self.max_angle

        angle_step = (self.max_angle - self.min_angle) / len(self.array_result)    

        edge_array = sobel_filter(array_gaussian_blur(self.array_result))
        edge_average = sum(edge_array) / len(edge_array)

        for i in range(len(self.array_result)):
            distance = self.array_result[i]
            if distance < min_distance:
                min_distance = distance
                min_distance_index = i
        
        for i in range(min_distance_index, len(self.array_result)):
            if edge_array[i] > edge_average:
                end_limit = self.min_angle + i * angle_step
                break
        
        for i in range(min_distance_index, -1, -1):
            if edge_array[i] > edge_average:
                start_limit = self.min_angle + i * angle_step
                break
                
        return start_limit, end_limit
            

def radar_scan(robot, min_angle=0, max_angle=180, step=1):
    scan_result = []
    previous_angle = robot.pan_servo.current_angle
    robot.pan_servo.set_angle(min_angle)
    current_angle = min_angle
    while current_angle < max_angle:
        robot.pan_servo.set_angle(current_angle)
        time.sleep(0.05)
        distance = robot.ultra.get_distance_cm()
        scan_result.append(distance)
        current_angle += step
    
    robot.pan_servo.set_angle(previous_angle)
    return ScanResult(scan_result, min_angle, max_angle)
