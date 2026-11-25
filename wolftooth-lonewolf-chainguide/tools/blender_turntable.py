"""
Blender turntable render for the LoneWolf head STL.

Usage (from a terminal):
  blender -b -P tools/blender_turntable.py -- models/lonewolf_head_ext0mm.stl renders/lonewolf_turntable_blender.mp4
Optional extra args:  --cycles   (slower, nicer)   --seconds 6   --res 1080

Works with Blender 3.6 - 5.x. Run without -b to open the set-up scene instead.
"""
import sys, math, os
import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
stl = os.path.abspath(argv[0] if argv else "models/lonewolf_head_ext0mm.stl")
out = os.path.abspath(argv[1] if len(argv) > 1 and not argv[1].startswith("--") else "renders/lonewolf_turntable_blender.mp4")
use_cycles = "--cycles" in argv
seconds = float(argv[argv.index("--seconds") + 1]) if "--seconds" in argv else 6.0
res = int(argv[argv.index("--res") + 1]) if "--res" in argv else 1080
fps = 30

# ---- clean scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---- import STL (operator name changed in 4.1+)
if hasattr(bpy.ops.wm, "stl_import"):
    bpy.ops.wm.stl_import(filepath=stl)
else:
    bpy.ops.import_mesh.stl(filepath=stl)
obj = bpy.context.selected_objects[0]
obj.name = "LoneWolfHead"

# model is in mm with Y = hole axis, Z up; scale to metres-ish scene units and centre
obj.scale = (0.01, 0.01, 0.01)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
obj.location = (0, 0, 0)
bpy.ops.object.shade_smooth()
# keep chamfers/edges crisp while smoothing curved faces
if hasattr(obj.data, "use_auto_smooth"):                     # Blender < 4.1
    obj.data.use_auto_smooth = True
    obj.data.auto_smooth_angle = math.radians(35)
else:                                                         # Blender 4.1+
    try:
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    except Exception:
        pass

# ---- material: slightly glossy black nylon
mat = bpy.data.materials.new("BlackNylon"); mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.025, 0.025, 0.03, 1)
bsdf.inputs["Roughness"].default_value = 0.45
for name in ("Specular IOR Level", "Specular"):
    if name in bsdf.inputs:
        bsdf.inputs[name].default_value = 0.5
        break
obj.data.materials.append(mat)

# ---- turntable: parent to an empty that spins
pivot = bpy.data.objects.new("Pivot", None); scene.collection.objects.link(pivot)
# constant-speed spin: new keys are linear (works on all versions, incl. 5.x layered actions)
bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
obj.parent = pivot
frames = int(seconds * fps)
scene.frame_start, scene.frame_end = 1, frames
pivot.rotation_euler = (0, 0, 0); pivot.keyframe_insert("rotation_euler", frame=1)
pivot.rotation_euler = (0, 0, math.radians(360)); pivot.keyframe_insert("rotation_euler", frame=frames + 1)
# ---- floor (shadow catcher look) and lights
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -obj.dimensions.z / 2 - 0.002))
floor = bpy.context.active_object
fm = bpy.data.materials.new("Floor"); fm.use_nodes = True
fm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.8, 0.82, 1)
fm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8
floor.data.materials.append(fm)

def area(name, loc, energy, size):
    light = bpy.data.lights.new(name, "AREA"); light.energy = energy; light.size = size
    o = bpy.data.objects.new(name, light); scene.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
area("Key", (-0.5, -0.6, 0.7), 60, 0.6)
area("Fill", (0.7, -0.3, 0.3), 20, 0.8)
area("Rim", (0.2, 0.8, 0.6), 45, 0.5)
world = bpy.data.worlds.new("World"); scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.92, 0.92, 0.94, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6

# ---- camera
cam_data = bpy.data.cameras.new("Cam"); cam_data.lens = 85
cam = bpy.data.objects.new("Cam", cam_data); scene.collection.objects.link(cam)
cam.location = (0, -1.25, 0.45)
cam.rotation_euler = (Vector((0, 0, 0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = cam

# ---- render settings
if use_cycles:
    scene.render.engine = "CYCLES"; scene.cycles.samples = 96
    try: scene.cycles.use_denoising = True
    except Exception: pass
else:
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = eng; break
        except TypeError:
            continue
scene.render.resolution_x = scene.render.resolution_y = res
scene.render.fps = fps
# Video output. Blender 5.0+ needs media_type = "VIDEO" before FFMPEG is allowed.
video_ok = False
try:
    ims = scene.render.image_settings
    if hasattr(ims, "media_type"):
        ims.media_type = "VIDEO"
    ims.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.filepath = out
    video_ok = True
except (TypeError, AttributeError) as ex:
    # fall back to a PNG sequence, then stitch it with ffmpeg if available
    print("Video output not available here (", ex, ") - rendering PNG frames instead")
    frames_dir = os.path.splitext(out)[0] + "_frames"
    os.makedirs(frames_dir, exist_ok=True)
    if hasattr(scene.render.image_settings, "media_type"):
        scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = os.path.join(frames_dir, "f_")

if bpy.app.background:
    bpy.ops.render.render(animation=True)
    if video_ok:
        print("Wrote", out)
    else:
        import shutil, subprocess
        if shutil.which("ffmpeg"):
            subprocess.run(["ffmpeg", "-y", "-framerate", str(fps), "-i",
                            os.path.join(frames_dir, "f_%04d.png"), "-c:v", "libx264",
                            "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out], check=True)
            print("Wrote", out)
        else:
            print("Frames are in", frames_dir, "- install ffmpeg or use Blender's Video Editor to make the MP4")
