# Artwork-to-model quality checks

For future artwork-derived prototypes and corrections in this directory:

- Inspect each exported color body in isolation on a neutral background. A full-color preview can conceal stray slivers.
- Check for specks, long narrow fragments, and unintended color along the silhouette, at the final physical size. Area filtering alone is insufficient.
- Use artwork-specific rules. For artwork with an intended enclosing black outline, keep other inks inside that outline and verify edge clearance in the actual exported mesh. Do not impose a black-border rule on designs without one.
- Preserve intended small dots, holes, lettering, and petal details. Report uncertain features for visual review instead of deleting them just because they are small.
- Record cleanup parameters, changes, component counts, and a layer-isolated before/after preview. The boxing-glove `cleaned/artwork_cleanup.py` module is an opt-in example, not a universal filter.
- When only artwork is corrected, verify that backing geometry, dimensions, and channel geometry are unchanged.
- Validate closed meshes, aligned parts, and absence of overlapping solid volumes. Test the delivered 3MF in the actual target slicer and check native imported filament assignments. File generation or preview color alone is insufficient.
- Keep physical printing and fit limitations explicit. Do not claim that an automated check guarantees all future images will be clean.

Do not change website/UI or unrelated product geometry while applying these prototype checks.
