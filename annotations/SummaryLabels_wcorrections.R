##### part of this script from DAVID FUNOSAS, thanks to him!! #####

library(dplyr)
library(seewave)
library(tuneR)

Dir= "C:/Users/yvesb/Documents/Tadarida/Elodie"
PrePostTrigger=3 #nombre de secondes à ajouter aux chuncks avant-après

can_convert_to_numeric <- function(x) {
  all(grepl('^(?=.)([+-]?([0-9]*)(\\.([0-9]+))?)$', x, perl = TRUE))  
}

annotations <- data.frame()

files=list.files(Dir,full.names=T,pattern=".txt$",recursive=T)

files=subset(files,!grepl("BirdNET.results",basename(files)))

files=subset(files,!grepl("_tdauda.txt",basename(files)))

files=subset(files,!grepl("sounds_mnhn_so",basename(files)))

files=subset(files,!grepl("_psibiom.txt",basename(files)))

files=subset(files,!basename(dirname(files))=="ToBeChecked")


filesCorr=subset(files,basename(dirname(files))=="corrections")

#replace files by their possible corrected version
files=subset(files,!(basename(files) %in% basename(filesCorr)))
files=c(files,filesCorr)


n_files <- length(files)

for (j in 1:n_files) {
  print(paste0("Processing annotation file ", as.character(j), " out of ", as.character(n_files)))
  file_name <- files[j]
  conn <- file(file_name, open="r")
  linn <-readLines(conn)
  
  # Min and max frequencies are not specified in the two mentioned data sets
  frequencies_annotated <- !(grepl("Juan Gómez-Gómez - Ester Vidaña-Vila - Xavier Sevillano", file_name, fixed = TRUE) | 
                               grepl("NIPS4Bplus - Veronica Morfi + Dan Stowell + Hanna Pamula", file_name, fixed = TRUE))
  
  if (frequencies_annotated) {
    index_list <- seq(1, length(linn), 2)
  } else {
    index_list <- seq(1, length(linn), 1)
  }
  
  for (i in index_list){
    line1 <- linn[i]
    line2 <- linn[i+1]
    
    recording_id <- j
    initial_time <- sub("\t.*", "", line1)
    final_time <- gsub(".*\t(.+)\t.*", "\\1", line1)
    vocalization_type <- "-"
    
    label_parts <- strsplit(sub(".*\t", "", line1), split = " ")[[1]]
    if (length(label_parts) == 4) { #Wild species
      label <- paste(label_parts[1], label_parts[2])
      sound_type <- "Animal"
      
      confidence_level <- label_parts[3]
      code_n_ind <- label_parts[4]
      
    } else if (length(label_parts) == 5) { #Bird or calling frog
      label <- paste(label_parts[1], label_parts[2])
      sound_type <- "Animal"
      
      if (can_convert_to_numeric(label_parts[3])) { #Bird
        confidence_level <- label_parts[3]
        vocalization_type <- case_when(label_parts[4] == "0" ~ "Unknown",
                                       label_parts[4] == "1" ~ "Song",
                                       label_parts[4] == "2" ~ "Call",
                                       label_parts[4] == "3" ~ "Flight call",
                                       label_parts[4] == "4" ~ "Drumming",
                                       label_parts[4] == "5" ~ "Flapping",
                                       TRUE ~ "-")
        
        label <- case_when(label == "Sylvia melanocephala" ~ "Curruca melanocephala",
                           label == "Sylvia undata" ~ "Curruca undata",
                           label == "Sylvia communis" ~ "Curruca communis",
                           label == "Regulus ignicapillus" ~ "Regulus ignicapilla",
                           label == "lullula arborea" ~ "Lullula arborea",
                           label == "Dendrocopos minor" ~ "Dryobates minor",
                           TRUE ~ label)
      } else { #Frog
        confidence_level <- label_parts[4]
        vocalization_type <- "-"
      }
      
      code_n_ind <- label_parts[5]
      
    }  else if (length(label_parts) == 2) { #Domestic species
      label <- paste(label_parts[1], label_parts[2])
      sound_type <- case_when(!(label %in% c("Non identifie", "Non identifié", "Bug informatique", "Déplacement animal")) ~ "Domestic animal",
                              TRUE ~ "Noise")
      
      confidence_level <- 1
      code_n_ind <- 0
      
    } else { #Noise
      if (label_parts[1] %in% c("Non", "Bug")) { # Non identifié ou Bug informatique
        label <- paste(label_parts[1], label_parts[2])
      } else {
        label <- label_parts[1]
      }
      sound_type <- "Noise"
      
      confidence_level <- 1
      code_n_ind <- 0
    }
    
    if (frequencies_annotated) {
      min_frequency <- gsub(".*\t(.+)\t.*", "\\1", line2)
      max_frequency <- sub(".*\t", "", line2)
    } else {
      min_frequency <- NA
      max_frequency <- NA
    }
    
    annotations <- rbind(annotations, c(recording_id, label, sound_type, initial_time, final_time, min_frequency, max_frequency, confidence_level, vocalization_type, code_n_ind))
  }
  
  close(conn)
}

colnames(annotations) <- c("recording_id", "label", "sound_type", "initial_time", "final_time", "min_frequency", "max_frequency", "confidence_level", "vocalization_type", "code_n_ind")



annotations <- annotations %>%
  mutate(recording_id = as.numeric(recording_id),
         initial_time = as.double(initial_time),
         final_time = as.double(final_time),
         min_frequency = as.double(min_frequency),
         max_frequency = as.double(max_frequency),
         confidence_level = as.integer(confidence_level),
         code_n_ind = as.integer(code_n_ind))

annotations <- annotations %>%
  mutate(species = case_when(sound_type == "Animal" ~ label,
                             TRUE ~ "-"))

annotations$file=gsub(".txt","",basename(files)[annotations$recording_id])

print(unique(annotations$file))

fwrite(annotations,paste0(Dir,"/annotations.csv"),sep=";")

