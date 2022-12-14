import pya
import numpy as np


class Point:
    """Class Representing a Point in 2D Space"""

    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y

    def offset_y(self, dy: int):
        """returns a new point offset by dy in y direction"""
        return Point(self.x, self.y + dy)

    def offset_x(self, dx: int):
        """returns a new point offset by dx in x direction"""
        return Point(self.x + dx, self.y)

    def offset(self, dx: int, dy: int):
        """returns a new point offset by dx in x direction and dy in y direction"""
        return Point(self.x + dx, self.y + dy)

    def __iter__(self):
        return iter((self.x, self.y))


class MyBox(pya.Box):
    """Class that wraps pya.Box so that it accepts a point reprecenting lower left corner, and a width and height"""

    def __init__(self, lower_left_pos: Point, width: int, height: int) -> None:

        self.lower_left_pos = lower_left_pos
        self.width = width
        self.height = height

        super().__init__(
            self.lower_left_pos.x,
            self.lower_left_pos.y,
            self.lower_left_pos.x + self.width,
            self.lower_left_pos.y + self.height,
        )


class Finger:
    """Class that represents a single finger on a LED hand. Defined by its lower left position and width and height"""

    def __init__(self, start_point: Point, width: int, height: int) -> None:

        self.start_point: Point = start_point
        self.width: int = width
        self.height: int = height

    def draw(self, top, layer) -> None:
        """Draws the finger at the given top and layer"""
        top.shapes(layer).insert(MyBox(self.start_point, self.width, self.height))


class Hand:
    """A class that represents a full hand LED."""

    def __init__(
        self,
        top,
        layer,
        layer_box,
        enclosing_box_fraction,
        start_pos: Point,
        finger_width: int,
        finger_pitch: int,
        width: int,
        height: int,
        scale: int,
        layer_etch=None,
    ) -> None:
        self.top = top
        self.layer = layer
        self.layer_box = layer_box
        self.layer_etch = layer_etch
        self.enclosing_box_fraction = enclosing_box_fraction
        self.start_pos: Point = start_pos
        self.finger_width: int = finger_width
        self.finger_pitch: int = finger_pitch
        self.width: int = width
        self.height: int = height
        self.vertical_bus_width: int = 30 * scale
        self.horizontal_bus_height: int = 50 * scale
        self.scale = scale

    def draw_base(self, etchmask=False):
        """Draws the base horizontal bus bar and vertical bussbar with parameters that are fixed in __init__"""

        if etchmask:
            offset_etchmask = 2.4 * self.scale
            self.top.shapes(self.layer_etch).insert(
                MyBox(
                    self.start_pos.offset(-offset_etchmask, -offset_etchmask),
                    self.width + 2 * offset_etchmask,
                    self.horizontal_bus_height + 2 * offset_etchmask,
                )
            )

            self.top.shapes(self.layer_etch).insert(
                MyBox(
                    self.start_pos.offset_x(
                        self.width / 2 - self.vertical_bus_width / 2
                    ).offset(-offset_etchmask, -offset_etchmask),
                    self.vertical_bus_width + 2 * offset_etchmask,
                    self.height + 2 * offset_etchmask,
                )
            )

        else:
            offset_etchmask = 0

            self.top.shapes(self.layer).insert(
                MyBox(
                    self.start_pos.offset(-offset_etchmask, -offset_etchmask),
                    self.width + 2 * offset_etchmask,
                    self.horizontal_bus_height + 2 * offset_etchmask,
                )
            )
            self.top.shapes(self.layer).insert(
                MyBox(
                    self.start_pos.offset_x(
                        self.width / 2 - self.vertical_bus_width / 2
                    ).offset(-offset_etchmask, -offset_etchmask),
                    self.vertical_bus_width + 2 * offset_etchmask,
                    self.height + 2 * offset_etchmask,
                )
            )

    def draw_fingers(self, etchmask=False):
        """Calculates how many fingers fit on the LED, and draws them"""
        num_fingers = int(
            (self.height - self.horizontal_bus_height)
            / (self.finger_width + self.finger_pitch)
        )

        for i in range(num_fingers):
            if etchmask:
                offset_etchmask = 2.4 * self.scale
            else:
                offset_etchmask = 0
            finger_pos = self.start_pos.offset(
                -offset_etchmask,
                i * (self.finger_width + self.finger_pitch)
                + self.horizontal_bus_height
                + self.finger_pitch
                - offset_etchmask,
            )

            finger = Finger(
                finger_pos,
                self.width + 2 * offset_etchmask,
                self.finger_width + 2 * offset_etchmask,
            )
            if etchmask:
                finger.draw(self.top, self.layer_etch)
            else:
                finger.draw(self.top, self.layer)

    def draw(self):
        """Method that draws the entire LED hand"""
        self.draw_base()
        self.draw_fingers()
        # self.draw_enclosing_box()
        self.draw_Info()

    def draw_etch_mask(self):
        self.draw_base(etchmask=True)
        self.draw_fingers(etchmask=True)
        self.draw_Info(etchmask=True)

    def __str__(self):
        return f"Finger width: {self.finger_width/self.scale}\nFinger Pitch: {self.finger_pitch//self.scale}"

    def draw_Info(self, etchmask=False):
        if etchmask:
            self.top.shapes(self.layer_etch).insert(
                MyBox(
                    self.start_pos.offset(
                        -30 * self.scale - 0.2 * self.width,
                        int(self.height * 1.2 - 20 * self.scale),
                    ),
                    self.width * 1.65,
                    100 * self.scale,
                )
            )
            return
        else:

            gen = pya.TextGenerator.default_generator()

            region = gen.text(str(self), gen.dbu(), 75)
            pos = self.start_pos.offset(-self.width * 0.2, int(self.height * 1.2))
            t = pya.Trans(*pos)
            region.transform(t)
            self.top.shapes(self.layer).insert(region)

    def draw_enclosing_box(self):

        self.top.shapes(self.layer_box).insert(
            MyBox(
                self.start_pos.offset(
                    -self.enclosing_box_fraction / 2 * self.width,
                    -self.enclosing_box_fraction / 2 * self.height,
                ),
                self.width * (1 + self.enclosing_box_fraction),
                self.height * (1 + self.enclosing_box_fraction),
            )
        )

    def draw_box_for_HF_mask(self, indent=5):
        offset = indent * self.scale
        self.top.shapes(self.layer_etch).insert(
            MyBox(
                self.start_pos.offset(offset, offset),
                self.width - 2 * offset,
                self.horizontal_bus_height - 2 * offset,
            )
        )

    def draw_box_for_metalization_mask(self, lenght=800):

        self.top.shapes(self.layer_etch).insert(
            MyBox(
                self.start_pos.offset_y(
                    self.horizontal_bus_height - lenght * self.scale
                ),
                self.width,
                lenght * self.scale,
            )
        )


def draw_grid(layout, top):

    # top = layout.create_cell("TOP")
    layer = layout.layer(0, 0)
    layer_txt = layout.layer(1, 0)
    layer_box = layout.layer(2, 0)

    scale = 1000

    LED_widht = 1000 * scale  # microns
    LED_heigth = 1000 * scale  # microns

    LED_spacing_x = 1600 * scale  # microns
    LED_spacing_y = 1600 * scale  # microns

    finger_widths = np.array([4, 4.5, 5, 5.5]) * scale  # microns
    finger_pitches = np.array([50, 100, 150, 230]) * scale  # microns

    startpos = Point(0, 0)

    enclosing_box_fraction = 0.05

    for x in range(4):
        for y in range(4):

            hand_point = startpos.offset(
                x * (LED_widht + LED_spacing_x), y * (LED_heigth + LED_spacing_y)
            )

            finger_width = finger_widths[y]
            finger_pitch = finger_pitches[x]

            single_hand = Hand(
                top,
                layer,
                layer_box,
                enclosing_box_fraction,
                hand_point,
                finger_width,
                finger_pitch,
                LED_widht,
                LED_heigth,
                scale,
            )

            single_hand.draw()


def draw_single_led():
    layout = pya.Layout()

    top = layout.create_cell("TOP")
    layer = layout.layer(0, 0)
    layer_txt = layout.layer(1, 0)
    layer_box = layout.layer(2, 0)

    scale = 1000

    LED_widht = 1000 * scale  # microns
    LED_heigth = 1000 * scale  # microns

    LED_spacing_x = 5000 * scale  # microns
    LED_spacing_y = 5000 * scale  # microns

    hand_point = Point(0, 0)

    enclosing_box_fraction = 0.1

    finger_width = 4 * scale
    finger_pitch = 36 * scale

    single_hand = Hand(
        top,
        layer,
        layer_box,
        enclosing_box_fraction,
        hand_point,
        finger_width,
        finger_pitch,
        LED_widht,
        LED_heigth,
        scale,
    )

    single_hand.draw()

    layout.write(
        "/Users/anders/Documents/Skole/5.host/Lab/FordypningLab/Single_LED.gds"
    )


def draw_grid_etch_mask(layout, top):

    # top = layout.create_cell("TOP")
    layer_box = layout.layer(0, 0)
    layer_etch = layout.layer(1, 0)
    layer = layout.layer(2, 0)

    scale = 1000

    LED_widht = 1000 * scale  # microns
    LED_heigth = 1000 * scale  # microns

    LED_spacing_x = 1600 * scale  # microns
    LED_spacing_y = 1600 * scale  # microns

    finger_widths = np.array([4, 4.5, 5, 5.5]) * scale  # microns
    finger_pitches = np.array([50, 100, 150, 230]) * scale  # microns

    startpos = Point(0, 0)

    enclosing_box_fraction = 0.6

    for x in range(4):
        for y in range(4):

            hand_point = startpos.offset(
                x * (LED_widht + LED_spacing_x), y * (LED_heigth + LED_spacing_y)
            )

            finger_width = finger_widths[y]
            finger_pitch = finger_pitches[x]

            single_hand = Hand(
                top,
                layer,
                layer_box,
                enclosing_box_fraction,
                hand_point,
                finger_width,
                finger_pitch,
                LED_widht,
                LED_heigth,
                scale,
                layer_etch=layer_etch,
            )

            single_hand.draw_etch_mask()


def draw_mesa_etch(layout, top):

    # top = layout.create_cell("TOP")
    layer_box = layout.layer(2, 0)
    layer_etch = layout.layer(2, 0)
    layer = layout.layer(2, 0)

    scale = 1000

    LED_widht = 1000 * scale  # microns
    LED_heigth = 1000 * scale  # microns

    LED_spacing_x = 1600 * scale  # microns
    LED_spacing_y = 1600 * scale  # microns

    finger_widths = np.array([4, 4.5, 5, 5.5]) * scale  # microns
    finger_pitches = np.array([50, 100, 150, 230]) * scale  # microns

    startpos = Point(0, 0)

    enclosing_box_fraction = 0.012

    for x in range(4):
        for y in range(4):

            hand_point = startpos.offset(
                x * (LED_widht + LED_spacing_x), y * (LED_heigth + LED_spacing_y)
            )

            finger_width = finger_widths[y]
            finger_pitch = finger_pitches[x]

            single_hand = Hand(
                top,
                layer,
                layer_box,
                enclosing_box_fraction,
                hand_point,
                finger_width,
                finger_pitch,
                LED_widht,
                LED_heigth,
                scale,
                layer_etch=layer_etch,
            )

            single_hand.draw_enclosing_box()
            single_hand.draw_Info(etchmask=True)


def draw_hf_etch(layout, top):
    layer_box = layout.layer(2, 0)
    layer_etch = layout.layer(2, 0)
    layer = layout.layer(2, 0)

    scale = 1000

    LED_widht = 1000 * scale  # microns
    LED_heigth = 1000 * scale  # microns

    LED_spacing_x = 1600 * scale  # microns
    LED_spacing_y = 1600 * scale  # microns

    finger_widths = np.array([4, 4.5, 5, 5.5]) * scale  # microns
    finger_pitches = np.array([50, 100, 150, 230]) * scale  # microns

    startpos = Point(0, 0)

    enclosing_box_fraction = 0.012

    for x in range(4):
        for y in range(4):

            hand_point = startpos.offset(
                x * (LED_widht + LED_spacing_x), y * (LED_heigth + LED_spacing_y)
            )

            finger_width = finger_widths[y]
            finger_pitch = finger_pitches[x]

            single_hand = Hand(
                top,
                layer,
                layer_box,
                enclosing_box_fraction,
                hand_point,
                finger_width,
                finger_pitch,
                LED_widht,
                LED_heigth,
                scale,
                layer_etch=layer_etch,
            )

            single_hand.draw_box_for_HF_mask()


def draw_metallizaiton_mask(layout, top):
    layer_box = layout.layer(2, 0)
    layer_etch = layout.layer(2, 0)
    layer = layout.layer(2, 0)

    scale = 1000

    LED_widht = 1000 * scale  # microns
    LED_heigth = 1000 * scale  # microns

    LED_spacing_x = 1600 * scale  # microns
    LED_spacing_y = 1600 * scale  # microns

    finger_widths = np.array([4, 4.5, 5, 5.5]) * scale  # microns
    finger_pitches = np.array([50, 100, 150, 230]) * scale  # microns

    startpos = Point(0, 0)

    enclosing_box_fraction = 0.012

    for x in range(4):
        for y in range(4):

            hand_point = startpos.offset(
                x * (LED_widht + LED_spacing_x), y * (LED_heigth + LED_spacing_y)
            )

            finger_width = finger_widths[y]
            finger_pitch = finger_pitches[x]

            single_hand = Hand(
                top,
                layer,
                layer_box,
                enclosing_box_fraction,
                hand_point,
                finger_width,
                finger_pitch,
                LED_widht,
                LED_heigth,
                scale,
                layer_etch=layer_etch,
            )

            single_hand.draw_box_for_metalization_mask()


if __name__ == "__main__":

    layout = pya.Layout()
    top = layout.create_cell("TOP")
    draw_hf_etch(layout, top)
    draw_grid(layout, top)
    layout.write(
        "/Users/anders/Documents/Skole/5.host/Lab/FordypningLab/E2_2022_LED_Metalization.gds"
    )
