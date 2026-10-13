// Six-wheel teaching cryptex. Select a part below and press F6 / Render.
// The mechanism is a classroom prop, not secure storage or a real lock.
part = "assembly"; // "assembly", "sleeve", "wheel", "plug", "collar"
wheel_index = 0;   // 0 through 5 when part = "wheel"

$fn = 96;
wheel_count = 6;
wheel_height = 18;
wheel_pitch = 19;
wheel_outer_radius = 24.85; // alphabet strip circumference is ~156 mm
wheel_inner_radius = 8.5;
notch_width = 3.0;
notch_depth = 5.0;
target_index = [1, 0, 2, 10, 20, 15]; // BACKUP, with A=0
stack_height = (wheel_count - 1) * wheel_pitch + wheel_height;

sleeve_inner_radius = 25.55;
sleeve_wall = 2.0;
sleeve_outer_radius = sleeve_inner_radius + sleeve_wall;
window_width = 8.0;
plug_radius = 7.2;
lug_length = 5.8;
lug_width = 2.6;
lug_height = 2.8;

module wheel(index) {
    difference() {
        cylinder(r = wheel_outer_radius, h = wheel_height);
        translate([0, 0, -0.1])
            cylinder(r = wheel_inner_radius, h = wheel_height + 0.2);
        rotate([0, 0, target_index[index] * 360 / 26])
            translate([wheel_inner_radius - 0.2, -notch_width / 2, -0.1])
                cube([notch_depth, notch_width, wheel_height + 0.2]);
    }
}

module sleeve() {
    difference() {
        cylinder(r = sleeve_outer_radius, h = stack_height);
        translate([0, 0, -0.1])
            cylinder(r = sleeve_inner_radius, h = stack_height + 0.2);
        // One long viewing/assembly window, facing the +X direction.
        translate([sleeve_inner_radius - 0.1, -window_width / 2, -0.1])
            cube([sleeve_wall + 0.3, window_width, stack_height + 0.2]);
    }
}

module plug() {
    union() {
        // The axial shaft slides only when every wheel's radial notch is aligned.
        cylinder(r = plug_radius, h = stack_height);
        for (index = [0 : wheel_count - 1]) {
            translate([plug_radius, -lug_width / 2,
                       index * wheel_pitch + wheel_height / 2 - lug_height / 2])
                cube([lug_length, lug_width, lug_height]);
        }
        // A hand grip remains outside the sleeve and pulls the plug free.
        translate([0, 0, -5]) cylinder(r = 13, h = 5);
    }
}

module collar() {
    difference() {
        cylinder(r = sleeve_outer_radius, h = 2);
        translate([0, 0, -0.1]) cylinder(r = 13.2, h = 2.2);
    }
}

module assembled_view() {
    color("gainsboro") sleeve();
    for (index = [0 : wheel_count - 1]) {
        translate([0, 0, index * wheel_pitch]) color("burlywood") wheel(index);
    }
    color("steelblue") plug();
    // End collars are separate print parts; glue or tape them after assembly.
    translate([0, 0, stack_height]) color("dimgray") collar();
}

if (part == "assembly") assembled_view();
if (part == "sleeve") sleeve();
if (part == "wheel") wheel(wheel_index);
if (part == "plug") plug();
if (part == "collar") collar();
