from tkinter import (Button,
                     Frame,
                     Canvas,
                     Tk,
                     Listbox,
                     END)

from .sokoban_engine import Storage
from .constants import (UP,
                        DOWN,
                        LEFT,
                        RIGHT)

from .settings import (LevelHandler,
                       Settings)


class Window:

    def __init__(self, program):
        self.program = program

    def dispose(self):
        pass

    def show(self):
        pass

    def change(self, window):
        self.program.set_window(window)


class LoginScreen(Window):

    def __init__(self, program):
        super().__init__(program)
        # self.buttons = []
        self.levels = None
        self.settings = program.settings
        self.level_handler = LevelHandler(program.settings)
        self.frame = Frame(program.master, width=800, height=800)
        self.frame.pack(side='top', fill='both', expand=1)
        self.show()

    def add_button(self, text, command):
        button = Button(self.frame, text=text, width=100, height=20,
                        command=command)
        button.pack()
        # self.buttons.append(button)

    def dispose(self):
        # for button in self.buttons:
        #     button.pack_forget()
        self.frame.pack_forget()
        # while self.buttons:
        #     button = self.buttons.pop()
        #     button.destroy()
        self.frame.destroy()
        self.frame = None

    def show(self):
        self.add_button('New Game', self.new_game)
        self.add_button('Load Game', self.load_game)
        # self.add_button('Load Level', self.load_level)
        self.add_button('Exit', self.exit)
        self.frame.tkraise()

    def new_game(self):
        self.dispose()
        g = Game(self.program)
        g.new()
        self.change(Game(self.program))

    def exit(self):
        self.program.exit()

    def load_game(self):
        self.dispose()
        lg = LoadGame(self.program)
        lg.show()
        self.change(lg)

    def clear(self):
        self.frame.pack_forget()
        self.level_handler = None
        self.frame.destroy()


class LoadGame(Window):

    def __init__(self, program):
        super().__init__(program)
        self.frame = Frame(program.master, width=800, height=800)
        self.frame.pack(side='top', fill='both', expand=1)
        self.listbox = Listbox()
        self.save_names = []

    def dispose(self):
        self.listbox.pack_forget()
        self.frame.pack_forget()
        self.listbox.destroy()
        self.frame.destroy()
        self.listbox = None
        self.frame = None

    def show(self):
        for file_name, file_path in self.program.settings.list_saves():
            self.listbox.insert(END, file_name)
            self.save_names.append(file_name)
        self.listbox.pack()
        self.add_button('Back', self.back)
        self.add_button('Load', self.load)

    def load(self):
        selection = next(iter(map(int, self.listbox.curselection())))
        self.dispose()
        g = Game(self.program)
        g.load(self.save_names[selection])
        self.change(g)

    def back(self):
        self.dispose()
        self.change(LoginScreen(self.program))

    def add_button(self, text, command):
        button = Button(self.frame, text=text, width=100, height=20,
                        command=command)
        button.pack()


class Game(Window):

    def __init__(self, program):
        super().__init__(program)
        self.master = program.master
        self.storage = None
        self.level_handler = LevelHandler(self.program.settings)
        self.frame = Frame(self.master, width=800, height=800)
        self.frame.pack(side='top', anchor='ne', fill='both', expand=1)
        self.canvas = Canvas(self.frame, width=800, height=800)
        self.canvas.pack(side='top', fill='both', expand=1)
        # self.canvas.tkraise()
        self.level = None
        self.moves = 0

    def load(self, save):
        plan = self.level_handler.load(save)
        Storage.validate(plan)
        self.storage = Storage.create(self, plan)
        self.level = save
        self.bind()
        self.update()

    def new(self):
        lvl_name, lvl_path = next(self.level_handler.list_levels())
        plan = self.level_handler.load_level(lvl_name)
        Storage.validate(plan)
        self.storage = Storage.create(self, plan)
        self.level = lvl_name
        self.bind()
        self.update()

    def save(self):
        self.level_handler.save(self.storage, 'last_save_{}'.format(self.level))

    def bind(self):
        self.master.bind('<Up>', self.on_up_key)
        self.master.bind('<Down>', self.on_down_key)
        self.master.bind('<Left>', self.on_left_key)
        self.master.bind('<Right>', self.on_right_key)
        self.master.bind('<F2>', self.on_f2_key)
        self.master.bind('<Escape>', self.on_esc_key)

    def unbind(self):
        self.master.unbind('<Up>')
        self.master.unbind('<Down>')
        self.master.unbind('<Left>')
        self.master.unbind('<Right>')
        self.master.unbind('<F2>')

    def show(self):
        self.bind()

    def dispose(self):
        self.unbind()
        self.master.unbind('<Escape>')

        self.canvas.delete("all")
        for child in self.canvas.winfo_children():
            child.pack_forget()
        self.canvas.pack_forget()
        self.frame.pack_forget()
        self.frame.destroy()
        self.canvas.destroy()

    def on_down_key(self, event):
        self.storage.get_player().move(DOWN)
        self.moves += 1
        self.update()

    def on_up_key(self, event):
        self.storage.get_player().move(UP)
        self.moves += 1
        self.update()

    def on_right_key(self, event):
        self.storage.get_player().move(RIGHT)
        self.moves += 1
        self.update()

    def on_left_key(self, event):
        self.storage.get_player().move(LEFT)
        self.moves += 1
        self.update()

    def on_esc_key(self, event):
        self.exit()

    def on_f2_key(self, event):
        self.save()

    def exit(self):
        self.dispose()
        self.program.reset()
        self.change(LoginScreen(self.program))

    def get_canvas_dimensions(self):
        return (self.program.settings.canvas_width,
                self.program.settings.canvas_height)

    def get_square_dimensions(self):
        return (self.program.settings.square_width,
                self.program.settings.square_height)

    def update(self):
        self.canvas.delete("all")
        self.storage.render(self.canvas)
        if self.storage.has_won():
            width, height = self.get_canvas_dimensions()
            self.unbind()
            self.canvas.create_text(width // 2,
                                    height // 2,
                                    text="You won! Press <ESC>",
                                    fill='#ffff00',
                                    anchor="center")
        self.canvas.create_text(50, 50, text='Moves {}'.format(self.moves),
                                fill='#ffff00', anchor='nw')


class Program:

    def __init__(self):
        self.settings = Settings()
        self.master = Tk()
        self.master.title('Sokoban')
        self.widow = LoginScreen(self)

    def set_window(self, window):
        self.window = window
        # self.window.frame.pack(side='top')

    def reset(self):
        self.master.pack_propagate(0)
        self.master.wm_resizable(*self.get_canvas_dimensions())

    def exit(self):
        self.settings.save()
        self.master.destroy()

    def get_square_dimensions(self):
        return (self.settings.square_width,
                self.settings.square_height)

    def get_canvas_dimensions(self):
        return (self.settings.canvas_width,
                self.settings.canvas_height)
