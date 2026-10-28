JOSH STRAW TOPPER — FIRST UNPRINTED PROTOTYPE

Original SVG is unchanged. This package contains experimental geometry, not a fit-certified or food-contact-certified product.

Dimensions in millimeters:
- Original visible black silhouette scaled to 63.5 mm wide.
- White body 16 mm thick; red/white artwork raised 0.8 mm above black; overall thickness 16.8 mm.
- Circular trial passage 10.2 mm diameter, runs along Y from bottom to top inside body.
- Passage center 35 mm from left silhouette edge; 8 mm above flat rear face.
- Nominal front/rear wall at passage center: 2.9 mm before raised artwork.
- No separate rear sleeve. Plain white rear face at Z=0.

Files:
- Josh-RAISED-0.8mm-PROTOTYPE.3mf: generic standards-based multipart assembly with material labels.
- white.stl, black.stl, red.stl: aligned millimeter meshes as fallback.
- validation.json: geometric checks; not a slicer or physical-print certification.
- build_prototype.py: reproducible prototype generation script.

Artwork processing:
Exterior background path excluded; first enclosing black path used as silhouette. Original painter order resolves visible colors before extrusion. Curves sampled at <=0.7 SVG units (about 0.032 mm); polygon simplification tolerance 0.003 mm. Microscopic polygons under 0.0001 mm2 omitted. Filament red/black/white assigned by original SVG regions. No deliberate thickening of fine lettering or claw tips. Very fine features may disappear in slicing.

BAMBU STUDIO REVIEW REQUIRED:
Open 3MF, choose P1S / 0.4 mm nozzle and your PLA profiles. This is a generic 3MF, not a saved Bambu print project; automatic material assignment is unverified. Confirm three aligned parts and explicitly assign white, black and red AMS slots. If generic 3MF import loses grouping, import all three STL files together as ONE object with multiple parts; preserve relative coordinates. Do not auto-arrange individual color parts.

Rear is flat on build plate in provided orientation. The circular horizontal tunnel has overhangs; inspect supports, bridging and passage obstruction. Do not print supports trapped inside the bore without a removal plan. A different orientation or later tunnel-design revision may be required. Inspect every layer near small letters, borders, claws and entry/exit openings. Check that the hole stays inside the silhouette between intended openings. This has NOT been verified in Bambu Studio here. No G-code is supplied.

Fit test on actual 10 mm plastic straw without force. 10.2 mm is nominal, not a guaranteed fit; printer tolerances can shrink openings. Stop if force is required. Inspect for cracks, sharp points, slipping, spinning, lid interference and mouth clearance. PLA can deform with heat; avoid dishwasher/hot-car exposure. Evaluate cleaning and use conditions separately.

REVISION: Black regions inset from Z=15.6 to 16.0 mm; red and white visible artwork at Z=16.0 to 16.8 mm. Black remains level with body top; rear remains white. Generic 3MF material colors still require Bambu Studio filament mapping; this is NOT a verified Bambu project.
