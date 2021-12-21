#-------------------------------------------------
#
# Project created by QtCreator 2017-02-04T09:52:58
#
#-------------------------------------------------

QT       += core gui widgets


TARGET = TadaridaL
TEMPLATE = app

win32 {
DEFINES += BUILDTIME=\\\"$$system('echo %time%')\\\"
DEFINES += BUILDDATE=\\\"$$system('echo %date%')\\\"
} else {
DEFINES += BUILDTIME=\\\"$$system(date '+%H:%M.%s')\\\"
DEFINES += BUILDDATE=\\\"$$system(date '+%d/%m/%y')\\\"
}


SOURCES += main.cpp\
        TadaridaMainWindow.cpp \
    detec.cpp \
    detectreatment.cpp \
    fenim.cpp \
    etiquette.cpp \
    loupe.cpp \
    recherche.cpp \
    param.cpp

HEADERS  += TadaridaMainWindow.h \
    detec.h \
    detectreatment.h \
    fenim.h \
    etiquette.h \
    loupe.h \
    recherche.h \
    param.h

INCLUDEPATH += "Headers" 

win32: LIBS += -L$$PWD/Libs/ -llibfftw3f-3 -llibsndfile-1
