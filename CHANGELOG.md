## 0.5.6 -- 31 October 2022
* Save image with Exif metadata
* Convert bytes -> human readable sizes
* Check corrupted images
* Convert items to list/tuple
* Init everything via `from upyog.all import *`
* Pretty DataFrame printing


## 0.5.5 -- 1 September 2022
* Add a bunch of utilities related to iterating in `utils.utils`
* `make_img_grid` in non-verbose mode... finally


## 0.5.4 -- 8 August 2022
* Add `upyog.utils.zip` -- utilities to easily zip files / folders in Python

## 0.5.1 -- 8 August 2022

* Added `nb2script` command line tool (copied over from the earliest nbdev mockup that worked on individual notebooks)
* Respect `PIL.Image.mode` after doing operations (not thoroughly tested). Previously we converted everything to RGB mode
* Classmethod for instantiating a `Visualiser`
* Load truncated images by default
* Added simple bbox utils for xyxy <-> xywh conversions
* Add `get_YYYY_MM_DD` convenience function
* Add `get_file_size` util
* Add patched methods to `pathlib.Path`:
  * `list_files()`
  * `ls()`
* Downloading utils copied over from `torchvision`

## 0.4.3 -- 25 March 2022

* Added `border_width` param (unexposed) to `opyog.image.draw._write_text`
* Added `find-common-files-between-folders` program

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
