#!/usr/bin/env python3

import pygame
import rospy
from geometry_msgs.msg import PoseStamped
from actionlib_msgs.msg import GoalStatusArray

# Inicializar Pygame y ROS
pygame.init()
rospy.init_node('waiter_robot_interface', anonymous=True)
pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)

# Colores
WHITE = (255, 228, 181)
BLACK = (0, 0, 0)
GRAY = (102, 205, 170)
LIGHT_GRAY = (220, 220, 220)
BLUE = (255, 140, 0)
GREEN = (100, 255, 100)

# Fuente
font = pygame.font.SysFont('Arial', 30, bold=True)
small_font = pygame.font.SysFont('Arial', 20)
discreet_font = pygame.font.SysFont('Arial', 15, italic=True)

# Dimensiones de pantalla
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Robot Waiter Interface')

# Estado del robot
robot_status = "Esperando orden..."

# Coordenadas de las mesas
positions = [
    {"x": -0.395, "y": -0.540, "name": "Mesa 1"},
    {"x": 1.600, "y": 0.510, "name": "Mesa 2"},
    {"x": -0.521, "y": 0.592, "name": "Mesa 3"},
    {"x": 0.508, "y": -1.544, "name": "Mesa 4"},
    {"x": -2.145, "y": 0.211, "name": "Mesa 5"},
    {"x": 2.079, "y": -0.606, "name": "Mesa 6"},
]

# Posición de Home
home_position = {"x": -1.719, "y": -0.553, "name": "Home"}

def draw_button(text, rect, color):
    pygame.draw.rect(screen, color, rect, border_radius=10)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(rect.x + rect.width/2, rect.y + rect.height/2))
    screen.blit(text_surface, text_rect)

def update_robot_status(status):
    global robot_status
    robot_status = status

def send_goal(x, y):
    goal = PoseStamped()
    goal.header.frame_id = "map"
    goal.header.stamp = rospy.Time.now()
    goal.pose.position.x = x
    goal.pose.position.y = y
    goal.pose.orientation.w = 1.0
    pub.publish(goal)

def status_callback(msg):
    global robot_status
    if msg.status_list:
        status = msg.status_list[-1].status
        if status == 1:
            robot_status = "Robot moviéndose a " + current_goal_name
        elif status == 3:
            robot_status = "Robot esperando siguiente orden"

rospy.Subscriber('/move_base/status', GoalStatusArray, status_callback)

# Main loop
running = True
current_goal_name = ""

while running:
    screen.fill(WHITE)

    # Mostrar texto discreto en la parte superior
    discreet_surface_1 = discreet_font.render("waiter_robot_1", True, GRAY)
    discreet_surface_2 = discreet_font.render("Designed by: Diego A. Torrez Ticona", True, GRAY)
    screen.blit(discreet_surface_1, (10, 10))
    screen.blit(discreet_surface_2, (10, 30))

    # Dibujar botones para cada mesa
    for i, pos in enumerate(positions):
        rect = pygame.Rect(50, 80 + i * 80, 200, 60)
        draw_button(pos["name"], rect, BLUE)
        if rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            current_goal_name = pos["name"]
            send_goal(pos["x"], pos["y"])
            update_robot_status(f"Robot moviéndose a {pos['name']} ({pos['x']}, {pos['y']})")

    # Botón de Home
    home_rect = pygame.Rect(550, 500, 200, 60)
    draw_button("Home", home_rect, GREEN)
    if home_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        current_goal_name = "Home"
        send_goal(home_position["x"], home_position["y"])
        update_robot_status(f"Robot moviéndose a {home_position['name']} ({home_position['x']}, {home_position['y']})")

    # Mostrar el estado del robot
    status_surface = small_font.render(f"Estado: {robot_status}", True, BLACK)
    screen.blit(status_surface, (50, 550))

    # Manejar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()
