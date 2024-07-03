from Mixolator import main as mixolator_main
from main import game_loop
from breeding import main as breeding_main
from hatchery import main as hatchery_main

def start_game():
    from main import game_loop
    game_loop()

def start_mixolator():
    from Mixolator import main as mixolator_main
    mixolator_main()

def start_breeding():
    from breeding import main as breeding_main
    breeding_main()

def start_hatchery():
    from hatchery import main as hatchery_main
    hatchery_main()

