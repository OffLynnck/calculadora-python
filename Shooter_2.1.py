
from pygame import *
from random import randint

# Inicialización
font.init()
font_main = font.Font(None, 36)
font_huge = font.Font(None, 72)

# Imágenes
img_back = "fondo.jpg"
img_hero = "p1.png"
img_bullet = "bala.webp"
img_enemy = "enemy.png"
img_enemy_adv = "zombie2.png" 
img_boss = "jefe.webp"         
img_win = "win.jpg"
img_los = "govr.png"

# --- CLASES ---
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0 or self.rect.y > win_height:
            self.kill()

class Enemy(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed, health=1):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.health = health

    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.y = 0
            self.rect.x = randint(80, win_width - 80)
            lost += 1

class AdvancedEnemy(Enemy):
    def update(self):
        super().update()
        if randint(1, 100) == 5:
            self.fire()

    def fire(self):
        enemy_bullet = Bullet(img_bullet, self.rect.centerx, self.rect.bottom, 15, 20, 7)
        enemy_bullets.add(enemy_bullet)

# Configuración de ventana
win_width, win_height = 564, 846
window = display.set_mode((win_width, win_height))
display.set_caption("Shooter: Zombie Invasion")
background = transform.scale(image.load(img_back), (win_width, win_height))

# FUNCIÓN DE REINICIO 
def reset_game():
    global score, lost, current_round, finish, boss_spawned, boss
    score = 0
    lost = 0
    current_round = 1
    finish = False
    boss_spawned = False
    boss = None # Limpiar referencia al jefe
    
    # Limpiar grupos
    monsters.empty()
    bullets.empty()
    enemy_bullets.empty()
    
    # Reposicionar jugador
    ship.rect.x = win_width // 2
    ship.rect.y = win_height - 100
    
    # Re-crear enemigos iniciales
    for i in range(5):
        m = Enemy(img_enemy, randint(50, win_width-80), randint(-400, -50), 80, 50, randint(1, 3))
        monsters.add(m)

# Objetos iniciales
ship = Player(img_hero, win_width//2, win_height - 100, 80, 100, 10)
monsters = sprite.Group()
bullets = sprite.Group()
enemy_bullets = sprite.Group()

# Llamamos al reset para iniciar la primera vez
reset_game()

run = True
while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE and not finish:
                ship.fire()
            # Lógica para reiniciar con la tecla R
            if e.key == K_r and finish:
                reset_game()

    if not finish:
        window.blit(background, (0, 0))

        # Lógica de Rondas
        if score >= 40 and current_round == 1:
            current_round = 2
            adv = AdvancedEnemy(img_enemy_adv, randint(50, win_width-80), -100, 80, 60, 1, 3)
            monsters.add(adv)
            
        if score >= 80 and current_round == 2:
            current_round = 3
            
        if score >= 120 and current_round == 3 and not boss_spawned:
            boss = AdvancedEnemy(img_boss, win_width//2 - 100, -200, 200, 150, 1, 20)
            monsters.add(boss)
            boss_spawned = True

        # Actualizaciones
        ship.update()
        monsters.update()
        bullets.update()
        enemy_bullets.update()

        # Colisiones
        collides = sprite.groupcollide(monsters, bullets, False, True)
        for m in collides:
            m.health -= 1
            if m.health <= 0:
                if isinstance(m, AdvancedEnemy):
                    score += 7
                else:
                    score += 2
                m.kill()
                if not isinstance(m, AdvancedEnemy) or current_round == 2:
                    new_m = Enemy(img_enemy, randint(50, win_width-80), -50, 80, 50, randint(1, 3))
                    monsters.add(new_m)

        # Dibujado
        ship.reset()
        monsters.draw(window)
        bullets.draw(window)
        enemy_bullets.draw(window)

        # Textos
        txt_score = font_main.render(f"Puntaje: {score}", True, (255, 255, 255))
        txt_lost = font_main.render(f"Fallidos: {lost}", True, (255, 255, 255))
        txt_round = font_main.render(f"Ronda: {current_round}", True, (255, 200, 0))
        window.blit(txt_score, (10, 20))
        window.blit(txt_lost, (10, 50))
        window.blit(txt_round, (win_width - 120, 20))

        # Derrota
        if sprite.spritecollide(ship, monsters, False) or sprite.spritecollide(ship, enemy_bullets, False) or lost >= 5:
            finish = True
            window.blit(transform.scale(image.load(img_los), (win_width, win_height)), (0, 0))
            # Instrucción de reinicio
            txt_restart = font_main.render("Presiona R para reiniciar", True, (255, 255, 255))
            window.blit(txt_restart, (win_width//2 - 130, win_height//2 -210))
            print("Finish")

        # Victoria
        if current_round == 3 and boss_spawned and not monsters.has(boss):
            finish = True
            window.blit(transform.scale(image.load(img_win), (win_width, win_height)), (0, 0))
            txt_restart = font_main.render("Presiona R para jugar de nuevo", True, (255, 255, 255))
            window.blit(txt_restart, (win_width//2 - 120, win_height//2 + 100))
            print("Finish")

    display.update()
    time.delay(30)
