# TadariDeep
 
 see a [1st draft of documentation here](https://docs.google.com/document/d/1IPfZtVYpi79kIjWRiagPAldr2eaenAE7EPsy6Zwp3Nw/edit?usp=sharing) 
 
For french speakers and end users of deep_predict (=getting predictions from new sounds and pre-built classifiers), there's [a tutorial here](https://docs.google.com/document/d/18JeXMPpvNKSvAsbN7jZJLUDto0TKTYmlVDxGnXkRKg8/edit?usp=sharing) with a little more info about Python install

the folder python_sources/weights contains 2 experimental classifiers:

- 7680-041 : targeting 13 french common urban bird species (moderate performance)

- 11240-085 : targeting common nocturnal french birds (both breeding and migrants), with a rather good performance but still highly perfectible! Noticeably concerning amphibians and crickets

There were not properly benchmarked agains Birdnet but on a few tests, we found that Birdnet performed better on high SNR songs, but less on calls or low SNR songs.

