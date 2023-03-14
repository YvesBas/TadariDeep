library(data.table)

DirBN="C:/Users/yvesb/Downloads/GSampleV3_Part1/bnauda_p1_auda"
Dir="C:/Users/yvesb/Downloads/GSampleV3_Part1/PA_230102"
#Dir="C:/Users/yvesb/Downloads/SampleV2_P2H2/BN"
TableSpeciesSel=fread("species_2022-12-01_sel.csv")
TableSpeciesSel=NA
FilterPeriod="Night"
FilterOutConf=T
DataPeriod=fread("C:/Users/yvesb/Documents/Tadarida/Vigie-Chiro_scripts/Vigie-Chiro_scripts/SummaryPeriod.csv")
DataConf=fread("C:/Users/yvesb/Documents/Tadarida/Vigie-Chiro_scripts/Vigie-Chiro_scripts/SummaryConfidential.csv")


Files=list.files(Dir,full.names=T)
#,pattern="tdauda")
Sub=substr(basename(Files),1,24)

if(FilterOutConf){
  ListOpen=subset(DataConf$ListCarre,DataConf$Conf==0)
  ListOpen=subset(ListOpen,ListOpen!="")
  ListOpen=subset(ListOpen,!grepl("irods",ListOpen))
  FilesFiltered=vector()
  for (h in 1:length(ListOpen)){
    Fileh=subset(Files,grepl(paste0("Car",ListOpen[h]),basename(Files)))
    FilesFiltered=c(FilesFiltered,Fileh)
  }
FilesFU=unique(FilesFiltered)  
Files=FilesFU
}

if(!is.na(FilterPeriod)){
  ListPeriod=subset(DataPeriod$ListPref,DataPeriod$Nocturnal==FilterPeriod)
  FilesFiltered=vector()
  for (h in 1:length(ListPeriod)){
    Fileh=subset(Files,grepl(ListPeriod[h],basename(Files)))
    FilesFiltered=c(FilesFiltered,Fileh)
  }
  FilesFU=unique(FilesFiltered)  
  Files=FilesFU
}




datalist=list()
for (i in 1:length(Files)){
  test=fread(Files[i])
  if(nrow(test)>0){
    datalist[[i]]=test
    
    datalist[[i]]$file=basename(Files[i])
    datalist[[i]]$sub=Sub[i]
  }
}
dataAll=rbindlist(datalist)



Files=list.files(DirBN,full.names=T)
#,pattern="tdauda")
Sub=substr(basename(Files),1,24)

datalist=list()
for (i in 1:length(Files)){
  test=fread(Files[i])
  if(nrow(test)>0){
    datalist[[i]]=test
    
    datalist[[i]]$file=basename(Files[i])
    datalist[[i]]$sub=Sub[i]
    
  }
}
dataBN=rbindlist(datalist)


NperFile=aggregate(dataAll$V1,by=list(dataAll$sub),length)

FileOrder=NperFile$Group.1[order(NperFile$x)]


#if(grepl(" - ",dataAll$V3[1])){
#  if(tstrsplit(dataAll$V3,split=" ")[[2]][1]=="-"){


dataBN$species=substr(tstrsplit(dataBN$V3,split=" ")[[1]],1,6)
table(dataBN$species) 
dataBN$confiance=as.numeric(tstrsplit(dataBN$V3,split=" ")[[3]])/100
hist(dataBN$confiance)  
#  dataBN$frequence=0
#}else{
dataAll$species=tstrsplit(dataAll$V3,split=" ")[[1]]
table(dataAll$species)
dataAll$confiance=as.numeric(tstrsplit(dataAll$V3,split=" ")[[2]])/100
hist(dataAll$confiance)
dataAll$frequence=as.numeric(tstrsplit(dataAll$V3,split=" ")[[4]])
hist(dataAll$frequence)

test=as.data.frame(table(dataAll$species))
scoremax=aggregate(dataAll$confiance,by=list(dataAll$species),max)
test=merge(test,scoremax,by.x="Var1",by.y="Group.1")

fwrite(test,paste0("species_",Sys.Date(),".csv"),sep=";")
ClassConf=round(dataAll$confiance*10)
table(ClassConf)

scoremax2=aggregate(dataAll$confiance,by=list(dataAll$file,dataAll$species),max)
fwrite(scoremax2,paste0("scores_",Sys.Date(),".csv"),sep=";")


#boxplot(dataAll$V4~dataAll$species,las=2)
#table(dataAll$species,ClassConf)[100:124,]

#
Synthesis=aggregate(dataAll$file,by=list(dataAll$species),length)
Synthesis2=aggregate(dataAll$confiance,by=list(dataAll$species),median)
#Synthesis3=aggregate(dataAll$frequence,by=list(dataAll$species),median)

Synthesis$confiance=Synthesis2$x
#Synthesis$frequence=Synthesis3$x

fwrite(Synthesis,paste0(Dir,".csv"),sep=";")

if(is.na(TableSpeciesSel)){
  SpeciesMax=Synthesis$Group.1
  
}else{
  SpeciesMax=subset(TableSpeciesSel$Var1,TableSpeciesSel$sel=="x")
  
}

dataAll$Dur=dataAll$V2-dataAll$V1
AggPerFile=aggregate(dataAll$V1,by=c(list(dataAll$sub),list(dataAll$species)),length)
AggPerFile2=aggregate(dataAll$confiance,by=c(list(dataAll$sub),list(dataAll$species)),max)
AggPerFile3=aggregate(dataAll$confiance,by=c(list(dataAll$sub),list(dataAll$species)),median)
AggPerFile4=aggregate(dataAll$Dur,by=c(list(dataAll$sub),list(dataAll$species)),mean)
AggPerFile5=aggregate(dataAll$frequence,by=c(list(dataAll$sub),list(dataAll$species)),median)
AggPerFile$ScoreMax=AggPerFile2$x
AggPerFile$ScoreMed=AggPerFile3$x
AggPerFile$Durmean=AggPerFile4$x
AggPerFile$FreqMed=AggPerFile5$x
AggTD=AggPerFile


AggPerFile=aggregate(dataBN$V1,by=c(list(dataBN$sub),list(dataBN$species)),length)
AggPerFile2=aggregate(dataBN$confiance,by=c(list(dataBN$sub),list(dataBN$species)),max)
AggPerFile3=aggregate(dataBN$confiance,by=c(list(dataBN$sub),list(dataBN$species)),median)
AggPerFile$ScoreMax_BN=AggPerFile2$x
AggPerFile$ScoreMed_BN=AggPerFile3$x
names(AggPerFile)[3]="N_BN"
AggAll=merge(AggTD,AggPerFile,by=c("Group.1","Group.2"),all.x=T,all.y=T)
AggAll[is.na(AggAll)]=0

testO=match(AggAll$Group.1,FileOrder)
AggAll=AggAll[order(testO),]

fwrite(AggAll,paste0(Dir,"_AggAll.csv"),sep=";")
