library(data.table)
library(seewave)

Dir="C:/Users/yvesb/Downloads/GSampleV3_Part1/PourElodie230102"
TolFreq=100
TolTemps=0.001

FilesWav=list.files(Dir,pattern=".wav$",full.names=T)

MarkerPsibiomFormat=gsub(".wav",".txt",FilesWav)
MarkerTadariDeep=list.files(Dir,pattern="_tdauda.txt$",full.names=T)

for (i in 1:length(MarkerPsibiomFormat)){
  if(file.exists(MarkerPsibiomFormat[i])){
    Datai=read.audacity(MarkerPsibiomFormat[i])
    hist(Datai$f1)
    hist(Datai$f2)
    TDi=subset(MarkerTadariDeep,grepl(gsub(".txt","",basename(MarkerPsibiomFormat[i]))
                                      ,basename(MarkerTadariDeep)))
    if(length(TDi)==1){
      DataTDi=fread(TDi)
      DataTDi$FreqMP=as.numeric(tstrsplit(DataTDi$V3,split="- ")[[2]])
      DataNewi=DataTDi
      DataNewi$FreqMP=NULL
      for (j in 1:nrow(DataTDi)){
        Labelsj=subset(Datai,Datai$f1<DataTDi$FreqMP[j]-TolFreq)
        Labelsj=subset(Labelsj,Labelsj$f2>DataTDi$FreqMP[j]+TolFreq)
        Labelsj=subset(Labelsj,Labelsj$t1<DataTDi$V1[j]-TolTemps)
        Labelsj=subset(Labelsj,Labelsj$t2>DataTDi$V2[j]+TolTemps)
        if(nrow(Labelsj)>0){
          if(nrow(Labelsj)>1){
            #stop("multiple")
            DataNewi$V3[j]=paste("multiple",DataTDi$FreqMP[j])
          }else{
            DataNewi$V3[j]=paste(Labelsj$label,DataTDi$FreqMP[j])
          }
          
        }else{
          #stop("none")
          DataNewi$V3[j]=paste("none",DataTDi$FreqMP[j])
        }
        
      }
      #table(DataNewi$V3)
      Namei=gsub("_tdauda.txt","_psibiom.txt",TDi)
      fwrite(DataNewi,Namei,sep="\t")
      
    }
    
  }
}
