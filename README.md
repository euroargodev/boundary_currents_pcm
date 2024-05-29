# PCM analysis in Boundary Currents

[![status](https://img.shields.io/badge/lifecycle-experimental-orange)](https://lifecycle.r-lib.org/articles/stages.html#experimental)
[![Binder](https://img.shields.io/static/v1.svg?logo=Jupyter&label=MyBinder&message=demo&color=blue)](https://mybinder.org/v2/gh/euroargodev/binder-sandbox/virtual-fleet?urlpath=git-pull%3Frepo%3Dhttps%253A%252F%252Fgithub.com%252Feuroargodev%252Fboundary_currents_pcm%26urlpath%3Dlab%252Ftree%252Fboundary_currents_pcm%252Fdocs%252FPCM-demo.ipynb)


[ci-energy-badge-census]: https://api.green-coding.berlin/v1/ci/badge/get?repo=euroargodev/boundary_currents_pcm&branch=main&workflow=26287325
[ci-energy-link-census]: https://metrics.green-coding.io/ci.html?repo=euroargodev/boundary_currents_pcm&branch=main&workflow=26287325

[ci-energy-badge-pcm]: https://api.green-coding.berlin/v1/ci/badge/get?repo=euroargodev/boundary_currents_pcm&branch=main&workflow=26287325
[ci-energy-link-pcm]: https://metrics.green-coding.io/ci.html?repo=euroargodev/boundary_currents_pcm&branch=main&workflow=26287325

Home page for the development of [Profile Classification Models (PCM)](https://pyxpcm.readthedocs.io/en/latest/overview.html) dedicated to the identification/classification of Argo profiles in boundary current systems of interest within the Euro-ArgoRISE project.  


## 🛠 Roadmap
1. Get one PCM for each boundary currents hydrography: [check progress here](https://github.com/euroargodev/boundary_currents_pcm/projects/1)
2. Get a product and real-time monitoring of BCs: [check progress here](https://github.com/euroargodev/boundary_currents_pcm/projects/2)

## 👋 Discussions
- [Help on PCM](https://github.com/euroargodev/boundary_currents/discussions/6)
- [Science questions about your PCM](https://github.com/euroargodev/boundary_currents/discussions?discussions_q=label%3Aclassification)
- [Technical issues about PCM in BCs](https://github.com/euroargodev/boundary_currents_pcm/issues)

# The "BC Monitor"

On this repository, a couple of analysis are run automatically to *monitor* Boundary Current systems.

🌿 Note that all BC monitors run on Github actions in order to minimise their impact on the environment, [since Github claims to be carbon neutral](https://github.blog/2021-04-22-environmental-sustainability-github). 

## Census
[![BC-status](https://github.com/euroargodev/boundary_currents_pcm/actions/workflows/status.yml/badge.svg)](https://github.com/euroargodev/boundary_currents_pcm/actions/workflows/status.yml)
[![CI Energy Censur][ci-energy-badge-census]][ci-energy-link-census]

Below are the profile count reported for each BCs over the last 10 days.  
You can click on badges to access directly to the corresponding index file.  
Counts and index are updated hourly.

[![index](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GSE_tight_status.json)](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GSE_tight_index.txt)  
[![index](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GoC_status.json)](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GoC_index.txt)  
[![index](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_West_Med_status.json)](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_West_Med_index.txt)  
[![index](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_Lig_Sea_status.json)](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_Lig_Sea_index.txt)  
[![index](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_EGC_status.json)](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_EGC_index.txt)

## NRT Supervised classification of profiles (PCM)
[![NRT-classif](https://github.com/euroargodev/boundary_currents_pcm/actions/workflows/nrt_classif.yml/badge.svg)](https://github.com/euroargodev/boundary_currents_pcm/actions/workflows/nrt_classif.yml)
[![CI Energy Censur][ci-energy-badge-pcm]][ci-energy-link-pcm]

For boundary currents [with a stable PCM](https://github.com/euroargodev/boundary_currents_pcm/tree/main/pcmbc/assets), we run a near real time (NRT) analysis of profiles.   
Results are saved in an [*augmented* index file](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GSE_tight_index_classified.txt) and synthesized in [figures like this one](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GSE_tight_index_classified.png): 

[![map](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GSE_tight_index_classified.png)](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GSE_tight_index_classified.txt)  

***

This repository has been developed within the framework of the Euro-ArgoRISE project. This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement no 824131. Call INFRADEV-03-2018-2019: Individual support to ESFRI and other world-class research infrastructures.

<p align="center">
<a href="https://www.euro-argo.eu/EU-Projects/Euro-Argo-RISE-2019-2022">
<img src="https://user-images.githubusercontent.com/59824937/146353317-56b3e70e-aed9-40e0-9212-3393d2e0ddd9.png" height="75"/>
</a>
</p>

