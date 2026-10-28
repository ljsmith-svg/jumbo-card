# Josh multicolor 3MF export correction

Open **Josh-35mm-10mm-Bambu-Colors.3mf** as a project in Bambu Studio. It contains three aligned existing components with white (1), black (2), and red (3) filament assignments. Match those logical filaments to your actual AMS slots before printing. No painting is required for these existing component colors.

## Scope

This is strictly an export correction for the existing 35 mm / 10 mm-opening trial. Every original mesh vertex and triangle attribute is preserved exactly in the delivered file. Width, height, backing, relief, channel dimensions, holes, and fine details were not regenerated. The whole assembly is translated to the center of a 256 mm bed; parts do not move relative to each other.

The latest instruction explicitly prohibited geometry changes. Therefore this file still contains the previous combined white backing/artwork mesh, black inlay, and raised red artwork. It is NOT the proposed four-part construction correction. The combined part is truthfully named White_Backing_and_Artwork. Backing/white-artwork separation and pre-existing small volume intersections remain a separate geometry task.

Nominal source dimensions: 35 mm artwork width (actual exported silhouette 34.998479 mm from pre-existing curve cleanup), proportional height 25.780941 mm, body 14 mm, red/white top 16 mm, black top 14 mm. Straw channel 10.00 mm, 0.00 mm added diameter clearance. These dimensions are unchanged. Physical fit/strength and minimum-wall checks remain outstanding from the prior prototype; successful import is not print certification.

## Root cause

The prior ZIP contained only the core model, content types, and package relationship. It had three meshes and core basematerial display colors, but no Metadata/project_settings.config or Metadata/model_settings.config. The Bambu importer did not recognize those core basematerial entries as filament groups, and project validation had no nozzle/profile configuration to load. Hence geometry loaded, the GUI issued the invalid-config warning, and parts defaulted to filament 1.

The new exporter adds a complete project configuration, official P1S 0.4 mm/PLA profile data, coherent three-filament index/variant arrays, and explicit per-part extruder assignments. It includes one plate and a centered assembly. Compatibility metadata follows the Bambu 3MF schema. It does not change shared generic exporters or any UI/application code.

## Verified evidence

Tested using the official BambuStudio **02.08.02.61** Ubuntu 24.04 release, on an isolated local Xorg display with software rendering. No printer was connected and no print command was issued.

- Real GUI opened the exact delivered file without the invalid-config warning; white, black and red loaded visibly. See Bambu-import-verified.png.
- Real Bambu CLI imported and re-exported the final file. Its saved part configs retained filament indices 1, 2, 3 and its project palette retained #FFFFFF, #020202, #F20512. Native re-export is included as Bambu-verified-roundtrip.3mf for audit; use the named delivery file above to preserve exact original coordinate strings.
- Geometry hashes before/after the delivery export match exactly. Native Bambu reserialization changes floating-point coordinate rounding by at most 0.0000016 mm; triangle indices and counts remain unchanged.
- GUI testing caught and corrected a filament_self_index/filament_extruder_variant count mismatch that CLI-only testing did not reject. Export checks now enforce the related three-filament lists.
- Standard STL copies are byte-for-byte unchanged. They retain alignment and carry no reliable color assignments. Import all three together as one multipart object if using STLs.
- No claim is made for older Bambu Studio versions, other slicers' project-setting compatibility, slicing success, or physical printing in this correction. Other slicers can use the unchanged STLs or the unchanged standard core 3MF in portable/.

## Reproduction

Python dependencies: numpy; geometry verification additionally uses only standard-library XML/ZIP parsing and numpy. The geometry builder is not run.

1. Obtain the official Bambu Studio release and its resources.
2. Export a template with that Bambu executable from the original portable 3MF: `bambu-studio --arrange 0 --orient 0 --export-3mf template.3mf --outputdir audit portable/Josh-Original-Core.3mf`.
3. Run `python export_bambu.py --source portable/Josh-Original-Core.3mf --template audit/template.3mf --resources /path/to/BambuStudio/resources --output Josh-35mm-10mm-Bambu-Colors.3mf`.
4. Use the real Bambu executable to import/export that result: `bambu-studio --arrange 0 --orient 0 --export-3mf verified-roundtrip.3mf --outputdir audit Josh-35mm-10mm-Bambu-Colors.3mf`.
5. Run `python verify_export.py portable/Josh-Original-Core.3mf Josh-35mm-10mm-Bambu-Colors.3mf audit/verified-roundtrip.3mf --report export-verification.json`.
6. Open the final result in the Bambu GUI and check the warning state, palette, Objects assignments, and alignment. Do not substitute successful generation/CLI exit for this GUI check.

This exporter is intentionally scoped to the existing three-component prototype. It fails on unexpected component names/counts or pre-existing build transforms; do not silently use it for a future four-component construction. That architecture requires a separate update and validation.

## Upstream references and attribution

Official release: https://github.com/bambulab/BambuStudio/releases/tag/v02.08.02.61
Bambu Studio source used for investigation: commit 926a7192574bcb9b3a732e1ec59a46d79cb45466.
- src/slic3r/GUI/Plater.cpp: check_project_config and invalid-config warning.
- src/libslic3r/Format/bbs_3mf.cpp: project/model settings and per-volume extruder loading.
- src/libslic3r/PresetBundle.cpp: filament variant/index consistency validation.
Profile data in the exported project derives from the official Bambu Studio BBL resources (machine, process, filament profiles), distributed under Bambu Studio's upstream licensing: https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/LICENSE . No Bambu executable or network plug-in is redistributed in this package.
