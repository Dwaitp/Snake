import pygame
import random
import socket
import pickle
import time


class SnakeClient:
    def __init__(self):

        self.HOST = '127.0.0.1'  # The server's hostname or IP address
        self.PORT = 65432        # The port used by the server

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def Connect(self):
        self.s.connect((self.HOST, self.PORT))

    def Send(self, snake):
        data = pickle.dumps(snake)
        self.s.sendall(data)

    def Receive(self):
        data = self.s.recv(1024)
        enemy_snake = pickle.loads(data)
        return enemy_snake


class Snake():
    """
    Single/MultiPlayer Snake
    """

    def __init__(self, Multiplayer=False):
        super().__init__()
        self.Multiplayer = Multiplayer
        self.yellow = (255, 255, 0)
        self.blue = (0, 0, 255)
        self.green = (0, 255, 0)
        self.red = (255, 0, 0)
        self.magenta = (255, 0, 255)
        self.cyan = (0, 255, 255)
        pygame.init()
        self.screen = pygame.display.set_mode((600, 600))

        pygame.display.set_caption('Snake')

        self.snake = [[300, 300], [300, 320]]
        self.running = True
        self.food_pos = []
        self.direction = "Up"
        self.current_direction = self.direction

        if self.Multiplayer:
            self.sc = SnakeClient()
            self.sc.Connect()
        self.enemy_snake = []

        self.GameLoop()

    def KeyPressed(self):
        key_input = pygame.key.get_pressed()
        if key_input[pygame.K_UP] and self.current_direction != "Down":
            self.direction = "Up"
        elif key_input[pygame.K_DOWN] and self.current_direction != "Up":
            self.direction = "Down"
        elif key_input[pygame.K_RIGHT] and self.current_direction != "Left":
            self.direction = "Right"
        elif key_input[pygame.K_LEFT] and self.current_direction != "Right":
            self.direction = "Left"

    def GameLoop(self):
        fps = 10
        frametime = 1/fps
        t = time.time()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                self.KeyPressed()
            if time.time() - t >= frametime:

                self.screen.fill((0, 0, 0))
                self.HeadPosition = self.snake[-1]
                self.MoveSnake()
                self.MapBorder()

                self.DrawSnake(self.snake, self.blue, self.yellow)
                if self.Multiplayer:

                    self.sc.Send(self.snake)
                    self.enemy_snake = self.sc.Receive()
                    self.food_pos = self.enemy_snake[-1]
                    self.Food()
                    self.enemy_snake = self.enemy_snake[:-1]
                    self.DrawSnake(self.enemy_snake, self.magenta, self.cyan)
                else:
                    self.Food()
                self.GetTailHit()

                pygame.display.flip()
                t = time.time()

    def DrawSnake(self, snake, head_color, tail_color):
        for index, value in enumerate(snake):
            try:
                next_value = snake[index + 1]
                if next_value[0] > value[0]:
                    pygame.draw.rect(self.screen, tail_color,
                                     (value[0] - 8, value[1] - 8, 20, 16))
                elif next_value[0] < value[0]:
                    pygame.draw.rect(self.screen, tail_color,
                                     (value[0] - 12, value[1] - 8, 20, 16))
                elif next_value[1] > value[1]:
                    pygame.draw.rect(self.screen, tail_color,
                                     (value[0] - 8, value[1] - 8, 16, 20))
                elif next_value[1] < value[1]:
                    pygame.draw.rect(self.screen, tail_color,
                                     (value[0] - 8, value[1] - 12, 16, 20))
            except:
                pygame.draw.rect(self.screen, head_color,
                                 (value[0] - 8, value[1] - 8, 16, 16))

    def SnakeDead(self):
        self.snake = [[300, 300], [320, 300]]

    def MapBorder(self):
        border_start = 0
        border_end = 580
        border_thickness = 20

        pygame.draw.rect(self.screen, self.green, (border_start,
                                                   border_start, border_end, border_thickness))
        pygame.draw.rect(self.screen, self.green, (border_start,
                                                   border_start, border_thickness, border_end))
        pygame.draw.rect(self.screen, self.green, (border_end,
                                                   border_start, border_thickness, border_end))
        pygame.draw.rect(self.screen, self.green, (border_start,
                                                   border_end, border_end + border_thickness, border_thickness))

        if not border_end > self.HeadPosition[1] > border_thickness:
            self.SnakeDead()
        if not border_end > self.HeadPosition[0] > border_thickness:
            self.SnakeDead()

    def MoveSnake(self):

        for index, value in enumerate(self.snake):
            try:
                self.snake[index] = [
                    int(self.snake[index + 1][0]), int(self.snake[index + 1][1])]
            except:
                if self.direction == "Down":
                    self.snake[index][1] += 20
                if self.direction == "Up":
                    self.snake[index][1] -= 20
                if self.direction == "Left":
                    self.snake[index][0] -= 20
                if self.direction == "Right":
                    self.snake[index][0] += 20
        self.current_direction = self.direction

    def Food(self):

        while not self.food_pos:
            x = random.randint(2, 28) * 20
            y = random.randint(2, 28) * 20
            if not [x, y] in self.snake:
                self.food_pos = [x, y]
        pygame.draw.rect(self.screen, self.red,
                         (self.food_pos[0] - 8, self.food_pos[1] - 8, 16, 16))

        if self.HeadPosition == self.food_pos:
            self.food_pos = []
            self.snake.insert(0, self.snake[0])

    def GetTailHit(self):
        if self.HeadPosition in self.snake[:-1] or self.HeadPosition in self.enemy_snake:
            self.SnakeDead()


if __name__ == "__main__":
    Snake(True)
