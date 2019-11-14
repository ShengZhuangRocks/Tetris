# A copycat of classic Tetris game written in python

to get the game logic straight, I am using python OOP here trying to get everything organise. The purpose is to make the code readable for everyone.

- brick--brick patterns, aka those falling pieces, how those small tiles form a specific brick pattern
- brick--physical logics like coalition, falling, rotating etc.
- wall --draw wall after brick attached
- wall --physical logics like to clear line when the line is solid, check if game over by the wall touching the ceiling
- game board -- draw the game board, the grids, next brick and score etc.
- Pygame -- game logic to switch between main screen, run, pause, restart the game

---

- brick.py

>all about brick pattern, in one class
>
>7 brick patterns in 4 directions each to be represented in a two-dimensional array.
>
>Basic brick pattern itself is a two-dimensional array
>
>also provide a method to get brick coordinate using array

- tetris.py

---
#### TODO

- add sound effects
- add levels, right now I only make the falling speed increase over time and make the score scale to the falling speed. 