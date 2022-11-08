TrainingSetDir=choose.dir()
SourceDir=choose.dir()

SpecDir=paste0(SourceDir,"/oiseaux1")

dir.create(SpecDir)

Spectrograms=list.files(TrainingSetDir,pattern=".jpg$",recursive=T,full.names=T)
Spectrograms=subset(Spectrograms,grepl("/ima2/",Spectrograms))


SpecInfos=tstrsplit(Spectrograms,split="/")
Species=SpecInfos[[length(SpecInfos)-2]]
print(table(Species))


SortedSpectrograms=paste0(SpecDir,"/",Species,"/",Species,"--",Species,"--",basename(Spectrograms))

DirsToCreate=unique(dirname(SortedSpectrograms))

for (i in 1:length(DirsToCreate)){
  dir.create(DirsToCreate[i])
  
}

file.copy(from=Spectrograms,to=SortedSpectrograms)
