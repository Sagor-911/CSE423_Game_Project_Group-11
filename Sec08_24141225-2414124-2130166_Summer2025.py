from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import math
import random
import time

camera_pos = [0.0, 500.0, 500.0]
camera_dist = math.hypot(camera_pos[0], camera_pos[1])
camera_angle = math.atan2(camera_pos[1], camera_pos[0])

fovY = 120  
GRID_LENGTH = 600

# --- Game state variables ---
player_pos = [0.0, 0.0]
player_angle = 0.0
player_height = 30.0
player_speed = 6.0
player_radius = 30.0

bullets = []
bullet_speed = 500.0
bullet_size = 12.0
bullets_missed = 0
max_missed = 10

enemies = []
enemy_count = 5
enemy_speed = 0.1
enemy_base_radius = 30.0
enemy_shrink_amp = 8.0

score = 0
life = 5
game_over = False

cheat_mode = False
cheat_auto_follow = False
last_auto_fire = 0.0
auto_fire_interval = 0.25

first_person = False

last_frame_time = time.time()

GROUND_Z = 0.0
random.seed(423)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18): # type: ignore
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_player():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_height)

    # === ROTATE WHOLE PLAYER ===
    glRotatef(player_angle, 0, 0, 1)

    # === HEAD ===
    glPushMatrix()
    glColor3f(0.95, 0.85, 0.65)
    glTranslatef(0, 0, 65)
    glutSolidSphere(15.0, 24, 24)
    glPopMatrix()

    # === TORSO ===
    glPushMatrix()
    glColor3f(0.2, 0.6, 1.0)
    glTranslatef(0, 0, 40)
    glutSolidCube(30.0)
    glPopMatrix()

    # === HANDS ===
    # Right hand
    glPushMatrix()
    glColor3f(0.7, 0.7, 0.7)
    glTranslatef(10, 15, 45)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 4.0, 4.0, 25.0, 20, 20)
    glPopMatrix()

    # Left hand
    glPushMatrix()
    glColor3f(0.7, 0.7, 0.7)
    glTranslatef(-10, 15, 45)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 4.0, 4.0, 25.0, 20, 20)
    glPopMatrix()

    # === GUN ===
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(0, 15, 45)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3.5, 3.5, 40.0, 20, 20)
    glPopMatrix()

    # Right leg
    glPushMatrix()
    glColor3f(0.3, 0.3, 0.3)
    glTranslatef(10, 0, 25)
    glRotatef(180, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5.0, 3.0, 25.0, 20, 20)
    glPopMatrix()

    # Left leg
    glPushMatrix()
    glColor3f(0.3, 0.3, 0.3)
    glTranslatef(-10, 0, 25)
    glRotatef(180, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5.0, 3.0, 25.0, 20, 20)
    glPopMatrix()


    glPopMatrix()

def draw_enemy(e):
    x, y = e['pos']
    t = time.time() + e['time_offset']
    r = e['base_radius'] + math.sin(t * 3.0) * enemy_shrink_amp

    glPushMatrix()
    glTranslatef(x, y, player_height)
    glPushMatrix()
    glTranslatef(0, 0, -6.0)
    glColor3f(1.0, 0.3, 0.3)
    glutSolidSphere(abs(r * 0.9), 16, 16)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0, r * 0.4)
    glColor3f(0.9, 0.6, 0.1)
    glutSolidSphere(abs(r * 0.6), 12, 12)
    glPopMatrix()
    glPopMatrix()

def reset_enemy(e):
    margin = GRID_LENGTH - 50
    side = random.choice([0, 1, 2, 3])
    if side == 0:
        x = random.uniform(-margin, margin)
        y = margin
    elif side == 1:
        x = random.uniform(-margin, margin)
        y = -margin
    elif side == 2:
        x = -margin
        y = random.uniform(-margin, margin)
    else:
        x = margin
        y = random.uniform(-margin, margin)

    e['pos'] = [x, y]
    e['time_offset'] = random.random() * 10.0
    e['base_radius'] = enemy_base_radius

def spawn_enemies():
    enemies.clear()
    for i in range(enemy_count):
        e = {'pos': [0.0, 0.0], 'base_radius': enemy_base_radius, 'time_offset': random.random() * 10.0}
        reset_enemy(e)
        enemies.append(e)

def fire_bullet():
    rad = math.radians(player_angle)

    dir_x = -math.sin(rad)
    dir_y = math.cos(rad)

    start_x = player_pos[0] + dir_x * 60.0
    start_y = player_pos[1] + dir_y * 60.0
    start_z = player_height + 26.0

    b = {
        'pos': [start_x, start_y, start_z],
        'dir': [dir_x, dir_y, 0.0],
        'alive': True
    }
    bullets.append(b)

def fire_bullet_at_target(target_pos):
    start_x = player_pos[0]
    start_y = player_pos[1]
    start_z = player_height + 26.0

    dx = target_pos[0] - start_x
    dy = target_pos[1] - start_y
    dist = math.hypot(dx, dy)

    if dist < 1e-6:
        dir_x, dir_y = 0, 0
    else:
        dir_x = dx / dist
        dir_y = dy / dist

    b = {
        'pos': [start_x, start_y, start_z],
        'dir': [dir_x, dir_y, 0.0],
        'alive': True
    }
    bullets.append(b)

def update_bullets(dt):
    global bullets_missed, game_over
    for b in bullets:
        if not b['alive']:
            continue
        b['pos'][0] += b['dir'][0] * bullet_speed * dt
        b['pos'][1] += b['dir'][1] * bullet_speed * dt

        if not cheat_mode:
            bx, by, bz = b['pos']
            wall_height = 120.0
            if (abs(bx) >= GRID_LENGTH and bz <= wall_height) or (abs(by) >= GRID_LENGTH and bz <= wall_height):
                b['alive'] = False
                bullets_missed += 1
                if bullets_missed >= max_missed:
                    game_over = True
            elif abs(bx) > GRID_LENGTH + 200 or abs(by) > GRID_LENGTH + 200:
                b['alive'] = False
                bullets_missed += 1
                if bullets_missed >= max_missed:
                    game_over = True
    bullets[:] = [b for b in bullets if b['alive']]

def update_enemies(dt):
    global life, game_over
    for e in enemies:
        ex, ey = e['pos']
        dx = player_pos[0] - ex
        dy = player_pos[1] - ey
        dist = math.hypot(dx, dy)
        if dist > 1e-6:
            e['pos'][0] += (dx / dist) * enemy_speed * dt * 60.0
            e['pos'][1] += (dy / dist) * enemy_speed * dt * 60.0
        if math.hypot(e['pos'][0] - player_pos[0], e['pos'][1] - player_pos[1]) < (player_radius + e['base_radius'] * 0.6):
            life -= 1
            reset_enemy(e)
            if life <= 0:
                game_over = True

def check_bullet_enemy_collisions():
    global score
    for b in bullets:
        if not b['alive']:
            continue
        for e in enemies:
            ex, ey = e['pos']
            dist = math.hypot(b['pos'][0] - ex, b['pos'][1] - ey)
            hit_radius = e['base_radius'] * 0.8
            if dist < hit_radius:
                b['alive'] = False
                score += 1
                reset_enemy(e)
                break
    bullets[:] = [b for b in bullets if b['alive']]

def keyboardListener(key, x, y):
    global cheat_mode, cheat_auto_follow, score, life, bullets_missed, game_over, first_person, player_angle

    if key == b's':
        rad = math.radians(player_angle)
        player_pos[0] += math.sin(rad) * player_speed
        player_pos[1] -= math.cos(rad) * player_speed
    elif key == b'w':
        rad = math.radians(player_angle)
        player_pos[0] -= math.sin(rad) * player_speed
        player_pos[1] += math.cos(rad) * player_speed
    elif key == b'a':
        player_angle = (player_angle + 6.0) % 360.0
    elif key == b'd':
        player_angle = (player_angle - 6.0) % 360.0
    elif key == b'c':
        cheat_mode = not cheat_mode
    elif key == b'v':
        cheat_auto_follow = not cheat_auto_follow
    elif key == b'r':
        score = 0
        life = 5
        bullets_missed = 0
        game_over = False
        spawn_enemies()
        bullets.clear()
    elif key == b'\x1b':
        glutLeaveMainLoop()

def specialKeyListener(key, x, y):
    global camera_pos, camera_angle, camera_dist
    if key == GLUT_KEY_UP:
        camera_pos[2] += 10
    elif key == GLUT_KEY_DOWN:
        camera_pos[2] -= 10
    elif key == GLUT_KEY_LEFT:
        camera_angle += 0.1
        camera_pos[0] = camera_dist * math.cos(camera_angle)
        camera_pos[1] = camera_dist * math.sin(camera_angle)
    elif key == GLUT_KEY_RIGHT:
        camera_angle -= 0.1
        camera_pos[0] = camera_dist * math.cos(camera_angle)
        camera_pos[1] = camera_dist * math.sin(camera_angle)

def mouseListener(button, state, x, y):
    global first_person, last_auto_fire, game_over
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not game_over:
            now = time.time()
            if now - last_auto_fire >= 0.07:
                fire_bullet()
                last_auto_fire = now
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person = not first_person

def setupCamera():
    global first_person
    if cheat_mode and cheat_auto_follow:
        first_person = True

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if first_person:
        rad = math.radians(player_angle)

        forwardX = -math.sin(rad)
        forwardY = math.cos(rad)

        eyeX = player_pos[0]
        eyeY = player_pos[1]
        eyeZ = player_height + 85.0

        centerX = eyeX + forwardX * 200.0
        centerY = eyeY + forwardY * 200.0
        centerZ = eyeZ

        gluLookAt(eyeX, eyeY, eyeZ, centerX, centerY, centerZ, 0, 0, 1)
    else:
        xcam, ycam, zcam = camera_pos
        gluLookAt(xcam, ycam, zcam, 0, 0, 0, 0, 0, 1)

def enemy_has_bullet(e):
    ex, ey = e['pos']
    for b in bullets:
        if not b['alive']:
            continue
        bx, by, _ = b['pos']

        dx = ex - bx
        dy = ey - by
        dot = b['dir'][0]*dx + b['dir'][1]*dy
        if dot > 0:
            dist = math.hypot(dx, dy)
            if dist < 10.0:
                continue
            return True
    return False

def idle():
    global last_frame_time, player_angle, last_auto_fire
    now = time.time()
    dt = now - last_frame_time
    if dt > 0.1:
        dt = 0.1
    last_frame_time = now

    if not game_over:
        if cheat_mode:
            player_angle = (player_angle + 120.0 * dt) % 360.0

            nowf = time.time()
            if nowf - last_auto_fire >= auto_fire_interval:
                for e in enemies:
                    if not enemy_has_bullet(e):
                        ex, ey = e['pos']
                        fire_bullet_at_target([ex, ey, player_height])
                last_auto_fire = nowf

        update_bullets(dt)
        update_enemies(dt)
        check_bullet_enemy_collisions()

    glutPostRedisplay()

def draw_grid_and_boundaries():
    square_size = 60
    num_squares = int(GRID_LENGTH * 2 / square_size)
    for i in range(-num_squares // 2, num_squares // 2):
        for j in range(-num_squares // 2, num_squares // 2):
            glColor3f(1.0, 1.0, 1.0) if (i + j) % 2 == 0 else glColor3f(0.7, 0.5, 0.95)
            glBegin(GL_QUADS)
            glVertex3f(i * square_size, j * square_size, 0)
            glVertex3f((i + 1) * square_size, j * square_size, 0)
            glVertex3f((i + 1) * square_size, (j + 1) * square_size, 0)
            glVertex3f(i * square_size, (j + 1) * square_size, 0)
            glEnd()

    wall_height = 120.0
    wall_thickness = 8.0
    glColor3f(0.3, 0.3, 0.3)
    #walls
    walls = [
        (-GRID_LENGTH - wall_thickness, GRID_LENGTH, GRID_LENGTH + wall_thickness, GRID_LENGTH),
        (-GRID_LENGTH - wall_thickness, -GRID_LENGTH, GRID_LENGTH + wall_thickness, -GRID_LENGTH),
        (GRID_LENGTH, -GRID_LENGTH - wall_thickness, GRID_LENGTH, GRID_LENGTH + wall_thickness),
        (-GRID_LENGTH, -GRID_LENGTH - wall_thickness, -GRID_LENGTH, GRID_LENGTH + wall_thickness)
    ]
    for w in walls:
        glBegin(GL_QUADS)
        glVertex3f(w[0], w[1], 0)
        glVertex3f(w[2], w[3], 0)
        glVertex3f(w[2], w[3], wall_height)
        glVertex3f(w[0], w[1], wall_height)
        glEnd()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    draw_grid_and_boundaries()
    draw_player()
    for e in enemies:
        draw_enemy(e)
    for b in bullets:
        if not b['alive']:
            continue
        glPushMatrix()
        glTranslatef(b['pos'][0], b['pos'][1], b['pos'][2])
        glColor3f(0.95, 0.95, 0.2)
        glutSolidCube(bullet_size)
        glPopMatrix()
    draw_text(10, 770, f"Score: {score}")
    draw_text(10, 740, f"Life: {life}")
    draw_text(10, 710, f"Missed: {bullets_missed}/{max_missed}")

    if game_over:
        draw_text(400, 400, "GAME OVER - Press R to Restart")
        glPushMatrix()
        glTranslatef(player_pos[0], player_pos[1], player_height - 8.0)
        glRotatef(90, 0, 1, 0)
        glColor3f(0.5, 0.2, 0.2)
        glutSolidSphere(22.0, 20, 20)
        glPopMatrix()
    glutSwapBuffers()

def main():
    global last_frame_time
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Game")
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    spawn_enemies()
    last_frame_time = time.time()
    glutMainLoop()

if __name__ == "__main__":
    main()