from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random, time
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18

# Global Variables
camera_pos = [0, 500,500]
first_person = False
camera_angle=0
fovY = 90

player_pos = [0.0, 0.0, 10.0]
player_angle = 0.0
player_speed = 5.0
jump_velocity = 0.0
is_jumping = False
gravity = -0.5
player_life = 3
player_velocity = [0.0, 0.0]
has_special_key = False
special_treasures_visible_end_time = 0

GRID_LENGTH = 600
score = 0
game_won = False
game_over = False
cheat_mode = False
power_up_active = False
power_up_end_time = 0
game_time = 60.0
start_time = time.time()
spawn_point = [0.0, 0.0, 10.0]

NUM_TREASURES = 10
treasures = []
SPECIAL_TREASURE_CHANCE = 0.2
special_key_pos = [0, 0, 10]

obstacles = []
traps = []
obstacle_heights = {} # Dictionary to store initial obstacle heights

# Ceiling collapse variables
ceiling_collapsing = False
ceiling_height = 100.0
ceiling_velocity = -5.0
collapse_start_time = 0
debris = []

# -----functions::
def reset_game():
    global player_pos, player_angle, score, game_won, game_over, treasures, obstacles, traps, player_speed, player_life, game_time, start_time, player_velocity, ceiling_collapsing, ceiling_height, debris, has_special_key, special_key_pos, random_bricks, brick_spawn_time, special_treasures_visible_end_time, obstacle_heights, brick_fall_stop_end_time, cheat_mode
    player_pos = spawn_point.copy()
    player_angle = 0.0
    score = 0
    game_won = False
    game_over = False
    player_speed = 5.0
    player_life = 3
    game_time = 60.0
    start_time = time.time()
    treasures = []
    obstacles = []
    traps = []
    player_velocity = [0.0, 0.0]
    ceiling_collapsing = False
    ceiling_height = 100.0
    debris = []
    has_special_key = False
    special_treasures_visible_end_time = 0
    special_key_pos = [random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50), random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50), 10]
    random_bricks = []
    brick_spawn_time = time.time()
    brick_fall_stop_end_time = 0
    obstacle_heights = {}
    cheat_mode = False # Reset cheat mode on new game

    # Create 2 special treasures and 8 regular ones
    for _ in range(2):
        tx = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        ty = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        treasures.append({'pos': [tx, ty, 10], 'special': True})

    for _ in range(NUM_TREASURES - 2):
        tx = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        ty = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        treasures.append({'pos': [tx, ty, 10], 'special': False})

    for i in range(205):
        ox = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        oy = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        obstacle = {'pos': [ox, oy, 20], 'size': 20}
        obstacles.append(obstacle)
        obstacle_heights[i] = 20 # Store initial height

    for _ in range(23):
        tx = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        ty = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        traps.append({'pos': [tx, ty, 0], 'size': 30})

reset_game()

# ----------------------- Drawing Functions ----------------------- #
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1920, 0, 1080)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_player():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0, 0, 1)

    # Main body/torso
    glColor3f(0.0, 0.0, 1.0)
    glPushMatrix()
    glTranslatef(0, 0, 10)
    glutSolidCube(20)
    glPopMatrix()

    # Head
    glColor3f(1.0, 1.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 25)
    gluSphere(gluNewQuadric(), 8, 10, 10)
    glPopMatrix()

    # Hands
    glColor3f(0.8, 0.5, 0.2)
    glPushMatrix()
    glTranslatef(0, 12, 10)
    glutSolidCube(5)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, -12, 10)
    glutSolidCube(5)
    glPopMatrix()


    # Legs
    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(5, 0, 0)
    glutSolidCube(10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-5, 0, 0)
    glutSolidCube(10)
    glPopMatrix()

    glPopMatrix()

def draw_treasure(treasure):
    current_time = time.time()
    # Simran Zaman Mayabi: Special treasure open with only key
    if treasure['special'] and not (has_special_key or cheat_mode or current_time < special_treasures_visible_end_time):
        return
    # Al-amin Sagor: Cheat mode has to see only key for open special treasure
    glPushMatrix()
    glTranslatef(treasure['pos'][0], treasure['pos'][1], treasure['pos'][2])

    if treasure['special']:
        if cheat_mode:
            glColor3f(0.0, 1.0, 0.0)
        else:
            glColor3f(1.0, 0.0, 1.0)
        
        glBegin(GL_QUADS)
        # Top pyramid
        glVertex3f(0, 0, 15)
        glVertex3f(10, 0, 5)
        glVertex3f(0, 10, 5)
        glVertex3f(0, 0, 15)
        glVertex3f(0, 10, 5)
        glVertex3f(-10, 0, 5)
        glVertex3f(0, 0, 15)
        glVertex3f(-10, 0, 5)
        glVertex3f(0, -10, 5)
        glVertex3f(0, 0, 15)
        glVertex3f(0, -10, 5)
        glVertex3f(10, 0, 5)
        # Bottom pyramid
        glVertex3f(0, 0, -5)
        glVertex3f(10, 0, 5)
        glVertex3f(0, 10, 5)
        glVertex3f(0, 0, -5)
        glVertex3f(0, 10, 5)
        glVertex3f(-10, 0, 5)
        glVertex3f(0, 0, -5)
        glVertex3f(-10, 0, 5)
        glVertex3f(0, -10, 5)
        glVertex3f(0, 0, -5)
        glVertex3f(0, -10, 5)
        glVertex3f(10, 0, 5)
        glEnd()

    else:
        glColor3f(1.0, 1.0, 0.0)
        glutSolidSphere(10, 10, 10)
    
    glPopMatrix()

def draw_special_key():
    glPushMatrix()
    glTranslatef(special_key_pos[0], special_key_pos[1], special_key_pos[2])
    glColor3f(0.8, 0.5, 0.2)
    glutSolidTorus(5, 10, 10, 10)
    glPopMatrix()

def draw_obstacle(obstacle):
    glPushMatrix()
    glTranslatef(obstacle['pos'][0], obstacle['pos'][1], obstacle['pos'][2])
    glColor3f(0.5, 0.5, 0.5)
    glutSolidCube(obstacle['size'])
    glPopMatrix()

def draw_trap(trap):
    glPushMatrix()
    glTranslatef(trap['pos'][0], trap['pos'][1], trap['pos'][2])
    glColor3f(1.0, 0.0, 0.0)
    glutSolidCube(trap['size'])
    glPopMatrix()

def draw_grid():
    glColor3f(0.55, 0.27, 0.07)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glEnd()

    wall_height = 50
    wall_thickness = 10
    step = 10
    for wall in [
        {'x1': -GRID_LENGTH - wall_thickness, 'y1': -GRID_LENGTH, 'x2': -GRID_LENGTH - wall_thickness,
         'y2': GRID_LENGTH},
        {'x1': GRID_LENGTH, 'y1': -GRID_LENGTH, 'x2': GRID_LENGTH, 'y2': GRID_LENGTH},
        {'x1': -GRID_LENGTH, 'y1': GRID_LENGTH, 'x2': GRID_LENGTH, 'y2': GRID_LENGTH},
        {'x1': -GRID_LENGTH, 'y1': -GRID_LENGTH - wall_thickness, 'x2': GRID_LENGTH,
         'y2': -GRID_LENGTH - wall_thickness} ]:
        glBegin(GL_QUADS)
        for x in range(int(min(wall['x1'], wall['x2'])), int(max(wall['x1'], wall['x2'])) + step, step):
            for y in range(int(min(wall['y1'], wall['y2'])), int(max(wall['y1'], wall['y2'])) + step, step):
                noise = math.sin(x / 50.0) * math.cos(y / 50.0) * 0.2 + 0.8
                glColor3f(0.4 * noise, 0.4 * noise, 0.45 * noise)
                glVertex3f(x, y, 0)
                glVertex3f(x + step, y, 0)
                glVertex3f(x + step, y + step, wall_height)
                glVertex3f(x, y + step, wall_height)
        glEnd()

    if ceiling_collapsing:
        glColor3f(0.4, 0.4, 0.45)
        glBegin(GL_QUADS)
        glVertex3f(-GRID_LENGTH, -GRID_LENGTH, ceiling_height)
        glVertex3f(GRID_LENGTH, -GRID_LENGTH, ceiling_height)
        glVertex3f(GRID_LENGTH, GRID_LENGTH, ceiling_height)
        glVertex3f(-GRID_LENGTH, GRID_LENGTH, ceiling_height)
        glEnd()

        for d in debris:
            glPushMatrix()
            glTranslatef(d['pos'][0], d['pos'][1], d['pos'][2])
            glColor3f(0.4, 0.4, 0.45)
            glutSolidCube(d['size'])
            glPopMatrix()
    
    for brick in random_bricks:
        glPushMatrix()
        glTranslatef(brick['pos'][0], brick['pos'][1], brick['pos'][2])
        glColor3f(0.6, 0.3, 0.1)
        glutSolidCube(brick['size'])
        glPopMatrix()

# ----------------------- Game Update Logic ----------------------- #
def update_game():
    global player_pos, jump_velocity, is_jumping, score, game_won, game_over, player_speed, power_up_active, power_up_end_time, game_time, player_life, player_velocity, ceiling_collapsing, ceiling_height, collapse_start_time, debris, has_special_key, special_key_pos, random_bricks, brick_spawn_time, special_treasures_visible_end_time, brick_fall_stop_end_time

    if game_won or game_over:
        if ceiling_collapsing:
            current_time = time.time()
            elapsed = current_time - collapse_start_time
            ceiling_height += ceiling_velocity
            for d in debris:
                d['pos'][2] += d['velocity']
            if elapsed > 5:
                ceiling_collapsing = False
        return

    current_time = time.time()
    elapsed = current_time - start_time
    game_time = max(0, 60.0 - elapsed)
    if game_time <= 0 and not ceiling_collapsing:
        game_over = True
        ceiling_collapsing = True
        collapse_start_time = current_time
        for _ in range(20):
            debris.append({
                'pos': [
                    random.uniform(-GRID_LENGTH, GRID_LENGTH),
                    random.uniform(-GRID_LENGTH, GRID_LENGTH),
                    ceiling_height
                ],
                'size': random.uniform(5, 15),
                'velocity': random.uniform(-10, -5)
            })

    if is_jumping or player_pos[2] > 10:
        jump_velocity += gravity
        player_pos[2] += jump_velocity
        player_pos[0] += player_velocity[0]
        player_pos[1] += player_velocity[1]
        # Simran Zaman Mayabi: Through the wall or jump at a time
        if player_pos[2] <= 10:
            player_pos[2] = 10
            jump_velocity = 0
            is_jumping = False
            player_velocity = [0.0, 0.0]

    if power_up_active and current_time > power_up_end_time:
        power_up_active = False
        player_speed = max(5.0, player_speed / 2)

    if not has_special_key:
        dx = player_pos[0] - special_key_pos[0]
        dy = player_pos[1] - special_key_pos[1]
        if math.hypot(dx, dy) < 20:
            has_special_key = True
            # Simran Zaman Mayabi: when special treasure increase for 5s
            special_treasures_visible_end_time = current_time + 10
            special_key_pos = [10000, 10000, 10000]

    for treasure in treasures[:]:
        dx = player_pos[0] - treasure['pos'][0]
        dy = player_pos[1] - treasure['pos'][1]
        if math.hypot(dx, dy) < 20:
            if treasure['special'] and (has_special_key or cheat_mode):
                treasures.remove(treasure)
                # Al-amin Sagor: Special treasure collecting improves health and increase remaining time by 5s
                game_time += 5  # Added 5s to game time
                player_life += 1
                # Al-amin Sagor: Collecting special treasure for 5s random brick falling will stop on myself
                if not cheat_mode:
                    has_special_key = False
            elif not treasure['special']:
                treasures.remove(treasure)
                score += 1 # Normal treasure gives 1 point
                player_speed += 0.5
                
    if not power_up_active:
        for obstacle in obstacles:
            dx = player_pos[0] - obstacle['pos'][0]
            dy = player_pos[1] - obstacle['pos'][1]
            dz = player_pos[2] - obstacle['pos'][2]
            if math.hypot(dx, dy) < 20 and abs(dz) < 20:
                dist = math.hypot(dx, dy)
                if dist > 0:
                    player_pos[0] = obstacle['pos'][0] + dx / dist * 20
                    player_pos[1] = obstacle['pos'][1] + dy / dist * 20
                    player_velocity = [0.0, 0.0]

    for trap in traps:
        dx = player_pos[0] - trap['pos'][0]
        dy = player_pos[1] - trap['pos'][1]
        if math.hypot(dx, dy) < trap['size'] / 2 + 10 and not power_up_active:
            player_life -= 1
            score = max(0, score - 1)
            if player_life <= 0:
                game_over = True
    
    for brick in random_bricks[:]:
        brick['pos'][2] += brick['velocity']
        dx = player_pos[0] - brick['pos'][0]
        dy = player_pos[1] - brick['pos'][1]
        dz = player_pos[2] - brick['pos'][2]
        if math.hypot(dx, dy) < brick['size'] / 2 + 10 and abs(dz) < 20:
            player_life -= 1
            random_bricks.remove(brick)
            if player_life <= 0:
                game_over = True
        elif brick['pos'][2] <= 0:
            random_bricks.remove(brick)

    # Al-amin Sagor: Obstacle height change in cheat mode
    if cheat_mode:
        for i, obstacle in enumerate(obstacles):
            obstacle['pos'][2] = 0 # Obstacles go down
    else:
        for i, obstacle in enumerate(obstacles):
            obstacle['pos'][2] = obstacle_heights[i] # Obstacles return to normal

    if not treasures:
        game_won = True

    player_pos[0] = max(-GRID_LENGTH, min(GRID_LENGTH, player_pos[0]))
    player_pos[1] = max(-GRID_LENGTH, min(GRID_LENGTH, player_pos[1]))

    glutPostRedisplay()

#OpenGL partss#

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1920 / 1080, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, 1920, 1080)
    setupCamera()

    draw_grid()
    for treasure in treasures:
        draw_treasure(treasure)
    for obstacle in obstacles:
        draw_obstacle(obstacle)
    for trap in traps:
        draw_trap(trap)
    draw_player()
    
    if not has_special_key and cheat_mode:
        draw_special_key()

    draw_text(10, 1050, f"Score: {score}  Treasures Left: {len(treasures)}")
    draw_text(10, 1020, f"Life: {player_life}  Time: {int(game_time)} s")
    if power_up_active:
        draw_text(10, 990, "Power-Up Active!")
    if game_won:
        draw_text(860, 540, "VICTORY! Press 'r' to restart.")
    if game_over:
        draw_text(860, 540, "GAME OVER! Press 'r' to restart.")

    if not has_special_key:
        draw_text(10, 960, "Special Treasure requires key!")
    
    current_time = time.time()
    # Simran Zaman Mayabi: when special treasure increase for 5s
    if has_special_key and current_time < special_treasures_visible_end_time:
        draw_text(10, 930, "Special Treasures are visible for 10s!")
    
    if cheat_mode:
        draw_text(10, 900, "Cheat Mode: Activated!")

    if ceiling_collapsing:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1920, 0, 1080)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.5, 0.5, 0.5, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(1920, 0)
        glVertex2f(1920, 1080)
        glVertex2f(0, 1080)
        glEnd()
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    glutSwapBuffers()

# event handle
def keyboardListener(key, x, y):
    global player_angle, player_pos, cheat_mode, jump_velocity, is_jumping, player_velocity
    if key == b'r':
        reset_game()
        return
    if game_won or game_over:
        return
    if key == b'w':
        speed = player_speed * 2 if power_up_active else player_speed
        player_velocity[0] = speed * math.cos(math.radians(player_angle))
        player_velocity[1] = speed * math.sin(math.radians(player_angle))
        if not is_jumping:
            player_pos[0] += player_velocity[0]
            player_pos[1] += player_velocity[1]
    elif key == b's':
        speed = player_speed * 2 if power_up_active else player_speed
        player_velocity[0] = -speed * math.cos(math.radians(player_angle))
        player_velocity[1] = -speed * math.sin(math.radians(player_angle))
        if not is_jumping:
            player_pos[0] += player_velocity[0]
            player_pos[1] += player_velocity[1]
    elif key == b'a':
        player_angle = (player_angle + 5) % 360
    elif key == b'd':
        player_angle = (player_angle - 5) % 360
    elif key == b' ':
        if not is_jumping and player_pos[2] <= 10:
            jump_velocity = 10
            is_jumping = True
    elif key == b'c':
        cheat_mode = not cheat_mode
    glutPostRedisplay()

def specialKeyListener(key, x, y):
    global camera_pos, camera_angle
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    global first_person
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person = not first_person
    glutPostRedisplay()

def idle():
    update_game()

# -- Main section #
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1920, 1080)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Treasure Collector")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
