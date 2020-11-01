"""
"""
import tracklib.algo.AlgoAF as algo
from tracklib.io.PostgresReader import PostgresReader

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
#      Chargement des fichiers
# ------------------------------------------------------------------------------------------------
sql = ' Select trace, idpoint, '
sql = sql + '         ST_X(ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 3857), 2154)) as lon, '
sql = sql + '         ST_Y(ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 3857), 2154)) as lat, '
sql = sql + '         timestamp as datetxt '
sql = sql + ' From c2c_gpx '
#sql = sql + ' Where trace = 352942 or trace = 184626 '
sql = sql + ' Where trace = 184626 '
sql = sql + ' Order by trace, timestamp '

param = {'host':'localhost', 'database':'cotation', 'user':'test', 'password':'test'}
PostgresReader.initParam(param)
trace = PostgresReader.readFromDataBase(sql, 4, 2, 3, -1)
trace.summary()
print ()

trace.estimate_speed()
trace.compute_abscurv()

# fig = plt.figure(figsize=(12,3))

S = trace.getAbsCurv()
V = trace.getSpeed()


trace.plot()
trace.plot('SPATIAL_SPEED_PROFIL')

trace.plotAnalyticalFeature(algo.BIAF_SPEED)
trace.plotAnalyticalFeature(algo.BIAF_SPEED, 'BOXPLOT')
