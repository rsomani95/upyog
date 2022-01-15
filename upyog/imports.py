import json, mimetypes
import operator
import os
import re
import shutil
import socket
import uuid
import warnings

from collections import OrderedDict, defaultdict, namedtuple
from dataclasses import dataclass
from datetime import datetime
from functools import partial, reduce
from pathlib import Path
from pprint import pprint
from typing import *

import fastcore.all as fastcore
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PIL
import pyperclip
import rich

from loguru import logger
from os_utilities.utils import *
from PIL import Image, ImageFile, ImageDraw, ImageFont
from PIL import features as PILFeatures
from rich.progress import track
from rich.traceback import install
from tqdm.auto import tqdm
from typing_extensions import Literal


install()
logger.opt(colors=True)
tqdm.pandas()

ImageFile.LOAD_TRUNCATED_IMAGES = True
# PILFeatures.pilinfo()
