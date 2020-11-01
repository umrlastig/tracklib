# -------------------------- Plot -------------------------------
# Class to plot GPS tracks and its AF
# ----------------------------------------------------------------

import matplotlib.pyplot as plt

# Pour le calcul des échelles on a besoin du max 
import tracklib.core.Operator as Operator

# Nan
import tracklib.core.core_utils as utils

#MODE_REPRESENT_TRACK2D = 1
#MODE_REPRESENT_SPEED_PROFIL = 2

COLOR_POINT = ['gold', 'orangered', 'dodgerblue', 'purple', 'lime', 'turquoise']


class Plot:
    

    def __init__(self, track):
        self.track = track
        
        
    def plot(self, template='TRACK2D', afs = []):
        '''
        Représentation d'une trace ou du profil de la trace.
        
        Pour visualiser une trace: template=TRACK2D
        Pour visualiser un profil, le nom du template doit respecter:
            XXX_YYYY_PROFILE
        avec:
            XXX: SPATIAL ou TEMPORAL
            YYY: ALTI, SPEED
            
            
        Si on affiche le profile de la trace on peut visualiser aussi des 
        indicateurs de marqueurs ou de transition.
        
        '''
        
        X = []
        Y = []
        ymax = -1  # y max
        xmin = -1
        xmax = -1
        
        tablegend = []
        tabplot = []
        
        nomaxes = template.split('_')
        if len(nomaxes) == 3:
            axe1 = nomaxes[0]
            if axe1 == 'SPATIAL':
                S = self.track.compute_abscurv()
                X = S
                xmin = self.track.operate(Operator.Operator.MIN, 'abs_curv')
                xmax = self.track.operate(Operator.Operator.MAX, 'abs_curv')
            elif axe1 == 'TEMPORAL':
                T = self.track.getT()
                X = T
                xmin = self.track.operate(Operator.Operator.MIN, 't')
                xmax = self.track.operate(Operator.Operator.MAX, 't')
            else:
                X = self.track.getX()
                
            axe2 = nomaxes[1]
            if axe2 == 'SPEED':
                V = self.track.estimate_speed()
                Y = V
                ymax = self.track.operate(Operator.Operator.MAX, 'speed')
            elif axe2 == 'ALTI':
                U = self.track.getZ()
                #print (U)
                Y = U
                ymax = self.track.operate(Operator.Operator.MAX, 'z')
            else:
                Y = self.track.getY()
                
            axe3 = 'PROFIL'
            tablegend.append(axe3)
        else:
            X = self.track.getX()
            Y = self.track.getY()
            axe1 = ''
            axe2 = ''
            axe3 = 'Track'
            xmin = self.track.operate(Operator.Operator.MIN, 'x')
            xmax = self.track.operate(Operator.Operator.MAX, 'x')

    
        fig, ax1 = plt.subplots(figsize=(10, 3))
        l = ax1.plot(X, Y, '-', color='forestgreen', label=axe3)
        tabplot.append(l)
        # plt.ylim([0, ymax + len(afs) * 0.3])
        plt.xlim([xmin, xmax])
        
        
        # ---------------------------------------------------------------------
        #   Ajout de la représentation des AF.
        # ---------------------------------------------------------------------
        limit = ymax + 0.5
        for (indice, af_name) in enumerate(afs):
            
            if self.track.isAFTransition(af_name):
            
                tabmarqueurs = self.track.getAnalyticalFeature(af_name)
                marqueurs = set(tabmarqueurs)
                if utils.NAN in marqueurs:
                    marqueurs.remove(utils.NAN)
            
                xaf = []
                yaf = []
                for i in range(len(tabmarqueurs)):
                    val = tabmarqueurs[i]
                    if val == 1:
                        xaf.append(X[i])
                        yaf.append(limit + indice*0.3)
                        
                l = ax1.plot(xaf, yaf, 'o', color=COLOR_POINT[indice], markersize=2.5, label=af_name)
                tabplot.append(l)
                tablegend.append(af_name)
            
            
        # ---------------------------------------------------------------------
        # Legend

        ax1.set(xlabel=axe1, ylabel=axe2)

        if len(tabplot) > 1:
            #chartBox = ax1.get_position()
            #ax1.set_position([chartBox.x0, chartBox.y0, chartBox.width, chartBox.height*0.8])
            ax1.legend(tabplot, 
              labels=tablegend, 
              loc='lower center', 
              borderaxespad=0.1, 
              title='', 
              bbox_to_anchor=(0.5, -0.55))
        
        
        
    
    def plotAnalyticalFeature(self, af_name, template='PLOT'):
        '''
        Plot AF values by abcisse curvilign.
        TODO: plot gérer l'axe des abscisses.
        '''
        
        self.track.compute_abscurv()
        
        fig, ax1 = plt.subplots(figsize=(8, 3))
        ax1.set(xlabel='absciss curvilign')
        
        if template == 'BOXPLOT':
            ax1.set_title(af_name)
            ax1.boxplot(self.track.getAnalyticalFeature(af_name), vert=False)
        else:
            ax1.plot(self.track.getAbsCurv(), self.track.getAnalyticalFeature(af_name), 'b-', markersize=2.5) 
        
        
    def show(self):
        plt.show()
        
        
    
    
    