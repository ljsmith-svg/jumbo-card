# Boxing-glove topper — edge-cleanup correction

Use **Boxing-Glove-35mm-Cleaned.3mf** instead of the first boxing-glove export. Open as a project in Bambu Studio and map white, black, hot pink and light pink to the actual AMS slots. Individual STL alternatives retain shared coordinates but do not carry filament assignments.

## What changed

Pale antialiased pixels along the JPEG's black outline became long, thin light-pink fragments. The first speck filter was based on area and missed them. This correction adds:

- An opt-in 0.20 mm outer black-outline guard for pink regions.
- A 0.06 mm morphological opening for the light-pink part to remove hairline fringes and spurs.
- A maximum-inscribed-width check for narrow isolated light-pink components (0.30 mm threshold). This check does not delete the intentional hot-pink butterfly dots.
- An export gate requiring a passing cleanup audit, plus verification of edge clearance on the **actual exported meshes**.
- An isolated light-pink before/after diagram so the marks cannot hide underneath other colors.

Seven unwanted light-pink components are removed: 47 components become 40. Total removed pink area is about 0.549 mm², or 0.26% of the original light-pink area. The hot-pink artwork and white detail mesh are unchanged. Removed pink volume becomes part of the existing black artwork, maintaining an exact, nonoverlapping partition. Fine light-pink tips are slightly rounded by the opening operation.

## What stayed the same

- 35 mm artwork width; proportional height 40.4877 mm.
- One separate, continuous 14 mm backing; artwork at Z14–16 mm.
- 10 mm nominal straw passage, zero added clearance; 9.99925 mm polygonal flat-to-flat representation.
- Backing mesh is **exactly unchanged**, including the channel and all its surfaces. Front/rear nominal walls remain 2 mm; irregular opening rims are not certified for a 2 mm minimum all around.
- Five named parts using four filaments: Backing/White_Detail = 1 white, Black_Artwork = 2 black, Hot_Pink_Artwork = 3 hot pink, Light_Pink_Artwork = 4 light pink.
- P1S 0.4 mm / PLA / 0.20 mm / Arachne settings and inward purge-tower placement.

## Validation

`cleanup-verification.json` checks the real 3MF mesh slices: minimum outer-edge clearance is about 0.411 mm for light pink and 0.443 mm for hot pink. This is an edge-color check, not a minimum-line-width guarantee. Backing and white detail mesh digests match the previous export exactly. All components are closed and pairwise overlap is below 1e-7 mm³.

`verification.json` and `Bambu-slice-result.json` record a fresh actual Bambu Studio 02.08.02.61 slice and native import/save check, including all five part names and four filament assignments. The corrected file was also opened in the Bambu GUI. No printer is connected or activated. The side-by-side diagram is actual XY geometry, not a photo.

Physical printing is still required to assess the smallest features and snug 10 mm fit. These checks reduce artifacts; they cannot guarantee that every future image will need no review. The reusable cleanup module is appropriate for this black-outlined design, not for arbitrary images with intended color at the outside edge. Prototype quality instructions now require isolated color checks for future work.

Original input artwork is retained locally and is not republished in this package. For rebuilding, extract its embedded JPEG as `source.jpg`, then run `build_topper.py` and `package_bambu.py` with numpy/scipy/Pillow/scikit-image/shapely/manifold3d/trimesh/matplotlib installed. Actual Bambu validation must be rerun after rebuilding. `verify_cleanup.py` also requires the previous export in its documented sibling folder.
