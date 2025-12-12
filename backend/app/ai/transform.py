# -*- coding: utf-8 -*-
# Transform utilities for image preprocessing
# Simplified version from Silent-Face-Anti-Spoofing

import numpy as np
import torch


class Compose:
    """Composes several transforms together."""
    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, img):
        for t in self.transforms:
            img = t(img)
        return img


class ToTensor:
    """Convert numpy.ndarray to tensor."""
    def __call__(self, pic):
        if isinstance(pic, np.ndarray):
            # handle numpy array
            if pic.ndim == 2:
                pic = pic.reshape((pic.shape[0], pic.shape[1], 1))
            img = torch.from_numpy(pic.transpose((2, 0, 1)))
            return img.float()
        else:
            raise TypeError('pic should be numpy.ndarray. Got {}'.format(type(pic)))

