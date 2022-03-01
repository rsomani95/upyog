
## 0.4.2 -- 2 Mar 2022
- `Visualiser` classmethods to init from RGB/BGR `np.ndarray`
- Allow `Visualiser.draw_bbox` without a `label`
- Improve error handling for all methods that accept `xy` or `xyxy` to ensure we have correct `len(xy|xyxy)`

## 0.4.1 -- 27 Jan 2022
- Adjust font path, export font with package

## 0.4 -- 27 Jan 2022

### New Features
Add `upyog.ann` - a subpackage that has interfaces to artificial
nearest neighbor libraries.
  - Added `AnnoyIndexer` and `AnnoyDataFrameIndexer`

### Enhancements
- Improve `upyog.utils.utils.flatten` to work with any iterable

## 0.3.2 -- 19th Jan 2022

- Bugfixes:
  - `move-files`
  - `generate-image-grid`

## 0.3.0 -- 19th Jan 2022

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
