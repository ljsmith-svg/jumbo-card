# Josh topper: separate backing and decorative artwork

Open **Josh-35mm-Separate-Backing.3mf** as a project in Bambu Studio. Expand the model under Objects to select its FOUR separate aligned components:

| Part | Z range | Thickness | Filament assignment |
|---|---|---|---|
| Backing | 0 to 14 mm | 14 mm | 1 — White |
| White_Artwork | 14 to 16 mm | 2 mm | 1 — White |
| Black_Artwork | 14 to 16 mm | 2 mm | 2 — Black |
| Red_Artwork | 14 to 16 mm | 2 mm | 3 — Red |

Backing and White_Artwork remain distinct parts even though they initially share white filament. You can change Backing's filament without changing White_Artwork. Match logical colors to your actual AMS slots. There is no need to paint individual details.

These are separate geometry components touching at the front face, intended to fuse together when printed in the supplied assembly. This is not a detachable faceplate or a glue-fit kit.

## Construction correction

- Backing is one continuous silhouette solid, with the bottom-to-top channel subtracted; no detailed artwork is embossed, inset, or extruded through it.
- Removed the old black inlay/recess inside the backing.
- Removed the old boolean union between white decorative artwork and backing.
- All decorative colors are generated ABOVE the backing at Z14–16. They share a common top height; this revision does not put one artwork color higher than another.
- The front is resolved from the original SVG's visible color partition, using common boundaries. Boolean partitioning removes numerical sliver intersections and prevents duplicated solid volumes. No independent polygon smoothing or intentional fine-detail removal is applied.
- Original SVG remains unchanged locally and is not included in this delivery package. Curves are sampled for meshing, as in prior prototypes; finite mesh precision still applies.
- The overall width remains 35 mm with proportional height about 25.78094 mm. Mesh simplification used in the earlier trial is not applied to this revision; file size is therefore larger, and outer dimensions match the nominal 35 mm more closely.
- White back is plain. Standard STL exports are in geometry/, one file per component, and retain relative positions. Import all four together as one multipart object; do not arrange or drop the artwork parts separately onto the bed.

## Straw passage and fit

- Modeled nominal channel diameter: 10.00 mm.
- Nominal straw target: 10 mm outer diameter.
- Added diameter clearance: 0.00 mm.
- Axis is bottom-to-top, X=19.29133858 mm from artwork left, Z=7 mm centered in the backing.
- Bore is a 192-segment circular approximation: maximum diameter 10 mm, minimum flat-to-flat diameter approximately 9.99866 mm.
- Nominal front and rear backing walls: 2 mm each.

Exact-size holes can print snug. This is an unprinted prototype: sliced overhang/support review, actual straw fit, strength and irregular entry/exit wall checks remain required. Do not force onto a straw. No fit certification, exhaustive global minimum-wall certification, or printer-ready G-code is claimed.

## Validation performed

1. Backing is one connected, closed, consistently oriented solid.
2. Every decorative body is closed and entirely at Z14–16; backing ends at Z14.
3. Pairwise intersection volumes between all four parts are zero within the recorded numerical tolerance (1e-7 mm3); no duplicated solid volume is intentionally present.
4. The three decorative bodies cover exactly the common front layer within floating-point precision.
5. Channel remains unobstructed.
6. Serialized backing cross-sections near its rear and front match within 1e-6 mm2 numerical tolerance, confirming that artwork-shaped recesses do not extend through the backing. The measured residual is recorded in construction-verification.json.
7. Official Bambu Studio **02.08.02.61** GUI opened the delivery file without the invalid-config warning and showed the intended palette.
8. Actual Bambu import/export retained four parts and filament assignments Backing=1, White_Artwork=1, Black_Artwork=2, Red_Artwork=3. No printer was connected and no print was started.
9. The packaging exporter preserves the generated component mesh data exactly; native Bambu reserialization roundoff is measured in export-verification.json.

See geometry/geometry-validation.json, construction-verification.json, export-verification.json, and the real Bambu screenshots. These are engineering checks, not a physical print test. Other slicers may ignore Bambu-specific settings; use the generic core 3MF or aligned STLs for those slicers.

## Source and reproduction

This directory contains the geometry builder, scoped Bambu exporter, and both validation scripts. To reproduce, supply your original Josh.svg under source/; the uploaded source artwork is not redistributed here. No website, UI, other generator, original artwork file, or previous prototype was modified.

Python tools: numpy, svgpathtools, shapely, manifold3d, trimesh. The builder is intentionally scoped to this Josh SVG. It uses the existing SVG layer structure, rather than being a general background-removal implementation.

1. Run `python build_four_parts.py` to generate geometry/ and its core assembly.
2. Use `python export_bambu.py --source geometry/Josh-Four-Part-Core.3mf --template /path/to/Bambu-exported-project.3mf --resources /path/to/BambuStudio/resources --output Josh-35mm-Separate-Backing.3mf` with Bambu 02.08.02.61 resources and a project-settings template exported by that version.
3. Run `python verify_construction.py`.
4. Import and export through the real Bambu executable with arrangement/orientation disabled, then run `python verify_export.py geometry/Josh-Four-Part-Core.3mf Josh-35mm-Separate-Backing.3mf /path/to/verified-roundtrip.3mf --report export-verification.json`.
5. Reopen the delivery file in the Bambu GUI and inspect the four component assignments. Do not substitute a colored renderer preview for that check.

Profile data derives from official Bambu Studio BBL machine/process/filament resources, with upstream source and licensing at https://github.com/bambulab/BambuStudio/tree/v02.08.02.61 . No Bambu executable or network plug-in is redistributed.
