# RoboDude - Dungeon Game

RoboDude is a final project I wrote for university. It was my first enconter with the process of developing a 2D game.

In RoboDude, you navigate a maze, collect supplies and fight enemies, with the final objective of reaching *the gate*. Gameplay is split in 2 phases: **Navigation** and **Combat**. In the former, you have full view of the maze and everything within it, and are able to move around. In the latter, you're prevented from navigating the maze and are given options to fight the enemy you've encountered a turn-based manner.

With mechanics such as critical strike chance, possibility to *miss* an attack and critical strike meter (banking a critical attack), I've attempted to make gameplay non-linear.

Navigation:
![maze](./media/readme%20imgs/maze.png)

#

Legend:

![player](./media/readme%20imgs/player.png =250x250) - the player

![enemy](./media/readme%20imgs/ninja.png =250x250) - an enemy

![health blob](./media/readme%20imgs/health.png =250x250) - health blob (restores health)

![plasma blob](./media/readme%20imgs/plasma.png =250x250) - plasma blob (gives +1 ammo)

#

Entering conflict:
![battle](./media/readme%20imgs/prepare.png)

![battle](./media/readme%20imgs/battle.png)

By default, combat begins with *QuickMode* disabled. The game gives you a detailed description and stat listing for every attack inputted by the player, and asks for confirmation before executing it. In *QuickMode* this process is entirely skipped.

![confirm](./media/readme%20imgs/confirm.png)

Since combat is turn-based, the enemy will always strike back after a player attacks.

![enemy attack](./media/readme%20imgs/enemy_attack.png)

The bottom caption will display the most recent action and its effects.

![mid fight](./media/readme%20imgs/progression.png)

The conflict is resolved only when either duelist dies.

![mid fight](./media/readme%20imgs/victory.png)

#

Despite the lack of audio effects and flinching animations, I'm pretty satisfied with the end result. Maybe I should revisit this and add boss music?