
## Unreleased
* Bugfixes:
  - `Box.center_left` xy coords
* Added:
  - `__all__` to all modules for cleaner imports
  - `draw_multiline_text`
  - New CLI program:
    - `generate-image-grid` to create grids of images from folders
* Changed:
  - Revamped `draw_text`:
    - more precise with text positioning
    - more text positions available
    - line spacing option
    - height and width constraints options
    - padding option

## 0.2.0 -- 18th Jan 2022
* Image: Added functions to draw keypoints, circles and ellipses
* Image: Some error handling when we fail to resize font size successfully
* Added new CLI program:
  - `remove-duplicates-from-folder`