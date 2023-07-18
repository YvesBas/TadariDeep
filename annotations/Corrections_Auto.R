library(readxl)
library(data.table)
library(seewave)
library(dplyr)

can_convert_to_numeric <- function(x) {
  all(grepl('^(?=.)([+-]?([0-9]*)(\\.([0-9]+))?)$', x, perl = TRUE))  
}

#DirValid="C:/Users/yvesb/Downloads/"
#FValid="C:/Users/yvesb/Documents/Tadarida/Pablo/annotations230222/PourValidation230317.xlsx"
FValid="C:/Users/yvesb/Downloads/Validations_audible (9).xlsx"
NbOnglets=5
DirMarkers="C:/Users/yvesb/Documents/Tadarida/Elodie"
# DirMarkers="C:/Users/yvesb/Documents/Tadarida/Pablo"
# DirMarkers="F:/PSIBIOM/Enregistrementsopportunistes"
HierarchieValid=c("avis_Stanislas_formate","avis_Stanislas","avis_Lucas","avis_Yves")
#HierarchieValid=c("avis_Lucas","avis_Yves")
#HierarchieValid=c("avis_Yves")

DirOut="C:/Users/yvesb/Documents/Tadarida/Annotations_Corrigees"


# Fvalids=list.files(DirValid,pattern="Validations_audible",full.names=T,recursive=T)
# Fvalidi=file.info(Fvalids)
# Fvalidi=Fvalidi[order(Fvalidi$mtime),]
# FValid=row.names(Fvalidi)[nrow(Fvalidi)]

dir.create(DirOut)
DirOut2=paste0(DirOut,"/",basename(DirMarkers))
dir.create(DirOut2)


ValidList=list()
for (i in 1:NbOnglets){
  ValidList[[i]]=read_excel(FValid,sheet=i)
  ValidList[[i]]$date=as.character(ValidList[[i]]$date)
  ValidList[[i]]$heure=as.character(ValidList[[i]]$heure)
}
ValidAll=rbindlist(ValidList,fill=T,use.names=T)

ColHierarchie=match(HierarchieValid,names(ValidAll))
if(sum(is.na(ColHierarchie))>0){stop("column missing")}

#summary(is.na(as.numeric(ValidAll$debut_origine)))
ValidAll$temps_debut=as.numeric(ValidAll$temps_debut)
ValidAll$temps_fin=as.numeric(ValidAll$temps_fin)
ValidAll$debut_origine=as.numeric(ValidAll$debut_origine)
ValidAll$freq_min=as.numeric(ValidAll$freq_min)
ValidAll$freq_max=as.numeric(ValidAll$freq_max)


ListMarkersCorrected=unique(ValidAll$fichier_origine)

ListMarkersExisting=list.files(DirMarkers,pattern=".txt$",recursive=T,full.names=T)

for (j in 1:length(ListMarkersCorrected)){
  Validj=subset(ValidAll,ValidAll$fichier_origine==ListMarkersCorrected[j])
  FMarkersj=subset(ListMarkersExisting
                   ,basename(ListMarkersExisting)==paste0(ListMarkersCorrected[j],".txt"))
  if(length(FMarkersj)>1){
    #stop("check doublons")
    FMarkersj=subset(FMarkersj,basename(dirname(FMarkersj))=="corrections")
  }
  if(length(FMarkersj)>1){
    stop("check doublons 2")
  }
  if(length(FMarkersj)==0){
    #skip
  }else{
    
    Markersj=read.audacity(FMarkersj)
    if("f1" %in% names(Markersj)){
    for (k in 1:nrow(Validj)){
          WhereIsMarkerK=(near(Markersj$t1,Validj$temps_debut[k]+Validj$debut_origine[k]
                           ,tol=1e-2)
                      # &near(Markersj$t2,Validj$temps_fin[k]+Validj$debut_origine[k]
                      #      ,tol=1e-4))
                      &near(Markersj$f1,Validj$freq_min[k],tol=1e-2))
      #&near(Markersj$f2,Validj$freq_max[k],tol=1e-4))
      if(sum(WhereIsMarkerK)==0){
        #stop("mismatch")
        WhereIsMarkerK=(#near(Markersj$t1,Validj$temps_debut[k]+Validj$debut_origine[k]
                         #    ,tol=1e-2)
                         #&
          near(Markersj$t2,Validj$temps_fin[k]+Validj$debut_origine[k]
                              ,tol=1e-4)#)
                        &near(Markersj$f1,Validj$freq_min[k],tol=1e-2))
        
        if(sum(WhereIsMarkerK)==0){stop("mismatch")}
          
        
        }
      if(sum(WhereIsMarkerK)>1){stop("doublon match")}
      
      PositionMarkerK=which.max(WhereIsMarkerK)
      
      Correctionl=F
      for (l in 1:length(ColHierarchie)){
        if(!Correctionl){
          NewLabell=as.data.frame(Validj)[k,ColHierarchie[l]]
          if(!is.na(NewLabell)){
            #stop()
            LastCharl=substr(NewLabell,nchar(NewLabell),nchar(NewLabell))
            BLastCharl=substr(NewLabell,nchar(NewLabell)-1,nchar(NewLabell)-1)
            #cas ou la confiance est renseignee dans la validation
            if(can_convert_to_numeric(LastCharl)&BLastCharl==" ")
            {
              Markersj[PositionMarkerK,]$label=NewLabell
            }else{
              #stop("coder cas ou la confiance n'est pas renseignee dans la validation")
              
              Labelo=Markersj[PositionMarkerK,]$label
              LastCharo=substr(Labelo,nchar(Labelo),nchar(Labelo))
              BLastCharo=substr(Labelo,nchar(Labelo)-1,nchar(Labelo)-1)
              #cas où il y avait la confiance à l'origine
              if(can_convert_to_numeric(LastCharo)&BLastCharo==" ")
              {
                if(substr(Labelo,nchar(Labelo)-5,nchar(Labelo)-5)==" ")
                {
                  Codeso=substr(Labelo,nchar(Labelo)-4,nchar(Labelo))
                  
                }else{
                  Codeso=substr(Labelo,nchar(Labelo)-2,nchar(Labelo))
                  
                }
                #cas où il y a doute dans la validation
                if(LastCharl=="?"){
                  Codesn=paste0("0",substr(Codeso,2,nchar(Codeso)))
                  NewLabell=paste0(gsub("\\?","",NewLabell)," ",Codesn)
                }else{
                  #stop("test")
                  Codesn=paste0("1",substr(Codeso,2,nchar(Codeso)))
                  NewLabell=paste0(NewLabell," ",Codesn)
                }
                
                
              }else{
                #stop("coder cas ou la confiance etait pas renseignee a l origine")
                if(LastCharl=="?"){
                  NewLabell=paste0(gsub("\\?","",NewLabell)," 0 2 1")
                }else{
                  NewLabell=paste0(NewLabell," 1 2 1")
                }
                
              }
              
              Markersj[PositionMarkerK,]$label=NewLabell
              
            }
            print(paste(j,NewLabell))
            
            Correctionl=T
            Markersj$file=NULL
            write.audacity(Markersj,paste0(DirOut2,"/",ListMarkersCorrected[j],".txt"))
            
          }
        }
        
      }
      }      
      
    }else{
      print("markers without frequency info")
    }
    
    
  }
}
