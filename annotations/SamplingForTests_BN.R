library(data.table)

Dir="C:/Users/yvesb/Downloads/GSampleV3_Part1/bnauda_p1_auda"
Dir="C:/Users/yvesb/Documents/Tadarida/Dbas_deepL/SampleV3/tdaudatxt_GSampleV3_Part1_premier_test"

#Dir="C:/Users/yvesb/Downloads/SampleV2_P2H2/BN"
TableSpeciesSel=fread("speciesBN_2022-09-17_sel.csv")
TableSpeciesSel=NA
RemainDir="C:/Users/yvesb/Downloads/GSampleV3_Part1/PA_221107"
#RemainDir=NA



NperSlot=10

Files=list.files(Dir,full.names=T)
#,pattern="tdauda")
Sub=substr(basename(Files),1,24)

if(!is.na(RemainDir)){
  FilesR=list.files(RemainDir,full.names=T)
  SubF=substr(basename(FilesR),1,24)
  Files=subset(Files,Sub %in% SubF)
  
}



datalist=list()
for (i in 1:length(Files)){
  test=fread(Files[i])
  if(nrow(test)>0){
    datalist[[i]]=test
    
    datalist[[i]]$file=basename(Files[i])
  }
}
dataAll=rbindlist(datalist)

if(grepl(" - ",dataAll$V3[1])){
  dataAll$species=tstrsplit(dataAll$V3,split=" ")[[1]]
  dataAll$confiance=as.numeric(tstrsplit(dataAll$V3,split=" ")[[2]])/100
hist(dataAll$confiance)
    dataAll$frequence=as.numeric(tstrsplit(dataAll$V3,split=" ")[[4]])
    hist(dataAll$frequence)
}else{
  dataAll$species=dataAll$V3
  dataAll$confiance=dataAll$V4
}

table(dataAll$species)
test=as.data.frame(table(dataAll$species))
fwrite(test,paste0("species_",Sys.Date(),".csv"),sep=";")
ClassConf=round(dataAll$confiance*10)
table(ClassConf)
#boxplot(dataAll$V4~dataAll$species,las=2)
#table(dataAll$species,ClassConf)[100:124,]

#
Synthesis=aggregate(dataAll$file,by=list(dataAll$species),length)
Synthesis2=aggregate(dataAll$confiance,by=list(dataAll$species),median)
#Synthesis3=aggregate(dataAll$frequence,by=list(dataAll$species),median)

Synthesis$confiance=Synthesis2$x
#Synthesis$frequence=Synthesis3$x

fwrite(Synthesis,paste0(Dir,".csv"),sep=";")

dataAll$confianceR=rank(dataAll$confiance)
#dataAll$confianceClass=floor(dataAll$confianceR*10/max(dataAll$confianceR))
dataAll$confianceClass=floor(dataAll$confiance*10)

table(dataAll$confianceClass)

dataNum=aggregate(dataAll$V1,by=list(dataAll$file),length)
dataNum$Rank=rank(dataNum$x)

if(is.na(TableSpeciesSel)){
  SpeciesMax=Synthesis$Group.1
  
}else{
  SpeciesMax=subset(TableSpeciesSel$Var1,TableSpeciesSel$Sel=="x")
  
}
SpeciesSel=vector()
DirSel=vector()
SpeciesSel=vector()
Ndir=0
i=0
while((length(Ndir)<(NperSlot/2))&(i<(length(SpeciesMax)*2))){
  i=i+1
  Parcimi=sample.int(max(dataNum$Rank),1)
  SiteP=subset(dataNum$Group.1,dataNum$Rank<=Parcimi)
  datai=subset(dataAll,dataAll$file %in% SiteP)
  table(datai$species)
  SpeciesP=unique(datai$species)
  SpeciesPM=subset(SpeciesP,SpeciesP %in% SpeciesMax)
  if(length(SpeciesPM)>0){
    Speciesi=sample(SpeciesPM,1)
    print(Speciesi)
    datai=subset(dataAll,dataAll$species==Speciesi)
    if(nrow(datai)>0){
      SpeciesSel=c(SpeciesSel,Speciesi)
      
      dataimax=subset(datai,datai$confiance==max(datai$confiance))
      DirSeli=sample(unique(dataimax$file),1)
      print(DirSeli)
      DirSel=c(DirSel,DirSeli)
      Ndir=unique(DirSel)
      print(length(Ndir))
    }
  }
}
DataMax=data.frame(DirSel,SpeciesSel,type="max")


type=rep("max",nrow(DataMax))
while(length(Ndir)<(NperSlot)){
  Parcimi=sample.int(max(dataNum$Rank),1)
  SiteP=subset(dataNum$Group.1,dataNum$Rank<=Parcimi)
  datai=subset(dataAll,dataAll$file %in% SiteP)
  table(datai$species)
  SpeciesP=unique(datai$species)
  SpeciesPM=subset(SpeciesP,SpeciesP %in% SpeciesMax)
  if(length(SpeciesPM)>0){
    Speciesi=sample(SpeciesPM,1)
    print(Speciesi)
  datai=subset(dataAll,dataAll$species==Speciesi)
  Classi=sample(c(0:10),1)
  print(Classi)
  dataic=subset(datai,datai$confianceClass==Classi)
  if(nrow(dataic)>0){
    #stop()
    SpeciesSel=c(SpeciesSel,Speciesi)
    type=c(type,Classi)
    DirSeli=sample(unique(dataic$file),1)
    print(DirSeli)
    DirSel=c(DirSel,DirSeli)
    Ndir=unique(DirSel)
    print(length(Ndir))
  }
  }
}
dataClass=data.frame(SpeciesSel,DirSel,type)
dataClass=dataClass[order(dataClass$DirSel),]
length(unique(DirSel))
fwrite(dataClass,paste0(Dir,"_",Sys.Date(),"_selected.csv"),sep=";")


table(dataAll$species)
print(head(table(dataAll$species)[order(table(dataAll$species),decreasing=T)],20))
