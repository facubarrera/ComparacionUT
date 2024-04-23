import datetime


def convert_epoca(year,doy,seg):
    hora=int(seg/60/60)
    minutos=int((seg/60/60-hora)*60)
    segundos=int(((seg/60/60-hora)*60-minutos)*60)
    mes,dia=doy2day(year,doy)
    diferencia=datetime.datetime(int(year), int(mes), int(dia), hora, minutos, segundos)-datetime.datetime(1858, 11, 17, 0, 0, 0) 
    mjd=diferencia.total_seconds()/86400
    return mjd
    
    
def doy2day(year,doy):
    diasnb=[31,28,31,30,31,30,31,31,30,31,30,31]
    diasb=[31,29,31,30,31,30,31,31,30,31,30,31]    
    mes=1
    resto=doy
    if not anio_bisiesto(year):
        while resto>0:
            day=resto
            resto=resto-diasnb[mes-1]
            mes=mes+1
    else:
        while resto>0:
            day=resto
            resto=resto-diasb[mes-1]
            mes=mes+1
    mes = mes-1
    return mes,day
	
		
	
	
def anio_bisiesto(year):
    if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
        return True
    else:
        return False