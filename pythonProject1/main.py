import tkinter as tk
import config
from LEVELS import LEVELS

window = tk.Tk()
window.title(config.GAME_TITLE)
window.geometry("500x400")

current_level = 0
energy = 20
steps = 0
score = 0
has_key = False
time_left = 120
total_time = 0
danger_hits = 0
level_danger_hits = 0
visited_cells = set()
achievements = set()

is_paused = False
game_over = False
timer_id = None

grid = []
player_r = 1
player_c = 1
cells = []


def start_game():
    global current_level, energy, steps, score, has_key, time_left
    global total_time, danger_hits, level_danger_hits, visited_cells, achievements
    global is_paused, game_over, timer_id

    current_level = 0
    score = 0
    steps = 0
    total_time = 0
    danger_hits = 0
    achievements = set()

    game_window = tk.Toplevel(window)
    game_window.title(config.GAME_TITLE)
    game_window.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
    game_window.minsize(480, 520)

    lbl_info = tk.Label(game_window, text="", font=("Arial", 11, "bold"))
    lbl_info.pack(pady=8)

    lbl_msg = tk.Label(game_window, text="Найдите ключ (K)", font=("Arial", 11), fg="green")
    lbl_msg.pack(pady=2)

    btn_frame = tk.Frame(game_window)
    btn_frame.pack(pady=5)

    center_frame = tk.Frame(game_window)
    center_frame.pack(expand=True)

    board_frame = tk.Frame(center_frame)
    board_frame.pack()

    pause_frame = tk.Frame(center_frame, bg="gray90", bd=2, relief="ridge", width=350, height=350)
    pause_frame.pack_propagate(False)
    tk.Label(pause_frame, text="ПАУЗА", font=("Arial", 20, "bold"), bg="gray90").pack(pady=60)
    tk.Button(pause_frame, text="Продолжить", font=("Arial", 12), width=15, command=lambda: toggle_pause()).pack(pady=10)
    tk.Button(pause_frame, text="Начать заново", font=("Arial", 12), width=15, command=lambda: restart_game()).pack(pady=10)

    cells.clear()
    for r in range(7):
        row_list = []
        for c in range(7):
            cell_box = tk.Frame(board_frame, width=50, height=50, bd=1, relief="solid")
            cell_box.pack_propagate(False)
            cell_box.grid(row=r, column=c)

            lbl = tk.Label(cell_box, text="", font=("Courier", 14, "bold"))
            lbl.pack(expand=True, fill="both")
            row_list.append(lbl)
        cells.append(row_list)

    def load_level(lvl_idx):
        global grid, player_r, player_c, energy, has_key, time_left, level_danger_hits, visited_cells

        energy = 20
        has_key = False
        time_left = 120
        level_danger_hits = 0
        visited_cells = set()

        grid = [list(row) for row in LEVELS[lvl_idx]]
        for r in range(7):
            for c in range(7):
                if grid[r][c] == 'S':
                    player_r = r
                    player_c = c
                    grid[r][c] = '.'

        visited_cells.add((player_r, player_c))
        lbl_msg.config(text=f"Сектор {lvl_idx + 1}: Найдите ключ (K)", fg="green")
        update_screen()

    def update_screen():
        k_text = "Да" if has_key else "Нет"
        mins = time_left // 60
        secs = time_left % 60
        time_str = f"{mins:02d}:{secs:02d}"

        lbl_info.config(
            text=f"Уровень: {current_level + 1}/3 | Время: {time_str} | Энергия: {energy}/20 | Очки: {score} | Шаги: {steps} | Ключ: {k_text}"
        )

        for r in range(7):
            for c in range(7):
                val = grid[r][c]
                color = "white"
                fg_color = "black"
                txt = val

                if val == '#':
                    color = "dimgray"
                    txt = ""
                elif val == '.':
                    color = "whitesmoke"
                    txt = ""
                elif val == 'K':
                    color = "gold"
                elif val == 'E':
                    color = "lightgreen"
                elif val == 'B':
                    color = "deepskyblue"
                elif val == 'X':
                    color = "red"

                if r == player_r and c == player_c:
                    color = "royalblue"
                    fg_color = "white"
                    txt = "p"

                cells[r][c].config(bg=color, fg=fg_color, text=txt)

    def show_end_screen(is_win, reason=""):
        global game_over, timer_id
        game_over = True
        if timer_id is not None:
            game_window.after_cancel(timer_id)
            timer_id = None

        for widget in game_window.winfo_children():
            widget.destroy()

        title_txt = "ПОБЕДА! СТАНЦИЯ ПРОЙДЕНА" if is_win else "ПОРАЖЕНИЕ"
        title_col = "green" if is_win else "red"

        tk.Label(game_window, text=title_txt, font=("Arial", 18, "bold"), fg=title_col).pack(pady=20)

        if not is_win:
            tk.Label(game_window, text=f"Причина: {reason}", font=("Arial", 13, "bold"), fg="darkred").pack(pady=5)
            tk.Label(game_window, text=f"Достигнутый уровень: {current_level + 1}", font=("Arial", 12)).pack(pady=3)

        tk.Label(game_window, text=f"Итоговый счёт: {score}", font=("Arial", 12)).pack(pady=3)
        tk.Label(game_window, text=f"Выполнено шагов: {steps}", font=("Arial", 12)).pack(pady=3)

        if is_win:
            t_mins = total_time // 60
            t_secs = total_time % 60
            tk.Label(game_window, text=f"Попаданий в опасные зоны: {danger_hits}", font=("Arial", 12)).pack(pady=3)
            tk.Label(game_window, text=f"Общее время: {t_mins:02d}:{t_secs:02d}", font=("Arial", 12)).pack(pady=3)

        ach_text = ", ".join(achievements) if achievements else "Нет"
        tk.Label(game_window, text=f"Достижения: {ach_text}", font=("Arial", 11, "italic"), wraplength=450).pack(pady=15)

        tk.Button(
            game_window,
            text="Начать новую игру",
            font=("Arial", 13),
            command=lambda: [game_window.destroy(), start_game()]
        ).pack(pady=15)

    def tick():
        global time_left, total_time, timer_id
        if game_over or not game_window.winfo_exists():
            return

        if not is_paused:
            if time_left > 0:
                time_left -= 1
                total_time += 1
                update_screen()
                if time_left == 0:
                    show_end_screen(False, "Время истекло")
                    return

        timer_id = game_window.after(1000, tick)

    def toggle_pause(event=None):
        global is_paused
        if game_over:
            return
        is_paused = not is_paused
        if is_paused:
            board_frame.pack_forget()
            pause_frame.pack()
        else:
            pause_frame.pack_forget()
            board_frame.pack()
            game_window.focus_force()

    def restart_game():
        global is_paused, game_over, current_level, score, steps, total_time, danger_hits, achievements, timer_id
        if timer_id is not None:
            game_window.after_cancel(timer_id)
            timer_id = None

        is_paused = False
        game_over = False
        current_level = 0
        score = 0
        steps = 0
        total_time = 0
        danger_hits = 0
        achievements = set()

        pause_frame.pack_forget()
        board_frame.pack()
        load_level(0)
        game_window.focus_force()
        tick()

    tk.Button(btn_frame, text="Пауза (Esc)", font=("Arial", 10), command=toggle_pause).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Начать заново", font=("Arial", 10), command=restart_game).pack(side="left", padx=10)

    def on_key(event):
        global player_r, player_c, energy, steps, has_key, score, current_level, danger_hits, level_danger_hits

        if game_over or is_paused:
            return

        code = event.keycode
        k = event.keysym.lower()
        dr, dc = 0, 0

        if k in ("up", "w") or code == 87:
            dr = -1
        elif k in ("down", "s") or code == 83:
            dr = 1
        elif k in ("left", "a") or code == 65:
            dc = -1
        elif k in ("right", "d") or code == 68:
            dc = 1
        else:
            return

        nr = player_r + dr
        nc = player_c + dc

        # Проверка границ и стен
        if 0 <= nr < 7 and 0 <= nc < 7 and grid[nr][nc] != '#':
            player_r = nr
            player_c = nc
            steps += 1
            energy -= 1
            visited_cells.add((nr, nc))

            cell_type = grid[nr][nc]

            if cell_type == 'K':
                has_key = True
                grid[nr][nc] = '.'
                score += 10
                lbl_msg.config(text="Ключ найден (+10 очков)! Идите к выходу (E)", fg="blue")

            elif cell_type == 'B':
                grid[nr][nc] = '.'
                energy = min(20, energy + 5)
                lbl_msg.config(text="Аккумулятор подобран (+5 энергии)!", fg="teal")

            elif cell_type == 'X':
                energy -= 3
                score = max(0, score - 5)
                danger_hits += 1
                level_danger_hits += 1
                lbl_msg.config(text="Опасная зона! -3 энергии, -5 очков", fg="red")

            elif cell_type == 'E':
                if not has_key:
                    lbl_msg.config(text="Дверь заперта! Сначала найдите ключ (K)", fg="orange")
                else:
                    if level_danger_hits == 0:
                        achievements.add("Без потерь")
                    if len(visited_cells) >= 15:
                        achievements.add("Исследователь")

                    score += 20
                    if current_level < len(LEVELS) - 1:
                        current_level += 1
                        load_level(current_level)
                        return
                    else:
                        achievements.add("Мастер станции")
                        update_screen()
                        show_end_screen(True)
                        return

            update_screen()

            if energy <= 0:
                show_end_screen(False, "Энергия закончилась")

    def on_close():
        global game_over, timer_id
        game_over = True
        if timer_id is not None:
            game_window.after_cancel(timer_id)
            timer_id = None
        game_window.destroy()

    game_window.protocol("WM_DELETE_WINDOW", on_close)
    game_window.bind("<Escape>", toggle_pause)
    game_window.bind("<KeyPress>", on_key)

    is_paused = False
    game_over = False
    load_level(0)
    game_window.focus_force()
    tick()


# Главное меню
tk.Label(window, text="Станция 13", font=("Arial", 22, "bold")).pack(pady=25)
tk.Label(
    window,
    text=("Правила:\n"
            "Соберите ключ (K) и дойдите до выхода (E) за 120 сек.\n"
            "Аккумулятор (B): +5 энергии | Опасная зона (X): -3 энергии, -5 очков."),
    font=("Arial", 10),
    justify="center"
).pack(pady=10)
tk.Button(window, text="Начать игру", font=("Arial", 14), command=start_game).pack(pady=25)

window.mainloop()
