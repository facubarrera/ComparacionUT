import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from glob import glob
import leer
import numpy as np

#Descargo los SINEX de la BKG y de USN que coinciden con los del IGN
leer.descargar('semanaign1')

#Listo los SINEX que tengo en cada carpeta
path_bkg = os.path.join(os.path.dirname(__file__), 'bkg', '*.sni')
sinex_bkg = glob(path_bkg)
path_usn = os.path.join(os.path.dirname(__file__), 'usn', '*.sni')
sinex_usn = glob(path_usn)
path_ign = os.path.join(os.path.dirname(__file__), 'semanaign1', '*.snx')
sinex_ign = glob(path_ign)

#Leo la información SINEX
tabla_bkg =leer.leer_sinex_crate(sinex_bkg)
tabla_usn =leer.leer_sinex_crate(sinex_usn)
tabla_ign =leer.leer_sinex_srate_solout(sinex_ign)

#Como el IGN entrega UT1-UTC y los demas entregan UT1-TAI, y la relación entre UTC y TAI es TAI-UTC=37000ms, entonces UT1-UTC-37000MS=UT1-(UTC+37000ms)=UT1-TAI
tabla_ign.UT1a=tabla_ign.UT1a-37000
tabla_ign.UT1b=tabla_ign.UT1b-37000
LOD_ign=tabla_ign.LOD# guardamos la columna de LOD en una variables

#Interpolamos las observaciones del IGN y USN a las espocas de observación de la BKG para hacerlos comparables
tabla_ign=leer.interpolateIGN(tabla_ign,tabla_bkg)
tabla_usn=leer.interpolateUSN(tabla_usn,tabla_bkg)


#Buscamos las pendientes de las rectas que representan la variación de los parámetros
pendiente_bkg= -tabla_bkg.LOD
pendiente_usn= -tabla_usn.LOD
pendiente_ign= -(LOD_ign)



plt.figure(1)
#Grafico todos para una misma época
plt.plot(tabla_ign.MJDint,tabla_ign.UT1int,'r.',label="UT1 IGN")
plt.plot(tabla_usn.MJDint,tabla_usn.UT1int,'g.',label="UT1 USN")
plt.plot(np.array(tabla_bkg.MJD),np.array(tabla_bkg.UT1),'b.',label="UT1 BKG")

#Grafico las rectas con pendientes para la variación de UT1-UTC en cada sesión
for i in np.arange(0,len(pendiente_bkg),1):
    epocha=tabla_bkg.MJD[i]-0.5;epochb=tabla_bkg.MJD[i]+0.5;
    uta=tabla_bkg.UT1[i]+pendiente_bkg[i]*(-0.5);utb=tabla_bkg.UT1[i]+pendiente_bkg[i]*0.5
    plt.plot([epocha,epochb],[uta,utb],'b--')
for i in np.arange(0,len(pendiente_usn),1):
    epocha=tabla_usn.MJD[i]-0.5;epochb=tabla_usn.MJD[i]+0.5;
    uta=tabla_usn.UT1[i]+pendiente_usn[i]*(-0.5);utb=tabla_usn.UT1[i]+pendiente_usn[i]*0.5
    plt.plot([epocha,epochb],[uta,utb],'g--')
for i in np.arange(0,len(tabla_ign.DOYa),1):
    epocha=tabla_ign.MJDint[i]-0.5;epochb=tabla_ign.MJDint[i]+0.5;
    uta=tabla_ign.UT1int[i]+pendiente_ign[i]*(-0.5);utb=tabla_ign.UT1int[i]+pendiente_ign[i]*0.5
    plt.plot([epocha,epochb],[uta,utb],'r--')

plt.grid()
plt.ylabel('UT1-UTC [ms]')
plt.xlabel('MJD')
plt.title('UT1-UTC')
plt.legend()
plt.savefig('./graficos/dx_valores.png')

plt.show()
diferenciaLOD_USN=np.mean(tabla_usn.LOD-tabla_ign.LOD)
diferenciaLOD_BKG=np.mean(tabla_bkg.LOD-tabla_ign.LOD)
diferenciaLOD_CONJUNTO=np.mean(pd.concat([tabla_usn.LOD-tabla_ign.LOD,tabla_bkg.LOD-tabla_ign.LOD], ignore_index=True))

