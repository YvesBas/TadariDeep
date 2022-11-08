TrainingSetDir=choose.dir()


SpecDir=paste0(TrainingSetDir,"/Spectrograms")

dir.create(SpecDir)

Spectrograms=list.files(TrainingSetDir,pattern=".jpg$",recursive=T,full.names=T)
Spectrograms=subset(Spectrograms,grepl("/ima2/",Spectrograms))


SpecInfos=tstrsplit(Spectrograms,split="/")
Species=SpecInfos[[length(SpecInfos)-2]]
print(table(Species))

SortedSpectrograms=paste0(SpecDir,"/",Species,"--",Species,"--",basename(Spectrograms))

file.copy(from=Spectrograms,to=SortedSpectrograms)
