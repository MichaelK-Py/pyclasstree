import sys
from inspect import isfunction, isclass
from tkinter import *
from math import asin, pi, log, ceil


RADIUS = 4


class CustomCanvas(Canvas):
    def create_circle(self, x, y, radius=2, **kwargs):
        x1, y1, x2, y2 = x - radius, y - radius, x + radius, y + radius
        circle_id = self.create_oval(x1, y1, x2, y2, **kwargs)
        return circle_id

    def find_all_tags(self, tag):
        tags = []
        for id_ in self.find_withtag(tag):
            for tg in self.gettags(id_):
                tags.append(tg)
        return tags

    def central_coord(self, tag_or_id):
        x1, y1, x2, y2 = self.bbox(tag_or_id)
        x = (x2 + x1) / 2
        y = (y2 + y1) / 2
        return x, y

    def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)


def vertical_graphic_dots(dots, dots_amount=1000):
    x1, y1, x2, y2 = dots
    if x1 == x2 or y1 == y2:    # if the graph is a straight line segment - return 2 points
        return dots

    # function parameters
    if (x1 < x2 and y1 < y2) or (x1 > x2 and y1 > y2):
        h = abs(y2 - y1) / pi    # length of function value range
    else:
        h = -(abs(y2 - y1) / pi)    # h < 0 if the graph of the function is decreasing

    w = round(2 / abs(x2 - x1), 5)    # function definition length

    x0 = abs(x1 - x2) / 2    # graph center by x
    y0 = abs(y1 - y2) / 2    # graph center by y

    offset_x = min(x1, x2)    # offset of function graph on canvas
    offset_y = min(y1, y2)

    new_dots_list = []
    interval = round((abs(x2 - x1) / dots_amount), 5)    # distance between each two points on the graph
    for i in range(2, dots_amount - 1):
        x = interval * i
        try:
            y = h * asin(w * (x - x0)) + y0
        except ValueError:
            continue
        else:
            new_dots_list.extend((x + offset_x, y + offset_y))

    if (x1 < x2 and y1 > y2) or (x1 > x2 and y1 < y2):
        new_dots_list = [min(x1, x2), max(y1, y2)] + new_dots_list + [max(x1, x2), min(y1, y2)]
    elif (x1 > x2 and y1 > y2) or (x1 < x2 and y1 < y2):
        new_dots_list = [min(x1, x2), min(y1, y2)] + new_dots_list + [max(x1, x2), max(y1, y2)]
    return new_dots_list


def horizontal_graphic_dots(dots, dots_amount=1000):
    x1, y1, x2, y2 = dots
    if x1 == x2 or y1 == y2:    # if the graph is a straight line segment - return 2 points
        return dots

    # function parameters
    if (x1 < x2 and y1 < y2) or (x1 > x2 and y1 > y2):
        h = (abs(x2 - x1) / pi)    # length of function value range
    else:
        h = -abs(x2 - x1) / pi    # h < 0 if the graph of the function is decreasing

    w = round(2 / abs(y2 - y1), 5)    # function definition length

    x0 = abs(x1 - x2) / 2    # graph center at x
    y0 = abs(y1 - y2) / 2    # graph center by y

    offset_x = min(x1, x2)    # offset of function graph on canvas
    offset_y = min(y1, y2)

    new_dots_list = []
    interval = round((abs(y2 - y1) / dots_amount), 5)    # distance between each two points on the graph
    for i in range(2, dots_amount - 1):
        y = interval * i
        try:
            x = h * asin(w * (y - y0)) + x0
        except ValueError:
            continue
        else:
            new_dots_list.extend((x + offset_x, y + offset_y))

    if (x1 < x2 and y1 > y2) or (x1 > x2 and y1 < y2):
        new_dots_list = [max(x1, x2), min(y1, y2)] + new_dots_list + [min(x1, x2), max(y1, y2)]
    elif (x1 > x2 and y1 > y2) or (x1 < x2 and y1 < y2):
        new_dots_list = [min(x1, x2), min(y1, y2)] + new_dots_list + [max(x1, x2), max(y1, y2)]
    return new_dots_list


class Node:
    """The node instance stores all its sockets and all associated lines."""
    node_num = 0
    selected = False

    all_connections = set()    # all canvas lines: {(tag_1, tag_2), (tag_2, tag_1)}
    all_nodes = {}    # {node_tag: node_instance}
    def __init__(self, canvas, x, y, tag, node_info, window):
        Node.node_num += 1
        self.canvas = canvas
        self.window = window
        self.info = node_info

        self.dct = self.info['dct']
        self.module = self.info['module']
        self.row = self.info['row']
        self.column = self.info['column']
        self.superclasses = self.info['superclasses']
        self.subclasses = self.info['subclasses']
        self.metaclass = self.info['metaclass']
        if self.info['ismetaclass'] or tag == 'type':
            self.color = '#CD5C5C'
        elif self.module == __name__:
            self.color = 'green'
        elif tag == 'object':
            self.color = '#483D8B'
        else:
            self.color = '#BDB76B'

        self.tag = tag
        self.top_socket_tag = None
        self.bottom_socket_tag = None
        self.x = x
        self.y = y
        self.offset_x = None
        self.offset_y = None

        self.sockets = {}    # {socket_tag: (x, y)}
        self.lines = {}    # {line_tag: line_instance}

        self.canvas.round_rectangle(self.x, self.y, self.x + 200, self.y + 50,
                             fill=self.color, outline='#585858', tags=(self.tag, 'node'))
        self.canvas.tag_bind(self.tag, "<ButtonPress-1>", self.select_node)
        self.canvas.tag_bind(self.tag, "<B1-Motion>", self.move_node)
        self.canvas.tag_bind(self.tag, "<ButtonRelease-1>", self.unselect_node)

        self.canvas.create_text(self.x + 100, self.y + 25, text=self.tag,
                                anchor=CENTER, tags=(self.tag, 'text'))
        self.create_sockets()
        Node.all_nodes[self.tag] = self

    def create_sockets(self):
        dots_list = self.count_socket_coord()
        top_socket = True
        for x, y in dots_list:
            if top_socket:
                socket_tag = f'top:{self.tag}'
                self.top_socket_tag = socket_tag
            else:
                socket_tag = f'bottom:{self.tag}'
                self.bottom_socket_tag = socket_tag
            top_socket = not top_socket
            self.canvas.create_circle(x, y, radius=RADIUS, fill='orange', activefill='green',
                                      tags=(socket_tag, 'socket', self.tag))
            self.sockets[socket_tag] = (x, y)

    def count_socket_coord(self):
        coord_list = [
            (self.x + 100,
             self.y),
            (self.x + 100,
             self.y + 50)]
        return coord_list

    def update_sockets(self):
        for tag in self.sockets.keys():
            new_x, new_y = self.canvas.central_coord(tag)
            self.sockets[tag] = (new_x, new_y)
            self.canvas.tkraise(tag)

    def select_node(self, event):
        Node.selected = True
        # memorize the cursor coordinates at the moment of the first click on the node
        self.offset_x = event.widget.canvasx(event.x)
        self.offset_y = event.widget.canvasy(event.y)
        for line_tag in self.lines.keys():
            self.canvas.itemconfigure(line_tag, fill='#66CDAA', width=1)

    def unselect_node(self, event):
        Node.selected = False
        self.offset_x = None
        self.offset_y = None
        self.update_sockets()
        self.update_lines()
        for line_tag in self.lines.keys():
            self.canvas.itemconfigure(line_tag, fill='black', width=2)

    def move_node(self, event):
        dx = event.widget.canvasx(event.x) - self.offset_x
        dy = event.widget.canvasy(event.y) - self.offset_y
        self.x += dx
        self.y += dy
        self.offset_x += dx  # warning! will work uncorrectly if the offset not added
        self.offset_y += dy
        self.canvas.move(self.tag, dx, dy)
        self.canvas.tkraise(self.tag)
        self.update_lines()
        self.update_sockets()

    def create_all_connections(self):
        if self.subclasses:
            for tag in self.subclasses:
                other_node = Node.all_nodes[tag]
                self.create_connection_line(other_node, superclass=True)
        if self.superclasses:
            for tag in self.superclasses:
                other_node = Node.all_nodes[tag]
                self.create_connection_line(other_node, superclass=False)
        if self.metaclass:
            other_node = Node.all_nodes[self.metaclass[0]]
            self.create_connection_line(other_node, superclass=False)

    def create_connection_line(self, other_node, superclass=True):
        if superclass:
            socket_tag_1 = self.bottom_socket_tag
            socket_tag_2 = other_node.top_socket_tag
        else:
            socket_tag_1 = self.top_socket_tag
            socket_tag_2 = other_node.bottom_socket_tag

        if ((socket_tag_1, socket_tag_2) in Node.all_connections or
                (socket_tag_2, socket_tag_1) in Node.all_connections):
            return
        else:
            Node.all_connections.add((socket_tag_1, socket_tag_2))
            Node.all_connections.add((socket_tag_2, socket_tag_1))

        x1, y1 = self.canvas.central_coord(socket_tag_1)
        x2, y2 = self.canvas.central_coord(socket_tag_2)
        line = Line(self.canvas, [x1, y1, x2, y2], window=self.window)
        line.socket_tag_1 = socket_tag_1
        line.socket_tag_2 = socket_tag_2
        line.update()
        self.lines[line.tag] = line
        other_node.lines[line.tag] = line

    def update_lines(self):
        for line in self.lines.values():
            line.update()


class Line:
    line_num = 0
    all_lines = {}    # {line_tag: line_instance}
    def __init__(self, canvas, two_dots, window=None):
        self.canvas = canvas
        self.window = window
        Line.line_num += 1

        self.tag = f'line{Line.line_num}'
        self.socket_tag_1 = None
        self.socket_tag_2 = None
        self.dots = None
        self.create_or_move_line(two_dots)
        Line.all_lines[self.tag] = self

    def create_or_move_line(self, dots, create=True):
        self.dots = dots
        all_dots = vertical_graphic_dots(dots, dots_amount=self.window.line_dots_amount)
        if create:
            self.canvas.create_line(all_dots, smooth=True, width=2, fill='black',
                                    splinesteps=50,
                                    tags=(self.tag, ))
        else:
            self.canvas.coords(self.tag, all_dots)
        self.canvas.tag_lower(self.tag)

    def update(self, new_dots=None):
        if new_dots:
            self.create_or_move_line(new_dots, create=False)
        else:
            if self.socket_tag_1 and self.socket_tag_2:
                x1, y1 = self.canvas.central_coord(self.socket_tag_1)
                x2, y2 = self.canvas.central_coord(self.socket_tag_2)
                self.create_or_move_line([x1, y1, x2, y2], create=False)


class MainWindow(Frame):
    def __init__(self, tree, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.root = parent

        self.tree_dict = tree
        self.rows = 0
        self.columns = 0
        self.line_dots_amount = 500
        self.canvas_w = self.root.winfo_screenwidth()
        self.canvas_h = self.root.winfo_screenheight()
        self.zoom = 0
        self.xscroll = self.canvas_w
        self.yscroll = self.canvas_h
        self.count_parameters()

        # create a canvas with scroll bars
        ################################################################################
        self.canvas = CustomCanvas(self, bg='#595959', width=700, height=500)
        self.canvas.config(scrollregion=(-self.canvas_w * 0.5,
                                         -self.canvas_h * 0.5,
                                         self.canvas_w * 1.5,
                                         self.canvas_h * 1.5))
        self.canvas.config(highlightthickness=0)

        self.scroll_x = Scrollbar(self, orient=HORIZONTAL, command=self.canvas.xview)
        self.scroll_y = Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)

        self.canvas.config(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        self.scroll_x.pack(side=BOTTOM, fill=X)
        self.scroll_y.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, expand=YES, fill=BOTH)
        ################################################################################
        self.canvas.addtag_all(ALL)

        # canvas event handlers
        self.canvas.bind("<ButtonPress-1>", self.move_start)
        self.canvas.bind("<B1-Motion>", self.move_canvas)
        if sys.platform[:3] == 'win':
            self.canvas.bind("<MouseWheel>", self.canvas_zoomer)
        else:
            self.canvas.bind("<Button-4>", self.canvas_zoomer)
            self.canvas.bind("<Button-5>", self.canvas_zoomer)

        # graph drawing
        self.create_nodes()
        self.create_all_lines()

    def count_parameters(self):
        self.rows = max(dct['row'] for dct in self.tree_dict.values())
        lines_amount = 0
        row_columns = {num: 1 for num in range(1, self.rows + 1)}
        for dct in self.tree_dict.values():
            row = dct['row']
            row_columns[row] += 1
            lines_amount += (len(dct['superclasses']) + len(dct['subclasses']))
        self.columns = max(col for col in row_columns.values())

        if (self.rows * 150) + 300 > self.canvas_h:
            self.canvas_h *= ceil((self.rows * 150 + 300) / self.canvas_h)
            self.xscroll = self.canvas_h
        if (self.columns * 300) + 600 > self.canvas_w:
            self.canvas_w *= ceil((self.columns * 300 + 600) / self.canvas_w)
            self.yscroll = self.canvas_w

        if 10 < lines_amount <= 150:
            self.line_dots_amount = round(log((lines_amount - 10), 0.96) + 130)
        elif lines_amount > 150:
            self.line_dots_amount = 8

    def create_nodes(self):
        row_columns = {num: 1 for num in range(1, self.rows + 1)}
        for name, dct in self.tree_dict.items():
            row = dct['row']
            column = row_columns[row]
            dct['column'] = column
            row_columns[row] += 1

            x = column * 300 - 250
            y = row * 150 - 100
            Node(self.canvas, x, y, tag=name, node_info=dct, window=self)

    @staticmethod
    def create_all_lines():
        for node in Node.all_nodes.values():
            node.create_all_connections()

    def canvas_zoomer(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if event.num == 4 or event.delta > 0:
            if self.zoom + 1 >= 20:
                return
            self.zoom += 1
            self.xscroll *= (11 / 10)
            self.yscroll *= (11 / 10)
            self.canvas.scale("all", x, y, (11 / 10), (11 / 10))
        elif event.num == 5 or event.delta < 0:
            if self.zoom - 1 <= -40:
                return
            self.zoom -= 1
            self.xscroll *= (10 / 11)
            self.yscroll *= (10 / 11)
            self.canvas.scale("all", x, y, (10 / 11), (10 / 11))
        self.canvas.config(scrollregion=(-self.xscroll * 0.5,
                                         -self.yscroll * 0.5,
                                         self.xscroll * 1.5,
                                         self.yscroll * 1.5))
        if self.zoom < -23:
            self.canvas.itemconfig('text', state=HIDDEN)
        else:
            self.canvas.itemconfig('text', state=NORMAL)

    def move_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def move_canvas(self, event):
        if Node.selected:
            return
        self.canvas.scan_dragto(event.x, event.y, gain=1)


################################################################################
# LOGIC OF PROCESSING AND BUILDING A CLASS TREE:
################################################################################
def all_paths(cls_obj):
    paths = []
    def path_dfs(cls, path=tuple()):
        if len(path) == 0:
            path += (cls,)
        if len(cls.__bases__) == 1 and cls.__bases__[0].__name__ == 'object':
            path += cls.__bases__
            paths.append(path)
            return
        else:
            for sup in cls.__bases__:
                path_dfs(sup, path=(path + (sup,)))
    path_dfs(cls_obj)
    return paths


tree_dict = {}
def inspect_class_tree(cls_list):
    add_type_dtc = False
    for cls in cls_list:
        tree_dict[cls.__name__] = dict()
        tree_dict[cls.__name__]['module'] = cls.__module__
        tree_dict[cls.__name__]['dct'] = [attr.__name__ for attr in cls.__dict__.values() if isfunction(attr)]
        tree_dict[cls.__name__]['row'] = max(len(path) for path in all_paths(cls))

        if type in cls.__mro__:
            tree_dict[cls.__name__]['superclasses'] = [sup.__name__ for sup in cls.__mro__[1:]]
            tree_dict[cls.__name__]['ismetaclass'] = True
            tree_dict[cls.__name__]['row'] = 3    # Place below than object and type
            add_type_dtc = True
        else:
            tree_dict[cls.__name__]['superclasses'] = [sup.__name__ for sup in cls.__bases__]
            tree_dict[cls.__name__]['ismetaclass'] = False

        if type in cls.__class__.__mro__ and object in cls.__bases__ and cls.__class__ not in (object, type):
            tree_dict[cls.__name__]['metaclass'] = [cls.__class__.__name__]
            tree_dict[cls.__name__]['row'] = 4    # Place below than object, type, and metaclass
        else:
            tree_dict[cls.__name__]['metaclass'] = []

        tree_dict[cls.__name__]['subclasses'] = []
        if type not in cls.__mro__:
            if cls.__subclasses__():
                tree_dict[cls.__name__]['subclasses'] = [sub.__name__ for sub in cls.__subclasses__()]

    if add_type_dtc:
        tree_dict['type'] = dict()
        tree_dict['type']['module'] = type.__module__
        tree_dict['type']['dct'] = [attr.__name__ for attr in type.__dict__.values() if isfunction(attr)]
        tree_dict['type']['row'] = 2
        tree_dict['type']['superclasses'] = ['object']
        tree_dict['type']['subclasses'] = []
        tree_dict['type']['ismetaclass'] = False
        tree_dict['type']['metaclass'] = []

    tree_dict['object'] = dict()
    tree_dict['object']['module'] = object.__module__
    tree_dict['object']['dct'] = [attr.__name__ for attr in object.__dict__.values() if isfunction(attr)]
    tree_dict['object']['row'] = 1
    tree_dict['object']['superclasses'] = []
    tree_dict['object']['subclasses'] = []
    tree_dict['object']['ismetaclass'] = False
    tree_dict['object']['metaclass'] = []


classes = []
def find_all_classes(cls):
    if cls is object or cls is type:
        return
    if type in cls.__class__.__mro__:
        if cls.__class__ not in classes and cls.__class__ is not type:
            classes.append(cls.__class__)
    if cls not in classes:
        classes.append(cls)
    for sup in cls.__bases__:
        if sup not in classes:
            find_all_classes(sup)
    for sub in cls.__subclasses__():
        if sub not in classes:
            find_all_classes(sub)


def check_obj(obj):
    if hasattr(obj, '__bases__') and hasattr(obj, '__subclass__') or isclass(obj):
        return obj
    elif hasattr(obj, '__class__'):
        return obj.__class__
    else:
        raise TypeError('argument must be a class or an instance of class')

# main function
def drawtree(obj):
    cls = check_obj(obj)
    find_all_classes(cls)
    inspect_class_tree(classes)

    root = Tk()
    MainWindow(tree=tree_dict, parent=root)
    root.mainloop()


if __name__ == '__main__':
    drawtree(Frame)
