library(data.table)
library(seewave)

Dir="C:/Users/yvesb/Downloads/GSampleV3_Part1/PourElodie230102"
Dir="C:/Users/yvesb/Documents/Tadarida/Pablo/annotations"

FilesWav=list.files(Dir,pattern=".wav$",full.names=T)

MarkerPsibiomFormat=gsub(".wav",".txt",FilesWav)
#MarkerTadariDeep=list.files(Dir,pattern="_tdauda.txt$",full.names=T)

Datalist=list()
for (i in 1:length(MarkerPsibiomFormat)){
  if(file.exists(MarkerPsibiomFormat[i])){
    Datai=read.audacity(MarkerPsibiomFormat[i])
    hist(Datai$f1)
    hist(Datai$f2)
    LabelInfo=tstrsplit(Datai$label,split=" ")
    if(length(LabelInfo)<2){
      Datai$class=LabelInfo[[1]]
        Datai$confiance=NA
        Datai$overlap=NA
        
    }else{
      
      Datai$class=ifelse(is.na(LabelInfo[[2]]),LabelInfo[[1]],paste(LabelInfo[[1]],LabelInfo[[2]]))
      if(length(LabelInfo)<3){
        Datai$confiance=NA
        Datai$overlap=NA
      }else{
        Datai$confiance=LabelInfo[[3]]
        if(length(LabelInfo)>4){
          Datai$overlap=ifelse(is.na(LabelInfo[[5]]),LabelInfo[[4]],LabelInfo[[5]])
        }else{
          if(length(LabelInfo)>3){
            
          Datai$overlap=LabelInfo[[4]]
          }else{
            Datai$overlap=NA
            
          }
        }
      }
    }
    Datalist[[i]]=Datai
  }
}
DataAll=rbindlist(Datalist)
table(DataAll$class)
table(DataAll$confiance)
DataToCheck1=subset(DataAll,DataAll$confiance==0)
DataToCheck2=subset(DataAll,DataAll$class %in% c("Non identifié","Anatidae","Non identifie"))
DataToCheck=rbind(DataToCheck1,DataToCheck2)
if(nrow(DataToCheck)>0){fwrite(DataToCheck,paste0("DataToCheck_",Sys.Date(),".csv"),sep=";")}
table(DataAll$overlap)

fwrite(DataToCheck,paste0(Dir,"/DataAll.csv"),sep=";")
