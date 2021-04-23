# -------------------------- Plot -------------------------------
# Class to plot GPS tracks and its AF
# ----------------------------------------------------------------

import matplotlib.pyplot as plt
import tracklib.algo.Analytics as algo
import tracklib.core.Operator as Operator
import tracklib.core.Utils as utils

#MODE_REPRESENT_TRACK2D = 1
#MODE_REPRESENT_SPEED_PROFIL = 2

COLOR_POINT = ['gold', 'orangered', 'dodgerblue', 'purple', 'lime', 'turquoise']


class Plot:
    

    def __init__(self, track):
        self.track = track
        self.color = 'forestgreen'
        self.w = 10
        self.h = 3
        self.pointsize = 5
        
    def __isAFTransition(track, af_name):
        '''
        Return true if AF is transition marker.
        For example return true if AF values are like: 
            000000000000010000100000000000000000001000000100000
        Values are contained in {0, 1}. 1 means there is a regime change
        '''
        tabmarqueurs = track.getAnalyticalFeature(af_name)
        marqueurs = set(tabmarqueurs)
        if utils.NAN in marqueurs:
            marqueurs.remove(utils.NAN)
        if len(marqueurs.intersection([0, 1])) == 2:
            return True
        else:
            return False		
		
    
    def plot(self, type='LINE', af_name = '', cmap=-1):

        '''
        Représentation d'une trace sous forme de ligne ou de point.
        On peut visualiser la valeur d'une AF avec une couleur sur les points.
        '''
    
        fig, ax1 = plt.subplots(figsize=(6, 3))
        
        X = self.track.getX()
        Y = self.track.getY()
        xmin = self.track.operate(Operator.Operator.MIN, 'x')
        xmax = self.track.operate(Operator.Operator.MAX, 'x')
        
        if af_name != None and af_name != '':
            
            if cmap == -1:
                cmap = utils.getColorMap((255, 0, 0), (32, 178, 170))
            
            values = self.track.getAnalyticalFeature(af_name)
            
            plt.scatter(X, Y, c = values, cmap = cmap, s=self.pointsize)
            plt.colorbar()
        
        elif type == 'POINT':
            #ax1.plot(X, Y, 'o', color=self.color, s=5)
            plt.scatter(X, Y, s=self.pointsize, c=self.color)
        
        else:
            ax1.plot(X, Y, '-', color=self.color)
        
        # TODO : tenir compte du type Coord
        ax1.set(xlabel='E', ylabel='N')
        
        plt.xlim([xmin, xmax])
        plt.title('Track ' + str(self.track.uid))
        
    
    
    def plotAnalyticalFeature(self, af_name, template='BOXPLOT'):
        '''
        Plot AF values by abcisse curvilign.
        '''
        if (not self.track.hasAnalyticalFeature(algo.BIAF_ABS_CURV)):
            self.track.compute_abscurv()
        
        #if template == 'BOXPLOT':
        self.__plotBoxplot(af_name)
        
    
        
    def __plotBoxplot(self, af_name):
        
        fig, ax1 = plt.subplots(figsize=(6, 2))
        ax1.set(xlabel='absciss curvilign')
        ax1.set_title(af_name + ' observations boxplot')
        ax1.boxplot(self.track.getAnalyticalFeature(af_name), vert=False)



    def plotProfil(self, template = 'SPATIAL_SPEED_PROFIL', afs = []):
        '''
        TEMPLATE: 
            SPATIAL_SPEED_PROFIL, SPATIAL_ALTI_PROFIL,
                  TEMPORAL_SPEED_PROFIL, TEMPORAL_ALTI_PROFIL
                  
        On sait déjà que l'abscur est calculée si nécessaire
                  
        afs: uniquement si 'isAFTransition'
        '''
        
        tabplot = []
        tablegend = []
        nomaxes = template.split('_')
        
        axe1 = nomaxes[0]
        if axe1 == 'SPATIAL':
            X = self.track.compute_abscurv()
            xmin = self.track.operate(Operator.Operator.MIN, 'abs_curv')
            xmax = self.track.operate(Operator.Operator.MAX, 'abs_curv')
            xtitle = 'curvilinear abscissa'
        elif axe1 == 'TEMPORAL':
            X = self.track.getT()
            xmin = self.track.operate(Operator.Operator.MIN, 't')
            xmax = self.track.operate(Operator.Operator.MAX, 't')
            xtitle = 'timestamp'
            
        axe2 = nomaxes[1]
        if axe2 == 'SPEED':
            Y = self.track.estimate_speed()
            ymax = self.track.operate(Operator.Operator.MAX, 'speed')
        elif axe2 == 'ALTI':
            Y = self.track.getZ()
            ymax = self.track.operate(Operator.Operator.MAX, 'z')
        else:
            Y = self.track.getAnalyticalFeature(axe2)
            ymax = self.track.operate(Operator.Operator.MAX, axe2)
       
        tablegend.append('PROFIL')
        
        fig, ax1 = plt.subplots(figsize=(10, 3))

        l = ax1.plot(X, Y, '-', color=self.color)

        tabplot.append(l)
        plt.xlim([xmin, xmax])
        
        ax1.set(xlabel=xtitle, ylabel=axe2)
        ax1.set_title("'" + axe2 + "' profil according to " + xtitle)
        
        
        # ---------------------------------------------------------------------
        #   Ajout de la représentation des AF.
        # ---------------------------------------------------------------------
        limit = ymax + 0.5
        for (indice, af_name) in enumerate(afs):

            if __isAFTransition(self.track, af_name):
                print ('---')
            
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
        if len(tabplot) > 1:
            #chartBox = ax1.get_position()
            #ax1.set_position([chartBox.x0, chartBox.y0, chartBox.width, chartBox.height*0.8])
            ax1.legend(tabplot, 
              labels=tablegend, 
              loc='lower center', 
              borderaxespad=0.1, 
              title='', 
              bbox_to_anchor=(0.5, -0.55))
        
        
        if (len(afs)>0 and afs[0] != None):
            plt.title(afs[0])
            
        

    def __plotProfile(self, af_name):
        
        fig, ax1 = plt.subplots(figsize=(8, 3))
        ax1.set(xlabel='absciss curvilign')
        
        ax1.plot(self.track.getAbsCurv(), self.track.getAnalyticalFeature(af_name), 'b-', markersize=2.5) 
                
        
    
        
    
    
        
    
        
        
    
    
    