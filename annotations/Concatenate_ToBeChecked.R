library(data.table)
library(seewave)
library(tuneR)


DirTBC="C:/Users/yvesb/Documents/Tadarida/Elodie/Echantillon1&2_Sonothèque/ToBeChecked"
DirTBC="D:/PSIBIOM/ToBeChecked"

Silence=1

WTBC=list.files(DirTBC,pattern=".wav$",full.names=T)

WTBC=subset(WTBC,!grepl("WaveConc",basename(WTBC)))

Order=as.integer(gsub(".wav","",tstrsplit(basename(WTBC),split="_")[[2]]))
#order(Order)
WTBC=WTBC[order(Order)]

SR=vector()
for (i in 1:length(WTBC)){
  Time=length(Wall@left)/Wall@samp.rate+Silence
  print(WTBC[i])
  Wi=readWave(WTBC[i])
  print(Wi@samp.rate)
  SR=c(SR,Wi@samp.rate)
}
DataW=data.frame(File=WTBC,SR)
fwrite(DataW,paste0(DirTBC,"/DataW.csv"),sep=";")

WTBCall=WTBC

for (h in 1:length(unique(SR))){
  
  WTBC=subset(WTBCall,SR==unique(SR)[h])
  
  W1=readWave(WTBC[1])
  M1=read.audacity(gsub(".wav",".txt",WTBC[1]))
  
  
  Wall=W1
  Mall=M1
  if(length(WTBC)>1){
    for (i in 2:length(WTBC)){
      Time=length(Wall@left)/Wall@samp.rate+Silence
      print(WTBC[i])
      Wi=readWave(WTBC[i])
      print(Wi@samp.rate)
      Inti=silence(duration=Silence*Wi@samp.rate,samp.rate = Wi@samp.rate,bit=Wi@bit,pcm=T)
      Wlist=list(Wall,Inti,Wi)
      Wall=do.call(tuneR::bind,Wlist)
      
      Mi=read.audacity(gsub(".wav",".txt",WTBC[i]))
      #Time=length(Wall@left)/Wall@samp.rate+Silence
      Mi$t1=Mi$t1+Time
      Mi$t2=Mi$t2+Time
      Mall=rbind(Mall,Mi)
      
    }
  }
  
  writeWave(Wall,filename=paste0(DirTBC,"/WaveConc_",unique(SR)[h],".wav"),extensible=F) #ecrit le nouveau fichier wave
  print(length(Wall@left)/Wall@samp.rate)
  Mall$file=NULL
  write.audacity(Mall,paste0(DirTBC,"/WaveConc_",unique(SR)[h],".txt"))
}
