#!/usr/bin/env python
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gimpfu import *
import gtk
from gobject import timeout_add


def show_ui(image, layer, min_range, max_range, *args):
    e = ElevationWindow(image, min_range, max_range)
    gtk.main()


class ElevationWindow(gtk.Window):
    def __init__(self, img, min_range, max_range, *args):
        self.img = img

        self.color = (0, 0, 0)
        self.foreground_elevation = 0.0
        self.background_elevation = 0.0
        self.min_value = min_range
        self.max_value = max_range

        self.old_foreground_elevation = 0.0
        self.old_background_elevation = 0.0

        win = gtk.Window.__init__(self, *args)
        self.set_default_size(200, -1)

        self.connect("destroy", gtk.main_quit)

        # Gui elements
        self.set_border_width(10)

        vbox = gtk.VBox(spacing=10, homogeneous=False)
        self.add(vbox)
        label = gtk.Label("Elevation to Color")
        vbox.add(label)
        label.show()

        table = gtk.Table(rows=6, columns=2, homogeneous=False)
        table.set_col_spacings(10)
        vbox.add(table)


        # Foreground elevation field
        label = gtk.Label("Elevation foreground color")
        label.set_alignment(xalign=0.0, yalign=1.0)
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0)
        label.show()
        
        felev = gtk.Adjustment(self.foreground_elevation, self.min_value, self.max_value, 0.01)
        felev.connect("value_changed", self.foreground_value_changed)

        fsbutton = gtk.SpinButton(felev)
        fsbutton.set_digits(2)
        table.attach(fsbutton, 1, 2, 0, 1)
        fsbutton.show()

        self.fscale = gtk.HScale(felev)
        self.fscale.set_digits(2)
        table.attach(self.fscale, 0, 2, 1, 2)
        self.fscale.show()

        # Background elevation field
        label = gtk.Label("Elevation background color")
        label.set_alignment(xalign=0.0, yalign=1.0)
        table.attach(label, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0)
        label.show()
        
        belev = gtk.Adjustment(self.background_elevation, self.min_value, self.max_value, 0.01)
        belev.connect("value_changed", self.background_value_changed)
        self.bscale = gtk.HScale(belev)
        self.bscale.set_digits(2)
        table.attach(self.bscale, 0, 2, 3, 4)
        self.bscale.show()
        table.show()

        vbox.show()
        self.show()

        self.update()

        return win

    def foreground_value_changed(self, val):
        pdb.gimp_context_set_foreground((1.0, 0.0, 1.0))
        
        color_value = (val.value - self.min_value)/ (self.max_value - self.min_value)
        self.foreground_elevation = val.value
        pdb.gimp_context_set_foreground((color_value, color_value, color_value))
        pdb.gimp_displays_flush()

    def background_value_changed(self, val):
        color_value = (val.value - self.min_value)/ (self.max_value - self.min_value)
        self.background_elevation = val.value
        pdb.gimp_context_set_background((color_value, color_value, color_value))
        pdb.gimp_displays_flush()

    def update(self, *args):
        foreground = pdb.gimp_context_get_foreground()
        foreground_elevation = foreground.r * (self.max_value - self.min_value) + self.min_value

        if foreground_elevation != self.old_foreground_elevation:
            self.old_foreground_elevation = foreground_elevation
            self.fscale.set_value(foreground_elevation)
        
        background = pdb.gimp_context_get_background()
        background_elevation = background.r * (self.max_value - self.min_value) + self.min_value

        if background_elevation != self.old_background_elevation:
            self.old_background_elevation = background_elevation
            self.bscale.set_value(background_elevation)

        timeout_add(1000, self.update, self)

        pdb.gimp_displays_flush()


register(
    "raster_elevation",
    "Get color representing elevation",
    "Get color representing elevation",
    "Bastiaan Roos",
    "Bastiaan Roos",
    "2017",
    "<Image>/Tekenen en rekenen/Raster Elevation",
    "",      # Alternately use RGB, RGB*, GRAY*, INDEXED etc.
    [(PF_FLOAT, "min_range", "Range min", -6.0),
     (PF_FLOAT, "max_range", "Range max", 6.0)],
    [],
    show_ui) #, menu="<Image>/Filters/Languages/Python-Fu"

main()
