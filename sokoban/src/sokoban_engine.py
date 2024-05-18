#!/usr/bin/env python3
from os.path import join

from PIL import (ImageTk,
                 Image)

from .constants import (STOREKEEPER,
                        CRATE,
                        WALL,
                        FINAL_POSITION,
                        FLOOR,
                        VALID_CHARACTERS)


class InvalidPlanException(Exception):
    pass


class Positionable:
    IMAGE = None

    def __init__(self, position, storage):
        self.x = position[0]
        self.y = position[1]
        self.storage = storage

    def get_position(self):
        return self.x, self.y

    def can_move(self, direction):
        return False

    def move(self, direction):
        pass
    
    def is_able_to_enter(self):
        return False

    def render(self, canvas):
        pass

    def marshall(self):
        pass

    def get_image(self):
        if self.__class__.IMAGE is None:
            raise Exception('IMAGE can not be None')
        if type(self.__class__.IMAGE) is str:
            sq_w, sq_h = self.storage.get_square_dimensions()
            img = Image.open(join('imgs/', self.__class__.IMAGE))
            img = img.resize((sq_w, sq_h), Image.ANTIALIAS)
            self.__class__.IMAGE = ImageTk.PhotoImage(img)
        return self.__class__.IMAGE


class Movable(Positionable):
    def can_move(self, direction):
        possible_position = self.get_new_position(direction)
        if not self.storage.is_in_bounderies(possible_position):
            return False
        if not self.storage.is_free(possible_position):
            return False
        return True

    def move(self, direction):
        if self.can_move(direction):
            self.update(direction)

    def get_new_position(self, direction):
        return self.x + direction[0], self.y + direction[1]

    def update(self, direction):
        self.storage.delete_from(self.get_new_position(direction))
        self.storage.place(self.get_new_position(direction), self)
        self.storage.delete_from(self.get_position())
        self.x += direction[0]
        self.y += direction[1]


class Crate(Movable):
    IMAGE = 'Crate.png'

    def render(self, graphics):
        square_width, square_height = self.storage.get_square_dimensions()
        x, y = self.get_position()

        graphics.create_image(
            x * square_width + (square_width // 2),
            y * square_height + (square_height // 2),
            image=self.get_image()
        )

    def marshall(self):
        return CRATE


class Wall(Positionable):
    IMAGE = 'Wall.png'

    def render(self, graphics):
        square_width, square_height = self.storage.get_square_dimensions()
        x, y = self.get_position()

        graphics.create_image(
            x * square_width + (square_width // 2),
            y * square_height + (square_height // 2),
            image=self.get_image()
        )

    def marshall(self):
        return WALL


class Storekeeper(Movable):
    IMAGE = 'StorageKeeper.png'

    def move(self, direction):
        possible_position = self.get_new_position(direction)
        if not self.storage.is_in_bounderies(possible_position):
            return
        if self.storage.is_free(possible_position):
            self.update(direction)
        else:
            obj = self.storage.get_object_on(possible_position)
            if obj.can_move(direction):
                obj.move(direction)
                self.update(direction)

    def marshall(self):
        return STOREKEEPER

    def render(self, graphics):
        square_width, square_height = self.storage.get_square_dimensions()

        x, y = self.get_position()

        graphics.create_image(
            x * square_width + (square_width // 2),
            y * square_height + (square_height // 2),
            image=self.get_image()
        )


class FinalPosition(Positionable):
    IMAGE = 'FinalPosition.png'

    def can_move(self, direction):
        return True

    def move(self, direction):
        pass

    def marshall(self):
        return FINAL_POSITION

    def render(self, graphics):
        square_width, square_height = self.storage.get_square_dimensions()
        x, y = self.get_position()
        graphics.create_image(
            x * square_width + (square_width // 2),
            y * square_height + (square_height // 2),
            image=self.get_image()
        )


class Storage:
    def __init__(self, dimensions, program):
        self.program = program
        self.storage_floor = []
        width, height = dimensions
        self.player = None
        self.crates = []

        for _ in range(width):
            self.storage_floor.append([None] * height)

        self.objects = []
        self.final_positions = {}

    def add_final_position(self, final_position):
        self.final_positions[final_position.get_position()] = final_position

    def add_crate(self, crate):
        self.crates.append(crate)
        self.add(crate)

    def add(self, positionable):
        self.place(positionable.get_position(), positionable)
        self.objects.append(positionable)

    def set_player(self, player):
        self.player = player
        self.place(player.get_position(), player)
        self.objects.append(player)

    def marshall(self):
        lines = []
        for y in range(len(self.storage_floor[0])):
            line = ''
            for x in range(len(self.storage_floor)):
                if self.storage_floor[x][y] is None:
                    if (x, y) not in self.final_positions:
                        line += FLOOR
                    else:
                        line += FINAL_POSITION
                else:
                    line += self.storage_floor[x][y].marshall()
            lines.append(line)
        return lines

    def is_on_final(self, position):
        return position in self.final_positions

    def is_free(self, position):        
        if self.get_object_on(position) is None:
            return True
        return False

    def has_won(self):
        for crate in self.crates:
            if crate.get_position() not in self.final_positions:
                return False
        return True

    def get_player(self):
        if self.player is None:
            for row in self.storage_floor:
                for obj in row:
                    if isinstance(obj, Storekeeper):
                        self.player = obj
        return self.player

    def get_object_on(self, position):
        x, y = position
        return self.storage_floor[x][y]

    def place(self, position, obj):
        if self.is_free(position):
            x, y = position
            self.storage_floor[x][y] = obj

    def get_dimensions(self):        
        return len(self.storage_floor), len(self.storage_floor[0])

    def get_square_dimensions(self): 
        return self.program.get_square_dimensions()

    def is_in_bounderies(self, position): 
        x, y = position
        max_x, max_y = self.get_dimensions()
        return 0 <= x < max_x and 0 <= y < max_y

    def delete_from(self, position):      
        x, y = position
        self.storage_floor[x][y] = None

    def _create_vertical_lines(self, graphics):
        canvas_height = self.program.get_canvas_dimensions()[1]
        width = self.get_dimensions()[0]
        square_width, square_height = self.get_square_dimensions()
        for i in range(1, width):
            graphics.create_line(
                i * square_width,
                0,
                i * square_width,
                canvas_height,
                fill='#dddddd')

    def _create_horizontal_lines(self, graphics):
        canvas_width = self.program.get_canvas_dimensions()[0]
        height = self.get_dimensions()[1]
        square_width, square_height = self.get_square_dimensions()
        for j in range(1, height):
            graphics.create_line(
                0,
                j * square_height,
                canvas_width,
                j * square_height,
                fill='#dddddd')

    def render(self, graphics):
        canvas_width, canvas_height = self.program.get_canvas_dimensions()
        graphics.create_rectangle(
            0, 0, canvas_width, canvas_height, fill='#444444')
        self._create_vertical_lines(graphics)
        self._create_horizontal_lines(graphics)
        for obj in self.final_positions.values():
            obj.render(graphics)

        for obj in self.objects:
            obj.render(graphics)

    @staticmethod
    def create(game, plan):
        storage = Storage((len(plan[0]), len(plan)), game)
        for y, row in enumerate(plan):
            for x, char in enumerate(row.strip()):
                if char == FLOOR:
                    continue
                elif char == FINAL_POSITION:
                    fin_p = FinalPosition((x, y), storage)
                    storage.add_final_position(fin_p)
                elif char == WALL:
                    wall = Wall((x, y), storage)
                    storage.add(wall)
                elif char == STOREKEEPER:
                    storekeeper = Storekeeper((x, y), storage)
                    storage.set_player(storekeeper)
                elif char == CRATE:
                    crate = Crate((x, y), storage)
                    storage.add_crate(crate)
        return storage

    @staticmethod
    def validate(plan):
        players = 0
        final_positions = 0
        crates = 0
        width = len(plan[0])
        for row in plan:
            row = row.strip()
            if len(row) != width:
                raise InvalidPlanException('Plan is not rectangular!')
            if not set(row).issubset(VALID_CHARACTERS):
                raise InvalidPlanException(
                    'Plan contains invalid character(s): {}'.format(set(row)))
            for char in row:
                if char == STOREKEEPER:
                    players += 1
                elif char == CRATE:
                    crates += 1
                elif char == FINAL_POSITION:
                    final_positions += 1
        if players != 1:
            raise InvalidPlanException(
                'More then one player in map is not possible!')
        elif final_positions != crates:
            raise InvalidPlanException(
                'Number of crates does not match number of final positions!')
