library(data.table)

Dir="C:/Users/yvesb/Documents/Tadarida/Dbas_deepL/SampleV2/Res2H2"

NperSlot=25

Files=list.files(Dir,full.names=T)

datalist=list()
for (i in 1:length(Files)){
  datalist[[i]]=fread(Files[i])
  datalist[[i]]$file=basename(Files[i])
}
dataAll=rbindlist(datalist)

dataAll$species=tstrsplit(dataAll$V3,split=" ")[[1]]
dataAll$confiance=as.numeric(tstrsplit(dataAll$V3,split=" ")[[2]])
dataAll$frequence=as.numeric(tstrsplit(dataAll$V3,split=" ")[[4]])

Synthesis=aggregate(dataAll$file,by=list(dataAll$species),length)
Synthesis2=aggregate(dataAll$confiance,by=list(dataAll$species),median)
Synthesis3=aggregate(dataAll$frequence,by=list(dataAll$species),median)

Synthesis$confiance=Synthesis2$x
Synthesis$frequence=Synthesis3$x

fwrite(Synthesis,paste0(Dir,".csv"),sep=";")

dataAll$confianceR=rank(dataAll$confiance)
dataAll$confianceClass=floor(dataAll$confianceR*10/max(dataAll$confianceR))
table(dataAll$confianceClass)

DirSel=vector()
SpeciesSel=vector()
Ndir=0
while(length(Ndir)<(NperSlot/2)){
  Speciesi=sample(Synthesis$Group.1,1)
  print(Speciesi)
  SpeciesSel=c(SpeciesSel,Speciesi)
  datai=subset(dataAll,dataAll$species==Speciesi)
  dataimax=subset(datai,datai$confiance==max(datai$confiance))
  DirSeli=sample(unique(dataimax$file),1)
  print(DirSeli)
  DirSel=c(DirSel,DirSeli)
  Ndir=unique(DirSel)
  print(length(Ndir))
}
DataMax=data.frame(DirSel,SpeciesSel,type="max")


type=rep("max",nrow(DataMax))
while(length(Ndir)<(NperSlot)){
  Speciesi=sample(Synthesis$Group.1,1)
  print(Speciesi)
  datai=subset(dataAll,dataAll$species==Speciesi)
  Classi=sample(c(0:10),1)
  print(Classi)
  dataic=subset(datai,datai$confianceClass==Classi)
  if(nrow(dataic)>0){
    SpeciesSel=c(SpeciesSel,Speciesi)
    type=c(type,Classi)
    DirSeli=sample(unique(dataic$file),1)
    print(DirSeli)
    DirSel=c(DirSel,DirSeli)
    Ndir=unique(DirSel)
    print(length(Ndir))
  }
}
dataClass=data.frame(SpeciesSel,DirSel,type)
length(unique(DirSel))
fwrite(dataClass,paste0(Dir,"_selected.csv"),sep=";")


table(dataAll$species)
print(head(table(dataAll$species)[order(table(dataAll$species),decreasing=T)],20))
