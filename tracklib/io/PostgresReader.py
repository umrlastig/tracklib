# -*- coding: utf-8 -*-
'''
Build a trace from data retrieved from a PostgreSQL database
'''

from tracklib.core.GPSTime import GPSTime
from tracklib.core.Obs import Obs
from tracklib.core.Coords import ENUCoords
import tracklib.core.Track as t
from tracklib.core.TrackCollection import TrackCollection
import tracklib.core.core_utils as utils

try:
    import psycopg2
except ImportError:
    print("Warning: psycopg2 library must be installed to use database interface")


class PostgresReader:
    
    HOST = 'localhost'
    PORT = '5432'
    USER = 'glagaffe'
    PASSWD = 'bubulle'
    DATABASE = 'madatabase'
    
    def initParam(param):
        if 'host' in param and param['host'] != None:
            PostgresReader.HOST = param['host']
        
        if 'port' in param and param['port'] != None:
            PostgresReader.PORT = param['port']
            
        if 'user' in param and param['user'] != None:
            PostgresReader.USER = param['user']
            
        if 'password' in param and param['password'] != None:
            PostgresReader.PASSWD = param['password']
            
        if 'database' in param and param['database'] != None:
            PostgresReader.DATABASE = param['database']
    

    def readFromDataBase(sql, id_T, id_E, id_N, id_U = -1):
        '''
        Read GPS track from a PostgreSQL database 
        param sql
        '''
        
        # 2020-08-06 15:58:33
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        # On se connecte à la base de données
        conn = psycopg2.connect(host=PostgresReader.HOST, port=PostgresReader.PORT, database=PostgresReader.DATABASE, user=PostgresReader.USER, password=PostgresReader.PASSWD)
            
        # ---------------------------------------------------------------------
        cur = conn.cursor()
            
        cur.execute(sql)
        res = cur.fetchall()     
        
        track = t.Track()
        for row in res:
            E = row[id_E]
            N = row[id_N]
            if (id_U < 0):
                U = 0
            else:
                U = (float)(row[id_U])

            # On controle le format de la date
            time = GPSTime.readTimestamp(str(row[id_T]).strip())
            point = Obs(ENUCoords(E,N,U), time)
            track.addObs(point)
                    
        cur.close()
            
        return track


    def getListeTrace(sql):
        '''
        Retourne la liste des identifiants des traces
        param sql
        '''
        IDTRACES = []
        
        # On se connecte à la base de données
        conn = psycopg2.connect(host=PostgresReader.HOST, port=PostgresReader.PORT, database=PostgresReader.DATABASE, user=PostgresReader.USER, password=PostgresReader.PASSWD)
            
        # ---------------------------------------------------------------------
        cur = conn.cursor()
            
        cur.execute(sql)
        res = cur.fetchall()     
            
        for row in res:
            idTrace = str(row[0])
            IDTRACES.append(idTrace)
                    
        cur.close()
            
        return IDTRACES
    
    
    def readCollectionFromDataBase(sql, tuid, id_T, id_E, id_N, id_U = -1):
        '''
        Charge plusieurs traces à partir d'une requete.
        Bien trié par identifiant de la trace
        Retourne une collection de trace
        '''
        TRACES = []
        
        GPSTime.setReadFormat("4Y-2M-2D 2h:2m:2s")
        
        # On se connecte à la base de données
        conn = psycopg2.connect(host=PostgresReader.HOST, port=PostgresReader.PORT, database=PostgresReader.DATABASE, user=PostgresReader.USER, password=PostgresReader.PASSWD)
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchall()     
        
        idOld = "-1"
        track = t.Track()
        for row in res:
            idTrace = str(row[tuid])
            
            if idOld != idTrace:
                if idOld != "-1":
                    track.sort()
                    TRACES.append(track)
                track = t.Track()
                track.uid = idTrace
                
            E = row[id_E]
            N = row[id_N]
            if (id_U < 0):
                U = 0
            else:
                U = (float)(row[id_U])

            # On controle le format de la date
            time = GPSTime.readTimestamp(str(row[id_T]).strip())
            point = Obs(ENUCoords(E,N,U), time)
            track.addObs(point)
            
            idOld = idTrace
        
        # La derniere trace
        track.sort()
        TRACES.append(track)
        
        cur.close()
        
        collection = TrackCollection(TRACES)
        return collection
        

    def writeCollectionToDataBase(collection):
        '''
        Charge les traces dans une table TRACKLIB.
        les paramètres de base (lon, lat, timestamp, id, trace)
        et les AF
        '''
        
        # On se connecte à la base de données
        conn = psycopg2.connect(host=PostgresReader.HOST, port=PostgresReader.PORT, database=PostgresReader.DATABASE, user=PostgresReader.USER, password=PostgresReader.PASSWD)
        cur = conn.cursor()        
        
        # -----
        # CREATE TABLE IF NOT EXISTS
        sql = " SELECT count(*) as nb FROM information_schema.tables "
        sql = sql + " WHERE  table_schema = 'public' AND table_name = 'tracklib' "
        cur.execute(sql)
        res = cur.fetchall()
        nb = res[0][0]
        
        # Partie AF
        traces = collection.getTracks()
        trace = traces[0]
        listAF =  trace.getListAnalyticalFeatures()
        sqlCAF = ""
        sqlIAF = ""
        for af in listAF:
            sqlCAF += " " + af + " double precision, "
            sqlIAF += af + ", "
        
        if nb > 0:
            #  On supprime
            sql = " DROP TABLE public.tracklib "
            cur.execute(sql)
            #conn.commit()
            
            #  On re crée
            sql = " CREATE TABLE public.tracklib ( "
            sql += "   trace integer NOT NULL, "
            sql += "   idpoint integer NOT NULL, "
            sql += "   gpstime character varying(50), "
            sql += "   x double precision NOT NULL, "
            sql += "   y double precision NOT NULL, "
            sql += "   ele double precision NOT NULL, "
            sql += "   point geometry(Point, 2154), "
            sql += sqlCAF
            sql += "   CONSTRAINT pk_tracklib PRIMARY KEY (trace, idpoint) "
            sql += " ) "
            cur.execute(sql)
            #conn.commit()
        
        # On ajoute les lignes
        for trace in collection.getTracks():
            cpt = 1
            for (i, obs) in enumerate(trace.getObsList()):
        
                sql = " INSERT INTO tracklib (trace, idpoint, gpstime, x, y, ele, "
                sql += sqlIAF + " point) VALUES ("
                sql += trace.uid + ", "
                sql += str(cpt) + ", "
                sql += "'" + str(obs.timestamp) + "', "
                sql += str(obs.position.E) + ", "
                sql += str(obs.position.N) + ", "
                sql += str(obs.position.U) + ", "
                for af in listAF:
                    #print (af)
                    val = trace.getObsAnalyticalFeature(af, i)
                    if utils.isnan(val):
                        val = -1
                    sql += str(val) + ", "
                sql += " ST_SetSRID(ST_MakePoint( " + str(obs.position.E) + ", " 
                sql += str(obs.position.N) + "), 2154)) "
                print (sql)
                cur.execute(sql)
                conn.commit()
                cpt += 1
        
        conn.commit()
        cur.close()
        
        