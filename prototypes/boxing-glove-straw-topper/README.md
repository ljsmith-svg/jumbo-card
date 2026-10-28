# Boxing-glove straw topper — physical-test release

Open **Boxing-Glove-35mm-P1S.3mf** as a project in Bambu Studio. Map the four project colors to your actual AMS slots. No manual artwork painting should be needed. The supplied STL files are uncolored alternatives, with shared coordinates; import them together as parts of one object rather than arranging them independently.

## Dimensions and construction

- Artwork width: 35.00 mm; proportional height: 40.4877 mm.
- One continuous, plain-white backing: Z0–14 mm.
- Separate decorative parts: Z14–16 mm, all 2 mm above the backing.
- Centered passage parallel to the artwork face, along the bottom-to-top Y direction. X17.5 mm, Z7 mm; 10.00 mm nominal diameter, **zero added clearance**. The 256-sided representation measures 9.99925 mm across flats.
- Front and rear nominal walls: 2 mm. This is not a certification of 2 mm walls around every irregular entry/exit rim. Physical fit and channel-roof bridging remain test-print checks.
- No rear sleeve or cap. White backing and white detail are independently selectable geometry, initially sharing filament 1. The separate parts fuse when printed together.

| Part | Project filament | Color |
| --- | --- | --- |
| Backing | 1 | White #FFFFFF |
| Black_Artwork | 2 | Black #020202 |
| Hot_Pink_Artwork | 3 | Hot pink #FF187E |
| Light_Pink_Artwork | 4 | Light pink #F8A3C7 |
| White_Detail | 1 | White #FFFFFF |

The small White_Detail part preserves three enclosed white spaces in the original drawing. It does not require a fifth filament.

## Source and cleanup

The uploaded SVG contains an embedded 1151×1366 JPEG and five traced shade layers. The SVG page crops the artwork. This release uses the **complete original embedded JPEG**, not the cropped page, traced extra shades, generated concept image, or Josh geometry.

The exterior white background is removed. Color quantization separates black, hot pink, light pink, and the enclosed white spaces. Saturation and the median color of each region enclosed by black linework flatten JPEG shading; a 3-pixel median filter removes noise. Vector contour simplification tolerance is 0.008 mm. Specks and holes below 0.006 mm² are removed. Color parts are constructed as a shared solid partition without overlapping volume. The source artwork file is retained locally, not republished in this delivery.

## Verification

Actual official Bambu Studio **02.08.02.61**:

- GUI opened the file with its four-color palette and no invalid-configuration warning.
- Actual 0.4 mm P1S / Generic PLA / 0.20 mm / Arachne slicing completed successfully, return code 0, no slicing warnings.
- Native Bambu import/save retained all five named parts and their intended filament assignments. All four filaments are used in generated toolpaths.
- Native-save coordinates differ only by float roundoff, maximum 0.000002588 mm.
- All component meshes are closed and consistently oriented; backing has one connected solid; pairwise overlap volumes are below 1e-7 mm³.
- The palette has a valid 4×4 purge matrix calculated by Bambu Studio. The prime tower was moved to X30/Y180 because the inherited Y220 position exceeded the bed with four colors. This did not change topper geometry.

Estimate: **108 minutes**, **26.47 g** including purge/tower, **8.00 g** in the model. Actual material and time depend on filament and slicing choices.

Fine details are not guaranteed printable simply because slicing succeeds. An actual top-layer toolpath check found some paths below 0.34 mm (about 2.8% of total top-layer path length). The smallest butterfly dots, petal lines, points, and the snug zero-clearance passage need a physical test. No physical print has been performed by this environment. This is a test-print release, not a production certification.

## Engineering files

`geometry-validation.json`, `verification.json`, and `nozzle-toolpath-check.json` record the checks. `artwork-geometry-preview.png` is a source-derived geometry diagram, not a photo of a printed item. `Bambu-import-verified.png` records the real GUI import. No printer-ready G-code is distributed.

For rebuilding, extract the original embedded JPEG from the supplied SVG into `source.jpg` beside the scripts, install numpy, scipy, Pillow, scikit-image, shapely, manifold3d, trimesh and matplotlib, then run `build_topper.py` followed by `package_bambu.py`. `p1s-profile-base.json` contains the official-profile-derived baseline, adapted by the exporter for these four colors. Verification additionally needs a new Bambu CLI slice/native export at the path shown in `verify_topper.py`; the Python geometry checks alone do not verify actual slicer compatibility.

Only this new prototype was created. Existing Josh exports, website, UI and other product generators were left unchanged.
