import cProfile
import pstats
import main  # Replace with your actual script name

profiler = cProfile.Profile()
profiler.enable()
main.game_loop()
profiler.disable()

stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats()
