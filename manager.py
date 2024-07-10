def game_manager(current_screen, selected_area, boss_dragon_filename, player_dragons):
    running = True
    displayed_quests = []
    boss_dragon_stats = None

    global selected_dragon_for_upgrade
    global inventory, egg_counts, inventory_slots
    inventory, egg_counts, inventory_slots = load_inventory_data()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if current_screen == 'hub':
                    selected_dragon_for_upgrade = handle_upgrade_dragon_click(
                        mouse_x, mouse_y, player_dragons)
                    for i, pos in enumerate([(100, 200), (300, 200), (500, 200), (700, 200), (900, 200)]):
                        dragon_image_file = selected_dragons[i]
                        dragon_image_path = os.path.join(os.path.dirname(__file__), 'assets', 'images', 'dragons', dragon_image_file)
                        dragon_image = load_and_resize_image_keeping_aspect(dragon_image_path, (150, 150))
                        image_rect = dragon_image.get_rect(center=pos)
                        if image_rect.collidepoint(mouse_x, mouse_y):
                            selected_area = list(CATEGORY_INFO.keys())[i]
                            boss_dragon_filename = dragon_image_file
                            boss_dragon = BossDragon(boss_dragon_filename, tier=1)
                            boss_dragon_stats = {
                                'health': boss_dragon.stats['health'],
                                'attack': boss_dragon.stats['attack'],
                                'defense': boss_dragon.stats['defense'],
                                'dodge': boss_dragon.stats['dodge']
                            }
                            all_quests = load_quests(selected_area)
                            displayed_quests = random.sample(all_quests, min(12, len(all_quests)))
                            current_screen = 'area'
                            break
                elif current_screen == 'area':
                    if handle_back_to_hub_click(mouse_x, mouse_y):
                        current_screen = 'hub'
                    else:
                        displayed_quests, quests_updated = handle_quest_click(selected_area, mouse_x, mouse_y,
                                                                              displayed_quests)
                        handle_player_dragon_slot_click(mouse_x, mouse_y, player_dragons)
                        if quests_updated:
                            draw_area_gameboard(selected_area, boss_dragon, player_dragons, displayed_quests)

        if current_screen == 'hub':
            if selected_dragon_for_upgrade:
                display_dragon_statistics(selected_dragon_for_upgrade)
        elif current_screen == 'area' and selected_area is not None:
            draw_area_gameboard(selected_area, boss_dragon, player_dragons, displayed_quests)

        pygame.display.flip()

    pygame.quit()
    print("Game loop ended")
