# Tracklib

<p align="center">
<table style="border:none;border:0;width:60%"><tr>
  <td align="center" style="width:30%"><img width="200px" src="https://github.com/umrlastig/tracklib/blob/main/doc/source/img/TracklibLogo.png" /></td>
  <td style="padding:16px;"><label>Tracklib</label> library provide a variety of tools, operators and functions to manipulate GPS trajectories</td>
</tr></table>
</p>

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![Tracklib build & test](https://github.com/umrlastig/tracklib/actions/workflows/ci.yml/badge.svg)](https://github.com/umrlastig/tracklib/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/umrlastig/tracklib/branch/main/graph/badge.svg?token=pHLaV21j2O)](https://codecov.io/gh/umrlastig/tracklib)
[![Documentation Status](https://readthedocs.org/projects/tracklib/badge/?version=latest)](https://tracklib.readthedocs.io/en/latest/?badge=latest)
[![Software License](https://img.shields.io/badge/Licence-Cecill--C-blue.svg?style=flat)](https://github.com/umrlastig/tracklib/blob/main/LICENCE)

[![Supported Python Versions](https://img.shields.io/pypi/pyversions/tracklib.svg)](https://www.python.org/downloads/)
[![PyPI Version](https://img.shields.io/pypi/v/tracklib.svg)](https://pypi.python.org/pypi/tracklib/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/tracklib?color=blue)](https://pypistats.org/packages/tracklib)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13899752.svg)](https://doi.org/10.5281/zenodo.13899752)


More and more datasets of GPS trajectories are now available and they are studied very frequently in many scientific domains. Currently available Python libraries for trajectories can separately load, simplify, interpolate, summarize or visualize them. But, as far as we know, there is no Python library that would contain all these basic functionalities. This is what tracklib is modestly trying to do. The library provides  some conventions, capabilities and techniques to manipulate GPS trajectories.

In tracklib, the core model supports a wide range of trajectory  applications:

1/ trajectory can be seen as a concept of (geo)located timestamps sequence to study for example an athlete's performance,

2/ trajectory can be seen as a concept of a curve which makes it possible to study trajectory shapes,

3/ a full trajectory dataset can be reduced into a regular grid of summarized features,

4/ with map matching process, trajectories can be seen as a network of routes.

Furthermore, adding analytical features (e.g. speed, curvilinear abscissa, inflection point, heading, acceleration, speed change, etc.) on a observation or on all observations of a trajectory (function of coordinates or timestamp) is, in general, a complex and a boring task. So, to make it easier, _Tracklib_ module offers a multitude of operators and  predicates to simplify the creation of analytical features on a GPS tracks.

## Documentation

The official online documentation is available at **[ReadTheDocs](https://tracklib.readthedocs.io)**

In particular, the docs include **[quick examples](https://tracklib.readthedocs.io/en/latest/userguide/gallery.html)** and some **[Use cases](https://tracklib.readthedocs.io/en/latest/usecase/index.html)**

## Installation

#### from pypi (i.e. via pip)

```bash
pip install tracklib
```

## Citation

If you use tracklib, please cite the following references:

<div style="background-color:rgba(200, 200, 200, 0.0470588); text-align:left; vertical-align: middle; padding:10px;">
Yann Méneroux, Marie-Dominique van Damme. Tracklib: a python library with a variety of tools, operators and functions to manipulate GPS trajectories. 2022, [HAL Id](https://hal.science/hal-04356178v1)
</div>



## Scientific papers whose experiments use the Tracklib library
<ul>
<li>Méneroux, Y., Muller, J.M., Seba, A., Bouquet, P., Ruaud, A., & Pierrot-Deseilligny, M.. 2025. Vers un couplage fort des approches topométrique et photogrammétrique pour le contrôle de trajectoire d’un véhicule autonome. XYZ : revue de l'Association française de topographie (n°183), 33-40.</li>
<li>Marie-Dominique Van Damme, Yann Méneroux, and Ana-Maria Olteanu-Raimond. 2024. A metrological analysis of a modular and iterative aggregation algorithm of GNSS trajectories. In Proceedings of the 32nd ACM International Conference on Advances in Geographic Information Systems (SIGSPATIAL '24). Association for Computing Machinery, New York, NY, USA, 633–636. https://doi.org/10.1145/3678717.3691325</li>
<li>Méneroux, Y., Maidaneh Abdi, I., Le Guilcher, A., & Olteanu-Raimond, A. M. (2022). Is the radial distance really a distance? An analysis of its properties and interest for the matching of polygon features. International Journal of Geographical Information Science, 37(2), 438–475. https://doi.org/10.1080/13658816.2022.2123487</li>
</ul>


## About

|                |                                                           |
| -------------- | --------------------------------------------------------- |
| _version_      | See [pypi](https://pypi.org/project/tracklib/#history)    |
| _status_       | Active since 2020 November 1st, 2020                      |
| _license_      | Cecill C                                                  |

## Development

Institute: LASTIG, Univ Gustave Eiffel, ENSG, IGN

Authors
- Yann Méneroux
- [Marie-Dominique Van Damme](https://www.umr-lastig.fr/mdvandamme/)
- Nisar Hakam
- [Lâmân LELÉGARD](https://www.umr-lastig.fr/laman-lelegard/) 
- [Mattia Bunel ](https://www.umr-lastig.fr/mattia-bunel/index_fr.html)














