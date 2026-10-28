# Josh artwork optimized for a 0.4 mm nozzle

Open **Josh-35mm-04Nozzle-Optimized.3mf** as a project in Bambu Studio. It retains four aligned components and three logical filament colors:
- Backing: white, filament 1; separately selectable and recolorable.
- White_Artwork: white, filament 1.
- Black_Artwork: black, filament 2.
- Red_Artwork: red, filament 3.

## What changed

The actual previous 3MF was measured, not merely its preview. Many white outlines were about 0.15–0.2 mm wide; 20 of 33 white regions had no location reaching the nominal 0.42 mm extrusion width. The previous profile used Classic walls, with thin-wall detection disabled.

This revision:
1. Widens whole deficient color components consistently, with offsets capped at 0.17 mm. This avoids lumpy edges from indiscriminate local dilation.
2. Enlarges small black letter counters rather than simply filling them.
3. Smooths sub-nozzle bumps and acute nicks, with 0.035/0.025 mm contour offsets and 0.008 mm contour simplification.
4. Absorbs unprintable color specks smaller than 0.04 mm2 and narrow detached black fragments into adjacent fill. Details and color boundaries are deliberately adjusted for this print-aware version; the original 3MF and SVG are unchanged.
5. Resolves all colors into a common front-layer partition so the parts do not duplicate solid volume.
6. Uses Arachne variable-width walls, retaining the 0.4 mm nozzle, 0.2 mm layer height and nominal 0.42 mm line width. Existing Arachne minimum-bead setting is 85% (0.34 mm).
7. Fixes an existing project-settings defect: three filaments had a 4x4 purge matrix. The corrected 3x3 values were calculated by actual Bambu Studio for white/black/red: [0,186,353; 663,0,499; 679,194,0]. The companion purge vector has six entries. This prototype is scoped to this exact palette; other palettes need recalculation.

## What did NOT change

- Backing mesh vertex/triangle data is EXACTLY unchanged; digest recorded in verification.json.
- Backing STL is copied byte-for-byte from the separate-backing version.
- Body remains 14 mm thick, with plain white front/back supporting the artwork.
- Artwork remains above the body at Z14–16 mm (2 mm high).
- Overall silhouette remains 35 mm wide with proportional height approximately 25.78094 mm.
- Straw passage remains nominally 10 mm, with zero added diameter clearance; its position and nominal 2 mm front/rear body walls are unchanged.
- Four separate components and their filament assignments are retained.
- No website, interface, other generator, original artwork or previous prototype was modified.

## Validation and measured improvement

Official Bambu Studio **02.08.02.61**:
- Real GUI opened the delivery file with its three intended colors, separate backing and modified process profile, without the invalid-config warning.
- Actual slicing completed successfully (return_code 0), with all three filaments used. This was not just an import/export check.
- Actual sliced native 3MF retained the four part names, filament assignments and Arachne setting.
- Generated top-layer extrusion paths narrower than 0.34 mm decreased from 104.92 mm to 23.02 mm: approximately **78% less hair-thin path length**. Their fraction of measured top-layer extrusion length fell from about 8.7% to 1.6%. This comparison combines geometry and wall-generator improvements; it does not isolate their individual effects.
- Geometry checks verify closed, consistently oriented artwork solids, no pairwise duplicated volume beyond floating-point tolerance, unchanged backing data, and complete front-layer coverage.

artwork-comparison.png shows the measured before/after planar artwork, not an AI rendering. The audit toolpath image is an approximate rasterization of the final-layer G-code, with gray indicating uncovered area in that layer; it is NOT a photograph or a prediction of final surface appearance.

## Limits and print test

At 35 mm wide, not every tapered tip or microscopic color detail can be made robust with a 0.4 mm nozzle. Some sub-0.34 mm paths remain. This is an optimized test version, not a guaranteed exact reproduction of every source detail. Use larger artwork or a smaller nozzle if every fine border must be reproduced.

Physical printing, color bleed/flush calibration, PLA strength, channel overhangs, irregular entrance/exit walls, actual straw fit, and cleaning remain to be tested. Exact-size holes can fit tight; do not force onto the straw. Review your printer/filament settings and map logical colors to AMS slots. The package contains an UNSLICED editable 3MF; no ready-to-print G-code is supplied.

Individual STLs in geometry/ remain aligned. Import all four together as one multipart object; do not drop the artwork separately to the build plate. STLs carry no reliable filament colors.

## Reproduction

Python modules: numpy, scipy, shapely, scikit-image, manifold3d, trimesh, pillow, matplotlib.

Supply the previous separate-backing 3MF under input/Josh-35mm-Separate-Backing.3mf and optionally its unchanged Backing.stl under input/. The original source artwork is not redistributed here. The source 3MF is available in the preceding separate-backing delivery on the same GitHub prototype branch. JOSH_SOURCE_3MF can override its path.

Run, in order: analyze_artwork.py, optimize_vector.py, build_optimized.py. Then use the real Bambu executable to slice the result with its P1S 0.4 mm settings and Arachne profile. verify_optimized.py documents the native-slicer evidence paths used during this run; adjust those audit paths for a new run. No renderer preview can replace an actual slicing check.

The source algorithms and measured thresholds are scoped to this Josh prototype; they are not yet a universal artwork-cleaning engine. Official printer/process profile data inherits upstream Bambu Studio licensing and provenance described in the preceding export correction: https://github.com/bambulab/BambuStudio/tree/v02.08.02.61 . No Bambu executable or network plug-in is distributed.
