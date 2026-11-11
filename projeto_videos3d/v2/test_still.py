import bpy, sys, os, math, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))
import build as B
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
t0 = time.time()
B.setup_world(); B.build_street()
car = B.build_car('CarroTeo', (0.85, 0.12, 0.05))
car['root'].location = (-8, -1.75, 0)
kid = B.build_character('Menino', B.KID, B.new_coll('Menino'))
kid['root'].location = (0.0, -2.3, 0); kid['root'].rotation_euler = (0, 0, math.radians(-100))
B.pose(kid, **{'thigh.L': (-40, 0, 0), 'thigh.R': (30, 0, 0), 'shin.L': (40, 0, 0), 'shin.R': (60, 0, 0), 'upper_arm.L': (35, 0, 0), 'upper_arm.R': (-40, 0, 0), 'forearm.R': (-50, 0, 0)})
B.set_face(kid, {'alarm': 1.0})
print('build', round(time.time() - t0, 1), 's')
B.setup_render(int(sys.argv[-2]), int(sys.argv[-1]), 16)
sc = bpy.context.scene
cam = B.link(bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))); sc.camera = cam; cam.data.lens = 28
shots = {'a': ((-4, -7.5, 1.6), (-6.5, -1.6, 0.9)), 'b': ((-30, 9, 9), (-2, -2, 0)), 'c': ((2.5, -4.6, 0.9), (0, -2.3, 0.6))}
for k, (p, t) in shots.items():
    cam.location = p; d = Vector(t) - Vector(p); cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = f'/tmp/claude-0/still_{k}.png'; sc.render.use_overwrite = True
    t1 = time.time(); bpy.ops.render.render(write_still=True); print('render', k, round(time.time() - t1, 1), 's')
bpy.ops.wm.save_as_mainfile(filepath='/tmp/claude-0/test.blend')
