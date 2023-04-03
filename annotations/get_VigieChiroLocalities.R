library(mongolite)
library(data.table)
#library(beepr)
library(lubridate)


mongo=fread("C:/Users/yvesb/Documents/Tadarida/Vigie-Chiro_scripts/Vigie-Chiro_scripts/mongos.txt"
            ,sep="$",h=F)
test=F #T si base de test, F si base de prod
FLabels="C:/Users/yvesb/Documents/Tadarida/Elodie/Echantillon1&2_Sonothèque/annotationsToBeChecked.csv"
FLabels="D:/PSIBIOM/annotationsToBeChecked.csv"



Labels=fread(FLabels)



if(test){
  connection_string=mongo$V1[2]
}else{
  connection_string=mongo$V1[1]
}


sites = mongo(collection="sites", db="vigiechiro", url=connection_string)
#participations = mongo(collection="participations", db="vigiechiro", url=connection_string)
#users = mongo(collection="utilisateurs", db="vigiechiro", url=connection_string)
#listpart=fread("ccsps220906.csv")
#test=participations$export()
listpart=NA
#users = mongo(collection="utilisateurs", db="vigiechiro", url=connection_string)
NbJourEC=4


Sys.time()
#alldatapart<-participations$find(fields='{}')
Sys.time()
alldatasites <- sites$find(fields='{}')
Sys.time() #~1sec / 1e3 sites
#alldataobs <- users$find(fields='{}')
Sys.time()

Labels$coordonnees=""
Labels$date=""
Labels$heure=""
for (i in 1:nrow(Labels)){
  if(substr(Labels$file[i],1,3)=="Car"){
  NumCi=substr(Labels$file[i],4,9)
  sitesi=subset(alldatasites
                ,alldatasites$titre==paste0("Vigiechiro - Point Fixe-"
                                            ,NumCi))
  pointi=tstrsplit(Labels$file[i],split="-")[[4]]
  coordonneesi=subset(sitesi$localites[[1]]$geometries,sitesi$localites[[1]]$nom==pointi)
  
  if(nrow(coordonneesi)==1){
    Labels$coordonnees[i]=paste0(coordonneesi$geometries[[1]]$coordinates[[1]][1]
                                 ,",",coordonneesi$geometries[[1]]$coordinates[[1]][2])
  }
  
  Infoi=tstrsplit(Labels$file[i],split="_")
  Date0=Infoi[[length(Infoi)-2]]
  Datei=ymd(substr(Date0,nchar(Date0)-7,nchar(Date0)))
  #print(Datei)
  Labels$date[i]=Datei
  Heure0=Infoi[[length(Infoi)-1]]
  heurei=paste0(substr(Heure0,1,2),":",substr(Heure0,3,4))
  Labels$heure[i]=heurei
  }else{
    Infoi=tstrsplit(Labels$file[i],split="_")
    Date0=Infoi[[length(Infoi)]]
    Datei=ymd(substr(Date0,nchar(Date0)-7,nchar(Date0)))
    #print(Datei)
    Labels$date[i]=Datei
    Labels$heure[i]=""
    Labels$coordonnees[i]=""
    
  }
}

Labels$nom_fichier=Labels$fileNew
Labels$identification_origine=Labels$label
#Labels$'identification_expert-e'=""
#Labels$'confiance_expert-e'=""
Labels$'avis_expert-e1'=""
Labels$'avis_expert-e2'=""
Labels$'avis_expert-e3'=""
# Labels$temps_debut=round(Labels$initial_time,1)
# Labels$temps_fin=round(Labels$final_time,1)
# Labels$freq_min=round(Labels$min_frequency)
# Labels$freq_max=round(Labels$max_frequency)
Labels$temps_debut=Labels$initial_time-Labels$debut_origine
Labels$temps_fin=Labels$final_time-Labels$debut_origine
Labels$freq_min=Labels$min_frequency
Labels$freq_max=Labels$max_frequency
#coord
Labels$date=as.Date(as.numeric(Labels$date),origin="1970-01-01")
#heure
Labels$fichier_origine=Labels$file
#debut_origine


LabelsToBeChecked=subset(Labels,select=c("nom_fichier","identification_origine"
                                         ,"avis_expert-e1","avis_expert-e2","avis_expert-e3"
                                         ,"temps_debut","temps_fin","freq_min","freq_max"
                                         ,"coordonnees","date","heure","fichier_origine"
                                         ,"debut_origine"))

annotationsI_prioritized=LabelsToBeChecked
annotations_types=unique(data.table(cbind(annotationsI_prioritized$fichier_origine
                                          ,annotationsI_prioritized$identification_origine)))

annotationsI_prioritized$prioritaire=""
LabelsPrioritized=annotationsI_prioritized[0,]
for (i in 1:nrow(annotations_types)){
  ai=subset(annotationsI_prioritized
            ,(annotationsI_prioritized$fichier_origine==annotations_types$V1[i])
            &(annotationsI_prioritized$identification_origine==annotations_types$V2[i]))
  # if(nrow(ai)>1){
  duree=ai$temps_fin-ai$temps_debut
  ai=ai[order(duree,decreasing=T),]
  ai$prioritaire=c("oui",rep("non",nrow(ai)-1))
  # aimax=ai[1,]
  # aimax$prioritaire="oui"
  # Fminj=aimax$freq_min
  # Fmaxj=aimax$freq_max
  # 
  #ai_others=subset(ai,duree<max(duree))
  
  # }else{
  
  #stop()
  
  LabelsPrioritized=rbind(LabelsPrioritized,ai)
  #
}
table(LabelsPrioritized$prioritaire)

fwrite(LabelsPrioritized,paste0(dirname(FLabels),"/PourValidation",Sys.Date(),".csv"),sep=";")
