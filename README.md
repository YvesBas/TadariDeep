# TadariDeep
 
 
04/04/2022: as this project is far from mature and will undergo further development, this documentation is very brief and drafty. Please contact us if you need further information

TadariDeep is an adaptation of the Tadarida toolkit where Tadarida-C is replaced by a deep learning process. This intends to improve Tadarida performance on the much more diverse vocalisations in the audible frequencies: birds, amphibians, insects, etc
 
 see a [1st draft of documentation here](https://docs.google.com/document/d/1IPfZtVYpi79kIjWRiagPAldr2eaenAE7EPsy6Zwp3Nw/edit?usp=sharing) 
 
For french speakers and end users of deep_predict (=getting predictions from new sounds and pre-built classifiers), there's [a tutorial here](https://docs.google.com/document/d/18JeXMPpvNKSvAsbN7jZJLUDto0TKTYmlVDxGnXkRKg8/edit?usp=sharing) with a little more info about Python install

the folder python_sources/weights contains 2 experimental classifiers:

- 7680-041 : targeting 13 french common urban bird species (moderate performance)

- 11240-085 : targeting common nocturnal french birds (both breeding and migrants), with a rather good performance but still highly perfectible! Probably very bad on amphibians and crickets on which we are waiting for labelled files!

You cans also download a classifier integrating ground crickets and frogs that we are currently testing (too big for Github): https://drive.google.com/file/d/1SE1AeFYsygSlvFpusByke3N9HmSNbqUn/view?usp=sharing

There were not properly benchmarked against Birdnet but on a few tests, we found that Birdnet performed better on high SNR songs, but less on calls or low SNR songs.

Training data used are mostly Xeno-Canto for birds, MNHN sound library (for crickets and frogs), and the remaining sounds labelled by Stuart Newson (BTO) and me through Tadarida-L

Current authors: Didier Bas (main developper) and Yves Bas (mainly involved in design and testing)
