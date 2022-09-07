# Boundary Currents Monitor

[![status](https://img.shields.io/badge/lifecycle-experimental-orange)](https://lifecycle.r-lib.org/articles/stages.html#experimental)

Within the Euro-ArgoRISE project, a couple of analysis are run automatically to *monitor* Boundary Current systems of interest in the following regions:

![BC](https://user-images.githubusercontent.com/1956032/168844751-a77785d1-bd65-413f-9598-34bcb36d1f9a.png)

🌿 Note that all BC monitors run on Github actions in order to minimise their impact on the environment, [since Github claims to be carbon neutral](https://github.blog/2021-04-22-environmental-sustainability-github). 

## Census
[![BC-status](https://github.com/euroargodev/boundary_currents_pcm/actions/workflows/status.yml/badge.svg)](https://github.com/euroargodev/boundary_currents_pcm/actions/workflows/status.yml)

Below are the profile count reported for each BCs over the last 10 days.  
You can **click on badges to access profile index file**.  
Counts and index are updated every 6 hours.

[![index](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GSE_tight_status.json)](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GSE_tight_index.txt)  
[![index](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GoC_status.json)](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GoC_index.txt)  
[![index](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_West_Med_status.json)](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_West_Med_index.txt)  
[![index](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_Lig_Sea_status.json)](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_Lig_Sea_index.txt)  
[![index](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_EGC_status.json)](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_EGC_index.txt)

## NRT Supervised classification of profiles (PCM)
[![NRT-classif](https://github.com/euroargodev/boundary_currents_pcm/actions/workflows/nrt_classif.yml/badge.svg)](https://github.com/euroargodev/boundary_currents_pcm/actions/workflows/nrt_classif.yml)

Our work include the development of [Profile Classification Models (PCM)](https://pyxpcm.readthedocs.io/en/latest/overview.html) dedicated to the identification/classification of Argo profiles in boundary current systems of interest. 

For boundary currents [with a stable PCM](https://github.com/euroargodev/boundary_currents_pcm/tree/main/pcmbc/assets), we run a near real time (NRT) analysis of profiles.   
Results are saved in an [*augmented* index file](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GSE_tight_index_classified.txt) and synthesized in [figures like this one](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GSE_tight_index_classified.png):

### Gulf Stream

[![map](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GSE_tight_index_classified.png)](https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GSE_tight_index_classified.txt)  

***

This repository has been developed within the framework of the Euro-ArgoRISE project. This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement no 824131. Call INFRADEV-03-2018-2019: Individual support to ESFRI and other world-class research infrastructures.

<p align="center">
<a href="https://www.euro-argo.eu/EU-Projects/Euro-Argo-RISE-2019-2022">
<img src="https://user-images.githubusercontent.com/59824937/146353317-56b3e70e-aed9-40e0-9212-3393d2e0ddd9.png" height="75"/>
</a>
</p>
