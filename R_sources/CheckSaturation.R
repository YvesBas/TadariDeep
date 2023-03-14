library(tuneR)
library(data.table)

DirWav="C:/Users/yvesb/Documents/Tadarida/Dbas_deepL/point du 15 novembre 2022/echantillons lpo/echantillon sons sans prediction sur classe attendue/wav_np1"
DirWav="C:/Users/yvesb/Documents/Tadarida/Dbas_deepL/point du 15 novembre 2022/echantillons lpo/echantillons sons lpo par tranches de confiance/wav_p50-100"

LW=list.files(DirWav,full.names=T)


Saturation=vector()
for (i in 1:length(LW))
{
  Wi=readWave(LW[i])
  Sys.time()
  Saturation1=length(subset(Wi@left,Wi@left==max(Wi@left)))
  Saturation2=length(subset(Wi@left,Wi@left==min(Wi@left)))
  Saturation=c(Saturation,(Saturation1+Saturation2)/length(Wi@left) )      
  Sys.time()
  print(Saturation[i])
}
DataS=data.frame(Fichier=basename(LW),Saturation)
print(mean(Saturation))

fwrite(DataS,paste0(DirWav,"/Saturation.csv"),sep=";")

