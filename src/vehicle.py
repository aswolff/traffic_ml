from config import *

class Veh:
    def __init__(self, x: int, y: int, direction:int):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = CAR_SPEED
        self.radius = CAR_RADIUS
        self.waiting_time = 0
        self.passed_intersection = False

    def move(self, cars: list['Veh']) -> None:
        """Moves the car
        Direction 0: Car moves right
        Direction 1: Car moves down
        Direction 2: Car moves left
        Direction 3: Car moves up
        Car stops if another car is in front of it
        """
        stop_offset = 20

        # Stop if there is a car in front of the current one
        for other_car in cars:
            if self != other_car:
                if self.direction == other_car.direction:
                    if self.direction == 0 and other_car.x > self.x and (other_car.x - self.x) < stop_offset:
                        self.speed = 0
                        return
                    elif self.direction == 2 and other_car.x < self.x and (self.x - other_car.x) < stop_offset:
                        self.speed = 0
                        return
                    elif self.direction == 1 and other_car.y < self.y and (self.y - other_car.y) < stop_offset:
                        self.speed = 0
                        return
                    elif self.direction == 3 and other_car.y > self.y and (other_car.y - self.y) < stop_offset:
                        self.speed = 0
                        return
        
        match self.direction:
            case 0:
                self.x += self.speed
            case 1:
                self.y -= self.speed
            case 2:
                self.x -= self.speed
            case 3:
                self.y += self.speed

        if self.speed == 0:
            self.waiting_time += 1/60