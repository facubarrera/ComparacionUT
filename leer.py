import numpy as np
import pandas as pd
from glob import glob
import io
import os
import subprocess
from conertidor import convert_epoca

def leer_sinex_crate(path):# Leo los sinex con formato de la BKG y USN
    m=len(path)
    tabla= pd.DataFrame({'SESION':[], 'MJD':[], 'YEAR':[], 'DOY':[],'EPOCA':[],'UT1':[],'LOD':[],'XPO':[],'XPOR':[]})#creo una tabla vacía a rellenar
    for archivo in path:#recorro los sinex guardados en el path
        sinex=open(archivo,'r')        
        contenido = sinex.readlines()#leo la lineas
        n=len(contenido)    
        for i in np.arange(0,n,1):#busco la sección donde esta la información que me interesa
            if '+SOLUTION/ESTIMATE' in contenido[i]:
                n_sol_i=i
            if '-SOLUTION/ESTIMATE' in contenido[i]:
                n_sol_f=i
        
        for i in np.arange(n_sol_i,n_sol_f+1,1):#Leo en la sección los parametros que me interesan
            if 'UT1 ' in contenido[i]:
                UT1d=contenido[i][47:68]
            if 'LOD ' in contenido[i]:
                LODd=contenido[i][47:68]
            if 'XPO ' in contenido[i]:
                XPOd=contenido[i][47:68]
            if 'XPOR ' in contenido[i]:
                XPORd=contenido[i][47:68]
                EPOCHe=contenido[i][34:39]
                DOYe=contenido[i][30:33]
                YEARe=contenido[i][27:29]
        UT1e=UT1d.replace('D','e')#convierto a float los datos
        UT1=float(UT1e)
        LODe=LODd.replace('D','e')
        LOD=float(LODe)
        XPOe=XPOd.replace('D','e')
        XPO=float(XPOe)
        XPORe=XPORd.replace('D','e')
        XPOR=float(XPORe)
        EPOCH=float(EPOCHe)
        DOY=float(DOYe)
        YEAR=float(YEARe)+2000
        MJD=convert_epoca(YEAR,DOY,EPOCH)#convierto a Modified Julian Date la época
        SESIONe=archivo[len(archivo)-28:len(archivo)-20]#busco el nombre de la sesión a partir del nombre del archivo
        valores=pd.DataFrame({'SESION':[SESIONe], 'MJD':[MJD], 'YEAR':[YEAR], 'DOY':[DOY], 'EPOCA':[EPOCH], 'UT1':[UT1],'LOD':[LOD],'XPO':[XPO],'XPOR':[XPOR]})#cargo los datos a una tabla de una sola linea
        tabla=pd.concat([tabla,valores], ignore_index=True)#concateno a la tabla con info que voy agregando en el for los valores anteriores
        #print(UT1e,LOD)
        sinex.close
        
    return tabla


def leer_sinex_srate_solout(path):#Leo los SINEX con el formato de IGN
    #print(path)
    m=len(path)
    tabla= pd.DataFrame({'SESION':[], 'MJDa':[], 'YEARa':[], 'DOYa':[],'EPOCAa':[],'UT1a':[], 'MJDb':[], 'YEARb':[], 'DOYb':[],'EPOCAb':[],'UT1b':[]})#Creo una tabla a rellenar

    for archivo in path:#trabajo sobre cada archivo
        sinex=open(archivo,'r')
        
        contenido = sinex.readlines()#leo las lineas del SINEX
        n=len(contenido)
    
        for i in np.arange(0,n,1):#encuentro la sección donde esta la información que me interesa
            if '+SOLUTION/ESTIMATE' in contenido[i]:
                n_sol_i=i
            if '-SOLUTION/ESTIMATE' in contenido[i]:
                n_sol_f=i

        
        l=0
        q=0
        for i in np.arange(n_sol_i,n_sol_f+1,1):#Busco los dos UT en la sección que predefinimos
            if ('UT ' in contenido[i]) and l==0:#pongo la condición de l==0 para que entre a este if una sola vez y que cuando encuentre el segundo párametro no me sobrecriba el primero
                UT1ad=contenido[i][47:68]
                EPOCHea=contenido[i][34:39]
                DOYea=contenido[i][30:33]
                YEARea=contenido[i][27:29]
                l=1
            if 'UT ' in contenido[i]:
                EPOCHeb=contenido[i][34:39]
                DOYeb=contenido[i][30:33]
                UT1bd=contenido[i][47:68]
                YEAReb=contenido[i][27:29]
               
        UT1ae=UT1ad.replace('D','e')#hago las modificaciones necesarias para cambiar los type a float
        UT1a=float(UT1ae)
        UT1be=UT1bd.replace('D','e')
        UT1b=float(UT1be)
        YEARa=float(YEARea)+2000
        YEARb=float(YEAReb)+2000
        EPOCHa=float(EPOCHea)
        DOYa=float(DOYea)
        EPOCHb=float(EPOCHeb)
        DOYb=float(DOYeb)
        MJDa=convert_epoca(YEARa,DOYa,EPOCHa)#convierto la epoca a MJD (Modified Julian Date)
        MJDb=convert_epoca(YEARb,DOYb,EPOCHb)
        SESIONe=archivo[len(archivo)-19:len(archivo)-11]
        valores=pd.DataFrame({'SESION':[SESIONe], 'MJDa':[MJDa], 'YEARa':[YEARa],'DOYa':[DOYa],'EPOCAa':[EPOCHa],'UT1a':[UT1a], 'MJDb':[MJDb], 'YEARb':[YEARb], 'DOYb':[DOYb],'EPOCAb':[EPOCHb],'UT1b':[UT1b]})#relleno con la info de la sesión
        tabla=pd.concat([tabla,valores], ignore_index=True)# agrego la info a la tabla
        #print(UT1e,LOD)
        sinex.close
    tabla['LOD']=(tabla.UT1a-tabla.UT1b)#calculo el LOD
	
    return tabla

def descargar(path):#Descargo los archivos de la BKG y de USN
    if not os.path.isdir("./bkg"):#creo las carpetas si no existen donde se van a descargar los SINEX.
        os.mkdir("./bkg")
    if not os.path.isdir("./usn"):
        os.mkdir("./usn")
    path0 = os.path.join(os.path.dirname(__file__), path, '*.snx')#me fijo que SINEX del IGN tengo guardados
    listasnx = glob(path0)
    for nombre in listasnx:#recorro SINEX por SINEX del IGN para descargar los demás.
        if nombre[60]=='X':#si el nombre del sinex tiene una X se dascarga con una forma y si no, con otra. Esto es debido a que la convencion de los nombres cambia en el 2023
            print('descargando',nombre[53:62])
			#Descargo si no esta descargado
            if not os.path.isfile('./bkg/'+ nombre[53:62] +'_bkg2023a.sni.gz'):
                shell_command = 'curl -c usr_cookies.dat -b usr_cookies.dat --netrc-file ./.netrc -L  "https://cddis.nasa.gov/archive/vlbi/ivsproducts/int_sinex/bkg2023a/'+ nombre[53:62] + '_bkg2023a.sni.gz" > ./bkg/'+ nombre[53:62] +'_bkg2023a.sni.gz'
                result = subprocess.run(shell_command, shell=True, capture_output=True, text=True)
                #Descomprimo
                shell_command = 'gzip -d -f ./bkg/'+ nombre[53:62] +'_bkg2023a.snx.gz'
                result = subprocess.run(shell_command, shell=True, capture_output=True, text=True)
            else:
                print('ya se descargo',nombre[53:62])
            if not os.path.isfile('./usn/'+ nombre[53:62] +'_usn2023c.sni.gz'):
                shell_command = 'curl -c usr_cookies.dat -b usr_cookies.dat --netrc-file ./.netrc -L  "https://cddis.nasa.gov/archive/vlbi/ivsproducts/int_sinex/usn2023c/'+ nombre[53:62] + '_usn2023c.sni.gz" > ./usn/'+ nombre[53:62] +'_usn2023c.sni.gz'
                result = subprocess.run(shell_command, shell=True, capture_output=True, text=True)
                shell_command = 'gzip -d -f ./usn/'+ nombre[53:62] +'_usn2023c.snx.gz'
                result = subprocess.run(shell_command, shell=True, capture_output=True, text=True)
            else:
                print('ya se descargo',nombre[53:62])
        else:
            print('descargando',nombre[53:68])
            if not os.path.isfile('./bkg/'+ nombre[53:68] +'_bkg2023a.sni.gz'):
                shell_command = 'curl -c usr_cookies.dat -b usr_cookies.dat --netrc-file ./.netrc -L  "https://cddis.nasa.gov/archive/vlbi/ivsproducts/int_sinex/bkg2023a/'+ nombre[53:68] + '_bkg2023a.sni.gz" > ./bkg/'+ nombre[53:68] +'_bkg2023a.sni.gz'
                result = subprocess.run(shell_command, shell=True, capture_output=True, text=True)
                shell_command = 'gzip -d -f ./bkg/'+ nombre[53:68] +'_bkg2023a.sni.gz'
                result = subprocess.run(shell_command, shell=True, capture_output=True, text=True)
            else:
                print('ya se descargo',nombre[53:68])
            if not os.path.isfile('./usn/'+ nombre[53:68] +'_usn2023c.sni.gz'):
                shell_command = 'curl -c usr_cookies.dat -b usr_cookies.dat --netrc-file ./.netrc -L  "https://cddis.nasa.gov/archive/vlbi/ivsproducts/int_sinex/usn2023c/'+ nombre[53:68] + '_usn2023c.sni.gz" > ./usn/'+ nombre[53:68] +'_usn2023c.sni.gz'
                result = subprocess.run(shell_command, shell=True, capture_output=True, text=True)
                shell_command = 'gzip -d -f ./usn/'+ nombre[53:68] +'_usn2023c.sni.gz'
                result = subprocess.run(shell_command, shell=True, capture_output=True, text=True)
            else:
                print('ya se descargo',nombre[53:68])
            
def interpolateIGN(tabla,tablaint):#Interpolo los valores del IGN hacia la epoca en que estiman los de BKG
    tableUT1=pd.Series([])
    tableMJD=pd.Series([])
    i=0
    for j in tabla.SESION:
        if (tablaint.SESION==j).any():#Busco si la sesion del IGN esta en la BKG
            LODn=np.array(tabla.UT1b[tabla.SESION==j])-np.array(tabla.UT1a[tabla.SESION==j])
            UT1int=np.array(tabla.UT1a[tabla.SESION==j])+LODn*np.array((tablaint.MJD[tablaint.SESION==j])-np.array(tabla.MJDa[tabla.SESION==j]))#Interpolo linealmente
            tableMJD[i]=np.array(tablaint.MJD[tablaint.SESION==j])
            tableUT1[i]=UT1int
            i=i+1
        else:
            tableMJD[i] = None
            i=i+1
    tabla['UT1int']=tableUT1
    tabla['MJDint']=tableMJD
    return tabla
    
def interpolateUSN(tabla,tablaint):#Interpolo los valores del USN hacia la epoca en que estiman los de BKG
    tableUT1=pd.Series([])
    tableMJD=pd.Series([])
    i=0
    for j in tabla.SESION:
        if (tablaint.SESION==j).any():#Busco si la sesion del USN esta en la BKG
            LOD=np.array(tabla.LOD[tabla.SESION==j])
            UT1int=np.array(tabla.UT1[tabla.SESION==j])+LOD*np.array((tablaint.MJD[tablaint.SESION==j])-np.array(tabla.MJD[tabla.SESION==j]))
            tableMJD[i]=np.array(tablaint.MJD[tablaint.SESION==j])
            tableUT1[i]=UT1int
            i=i+1
        else:
            tableMJD[i] = None
            tableUT1[i] = None
            i=i+1
    tabla['UT1int']=tableUT1
    tabla['MJDint']=tableMJD
    return tabla 
    
    
    
    
    
    
    
    

