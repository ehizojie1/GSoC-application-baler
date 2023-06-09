<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.

# Introduction
Thank you for applying! In this project we will be improving the tool our team is developing to compress scientific data using machine learning. The tool is called "Baler" and as part of your application, you will apply baler to a given particle physics dataset, a data set of your choice, and present your results. This will test your skills of working with python libraries, autoencoders, and communication skills.

Baler is a tool used to test the feasibility of compressing different types of scientific data using machine learning-based autoencoders.

# Table of contents
1. [Setup](#setup)
2. [Tutorial Example](#tutorial)
3. [Your Task](#task)
4. [Rules](#rules)
5. [Deliverables](#deliverables)

# Before you begin
Before you begin, fork this repository. Your submission relies on you sharing the link to your fork beause you will put the results of your work in the `GSoC-application-baler/deliverables` diretory of your fork.

# Setup <a name="setup"></a>
## If you are using Windows 10/11
* If you are using a Mac on Linux system, skip to the [next section](#linux)
* The best way to run baler on Windows is to do so using the "Windows Subsystem for Linux"
* Install "git for windows": https://github.com/git-for-windows/git/releases/tag/v2.39.1.windows.1
  * For a 64 bit system, probably use this one: https://github.com/git-for-windows/git/releases/download/v2.39.1.windows.1/Git-2.39.1-64-bit.exe
* Go to your windows search bar and search for "powershell". Right-click powerhsell and select "run as administrator"
* Enable Linux subsystem by entering this into the PowerShell and hitting enter: `Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux`
* Go to the windows store and download "Ubuntu 22.04.1 LTS"
* Once downloaded, open it. This will start Ubuntu as a "terminal". After picking a username and password, input the following commands into that terminal. You can copy the commands using ctrl+c or the button to the right of the text. But pasting it into the terminal can only be done by right-clicking anywhere in the terminal window.

Start by updating the Windows Subsystem for Linux
```console
wsl.exe --update
```
Then, synch your clock:
```console
sudo hwclock --hctosys
```
Update your Linux packages
```console
sudo apt-get update
```
Configure git to use tour windows credentials helper, this is necessary for you to authenticate yourself on GitHub.
```console
git config --global credential.helper "/mnt/c/Program\ Files/Git/mingw64/bin/git-credential-manager-core.exe"
```
Install pip3 for downloading python packages
```console
sudo apt-get install python3-pip
```
At this point, you have a working Linux environment and you can follow the next section for the Linux setup

## Setup (Linux/Mac or Windows Subsystem for Linux) <a name="linux"></a>
For some Linux users (Ubuntu), disable the KDE keyring
```console
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
```
Install poetry for managing the python environment
```console
pip3 install poetry
```
Add poetry to path in your current session (Maybe not necessary for Mac)
```console
source ~/.profile
```
Clone **your fork** of this  repository
```console
git clone https://github.com/USERNAME/GSoC-application-baler
```
Move into the Baler directory
```console
cd GSoC-application-baler
```
Use Poetry to install the project dependencies
```console
poetry install
```
Download the tutorial dataset, this will take a while
```console
wget http://opendata.cern.ch/record/21856/files/assets/cms/mc/RunIIFall15MiniAODv2/ZprimeToTT_M-3000_W-30_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/10000/DAA238E5-29D6-E511-AE59-001E67DBE3EF.root -O data/example/example.root
```
Finally, verify that the download was successful
```console 
md5sum data/example/example.root 
> 28910642bf94e0fa9442bc804830f88b  data/example/example.root
```

# Tutorial Example  <a name="tutorial"></a>
## Create New Project 
Start by creating a new project directory. This will create the standardized directory structure needed, and create a skeleton config, pre-processing script, analysis script, and output directories. In this example, these will live under `./projects/example/`.
```console
poetry run python baler --project=example --mode=new_project
```

## Pre-processing
Baler Currently only supports Pandas dataframes, saved as pickles, as input. Therefore, most data needs to go through some kind of pre-processing before Baler can work on that data.

To run the pre-processing for this specific example dataset, run:
```console
poetry run python baler --project=example --mode=preprocessing
```
The pre-processing was done using the script found at `./projects/example/example_preprocessing.py`

## Training
To train the autoencoder to compress your data, you run the following command. The config file defines the path of the input data, the number of epochs, and all the other parameters.
```console
poetry run python baler --project=example --mode=train
```

## Compressing
To use the derived model for compression, you can now choose ``--mode=compress``, which can be run as
```console
poetry run python baler --project=example --mode=compress
```
This will output a compressed file called "compressed.pickle", and this is the latent space representation of the input dataset. It will also output cleandata_pre_comp.pickle which is just a copy of the original data.

## Decompressing
To decompress the compressed file, we choose ``--mode=decompress`` and run:
```console
poetry run python baler --project=example --mode=decompress
```
This will output ``./projects/example/decompressed_output/decompressed.pickle``. To double-check the file sizes, we can run
```console
poetry run python baler --project=example --mode=info
```
which will print the file sizes of the data we’re compressing, the compressed dataset & the decompressed dataset.

## Evaluating Performance
To evaluate the performance of our compression, we compare our data before the compression to the data after compression+decompression. We do this by plotting the variable distribution before and after, as well as the response distribution R=(before-after)/before.

To run the standard evaluation, we use the following command to generate a .pdf document under ``./projects/example/plotting/evaluation.pdf``

```console
poetry run python baler --project=example --mode=evaluate
```

## Custom analysis
A lot of scientists interested in using Baler wants to see how compression affects their measurements. Therefore, Baler supports users running their own custom analysis as part of Baler to compare their measurements before and after compression.

Custom analyses are defined under ``./projects/example/example_analysis.py``. In our example, the analysis fits the particle mass distribution, and compares the mass derived from the fit before and after compression. You can run the custom analysis using

```console
poetry run python baler --project=example --mode=analysis
```

The results of the analysis comparison is shown in ``./projects/example/plotting/analysis.pdf``

# Your Task  <a name="task"></a>
## Improve Baler for High Energy Particle Physics (HEP) Data
Your task in this application is to minimize the difference between the mass calculated before and after compression (this value is found in ./projects/example/plotting/analysis.pdf after running the analysis). You will do this by making improvements to the source code of Baler. **You are not allowed to make changes to the analysis script.**

The most probable places for improvements are in:
- Autoencoder model: ``baler/baler/modules/models.py``
- Data Normalization: ``baler/baler/modules/data_processing.py``
- Training Procedure: ``baler/baler/modules/training.py``
- Training Utilities (Loss function, early stopping, etc.): ``baler/baler/modules/utils.py``

## Run Baler on a Dataset of your choice
Baler works on a lot of different data, all the way from particle physics and computational fluid dynamics to life sciences on .csv files. Create or copy an analysis from a dataset of your choice and present the analysis before/after compression. No need to optimze the training!

# Rules <a name="rules"></a>
- You are not allowed to make changes to the analysis script. You can make a copy of it if you wish to have it in another project directory, but the code for the analysis needs to be the same as in the example
- You are not allowed to train for more epochs than 100
- You are not allowed to use a batch size larger than 512

# Deliverables <a name="deliverables"></a>
In response to your application email, you received a link to a Google classroom. This google classroom has an assignement with details and a Google form. Your main deliverable is a link to your fork of this reository. You will provide us the link via the Google form.

The other four deliverables listed below you will submit by puttng them as ".pdf" files in the `GSoC-application-baler/deliverables` directory of your fork.

The deadline for your work is **20th of March 15:00 Central European Standard Time**

## Present Improvements for HEP Data
After you are satisfied with the your improvements you will make a "Power Point" style presentation of maximum 5 slides, which present:
- Your improvements: Why and how they were implemented
- Results: Show your results, at least by showing the output of the evaluation and analysis steps
- Discussion
  - Discuss the results
  - Why your improvements work?
  - What could be improved further
  - What is better, a good overall evalation or a good analysis result?
  - Can you think of any fundamental flaws with Baler? (We already know many!)

## Present results from your own analysis and dataset
Once you have performed a simple analysis before and after compression on a dataset of your choice you will make a "Power Point" style presentation of maximum 5 slides, which present:
- The dataset
- The analysis
- Possible improvements
- How you made it work with Baler
- The impact on society this could have

## Your Resume/CV
Put acopy of you resume/CV in the deliverables diectory of your fork.

## Statement of motivation
A short text describing your motivation for working on this project with us

# Assessment
Your performance will be assessed by the improvements and implementations you are able to achieve. But equally important is your ability to communicate your work, results, and ability to discuss. The latter is very important because the Baler collaboration is an international collaboration working together remotely most of the time.
