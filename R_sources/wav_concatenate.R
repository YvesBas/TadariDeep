library(tuneR)
library(data.table)

DirW="C:/Users/yvesb/Downloads/Nilsson2"
DirOut="C:/Users/yvesb/Downloads/Nilsson2Conc"
LW=list.files(DirW,pattern=".wav$",full.names=T)
RatioCorrectionTemps=10
GroupSize=100

dir.create(DirOut)

Pref=substr(basename(LW),1,24)

ListPref=unique(Pref)



for (i in 1:length(ListPref)){
  print(i)
  print(Sys.time())
  Wi=subset(LW,Pref==ListPref[i])
  
  for (j in 1:ceiling(length(Wi)/GroupSize)){
  Wij=Wi[(1+(j-1)*GroupSize):min(length(Wi),j*GroupSize)]
    
    Wlist=list()
    Length=vector()
    SR=vector()
    for (h in 1:length(Wij)){
    #for (i in 1:length(LW)){
    Wlist[[h]]=readWave(Wij[h])
    #print(class(Wlist[[i]]))
    Length[h]=length(Wlist[[h]])
    SR[h]=Wlist[[h]]@samp.rate
  }
    Wbig=do.call(tuneR::bind,Wlist)
    Wbig@samp.rate=Wbig@samp.rate*RatioCorrectionTemps
    writeWave(Wbig,filename=paste0(DirOut,"/",basename(Wij[1])),extensible=F) #ecrit le nouveau fichier wave
  Ancillary=data.frame(Length,SR)
    fwrite(Ancillary,paste0(DirOut,"/"
                                     ,gsub(".wav","_chunksize.csv"
                                           ,basename(Wij[1])))
           ,sep=";")
  }
}
