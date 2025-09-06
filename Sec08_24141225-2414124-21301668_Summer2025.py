from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random, time
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18







# Global Variables
camera_pos = [0, 500,500]
first_person =False
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

obstacles = []
traps = []

# Ceiling collapse vari
ceiling_collapsing = False
ceiling_height = 100.0
ceiling_velocity = -5.0
collapse_start_time = 0
debris = []


# -----fucntions::
def reset_game():
    global player_pos, player_angle, score, game_won, game_over, treasures, obstacles, traps, player_speed, player_life, game_time, start_time, player_velocity, ceiling_collapsing, ceiling_height, debris
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

    for _ in range(NUM_TREASURES):
        tx = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        ty = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        is_special = random.random() < SPECIAL_TREASURE_CHANCE
        treasures.append({'pos': [tx, ty, 10], 'special': is_special})

    for _ in range(205):  # Increased from 5 to 205
        ox = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        oy = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        obstacles.append({'pos': [ox, oy, 20], 'size': 20})

    for _ in range(23):  # Increased from 3 to 23
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

    glColor3f(0.0, 0.0, 1.0)
    glPushMatrix()
    glTranslatef(0, 0, 10)
    glutSolidCube(20)
    glPopMatrix()



    glColor3f(1.0, 1.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 25)
    gluSphere(gluNewQuadric(), 8, 10, 10)
    glPopMatrix()


    glPopMatrix()




def draw_treasure(treasure):
    glPushMatrix()
    glTranslatef(treasure['pos'][0], treasure['pos'][1], treasure['pos'][2])
    if treasure['special']:
        glColor3f(1.0, 0.0, 1.0)
    else:
        glColor3f(1.0, 1.0, 0.0)
    if cheat_mode:
        glColor3f(0.0, 1.0, 0.0)
    glutSolidSphere(10, 10, 10)
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
    # Draw solid brown floor
    glColor3f(0.55, 0.27, 0.07)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glEnd()

    # boundary walls with cave texture looks niuce


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



    # ceiling and debris during collapse  feature
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


# ----------------------- Game Update Logic ----------------------- #
def update_game():
    global player_pos, jump_velocity, is_jumping, score, game_won, game_over, player_speed, power_up_active, power_up_end_time, game_time, player_life, player_velocity, ceiling_collapsing, ceiling_height, collapse_start_time, debris

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

    #  timer  feature
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

    #  jump and movement  feature
    if is_jumping or player_pos[2] > 10:
        jump_velocity += gravity
        player_pos[2] += jump_velocity
        player_pos[0] += player_velocity[0]
        player_pos[1] += player_velocity[1]
        if player_pos[2] <= 10:
            player_pos[2] = 10
            jump_velocity = 0
            is_jumping = False
            player_velocity = [0.0, 0.0]

    #  power-up  feature
    if power_up_active and current_time > power_up_end_time:
        power_up_active = False
        player_speed = max(5.0, player_speed / 2)

    # Treasure collection feature
    for treasure in treasures[:]:
        dx = player_pos[0] - treasure['pos'][0]
        dy = player_pos[1] - treasure['pos'][1]
        if math.hypot(dx, dy) < 20:
            treasures.remove(treasure)
            score += 1
            player_speed += 0.5
            if treasure['special']:
                power_up_active = True
                power_up_end_time = current_time + 5
                player_speed *= 2
                game_time += 10

    # Obstacle collision feature
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

    # Trap collision feature
    for trap in traps:
        dx = player_pos[0] - trap['pos'][0]
        dy = player_pos[1] - trap['pos'][1]
        if math.hypot(dx, dy) < trap['size'] / 2 + 10 and not power_up_active:
            player_life -= 1
            score = max(0, score - 1)
            if player_life <= 0:
                game_over = True

    # Victory feature
    if not treasures:
        game_won = True

    # Boundary check
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

    offset = 50
    height = 30
    angle_rad = math.radians(player_angle)
    eyeX = player_pos[0] - math.cos(angle_rad) * offset
    eyeY = player_pos[1] - math.sin(angle_rad) * offset
    eyeZ = player_pos[2] + height
    centerX = player_pos[0]
    centerY = player_pos[1]
    centerZ = player_pos[2] + 20
    gluLookAt(eyeX, eyeY, eyeZ, centerX, centerY, centerZ, 0, 0, 1)





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



    draw_text(10, 1050, f"Score: {score}  Treasures Left: {len(treasures)}")
    draw_text(10, 1020, f"Life: {player_life}  Time: {int(game_time)} s")
    if power_up_active:
        draw_text(10, 990, "Power-Up Active!")
    if game_won:
        draw_text(860, 540, "VICTORY! Press 'r' to restart.")
    if game_over:
        draw_text(860, 540, "GAME OVER! Press 'r' to restart.")




    # smoke/hazy effect during ceiling collapse feature
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
        glColor4f(0.5, 0.5, 0.5, 0.3)  # Grayish, semi-transparent
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
